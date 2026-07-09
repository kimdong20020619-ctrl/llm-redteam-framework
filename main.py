import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔 기본 codepage(cp949)로 인한 한글 깨짐 방지
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))  # src 레이아웃: 패키지 미설치 상태로 직접 실행 지원

from redteam.config import build_judge, build_payload_source, build_reporter, build_target, load_config
from redteam.engine import AttackEngine


def main(config_path: str = "config.yaml") -> None:
    config = load_config(config_path)
    engine = AttackEngine(
        target=build_target(config),
        judge=build_judge(config),
        reporter=build_reporter(config),
        payload_source=build_payload_source(config),
    )
    engine.run()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    main(path)
