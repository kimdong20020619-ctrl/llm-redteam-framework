from abc import ABC, abstractmethod

from redteam.models import JudgeResult


class Reporter(ABC):
    @abstractmethod
    def render(self, results: list[JudgeResult]) -> None:
        ...


class ConsoleReporter(Reporter):
    def render(self, results: list[JudgeResult]) -> None:
        total = len(results)
        succeeded = sum(1 for r in results if r.success)
        print(f"총 {total}개 페이로드 중 {succeeded}개 성공")
        print("-" * 60)

        for r in results:
            status = "성공" if r.success else "실패"
            print(f"[{status}] [{r.payload.category}] {r.payload.text[:40]}")
            print(f"  판정: {r.detail}")

        print("-" * 60)
        print("카테고리별 성공률:")

        counts: dict[str, list[int]] = {}
        for r in results:
            bucket = counts.setdefault(r.payload.category, [0, 0])
            bucket[0] += 1
            if r.success:
                bucket[1] += 1

        for category, (count, success_count) in counts.items():
            rate = (success_count / count * 100) if count else 0
            print(f"  {category}: {success_count}/{count} ({rate:.0f}%)")
