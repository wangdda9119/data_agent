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

from rich.logging import RichHandler
from rich.console import Console

console = Console()

# ═══════════════════════════════════════════════════════════════
# 📝 Rich Logging Configuration (Markdown Rendering)
# ═══════════════════════════════════════════════════════════════
logger = logging.getLogger("VectorStore")
logger.setLevel(logging.INFO)

# Rich Handler for console output with markdown rendering
rich_handler = RichHandler(
    console=console,
    show_time=True,
    show_level=True,
    markup=True,  # Enable markdown rendering
)
rich_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(rich_handler)

# File handler (plain text)
file_handler = logging.FileHandler("vectorstore.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("[%(levelname)-8s] %(asctime)s | %(name)s - %(message)s"))
logger.addHandler(file_handler)

load_dotenv()


# ═══════════════════════════════════════════════════════════════
# 👁️  Watchdog Handler - PDF File Monitoring
# ═══════════════════════════════════════════════════════════════
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
            logger.error(
                "❌ **파일 생성 이벤트 처리에 실패했습니다.**\n"
                "오류 내용:\n%s",
                traceback.format_exc()
            )

    def on_moved(self, event):
        try:
            if event.is_directory:
                return
            if str(event.dest_path).lower().endswith(".pdf"):
                self.vector_store.process_file(Path(event.dest_path))
        except Exception:
            logger.error(
                "❌ **파일 이동 이벤트 처리에 실패했습니다.**\n"
                "오류 내용:\n%s",
                traceback.format_exc()
            )


# ═══════════════════════════════════════════════════════════════
# 🔍 VectorStore - LangChain + FAISS Integration
# ═══════════════════════════════════════════════════════════════
class VectorStore:
    """
    ## FAISS Vector Store 관리
    - **저장**: `FAISS.save_local(dir)` → `dir/index.faiss` + `dir/index.pkl`
    - **로드**: `FAISS.load_local(dir, embeddings, allow_dangerous_deserialization=True)`

    ## 주요 기능
    - 노이즈 정규식 제거 + 유니코드 정규화 + 불용어 제거 → 청킹 → 임베딩
    - `search` 기본 topk=8 + `top_k` 파라미터 호환
    - Windows 비ASCII 경로(예: "벡터디비") FAISS 저장 실패 방지
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
            f"""✅ **벡터스토어 설정이 완료되었습니다.**
📋 설정 정보:
  • 임베딩 모델: `{self.embedding_model_name}`
  • 청크 크기: `{self.chunk_size}` (오버랩: `{self.chunk_overlap}`)
  • 데이터베이스 경로: `{self.vector_db_path}`
  • 임베드 폴더: `{self.embedded_folder}`
  • 불용어 필터: `{self.use_stopwords}` (활성화됨)

다음 단계를 진행해주세요."""
        )

    # ═══════════════════════════════════════════════════════════════
    # 🛡️  Path Safety for Windows + FAISS
    # ═══════════════════════════════════════════════════════════════
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
                f"""⚠️  **비ASCII 경로가 감지되었습니다.**
경로: `{path_str}`
Windows 환경에서 호환성 문제가 발생할 수 있어 `vector_db`로 대체합니다.
필요한 경우 경로를 영문으로 변경해주세요."""
            )
            return "vector_db"

        safe = p.parent / "vector_db"
        logger.warning(
            f"""⚠️  **비ASCII 경로가 변환되었습니다.**
🗒️ 경로 정보:
  • 원본 경로: `{path_str}`
  • 변환된 경로: `{str(safe)}`

호환성을 위해 자동 변환되었습니다."""
        )
        return str(safe)

    # ═══════════════════════════════════════════════════════════════
    # 💾 Persistence - FAISS Index Management
    # ═══════════════════════════════════════════════════════════════
    def has_existing_vector_store(self) -> bool:
        db_dir = Path(self.vector_db_path)
        faiss_file = db_dir / "index.faiss"
        pkl_file = db_dir / "index.pkl"
        return faiss_file.exists() and pkl_file.exists()

    def load_existing_vector_store(self) -> bool:
        try:
            if not self.has_existing_vector_store():
                logger.info(
                    """ℹ️  **벡터스토어를 찾을 수 없습니다.**
처음 설정이거나 데이터베이스가 초기화된 상태입니다.
PDF 파일을 추가하면 새로운 벡터스토어가 생성됩니다."""
                )
                return False

            self.vector_store = FAISS.load_local(
                self.vector_db_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info(
                f"""✅ **벡터스토어가 성공적으로 로드되었습니다.**
🗒️ 위치: `{self.vector_db_path}`
이제 검색을 수행할 수 있습니다."""
            )
            return True
        except Exception:
            error_msg = traceback.format_exc()
            logger.error(
                f"""😞 **벡터스토어 로드 실패...**
오류 내용:
```
{error_msg}
```
새로운 벡터스토어를 생성하거나 파일 경로를 확인해주세요."""
            )
            self.vector_store = None
            return False

    def save_vector_store(self) -> None:
        self._save_vector_store()

    def _save_vector_store(self) -> None:
        if self.vector_store is None:
            logger.warning(
                """⚠️  **저장할 벡터스토어가 없습니다.**
아직 생성되지 않았거나 초기화된 상태입니다."""
            )
            return
        Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(self.vector_db_path)
        logger.info(
            f"""💾 **벡터스토어가 저장되었습니다.**
🗒️ 저장 위치: `{self.vector_db_path}`
📄 파일: `index.faiss` + `index.pkl`
다음 실행 시 자동으로 로드됩니다."""
        )

    # ═══════════════════════════════════════════════════════════════
    # 📊 Document Count - Utility Method
    # ═══════════════════════════════════════════════════════════════
    def count_documents(self) -> int:
        """
        Returns the number of documents (chunks) in FAISS docstore.
        Used by `create_vector_db.py` for status reporting.
        """
        try:
            if self.vector_store is None:
                return 0
            store = getattr(self.vector_store, "docstore", None)
            d = getattr(store, "_dict", {}) if store else {}
            return len(d) if isinstance(d, dict) else 0
        except Exception:
            error_msg = traceback.format_exc()
            logger.error(
                f"""😞 **문서 개수를 조회할 수 없었습니다.**
오류 내용:
```
{error_msg}
```"""
            )
            return 0

    # ═══════════════════════════════════════════════════════════════
    # 🧹 Text Preprocessing Pipeline
    # ═══════════════════════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════════════════════
    # 🔨 Build & Update - Embedding Generation
    # ═══════════════════════════════════════════════════════════════
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
        logger.info(
            f"""🔄 **임베딩 재생성을 시작합니다.**
📁 원본 폴더: `{str(target_folder_path)}`
진행 중입니다. 잠시만 기다려주세요..."""
        )
        self.embed_folder(str(target_folder_path))
        self._save_vector_store()

    def embed_folder(self, folder_path: str) -> None:
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"Folder not found: {folder_path}")

        pdf_files = list(folder.glob("**/*.pdf"))
        logger.info(
            f"""📄 **PDF 파일을 검색했습니다.**
📁 폴더: `{str(folder)}`
🔍 발견된 파일: `{len(pdf_files)}`개
이제 각 파일을 처리하겠습니다."""
        )

        for i, pdf in enumerate(pdf_files, 1):
            progress = int((i / len(pdf_files)) * 100)
            logger.info(
                f"""⚙️  **파일 처리 중** [{i}/{len(pdf_files)}]
📄 파일명: `{pdf.name}`
진행율: {progress}%"""
            )
            self.process_file(pdf)

        logger.info(
            f"""✅ **폴더 임베딩이 완료되었습니다.**
📁 처리된 폴더: `{folder_path}`
📊 모든 PDF 파일이 벡터화되었습니다.
검색을 위해 준비되었습니다."""
        )

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
                logger.warning(
                    f"""⏳ **파일이 아직 저장 중입니다.**
📄 파일: `{str(file_path)}`
저장이 완료될 때까지 기다렸으나 시간이 초과되었습니다.
잠시 후 다시 시도해주세요."""
                )
                return

            source_str = str(file_path.resolve())
            if self._already_indexed_source(source_str):
                logger.info(
                    f"""↩️  **이미 처리된 파일입니다.**
📄 파일: `{file_path.name}`
중복 처리를 피하기 위해 건너뜁니다."""
                )
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
                logger.warning(
                    f"""⚠️  **문서가 처리되지 않았습니다.**
📄 파일: `{str(file_path)}`
노이즈 제거 후 내용이 너무 적거나 없습니다.
파일의 내용을 확인해주세요."""
                )
                return

            chunks = self.text_splitter.split_documents(documents)
            if not chunks:
                logger.warning(
                    f"""⚠️  **청크 생성에 실패했습니다.**
📄 파일: `{str(file_path)}`
문서를 청크로 분할할 수 없었습니다."""
                )
                return

            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(chunks, self.embeddings)
                logger.info(
                    "✨ **새로운 FAISS 벡터스토어가 생성되었습니다.**\n"
                    "📊 청크 수: `%d`개\n"
                    "첫 번째 임베딩이 완료되었습니다.",
                    len(chunks)
                )
            else:
                self.vector_store.add_documents(chunks)
                logger.info(
                    "➕ **청크가 벡터스토어에 추가되었습니다.**\n"
                    "📊 추가된 청크: `%d`개\n"
                    "총 문서 수가 증가했습니다.",
                    len(chunks)
                )

            self._save_vector_store()

        except Exception:
            logger.error(
                "❌ **PDF 파일 처리에 실패했습니다.**\n"
                "📄 파일: `%s`\n"
                "오류 내용:\n%s\n"
                "파일 형식을 확인하거나 관리자에게 문의해주세요.",
                str(file_path),
                traceback.format_exc()
            )

    # ═══════════════════════════════════════════════════════════════
    # 🔎 Search & Query
    # ═══════════════════════════════════════════════════════════════
    def search(self, query: str, k: int = 8, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        if self.vector_store is None:
            logger.warning(
                """⚠️  **벡터스토어가 준비되지 않았습니다.**
검색을 수행할 수 없습니다.
먼저 PDF 파일을 추가하여 벡터스토어를 생성해주세요."""
            )
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
            error_msg = traceback.format_exc()
            logger.error(
                f"""😞 **검색 수행에 실패했습니다.**
오류 내용:
```
{error_msg}
```
쿼리를 확인하거나 다시 시도해주세요."""
            )
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
            logger.error(
                "❌ **통계 정보 조회에 실패했습니다.**\n"
                "오류 내용:\n%s\n"
                "나중에 다시 시도해주세요.",
                traceback.format_exc()
            )
            return {"error": "통계 정보를 조회할 수 없습니다."}

    # ═══════════════════════════════════════════════════════════════
    # 👁️  File Watcher - Auto-indexing on File Changes
    # ═══════════════════════════════════════════════════════════════
    def start_watching(self, recursive: bool = True) -> None:
        if self.observer is not None:
            logger.warning(
                "⚠️  **파일 감시자가 이미 실행 중입니다.**\n"
                "중복 실행을 방지하기 위해 요청이 무시되었습니다.\n"
                "필요시 먼저 감시를 중지해주세요."
            )
            return

        embedded_path = Path(self.embedded_folder)
        embedded_path.mkdir(parents=True, exist_ok=True)

        self.embed_folder(str(embedded_path))
        self._save_vector_store()

        handler = PDFWatcher(self)
        self.observer = Observer()
        self.observer.schedule(handler, str(embedded_path), recursive=recursive)
        self.observer.start()
        logger.info(
            "👁️  **파일 감시가 시작되었습니다.**\n"
            "📁 감시 폴더: `%s`\n"
            "🔄 재귀 감시: `%s`\n"
            "이제 이 폴더에 추가되는 PDF 파일이 자동으로 처리됩니다.",
            str(embedded_path),
            "활성화" if recursive else "비활성화"
        )

    def stop_watching(self) -> None:
        if self.observer is None:
            logger.warning(
                "⚠️  **파일 감시자가 실행 중이 아닙니다.**\n"
                "이미 중지된 상태입니다."
            )
            return

        self.observer.stop()
        self.observer.join()
        self.observer = None
        logger.info(
            "⏹️  **파일 감시가 중지되었습니다.**\n"
            "📁 감시 폴더에 대한 자동 처리가 비활성화되었습니다.\n"
            "필요시 언제든 다시 시작할 수 있습니다."
        )


def get_vector_store() -> VectorStore:
    return VectorStore()
