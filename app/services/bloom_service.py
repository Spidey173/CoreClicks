import hashlib
import math
import os
import threading
from typing import Optional

try:
    import mmh3
except ImportError:
    mmh3 = None

try:
    import redis
except ImportError:
    redis = None


class BloomFilter:
    """
    High-performance probabilistic Bloom Filter.
    Supports either Redis Bitfield backend or fast in-memory bitarray with Redis sync.
    Prevents cache penetration for non-existent short links.
    """
    def __init__(self, capacity: int = 500000, error_rate: float = 0.001, redis_url: Optional[str] = None):
        self.capacity = capacity
        self.error_rate = error_rate
        # Calculate optimal size (m) and hash count (k)
        self.size = int(- (capacity * math.log(error_rate)) / (math.log(2) ** 2))
        self.hash_count = int((self.size / capacity) * math.log(2))
        self._lock = threading.Lock()

        # In-memory bit array fallback
        self._bit_array = bytearray((self.size + 7) // 8)

        # Redis connection if available
        self.redis_client = None
        redis_conn_str = redis_url or os.environ.get("REDIS_URL")
        if redis and redis_conn_str:
            try:
                self.redis_client = redis.Redis.from_url(redis_conn_str, decode_responses=False)
                self.redis_client.ping()
            except Exception:
                self.redis_client = None

    def _get_hashes(self, item: str):
        """Kirsch-Mitzenmacher optimization using mmh3 or standard hashlib."""
        if mmh3:
            h1, h2 = mmh3.hash64(item)
        else:
            h1 = int(hashlib.md5(item.encode("utf-8")).hexdigest()[:16], 16)
            h2 = int(hashlib.sha256(item.encode("utf-8")).hexdigest()[:16], 16)

        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size

    def add(self, item: str) -> None:
        """Adds an item into the Bloom filter."""
        hashes = list(self._get_hashes(item))
        with self._lock:
            for bit_offset in hashes:
                byte_idx = bit_offset // 8
                bit_idx = bit_offset % 8
                self._bit_array[byte_idx] |= (1 << bit_idx)

        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                for bit_offset in hashes:
                    pipe.setbit("bloom:short_urls", bit_offset, 1)
                pipe.execute()
            except Exception:
                pass

    def contains(self, item: str) -> bool:
        """Checks if an item might exist in the filter."""
        hashes = list(self._get_hashes(item))
        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                for bit_offset in hashes:
                    pipe.getbit("bloom:short_urls", bit_offset)
                results = pipe.execute()
                return all(results)
            except Exception:
                pass

        with self._lock:
            for bit_offset in hashes:
                byte_idx = bit_offset // 8
                bit_idx = bit_offset % 8
                if not (self._bit_array[byte_idx] & (1 << bit_idx)):
                    return False
            return True


# Global bloom filter instance
url_bloom_filter = BloomFilter(capacity=100000, error_rate=0.001)
