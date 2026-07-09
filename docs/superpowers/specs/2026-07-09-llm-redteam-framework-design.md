# LLM 레드티밍 자동화 프레임워크 — 설계 스펙

- 작성일: 2026-07-09
- 상태: 설계 승인 대기

## 개요

LLM 기반 챗봇에 자동으로 탈옥(jailbreak)·프롬프트 인젝션 페이로드를 주입해 가드레일이 뚫리는지 판정하고, 결과를 리포트로 정리하는 공격 시뮬레이션 도구. 공격 대상은 항상 직접 만든 더미 챗봇(로컬 Ollama 모델 + 시스템 프롬프트)이며, 실제 상용 서비스를 대상으로 하지 않는다.

## 목표 / 비목표

**목표**
- 알려진 탈옥 기법(DAN, 역할극, 인코딩 우회 등)을 자동으로 순차 주입하고 성공 여부를 판정
- 마일스톤 전환(게임형 → 실무형 타겟, 키워드 매칭 → LLM-as-judge) 시 코드 재작성 없이 설정만 교체
- 터미널 요약 → HTML/Markdown 공유용 리포트로 결과물 고도화

**비목표**
- Multi-turn 대화형 공격 (스트레치 골로 보류)
- 상용 API(OpenAI/Claude) 타겟 지원 (스트레치 골로 보류)
- 실제 프로덕션 서비스에 대한 공격 (범위 밖, 항상 자체 더미 타겟만 사용)

## 아키텍처

4개의 독립 컴포넌트를 `AttackEngine`이 조립하는 구조.

| 컴포넌트 | 역할 | 인터페이스 | 마일스톤 1 구현체 | 마일스톤 2 구현체 |
|----------|------|-----------|-------------------|-------------------|
| `Target` | 공격 대상 챗봇과 통신 | `send(payload: str) -> str` | `GameTarget` (비밀번호 사수, Ollama) | `PolicyTarget` (기밀 키워드 사수, Ollama) |
| `PayloadSource` | 카테고리별 페이로드 로드 | `load() -> list[Payload(category, text)]` | 공개 탈옥 기법 목록 (YAML) | 동일 + 직접 창작 페이로드 추가 |
| `Judge` | 공격 성공 여부 판정 | `evaluate(payload, response) -> JudgeResult(success, detail)` | `KeywordMatchJudge` | `LLMJudge` (문맥상 유출까지 판단, 별도 LLM 호출) |
| `Reporter` | 결과 출력 | `render(results: list[JudgeResult]) -> None` | `ConsoleReporter` | `HtmlReporter` |

각 컴포넌트는 추상 베이스 클래스(ABC)로 정의하고, 실제 사용할 구현체는 `config.yaml`에서 지정한다.

## 데이터 흐름

1. `config.yaml` 로드 — 타겟 종류, 모델명, 지켜야 할 비밀/규칙, 판정 방식, 페이로드 파일 경로, 리포터 종류
2. `main.py`가 config를 읽어 `Target` / `Judge` / `Reporter` 인스턴스 생성
3. `PayloadSource.load()`로 페이로드 목록 로드
4. `AttackEngine`이 페이로드마다 순회: `Target.send(payload)` → `Judge.evaluate(payload, response)` → 결과 누적
5. `Reporter.render(results)`로 최종 출력

## 설정 파일 예시 (`config.yaml`)

```yaml
target:
  type: game        # game | policy
  model: llama3      # Ollama 모델명
  secret: "hunter2"  # 마일스톤1: 지켜야 할 비밀번호

judge:
  type: keyword      # keyword | llm

payload_source:
  path: payloads/known_jailbreaks.yaml

reporter:
  type: console      # console | html
```

## 에러 처리

- Ollama 연결 실패: 1회 재시도 후 실패 시 해당 페이로드를 "오류"로 기록하고 다음 페이로드로 진행 (전체 실행 중단 안 함)
- 페이로드 파일의 형식 오류: 해당 항목만 건너뛰고 경고 로그 출력
- `Judge` 판정 중 예외 발생: "판정 불가"로 기록하고 계속 진행

## 테스트 전략

- `KeywordMatchJudge`: 알려진 성공/실패 응답 샘플로 단위 테스트
- `AttackEngine`: 가짜(mock) `Target`으로 실제 Ollama 없이 페이로드 로드 → 판정 → 리포트 전체 파이프라인 검증
- `LLMJudge`(마일스톤2): 판정 정확도를 사람이 라벨링한 샘플 응답 세트로 검증

## 마일스톤 및 예상 기간 (총 6~8주)

### 마일스톤 1 — 핵심 프레임워크 + 게임형 타겟 (약 3주)
- 1주차: Ollama 로컬 모델 설치·설정, 프로젝트 구조 및 인터페이스(ABC) 설계, `GameTarget` 구현
- 2주차: `AttackEngine`, `KeywordMatchJudge`, `ConsoleReporter` 구현
- 3주차: 디버깅, 페이로드 카테고리 확장, 단위 테스트 작성

### 마일스톤 2 — 실무형 타겟 + 판정 고도화 + 정식 리포트 (약 3주)
- 4주차: `PolicyTarget`(기밀 키워드 시나리오)로 타겟 교체, 시나리오·페이로드 설계
- 5주차: `LLMJudge` 구현 및 정확도 검증
- 6주차: `HtmlReporter` 구현, 전체 마무리 및 포트폴리오 문서화

### 확장 과제 (선택, 약 1~2주)
- Multi-turn 대화형 공격 기법 추가
- 상용 API(OpenAI/Claude) 타겟과의 비교 테스트

## 저장소 / 문서 관리

- 코드: `llm-redteam-framework` 깃허브 저장소 (GitHub Desktop에 클론됨, 커밋/푸시는 사용자가 직접 진행)
- 진행 상황·의사결정 기록: Obsidian `security-study` 볼트 내 `projects/01-LLM-레드티밍-자동화/진행노트.md`
