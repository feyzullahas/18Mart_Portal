"""
Merkezi cache servisi için tüm servisler
"""
from datetime import datetime, timedelta
from typing import Any, Optional

class CentralCache:
    def __init__(self):
        self._cache: dict[str, dict] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Cache'den veri al"""
        if key in self._cache:
            item = self._cache[key]
            if datetime.now() < item["expires"]:
                return item["data"]
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, data: Any, ttl_minutes: int = 60) -> None:
        """Cache'e veri kaydet"""
        self._cache[key] = {
            "data": data,
            "expires": datetime.now() + timedelta(minutes=ttl_minutes)
        }
    
    def clear(self, pattern: str = None) -> None:
        """Cache'i temizle"""
        if pattern:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for k in keys_to_delete:
                del self._cache[k]
        else:
            self._cache.clear()
    
    def size(self) -> int:
        """Cache boyutunu döndür"""
        return len(self._cache)

# Global cache instance
cache = CentralCache()
