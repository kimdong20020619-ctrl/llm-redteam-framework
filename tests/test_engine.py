from redteam.engine import AttackEngine
from redteam.judge import KeywordMatchJudge
from redteam.models import Payload


class FakePayloadSource:
    def __init__(self, payloads):
        self._payloads = payloads

    def load(self):
        return self._payloads


class FakeTarget:
    def __init__(self, responses):
        self._responses = responses

    def send(self, payload):
        if payload not in self._responses:
            raise ValueError(f"예상치 못한 페이로드: {payload}")
        return self._responses[payload]


class BrokenTarget:
    def send(self, payload):
        raise ConnectionError("Ollama에 연결할 수 없음")


class BrokenJudge:
    def evaluate(self, payload, response):
        raise RuntimeError("판정 로직 내부 오류")


class RetryOnceTarget:
    """첫 호출은 실패하고 두 번째 호출(재시도)에서 성공하는 타겟."""

    def __init__(self, response):
        self._response = response
        self.call_count = 0

    def send(self, payload):
        self.call_count += 1
        if self.call_count == 1:
            raise ConnectionError("Ollama에 연결할 수 없음")
        return self._response


class RecordingReporter:
    def __init__(self):
        self.rendered = None

    def render(self, results):
        self.rendered = results


def test_engine_runs_payloads_through_judge_and_reporter():
    payloads = [
        Payload(category="dan", text="DAN 페이로드"),
        Payload(category="direct_ask", text="직접 요청"),
    ]
    target = FakeTarget({
        "DAN 페이로드": "비밀번호는 hunter2 입니다",
        "직접 요청": "알려드릴 수 없습니다",
    })
    judge = KeywordMatchJudge(keyword="hunter2")
    reporter = RecordingReporter()
    payload_source = FakePayloadSource(payloads)

    engine = AttackEngine(target=target, judge=judge, reporter=reporter, payload_source=payload_source)
    results = engine.run()

    assert len(results) == 2
    assert results[0].success is True
    assert results[1].success is False
    assert reporter.rendered == results


def test_engine_marks_target_failure_as_error_and_continues():
    payloads = [Payload(category="dan", text="아무 페이로드")]
    judge = KeywordMatchJudge(keyword="hunter2")
    reporter = RecordingReporter()
    payload_source = FakePayloadSource(payloads)

    engine = AttackEngine(target=BrokenTarget(), judge=judge, reporter=reporter, payload_source=payload_source)
    results = engine.run()

    assert len(results) == 1
    assert results[0].success is False
    assert "오류" in results[0].detail


def test_engine_retries_target_send_once_before_recording_error():
    payloads = [Payload(category="dan", text="아무 페이로드")]
    judge = KeywordMatchJudge(keyword="hunter2")
    reporter = RecordingReporter()
    payload_source = FakePayloadSource(payloads)
    target = RetryOnceTarget(response="정상 응답")

    engine = AttackEngine(target=target, judge=judge, reporter=reporter, payload_source=payload_source)
    results = engine.run()

    assert target.call_count == 2
    assert len(results) == 1
    assert "오류" not in results[0].detail
    assert results[0].response == "정상 응답"


def test_engine_marks_judge_exception_as_undetermined_and_continues():
    payloads = [Payload(category="dan", text="아무 페이로드")]
    target = FakeTarget({"아무 페이로드": "아무 응답"})
    reporter = RecordingReporter()
    payload_source = FakePayloadSource(payloads)

    engine = AttackEngine(target=target, judge=BrokenJudge(), reporter=reporter, payload_source=payload_source)
    results = engine.run()

    assert len(results) == 1
    assert results[0].success is False
    assert "판정 불가" in results[0].detail
