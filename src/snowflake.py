import datetime


class SnowflakeGenerator:
    EPOCH = int(datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
    WORKER_ID_BITS = 10
    SEQUENCE_BITS = 12
    MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1
    TIMESTAMP_SHIFT = WORKER_ID_BITS + SEQUENCE_BITS
    WORKER_ID_SHIFT = SEQUENCE_BITS

    def __init__(self, worker_id: int):
        if not 0 <= worker_id <= self.MAX_WORKER_ID:
            raise ValueError(f"worker_id must be between 0 and {self.MAX_WORKER_ID}")
        self.worker_id = worker_id
        self.last_ts = 0
        self.sequence = 0

    def _now(self):
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000) - self.EPOCH

    def generate_id(self) -> int:
        ts = self._now()
        if ts < self.last_ts:
            raise RuntimeError("Clock moved backwards")
        if ts == self.last_ts:
            self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
            if self.sequence == 0:
                while (ts := self._now()) == self.last_ts:
                    pass
        else:
            self.sequence = 0
        self.last_ts = ts
        return (ts << self.TIMESTAMP_SHIFT) | (self.worker_id << self.WORKER_ID_SHIFT) | self.sequence
