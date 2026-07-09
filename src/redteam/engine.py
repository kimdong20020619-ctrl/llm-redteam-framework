from redteam.judge import Judge
from redteam.models import JudgeResult
from redteam.payload_source import PayloadSource
from redteam.reporter import Reporter
from redteam.target import Target


class AttackEngine:
    def __init__(self, target: Target, judge: Judge, reporter: Reporter, payload_source: PayloadSource):
        self.target = target
        self.judge = judge
        self.reporter = reporter
        self.payload_source = payload_source

    def run(self) -> list[JudgeResult]:
        payloads = self.payload_source.load()
        results: list[JudgeResult] = []

        for payload in payloads:
            try:
                response = self.target.send(payload.text)
            except Exception as e:
                results.append(
                    JudgeResult(payload=payload, response="", success=False, detail=f"오류: {e}")
                )
                continue

            try:
                result = self.judge.evaluate(payload, response)
            except Exception as e:
                result = JudgeResult(
                    payload=payload, response=response, success=False, detail=f"판정 불가: {e}"
                )
            results.append(result)

        self.reporter.render(results)
        return results
