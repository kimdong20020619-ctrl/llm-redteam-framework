from dataclasses import dataclass
from enum import Enum


@dataclass
class Payload:
    category: str
    text: str


class JudgeStatus(Enum):
    SUCCESS = "success"
    BLOCKED = "blocked"
    ERROR = "error"
    UNDETERMINED = "undetermined"


@dataclass
class JudgeResult:
    payload: Payload
    response: str
    status: JudgeStatus
    detail: str

    @property
    def success(self) -> bool:
        return self.status == JudgeStatus.SUCCESS
