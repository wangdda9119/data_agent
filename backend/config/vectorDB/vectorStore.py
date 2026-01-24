import os
import time
import re
import unicodedata
import logging
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterable, Set

from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------
# Logging
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vectorstore.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("VectorStore")

load_dotenv()


# -----------------------
# Watchdog handler
# -----------------------
class PDFWatcher(FileSystemEventHandler):
    def __init__(self, vector_store: "VectorStore"):
        self.vector_store = vector_store

    def on_created(self, event):
        try:
            if event.is_directory:
                return
            if str(event.src_path).lower().endswith(".pdf"):
                self.vector_store.process_file(Path(event.src_path))
        except Exception:
            logger.error("on_created error:\n%s", traceback.format_exc())

    def on_moved(self, event):
        try:
            if event.is_directory:
                return
            if str(event.dest_path).lower().endswith(".pdf"):
                self.vector_store.process_file(Path(event.dest_path))
        except Exception:
            logger.error("on_moved error:\n%s", traceback.format_exc())


# -----------------------
# VectorStore (LangChain FAISS)
# -----------------------
class VectorStore:
    """
    - 저장: FAISS.save_local(dir) -> dir/index.faiss + dir/index.pkl
    - 로드: FAISS.load_local(dir, embeddings, allow_dangerous_deserialization=True)

    추가:
    - 노이즈 정규식 제거 + 유니코드 정규화 + 불용어 제거 -> 청킹 -> 임베딩
    - search 기본 topk=8 + (top_k=...) 호환
    - Windows에서 비ASCII 경로(예: "벡터디비")로 FAISS 저장 실패 방지를 위한 경로 안전화
    """

    DEFAULT_STOPWORDS_KO: Set[str] = {
        "은", "는", "이", "가", "을", "를", "에", "의", "와", "과", "도", "로", "으로",
        "에서", "에게", "한테", "께", "및", "또는", "그리고", "또한", "등", "수", "좀",
        "더", "때", "것", "거", "때문", "관련", "대해", "대한"
    }
    DEFAULT_STOPWORDS_EN: Set[str] = {
        "a", "an", "the", "and", "or", "to", "of", "in", "on", "for", "with", "as", "at", "by",
        "is", "are", "was", "were", "be", "been", "it", "this", "that", "these", "those"
    }

    def __init__(
        self,
        embedding_model_name: str = None,
        chunk_size: int = None,
        chunk_overlap: int = None,
        vector_db_path: str = None,
        embedded_folder: str = None,
        use_stopwords: bool = True,
        extra_stopwords: Optional[Iterable[str]] = None,
    ):
        self.embedding_model_name = embedding_model_name or os.getenv(
            "EMBEDDING_MODEL", "text-embedding-3-small"
        )
        self.chunk_size = int(chunk_size or os.getenv("CHUNK_SIZE", "512"))
        self.chunk_overlap = int(chunk_overlap or os.getenv("CHUNK_OVERLAP", "50"))

        raw_db_path = str(vector_db_path or os.getenv("VECTOR_DB_PATH", "vector_db"))
        self.vector_db_path = self._make_faiss_path_safe(raw_db_path)

        self.embedded_folder = str(embedded_folder or os.getenv("EMBEDDED_FOLDER", "embedded"))

        self.use_stopwords = bool(use_stopwords)
        self.stopwords: Set[str] = set(self.DEFAULT_STOPWORDS_KO) | set(self.DEFAULT_STOPWORDS_EN)
        if extra_stopwords:
            self.stopwords |= {str(x).strip() for x in extra_stopwords if str(x).strip()}

        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        self.vector_store: Optional[FAISS] = None
        self.observer: Optional[Observer] = None

        # 시작 시 기존 벡터스토어가 있으면 자동 로드
        self.load_existing_vector_store()

        logger.info(
            "VectorStore init | model=%s, chunk=%s, overlap=%s, db=%s, embedded=%s, stopwords=%s",
            self.embedding_model_name,
            self.chunk_size,
            self.chunk_overlap,
            self.vector_db_path,
            self.embedded_folder,
            self.use_stopwords,
        )

    # -----------------------
    # Path safety (Windows + FAISS)
    # -----------------------
    def _make_faiss_path_safe(self, path_str: str) -> str:
        p = Path(path_str)

        def _is_ascii(s: str) -> bool:
            try:
                s.encode("ascii")
                return True
            except Exception:
                return False

        if _is_ascii(str(p)):
            return str(p)

        if not p.is_absolute():
            logger.warning(
                "VECTOR_DB_PATH has non-ascii path (%s). FAISS may fail on Windows. "
                "Using fallback: vector_db",
                path_str,
            )
            return "vector_db"

        safe = p.parent / "vector_db"
        logger.warning(
            "VECTOR_DB_PATH has non-ascii path (%s). FAISS may fail on Windows. "
            "Using fallback: %s",
            path_str,
            str(safe),
        )
        return str(safe)

    # -----------------------
    # Persistence (index.faiss + index.pkl)
    # -----------------------
    def has_existing_vector_store(self) -> bool:
        db_dir = Path(self.vector_db_path)
        faiss_file = db_dir / "index.faiss"
        pkl_file = db_dir / "index.pkl"
        return faiss_file.exists() and pkl_file.exists()

    def load_existing_vector_store(self) -> bool:
        try:
            if not self.has_existing_vector_store():
                logger.info("No existing vector store found.")
                return False

            self.vector_store = FAISS.load_local(
                self.vector_db_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info("Loaded existing vector store from: %s", self.vector_db_path)
            return True
        except Exception:
            logger.error("Failed to load existing vector store:\n%s", traceback.format_exc())
            self.vector_store = None
            return False

    def save_vector_store(self) -> None:
        self._save_vector_store()

    def _save_vector_store(self) -> None:
        if self.vector_store is None:
            logger.warning("No vector store to save.")
            return
        Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(self.vector_db_path)
        logger.info("Saved vector store to: %s (index.faiss + index.pkl)", self.vector_db_path)

    # -----------------------
    # Count documents (chunks)
    # -----------------------
    def count_documents(self) -> int:
        """
        create_vector_db.py에서 기대하는 메서드.
        FAISS docstore에 들어있는 문서(=청크) 개수를 반환.
        """
        try:
            if self.vector_store is None:
                return 0
            store = getattr(self.vector_store, "docstore", None)
            d = getattr(store, "_dict", {}) if store else {}
            return len(d) if isinstance(d, dict) else 0
        except Exception:
            logger.error("count_documents failed:\n%s", traceback.format_exc())
            return 0

    # -----------------------
    # Text cleaning pipeline
    # -----------------------
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r"[\r\n\t]+", " ", text)
        text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", " ", text)
        text = re.sub(r"\\[nrtqvf]", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()
        return text

    def _remove_stopwords(self, text: str) -> str:
        if not text or not self.use_stopwords:
            return text
        tokens = text.split()
        kept = [t for t in tokens if t not in self.stopwords]
        return " ".join(kept).strip()

    def _preprocess_documents(self, documents):
        cleaned_docs = []
        for d in documents:
            content = getattr(d, "page_content", "") or ""
            content = self._clean_text(content)
            content = self._remove_stopwords(content)

            if len(content) < 20:
                continue

            d.page_content = content
            cleaned_docs.append(d)
        return cleaned_docs

    # -----------------------
    # Build / Update
    # -----------------------
    def create_new_embeddings(self, folder_path: Optional[str] = None, reset_db: bool = True) -> None:
        target_folder = folder_path or self.embedded_folder
        target_folder_path = Path(target_folder)
        target_folder_path.mkdir(parents=True, exist_ok=True)

        if reset_db:
            db_dir = Path(self.vector_db_path)
            if db_dir.exists():
                for name in ["index.faiss", "index.pkl"]:
                    p = db_dir / name
                    if p.exists():
                        p.unlink()
                try:
                    if not any(db_dir.iterdir()):
                        db_dir.rmdir()
                except Exception:
                    pass

        self.vector_store = None
        logger.info("Rebuilding embeddings from folder: %s", str(target_folder_path))
        self.embed_folder(str(target_folder_path))
        self._save_vector_store()

    def embed_folder(self, folder_path: str) -> None:
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"Folder not found: {folder_path}")

        pdf_files = list(folder.glob("**/*.pdf"))
        logger.info("found pdfs: %d", len(pdf_files))

        for i, pdf in enumerate(pdf_files, 1):
            logger.info("[%d/%d] embed: %s", i, len(pdf_files), pdf.name)
            self.process_file(pdf)

        logger.info("Folder embedding done: %s", folder_path)

    def _wait_until_file_stable(self, path: Path, timeout_sec: int = 30) -> bool:
        start = time.time()
        last_size = -1
        stable_count = 0

        while time.time() - start < timeout_sec:
            if not path.exists():
                time.sleep(0.2)
                continue

            size = path.stat().st_size
            if size == last_size and size > 0:
                stable_count += 1
                if stable_count >= 3:
                    return True
            else:
                stable_count = 0
                last_size = size

            time.sleep(0.2)

        return False

    def _already_indexed_source(self, source_path: str) -> bool:
        if self.vector_store is None:
            return False

        try:
            store = getattr(self.vector_store, "docstore", None)
            if store is None:
                return False

            d = getattr(store, "_dict", None)
            if not isinstance(d, dict):
                return False

            for _, doc in d.items():
                meta = getattr(doc, "metadata", {}) or {}
                if str(meta.get("source", "")) == source_path:
                    return True
            return False
        except Exception:
            logger.debug("Dedup check failed:\n%s", traceback.format_exc())
            return False

    def process_file(self, file_path: Path) -> None:
        try:
            if file_path.suffix.lower() != ".pdf":
                return

            if not self._wait_until_file_stable(file_path):
                logger.warning("File not stable (skip): %s", str(file_path))
                return

            source_str = str(file_path.resolve())
            if self._already_indexed_source(source_str):
                logger.info("Already indexed (skip): %s", file_path.name)
                return

            loader = PyPDFLoader(str(file_path))
            documents = loader.load()

            for d in documents:
                d.metadata = d.metadata or {}
                d.metadata["file_name"] = file_path.name
                d.metadata["file_path"] = source_str
                d.metadata.setdefault("source", source_str)

            documents = self._preprocess_documents(documents)
            if not documents:
                logger.warning("All pages became empty/noisy after preprocessing: %s", str(file_path))
                return

            chunks = self.text_splitter.split_documents(documents)
            if not chunks:
                logger.warning("No chunks extracted from: %s", str(file_path))
                return

            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(chunks, self.embeddings)
                logger.info("created new FAISS store with %d chunks", len(chunks))
            else:
                self.vector_store.add_documents(chunks)
                logger.info("added %d chunks to existing store", len(chunks))

            self._save_vector_store()

        except Exception:
            logger.error("process_pdf failed: %s\n%s", str(file_path), traceback.format_exc())

    # -----------------------
    # Search
    # -----------------------
    def search(self, query: str, k: int = 8, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        if self.vector_store is None:
            logger.warning("Vector store not initialized.")
            return []

        try:
            final_k = int(top_k) if top_k is not None else int(k)
            docs_and_scores = self.vector_store.similarity_search_with_score(query, k=final_k)

            results: List[Dict[str, Any]] = []
            for rank, (doc, score) in enumerate(docs_and_scores, 1):
                if isinstance(doc, dict):
                    content = doc.get("page_content", "")
                    metadata = doc.get("metadata", {})
                else:
                    content = getattr(doc, "page_content", "")
                    metadata = getattr(doc, "metadata", {})

                results.append(
                    {
                        "rank": rank,
                        "score": float(score),
                        "content": content,
                        "metadata": metadata,
                    }
                )
            return results
        except Exception:
            logger.error("search failed:\n%s", traceback.format_exc())
            return []

    def get_stats(self) -> Dict[str, Any]:
        try:
            if self.vector_store is None:
                return {
                    "loaded": False,
                    "embedding_model": self.embedding_model_name,
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "vector_db_path": self.vector_db_path,
                    "embedded_folder": self.embedded_folder,
                    "total_docs": 0,
                }

            store = getattr(self.vector_store, "docstore", None)
            d = getattr(store, "_dict", {}) if store else {}
            total_docs = len(d) if isinstance(d, dict) else 0

            return {
                "loaded": True,
                "embedding_model": self.embedding_model_name,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "vector_db_path": self.vector_db_path,
                "embedded_folder": self.embedded_folder,
                "total_docs": total_docs,
                "has_index_files": self.has_existing_vector_store(),
                "stopwords_enabled": self.use_stopwords,
                "stopwords_count": len(self.stopwords),
            }
        except Exception:
            logger.error("get_stats failed:\n%s", traceback.format_exc())
            return {"error": "get_stats failed"}

    # -----------------------
    # Watch embedded folder
    # -----------------------
    def start_watching(self, recursive: bool = True) -> None:
        if self.observer is not None:
            logger.warning("Watcher already running.")
            return

        embedded_path = Path(self.embedded_folder)
        embedded_path.mkdir(parents=True, exist_ok=True)

        self.embed_folder(str(embedded_path))
        self._save_vector_store()

        handler = PDFWatcher(self)
        self.observer = Observer()
        self.observer.schedule(handler, str(embedded_path), recursive=recursive)
        self.observer.start()
        logger.info("Started watching folder: %s (recursive=%s)", str(embedded_path), recursive)

    def stop_watching(self) -> None:
        if self.observer is None:
            logger.warning("Watcher is not running.")
            return

        self.observer.stop()
        self.observer.join()
        self.observer = None
        logger.info("Stopped watching.")


def get_vector_store() -> VectorStore:
    return VectorStore()
