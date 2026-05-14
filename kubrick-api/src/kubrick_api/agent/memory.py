from datetime import datetime

import pixeltable as pxt
from loguru import logger
from pydantic import BaseModel


class MemoryRecord(BaseModel):
    session_id: str
    message_id: str
    role: str
    content: str
    timestamp: datetime
    clip_path: str | None = None


class Memory:
    def __init__(self, name: str):
        self.directory = name

        pxt.create_dir(self.directory, if_exists="ignore")
        self._setup_table()
        self._memory_table = pxt.get_table(f"{self.directory}.memory")

    def _setup_table(self):
        self._memory_table = pxt.create_table(
            f"{self.directory}.memory",
            {
                "session_id": pxt.String,
                "message_id": pxt.String,
                "role": pxt.String,
                "content": pxt.String,
                "timestamp": pxt.Timestamp,
                "clip_path": pxt.String,
            },
            if_exists="ignore",
        )

    def reset_memory(self):
        logger.info(f"Resetting memory: {self.directory}")
        pxt.drop_dir(self.directory, if_not_exists="ignore", force=True)

    def insert(self, memory_record: MemoryRecord):
        self._memory_table.insert([memory_record.model_dump()])

    def get_all(self) -> list[MemoryRecord]:
        return [MemoryRecord(**record) for record in self._memory_table.collect()]

    def get_latest(self, n: int) -> list[MemoryRecord]:
        return self.get_all()[-n:]

    def get_by_message_id(self, message_id: str) -> MemoryRecord:
        return self._memory_table.where(
            self._memory_table.message_id == message_id
        ).collect()[0]

    def get_by_session_id(self, session_id: str, n: int = None) -> list[MemoryRecord]:
        message_in_session = self._memory_table.where(
            self._memory_table.session_id == session_id
        ).collect()
        records = [MemoryRecord(**record) for record in message_in_session]
        return records[-n:] if n else records
