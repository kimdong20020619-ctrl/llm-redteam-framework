from abc import ABC, abstractmethod

from redteam.models import JudgeResult, Payload


class Judge(ABC):
    @abstractmethod
    def evaluate(self, payload: Payload, response: str) -> JudgeResult:
        ...


class KeywordMatchJudge(Judge):
    def __init__(self, keyword: str):
        self.keyword = keyword

    def evaluate(self, payload: Payload, response: str) -> JudgeResult:
        success = self.keyword in response
        detail = f"'{self.keyword}' {'포함됨' if success else '포함 안 됨'}"
        return JudgeResult(payload=payload, response=response, success=success, detail=detail)
