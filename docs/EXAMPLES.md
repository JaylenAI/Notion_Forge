# 예제 갤러리 (Examples)

NotionForge가 생성하는 템플릿 예시입니다. 모두 `recipes/`에 결정적 블루프린트로 포함되어 있으며, 실제 Notion에 생성·검증되었습니다. `/api/recipes/{id}` 또는 자연어 프롬프트로 생성할 수 있습니다.

| 예제 | 복잡도 | 핵심 기능 | 라이브 검증 |
|---|---|---|---|
| **CRM 대시보드** (`crm-dashboard`) | advanced | 고객↔딜 멀티DB(dual relation), **rollup 자동집계**(총 딜금액 합산/딜 수), formula(남은일수), 통화 포맷(₩), 샘플 링크 | 고객별 총딜금액 ₩50M/₩80M… 실제 합산 ✅ |
| **OKR 목표 관리** (`okr-dashboard`) | advanced | 목표↔핵심결과 멀티DB, **rollup 평균**(목표 진행률 = KR 달성률 평균), cross-DB rollup-of-formula | 진행률 62/75/33 자동 집계 ✅ |
| **프로젝트 보드** (`project-board`) | standard | 칸반/타임라인 뷰, status, formula(D-Day), 우선순위/카테고리 | D-Day formula 렌더 ✅ |
| **독서 기록** (`reading-log`) | simple | 갤러리 뷰, 평점, 샘플 5권 | 샘플 5/5 삽입 ✅ |

## 무엇이 "유료급"을 만드는가

- **자동 집계(rollup)**: 고객을 딜에 연결하면 총 거래액이 자동 계산됩니다. 단순 표가 아니라 살아있는 대시보드입니다.
- **양방향 관계(dual relation)**: 어느 쪽에서 연결해도 동기화됩니다.
- **계산 속성(formula)**: D-Day, 달성률 등이 자동 계산됩니다.
- **현실적 샘플 데이터**: 빈 템플릿이 아니라 바로 쓸 수 있는 예시 데이터가 채워집니다.
- **통화/퍼센트 포맷**: 금액이 ₩, 달성률이 % 로 표시됩니다.

## 직접 생성하기

```bash
# 레시피로 생성 (REST)
curl -X POST localhost:9500/api/templates/blueprint/import \
  -H 'Content-Type: application/json' \
  -d @recipes/crm-dashboard.json

# 또는 자연어로 (WebSocket /ws/chat 또는 /api/templates/generate)
#   "고객 관리 CRM 만들어줘"  →  AI가 멀티DB + rollup 구조 생성
```

> 참고: AI 생성은 비결정적이라 자연어 결과는 매번 조금씩 다릅니다. 레시피(`recipes/`)는 결정적 예시로 동일하게 재현됩니다. ([README](../README.md)의 "Notes & Limitations" 참고)
