import html
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


_STATUS_BADGE_CLASS = {
    JudgeStatus.SUCCESS: "badge-success",
    JudgeStatus.BLOCKED: "badge-blocked",
    JudgeStatus.ERROR: "badge-error",
    JudgeStatus.UNDETERMINED: "badge-undetermined",
}
_STATUS_LABEL = {
    JudgeStatus.SUCCESS: "성공",
    JudgeStatus.BLOCKED: "차단",
    JudgeStatus.ERROR: "오류",
    JudgeStatus.UNDETERMINED: "판정불가",
}


class HtmlReporter(Reporter):
    def __init__(self, output_path: str = "report.html"):
        self.output_path = output_path

    def render(self, results: list[JudgeResult]) -> None:
        content = self._build_html(results)
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"HTML 리포트 생성됨: {self.output_path}")

    def _build_html(self, results: list[JudgeResult]) -> str:
        total = len(results)
        counts = {status: 0 for status in JudgeStatus}
        for r in results:
            counts[r.status] += 1

        cat_counts: dict[str, dict[str, int]] = {}
        for r in results:
            bucket = cat_counts.setdefault(r.payload.category, {"total": 0, "success": 0})
            bucket["total"] += 1
            if r.status == JudgeStatus.SUCCESS:
                bucket["success"] += 1

        category_rows = "\n".join(
            f"<tr><td>{html.escape(cat)}</td><td>{b['success']}/{b['total']}</td>"
            f"<td>{(b['success'] / b['total'] * 100) if b['total'] else 0:.0f}%</td></tr>"
            for cat, b in cat_counts.items()
        )

        result_rows = "\n".join(
            f'<tr><td><span class="badge {_STATUS_BADGE_CLASS[r.status]}">{_STATUS_LABEL[r.status]}</span></td>'
            f"<td>{html.escape(r.payload.category)}</td><td>{html.escape(r.payload.text)}</td>"
            f"<td>{html.escape(r.detail)}</td></tr>"
            for r in results
        )

        return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>LLM 레드티밍 결과 리포트</title>
<style>
body {{ font-family: sans-serif; margin: 2rem; color: #222; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; }}
th {{ background: #f0f0f0; }}
.badge {{ padding: 0.2rem 0.5rem; border-radius: 4px; color: white; font-size: 0.85rem; }}
.badge-success {{ background: #2e7d32; }}
.badge-blocked {{ background: #757575; }}
.badge-error {{ background: #f9a825; }}
.badge-undetermined {{ background: #ef6c00; }}
</style>
</head>
<body>
<h1>LLM 레드티밍 결과 리포트</h1>
<p>총 {total}개 페이로드 중 {counts[JudgeStatus.SUCCESS]}개 성공
(차단 {counts[JudgeStatus.BLOCKED]}개, 오류 {counts[JudgeStatus.ERROR]}개, 판정불가 {counts[JudgeStatus.UNDETERMINED]}개)</p>

<h2>카테고리별 성공률</h2>
<table>
<tr><th>카테고리</th><th>성공/전체</th><th>성공률</th></tr>
{category_rows}
</table>

<h2>페이로드별 상세 결과</h2>
<table>
<tr><th>상태</th><th>카테고리</th><th>페이로드</th><th>판정 상세</th></tr>
{result_rows}
</table>
</body>
</html>
"""
