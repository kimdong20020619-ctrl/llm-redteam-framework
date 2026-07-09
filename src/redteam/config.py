import yaml

from redteam.judge import Judge, KeywordMatchJudge, LLMJudge
from redteam.payload_source import PayloadSource, YamlPayloadSource
from redteam.reporter import ConsoleReporter, HtmlReporter, Reporter
from redteam.target import GameTarget, PolicyTarget, Target


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_target(config: dict) -> Target:
    target_config = config["target"]
    target_type = target_config["type"]
    if target_type == "game":
        return GameTarget(model=target_config["model"], secret=target_config["secret"])
    if target_type == "policy":
        return PolicyTarget(
            model=target_config["model"],
            confidential_keywords=target_config["confidential_keywords"],
        )
    raise ValueError(f"지원하지 않는 target type: {target_type}")


def build_judge(config: dict) -> Judge:
    judge_config = config["judge"]
    judge_type = judge_config["type"]
    if judge_type == "keyword":
        return KeywordMatchJudge(keyword=config["target"]["secret"])
    if judge_type == "llm":
        return LLMJudge(
            model=config["target"]["model"],
            confidential_info=config["target"]["confidential_keywords"],
        )
    raise ValueError(f"지원하지 않는 judge type: {judge_type}")


def build_reporter(config: dict) -> Reporter:
    reporter_config = config["reporter"]
    reporter_type = reporter_config["type"]
    if reporter_type == "console":
        return ConsoleReporter()
    if reporter_type == "html":
        output_path = reporter_config.get("output_path", "report.html")
        return HtmlReporter(output_path=output_path)
    raise ValueError(f"지원하지 않는 reporter type: {reporter_type}")


def build_payload_source(config: dict) -> PayloadSource:
    return YamlPayloadSource(path=config["payload_source"]["path"])
