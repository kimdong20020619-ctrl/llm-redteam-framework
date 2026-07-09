import yaml

from redteam.judge import Judge, KeywordMatchJudge
from redteam.payload_source import PayloadSource, YamlPayloadSource
from redteam.reporter import ConsoleReporter, Reporter
from redteam.target import GameTarget, Target


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_target(config: dict) -> Target:
    target_config = config["target"]
    if target_config["type"] == "game":
        return GameTarget(model=target_config["model"], secret=target_config["secret"])
    raise ValueError(f"지원하지 않는 target type: {target_config['type']}")


def build_judge(config: dict) -> Judge:
    judge_config = config["judge"]
    if judge_config["type"] == "keyword":
        return KeywordMatchJudge(keyword=config["target"]["secret"])
    raise ValueError(f"지원하지 않는 judge type: {judge_config['type']}")


def build_reporter(config: dict) -> Reporter:
    reporter_config = config["reporter"]
    if reporter_config["type"] == "console":
        return ConsoleReporter()
    raise ValueError(f"지원하지 않는 reporter type: {reporter_config['type']}")


def build_payload_source(config: dict) -> PayloadSource:
    return YamlPayloadSource(path=config["payload_source"]["path"])
