# ADR 0001 — Gate 1 안정성 횡단 결정

- 상태: 채택(Accepted)
- 일자: 2026-05-30
- 맥락: v1.0.0 공개를 위한 안정성 봉합(Gate 1). 감사에서 "구현됐으나 프로덕션에 배선되지 않은 dead code" 다수 발견.

이 문서는 여러 도메인(Agent/보안/관측성/릴리스)에 영향을 주는 3개 횡단 결정을 기록한다.

## 결정 1 — Provider Fallback: **배선(wire)**

5개 AI provider 폴백 체인(`resolve_with_fallback`)이 구현돼 있었으나 프로덕션 호출은 전부 `resolve()`였다(폴백 미적용).

- **결정**: `blueprint_generator`/`pipeline`/`agent_loop`의 provider 해석을 `resolve_with_fallback`로 전환한다. `_FALLBACK_ORDER`에 `copilot` 포함.
- **근거**: primary provider 장애 시 전체 생성이 죽는 것을 막는다. README의 "5 provider 폴백" 주장이 사실이 된다.
- **세부**: 폴백은 키가 불필요한 `copilot`(구독 인증) 또는 settings 키가 있는 provider만 선택한다. 키 없는 fallback은 건너뛴다.
- **영향**: 코드 — `providers/router.py`. 문서 — fallback이 실제 동작하므로 README/ARCHITECTURE 주장 유지.

## 결정 2 — Approval Gate: **배선(wire)**

`process()`가 승인 이벤트를 대기하지 않고 무조건 자동 생성했다. 프론트엔드(confirm/cancel UI)와 모든 호출자(`template`/`tasks` 라우터)는 이미 `approval_request`를 기대하고 있었다.

- **결정**: blueprint 미리보기 후 `approval_request`를 emit하고, `require_approval=True`면 승인을 대기한다(`approval_timeout_seconds` 타임아웃).
  - WebSocket: 사용자 confirm/cancel → `approve_creation()`.
  - REST/Task: `approval_request` 수신 즉시 자동 승인(기존 동작 유지).
  - 타임아웃: 워크스페이스에 임의 생성 방지를 위해 **생성하지 않고 종료**.
- **근거**: 사용자 워크스페이스에 실제 페이지를 만드는 도구이므로, 미리보기 후 명시적 승인이 안전하고 프론트 UX와 정합한다.
- **영향**: 코드 — `orchestrator.py`. 문서 — Approval Gate가 실제 동작하므로 기능을 사실대로 기술(삭제 작업 불필요).

## 결정 3 — 멀티워커 상태: **단일워커 강제 + 문서화**

task store / OAuth state / 세션 / rate limit / 메트릭이 전부 in-memory dict이며, 다중 워커에서 워커 간 불일치가 발생한다.

- **결정**: **단일 워커 운영을 표준으로 강제**하고 문서에 명시한다(외부 store 추상화는 1.0 이후로 연기).
  - 운영: `uvicorn --workers 1` (셀프호스트 기본).
  - `SECURITY.md`의 "TASK_STORE=redis" 등 미구현 주장은 "미구현/예정"으로 강등(Gate 6 처리).
- **근거**: 1인/셀프호스트 오픈소스 현실에 부합. redis 등 외부 의존성 추가는 과도한 초기 복잡도.
- **영향**: 코드 — in-memory 상태 유지(정리/누수 방지만 보강). 문서 — README/SECURITY/DEPLOYMENT에 "수평 확장 불가, 단일 워커" 명시(Gate 6).

## 비고

- 테스트 격리: 테스트는 기본적으로 실제 LLM provider를 호출하지 않도록 전역 mock을 강제한다(`tests/conftest.py`). 실 provider 검증은 명시적 opt-in.
