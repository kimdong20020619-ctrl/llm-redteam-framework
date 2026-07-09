from redteam.config import build_judge, build_payload_source, build_reporter, build_target, load_config
from redteam.judge import KeywordMatchJudge, LLMJudge
from redteam.payload_source import YamlPayloadSource
from redteam.reporter import ConsoleReporter, HtmlReporter
from redteam.target import GameTarget, PolicyTarget

import pytest


SAMPLE_CONFIG = {
    "target": {"type": "game", "model": "llama3", "secret": "hunter2"},
    "judge": {"type": "keyword"},
    "payload_source": {"path": "payloads/known_jailbreaks.yaml"},
    "reporter": {"type": "console"},
}

POLICY_CONFIG = {
    "target": {
        "type": "policy",
        "model": "llama3",
        "confidential_keywords": ["프로젝트 오로라", "임원 성과급 15%"],
    },
    "judge": {"type": "llm"},
    "payload_source": {"path": "payloads/policy_bot_payloads.yaml"},
    "reporter": {"type": "html", "output_path": "report.html"},
}


def test_load_config_reads_yaml_file(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "target:\n  type: game\n  model: llama3\n  secret: hunter2\n"
        "judge:\n  type: keyword\n"
        "payload_source:\n  path: payloads/known_jailbreaks.yaml\n"
        "reporter:\n  type: console\n",
        encoding="utf-8",
    )

    config = load_config(str(config_file))

    assert config["target"]["type"] == "game"
    assert config["target"]["secret"] == "hunter2"


def test_build_target_returns_game_target_for_game_type():
    target = build_target(SAMPLE_CONFIG)
    assert isinstance(target, GameTarget)
    assert target.model == "llama3"
    assert target.secret == "hunter2"


def test_build_target_returns_policy_target_for_policy_type():
    target = build_target(POLICY_CONFIG)
    assert isinstance(target, PolicyTarget)
    assert target.model == "llama3"
    assert target.confidential_keywords == ["프로젝트 오로라", "임원 성과급 15%"]


def test_build_target_raises_for_unsupported_type():
    with pytest.raises(ValueError):
        build_target({"target": {"type": "nonexistent"}})


def test_build_judge_returns_keyword_match_judge_using_secret_as_keyword():
    judge = build_judge(SAMPLE_CONFIG)
    assert isinstance(judge, KeywordMatchJudge)
    assert judge.keyword == "hunter2"


def test_build_judge_returns_llm_judge_using_confidential_keywords():
    judge = build_judge(POLICY_CONFIG)
    assert isinstance(judge, LLMJudge)
    assert judge.model == "llama3"
    assert judge.confidential_info == ["프로젝트 오로라", "임원 성과급 15%"]


def test_build_judge_raises_for_unsupported_type():
    with pytest.raises(ValueError):
        build_judge({"target": {"secret": "x"}, "judge": {"type": "nonexistent"}})


def test_build_reporter_returns_console_reporter():
    reporter = build_reporter(SAMPLE_CONFIG)
    assert isinstance(reporter, ConsoleReporter)


def test_build_reporter_returns_html_reporter_with_output_path():
    reporter = build_reporter(POLICY_CONFIG)
    assert isinstance(reporter, HtmlReporter)
    assert reporter.output_path == "report.html"


def test_build_reporter_html_defaults_output_path_when_not_specified():
    config = {"reporter": {"type": "html"}}
    reporter = build_reporter(config)
    assert isinstance(reporter, HtmlReporter)
    assert reporter.output_path == "report.html"


def test_build_reporter_raises_for_unsupported_type():
    with pytest.raises(ValueError):
        build_reporter({"reporter": {"type": "nonexistent"}})


def test_build_payload_source_returns_yaml_payload_source_with_configured_path():
    source = build_payload_source(SAMPLE_CONFIG)
    assert isinstance(source, YamlPayloadSource)
    assert source.path == "payloads/known_jailbreaks.yaml"
