from dataclasses import dataclass


@dataclass
class Payload:
    category: str
    text: str


@dataclass
class JudgeResult:
    payload: Payload
    response: str
    success: bool
    detail: str
