"""
인메모리 토큰 저장소 (Redis 대체)
- 단일 인스턴스(Render) 환경에서 사용
- 서버 재시작 시 토큰 데이터 초기화됨 (사용자 재로그인 필요)
- get_redis() 인터페이스를 유지하여 auth.py 호환성 보장
"""
import time
import asyncio


class InMemoryTokenStore:
    """Redis API와 호환되는 인메모리 토큰 저장소"""

    def __init__(self):
        self._store: dict[str, tuple[str, float]] = {}  # key → (value, expire_timestamp)
        self._cleanup_interval = 300  # 5분마다 만료 키 정리
        self._cleanup_task: asyncio.Task | None = None

    async def start_cleanup(self):
        """백그라운드 만료 키 정리 태스크 시작"""
        if self._cleanup_task is None:
            try:
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(self._periodic_cleanup())
            except RuntimeError:
                pass

    async def _periodic_cleanup(self):
        """주기적으로 만료된 키 제거"""
        while True:
            await asyncio.sleep(self._cleanup_interval)
            now = time.time()
            expired_keys = [k for k, (_, exp) in self._store.items() if exp <= now]
            for k in expired_keys:
                del self._store[k]

    async def setex(self, key: str, ttl: int, value: str):
        """키에 TTL과 함께 값 저장 (Redis SETEX 호환)"""
        expire_at = time.time() + ttl
        self._store[key] = (value, expire_at)

    async def exists(self, key: str) -> bool:
        """키 존재 여부 확인 (만료 확인 포함, Redis EXISTS 호환)"""
        if key not in self._store:
            return False
        _, expire_at = self._store[key]
        if time.time() >= expire_at:
            del self._store[key]
            return False
        return True

    async def delete(self, key: str):
        """키 삭제 (Redis DEL 호환)"""
        self._store.pop(key, None)


# 싱글턴 인스턴스
token_store = InMemoryTokenStore()


async def get_redis():
    """기존 get_redis() 인터페이스 유지 (auth.py 호환)"""
    await token_store.start_cleanup()
    return token_store
