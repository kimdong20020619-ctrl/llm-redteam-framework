from abc import ABC, abstractmethod

from redteam.models import JudgeResult, JudgeStatus


class Reporter(ABC):
    @abstractmethod
    def render(self, results: list[JudgeResult]) -> None:
        ...


class ConsoleReporter(Reporter):
    def render(self, results: list[JudgeResult]) -> None:
        total = len(results)
        counts = {status: 0 for status in JudgeStatus}
        for r in results:
            counts[r.status] += 1

        print(
            f"총 {total}개 페이로드 중 {counts[JudgeStatus.SUCCESS]}개 성공 "
            f"(차단 {counts[JudgeStatus.BLOCKED]}개, 오류 {counts[JudgeStatus.ERROR]}개, "
            f"판정불가 {counts[JudgeStatus.UNDETERMINED]}개)"
        )
        print("-" * 60)

        status_label = {
            JudgeStatus.SUCCESS: "성공",
            JudgeStatus.BLOCKED: "차단",
            JudgeStatus.ERROR: "오류",
            JudgeStatus.UNDETERMINED: "판정불가",
        }
        for r in results:
            print(f"[{status_label[r.status]}] [{r.payload.category}] {r.payload.text[:40]}")
            print(f"  판정: {r.detail}")

        print("-" * 60)
        print("카테고리별 성공률:")

        cat_counts: dict[str, dict[str, int]] = {}
        for r in results:
            bucket = cat_counts.setdefault(r.payload.category, {"total": 0, "success": 0, "error_undetermined": 0})
            bucket["total"] += 1
            if r.status == JudgeStatus.SUCCESS:
                bucket["success"] += 1
            elif r.status in (JudgeStatus.ERROR, JudgeStatus.UNDETERMINED):
                bucket["error_undetermined"] += 1

        for category, b in cat_counts.items():
            rate = (b["success"] / b["total"] * 100) if b["total"] else 0
            extra = f" (오류/판정불가 {b['error_undetermined']}건)" if b["error_undetermined"] else ""
            print(f"  {category}: {b['success']}/{b['total']} ({rate:.0f}%){extra}")
