# NotionForge Frontend

React 기반 채팅 UI + 대시보드 프론트엔드.

## Tech Stack

| 기술 | 버전 | 용도 |
|------|------|------|
| React | 19 | UI 프레임워크 |
| TypeScript | 5.7 | 타입 안전성 |
| Vite | 7 | 빌드 도구 |
| TailwindCSS | 4 | 스타일링 |
| Zustand | 5 | 상태 관리 |
| react-markdown | 10 | AI 응답 렌더링 |

## 빠른 시작

```bash
# 의존성 설치
npm install

# 개발 서버 (http://localhost:9501)
npm run dev

# 빌드
npm run build

# 린트
npm run lint

# 타입 체크
npx tsc --noEmit
```

## 환경변수

`.env` 또는 Docker 환경변수로 설정:

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `VITE_API_URL` | `http://localhost:9500` | 백엔드 REST API URL |
| `VITE_WS_URL` | `ws://localhost:9500` | 백엔드 WebSocket URL |

## 프로젝트 구조

```
src/
  App.tsx              # 루트 컴포넌트 + 라우팅
  main.tsx             # 엔트리포인트
  index.css            # 글로벌 스타일 (Tailwind)
  
  components/
    chat/              # 채팅 인터페이스 (메시지, 입력, 진행률)
    common/            # 공통 UI 컴포넌트 (Button, Modal, Loading)
    dashboard/         # 대시보드 (통계, 이력)
    integrations/      # Notion OAuth 연동 UI
    layout/            # 레이아웃 (Sidebar, Header)
    library/           # 템플릿 라이브러리 (레시피 목록)
    profile/           # 사용자 프로필
    settings/          # 설정 페이지
    support/           # 도움말/지원

  stores/
    chatStore.ts       # 채팅 메시지 + AI 응답 상태
    connectionStore.ts # WebSocket 연결 상태
    settingsStore.ts   # 사용자 설정 (테마, 언어, 복잡도)
    themeStore.ts      # 다크/라이트 모드

  lib/                 # 유틸리티 함수
  types/               # TypeScript 타입 정의
```

## 주요 기능

- **실시간 채팅**: WebSocket 기반 AI 대화
- **진행률 표시**: 템플릿 생성 단계별 실시간 피드백
- **템플릿 라이브러리**: 레시피 검색 및 원클릭 생성
- **Notion OAuth**: 토큰 복붙 없이 OAuth 로그인
- **다크 모드**: 시스템 테마 연동
- **반응형**: 모바일/태블릿 대응

## 개발 가이드

### 컴포넌트 작성

```tsx
// 함수형 컴포넌트 + TypeScript props
interface Props {
  title: string;
  onAction: () => void;
}

export function MyComponent({ title, onAction }: Props) {
  return (
    <button onClick={onAction} className="px-4 py-2 bg-blue-500 text-white rounded">
      {title}
    </button>
  );
}
```

### 상태 관리 (Zustand)

```tsx
import { useChatStore } from '@/stores/chatStore';

function ChatInput() {
  const { sendMessage } = useChatStore();
  // ...
}
```

### 스타일링

- TailwindCSS 유틸리티 클래스 사용
- 커스텀 CSS는 `index.css`에 최소한으로
- 다크 모드: `dark:` prefix 활용

## 빌드 & 배포

```bash
# 프로덕션 빌드
npm run build

# 결과물: dist/ 폴더
# nginx 또는 정적 파일 서빙으로 배포
```

Docker 빌드는 `Dockerfile`에서 multi-stage로 처리됩니다.
