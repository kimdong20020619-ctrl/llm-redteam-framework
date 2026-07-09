from redteam.config import build_judge, build_payload_source, build_reporter, build_target, load_config
from redteam.judge import KeywordMatchJudge
from redteam.payload_source import YamlPayloadSource
from redteam.reporter import ConsoleReporter
from redteam.target import GameTarget


SAMPLE_CONFIG = {
    "target": {"type": "game", "model": "llama3", "secret": "hunter2"},
    "judge": {"type": "keyword"},
    "payload_source": {"path": "payloads/known_jailbreaks.yaml"},
    "reporter": {"type": "console"},
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


def test_build_judge_returns_keyword_match_judge_using_secret_as_keyword():
    judge = build_judge(SAMPLE_CONFIG)
    assert isinstance(judge, KeywordMatchJudge)
    assert judge.keyword == "hunter2"


def test_build_reporter_returns_console_reporter():
    reporter = build_reporter(SAMPLE_CONFIG)
    assert isinstance(reporter, ConsoleReporter)


def test_build_payload_source_returns_yaml_payload_source_with_configured_path():
    source = build_payload_source(SAMPLE_CONFIG)
    assert isinstance(source, YamlPayloadSource)
    assert source.path == "payloads/known_jailbreaks.yaml"
