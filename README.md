# LLM 레드티밍 자동화 프레임워크

로컬 Ollama로 돌아가는 더미 챗봇에 공개된 탈옥(jailbreak) 페이로드를 자동으로 주입하고, 가드레일이 뚫리는지 판정해 리포트로 정리하는 도구입니다.

## 실행 방법

1. [Ollama](https://ollama.com) 설치 후 `ollama pull llama3`
2. `python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements.txt`
3. `python main.py`

## 구조

- `Target`: 공격 대상 챗봇 (현재: 비밀번호를 지키는 게임형 챗봇)
- `PayloadSource`: 공개 탈옥 기법 페이로드 로더 (`payloads/known_jailbreaks.yaml`)
- `Judge`: 공격 성공 여부 판정 (현재: 키워드 매칭)
- `Reporter`: 결과 출력 (현재: 콘솔 요약)

설계 스펙: `docs/superpowers/specs/2026-07-09-llm-redteam-framework-design.md`

## 마일스톤

- 마일스톤 1 (완료): 게임형 타겟 + 키워드 매칭 + 콘솔 리포트
- 마일스톤 2 (예정): 정책봇 타겟 + LLM 판정 + HTML 리포트
