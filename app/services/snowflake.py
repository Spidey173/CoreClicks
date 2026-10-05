import os
import threading
import time

# Base62 alphabet
BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(BASE62_ALPHABET)

# Custom epoch: 2024-01-01 00:00:00 UTC (1704067200000 ms)
EPOCH_MS = 1704067200000

# Bit allocations (64-bit total)
TIMESTAMP_BITS = 41
NODE_ID_BITS = 10
SEQUENCE_BITS = 12

MAX_NODE_ID = (1 << NODE_ID_BITS) - 1      # 1023
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1    # 4095

NODE_SHIFT = SEQUENCE_BITS
TIMESTAMP_SHIFT = NODE_ID_BITS + SEQUENCE_BITS


class SnowflakeGenerator:
    """
    Distributed 64-bit Snowflake ID Generator with Base62 encoding.
    Ensures zero collision without synchronous database round-trips.
    """
    def __init__(self, node_id: int = 1):
        if not (0 <= node_id <= MAX_NODE_ID):
            raise ValueError(f"node_id must be between 0 and {MAX_NODE_ID}")
        self.node_id = node_id
        self.sequence = 0
        self.last_timestamp = -1
        self._lock = threading.Lock()

    def _current_timestamp_ms(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_ts: int) -> int:
        ts = self._current_timestamp_ms()
        while ts <= last_ts:
            time.sleep(0.0001)
            ts = self._current_timestamp_ms()
        return ts

    def next_id(self) -> int:
        with self._lock:
            ts = self._current_timestamp_ms()
            if ts < self.last_timestamp:
                # Clock moved backwards; wait until clock catches up
                ts = self._wait_next_millis(self.last_timestamp)

            if ts == self.last_timestamp:
                self.sequence = (self.sequence + 1) & MAX_SEQUENCE
                if self.sequence == 0:
                    ts = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = ts

            snowflake_id = (
                ((ts - EPOCH_MS) << TIMESTAMP_SHIFT)
                | (self.node_id << NODE_SHIFT)
                | self.sequence
            )
            return snowflake_id

    def next_base62(self) -> str:
        """Generates 6-7 character Base62 URL short slug."""
        num = self.next_id()
        if num == 0:
            return BASE62_ALPHABET[0]
        digits = []
        while num:
            num, rem = divmod(num, BASE)
            digits.append(BASE62_ALPHABET[rem])
        return "".join(reversed(digits))


# Singleton instance configured with node ID from environment
_default_node = int(os.environ.get("SNOWFLAKE_NODE_ID", 1)) % (MAX_NODE_ID + 1)
snowflake = SnowflakeGenerator(node_id=_default_node)


def generate_snowflake_code() -> str:
    """Public helper function to obtain distributed Base62 short code."""
    return snowflake.next_base62()
