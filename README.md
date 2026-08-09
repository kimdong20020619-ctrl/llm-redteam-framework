# LLM 레드티밍 자동화 프레임워크

[![security](https://github.com/kimdong20020619-ctrl/llm-redteam-framework/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/kimdong20020619-ctrl/llm-redteam-framework/actions/workflows/security.yml)

로컬 Ollama로 돌아가는 더미 챗봇에 공개된 탈옥(jailbreak) 페이로드를 자동으로 주입하고, 가드레일이 뚫리는지 판정해 리포트로 정리하는 도구입니다.

> **도구 자체의 보안**: 판정 LLM에 대상 응답을 넘길 때 `<target_response>` 구분자로 감싸고, 그 내부를 지시가 아닌 데이터로 취급하도록 시스템 프롬프트에 못박아 2차 프롬프트 인젝션을 방어합니다. 의존성은 `requirements-lock.txt` 기준으로 `pip-audit` 정기 검증합니다.

## 실행 방법

1. [Ollama](https://ollama.com) 설치 후 `ollama pull llama3`
2. `python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements.txt`
3. 마일스톤1 시나리오(게임형 타겟 + 키워드 판정 + 콘솔 리포트): `python main.py`
4. 마일스톤2 시나리오(정책봇 타겟 + LLM 판정 + HTML 리포트): `python main.py config-milestone2.yaml` → 실행 후 `report.html`을 브라우저로 열어 확인

## 구조

- `Target`: 공격 대상 챗봇 — `GameTarget`(비밀번호를 지키는 게임형 챗봇) / `PolicyTarget`(기밀 키워드를 지키는 회사 정책봇)
- `PayloadSource`: 탈옥 기법 페이로드 로더 (`payloads/known_jailbreaks.yaml`, `payloads/policy_bot_payloads.yaml`)
- `Judge`: 공격 성공 여부 판정 — `KeywordMatchJudge`(키워드 매칭) / `LLMJudge`(문맥상 유출까지 LLM이 판단)
- `Reporter`: 결과 출력 — `ConsoleReporter`(터미널 요약) / `HtmlReporter`(공유 가능한 정적 HTML)
- `JudgeStatus`: 판정 결과를 SUCCESS(성공)/BLOCKED(차단)/ERROR(타겟 오류)/UNDETERMINED(판정 불가) 4가지로 구분

설계 스펙: `docs/superpowers/specs/2026-07-09-llm-redteam-framework-design.md`, `docs/superpowers/specs/2026-07-10-milestone2-design.md`

## 마일스톤

- 마일스톤 1 (완료): 게임형 타겟 + 키워드 매칭 + 콘솔 리포트
- 마일스톤 2 (완료): 정책봇 타겟 + LLM 판정 + HTML 리포트 + JudgeStatus 상태 구분
