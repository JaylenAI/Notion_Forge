import { useChatStore } from "../../stores/chatStore";
import ChatWindow from "../chat/ChatWindow";
import SettingsPanel from "../settings/SettingsPanel";

export default function MainLayout() {
  const { settingsOpen } = useChatStore();

  return (
    <div className="flex h-screen bg-zinc-900 text-white">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r border-zinc-700 bg-zinc-900">
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-lg font-bold">
            N
          </div>
          <div>
            <h1 className="text-sm font-semibold text-white">NotionForge</h1>
            <p className="text-xs text-zinc-400">AI 노션 템플릿 생성기</p>
          </div>
        </div>

        {/* New Chat */}
        <div className="px-3 pb-3">
          <button
            onClick={() => useChatStore.getState().clearMessages()}
            className="flex w-full items-center gap-2 rounded-lg border border-zinc-600 px-3 py-2.5 text-sm text-zinc-300 transition hover:border-zinc-500 hover:bg-zinc-800"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 5v14M5 12h14" />
            </svg>
            새 대화
          </button>
        </div>

        {/* Template shortcuts */}
        <div className="flex-1 overflow-y-auto px-3">
          <p className="mb-2 px-2 text-xs font-medium text-zinc-500">
            빠른 템플릿
          </p>
          {[
            { icon: "📊", label: "프로젝트 대시보드" },
            { icon: "✅", label: "습관 트래커" },
            { icon: "📚", label: "독서 기록" },
            { icon: "🔖", label: "북마크 정리" },
            { icon: "📝", label: "회의록 템플릿" },
            { icon: "🎯", label: "OKR 관리" },
          ].map((t) => (
            <button
              key={t.label}
              onClick={() =>
                useChatStore.getState().sendMessage(`${t.label} 만들어줘`)
              }
              className="flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left text-sm text-zinc-400 transition hover:bg-zinc-800 hover:text-white"
            >
              <span className="text-base">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </div>

        {/* Bottom: Settings */}
        <div className="border-t border-zinc-700 p-3">
          <ConnectionBadge />
          <button
            onClick={() => useChatStore.getState().toggleSettings()}
            className="mt-2 flex w-full items-center gap-2 rounded-lg px-2 py-2 text-sm text-zinc-400 transition hover:bg-zinc-800 hover:text-white"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            설정
          </button>
        </div>
      </aside>

      {/* Main content area */}
      <main className="relative flex flex-1 flex-col overflow-hidden">
        <ChatWindow />

        {/* Settings overlay */}
        {settingsOpen && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <SettingsPanel />
          </div>
        )}
      </main>
    </div>
  );
}

function ConnectionBadge() {
  const status = useChatStore((s) => s.connectionStatus);

  const config = {
    connected: {
      color: "bg-emerald-500",
      text: "WebSocket 연결됨",
      textColor: "text-emerald-400",
    },
    connecting: {
      color: "bg-yellow-500",
      text: "연결 중...",
      textColor: "text-yellow-400",
    },
    disconnected: {
      color: "bg-red-500",
      text: "REST 모드",
      textColor: "text-red-400",
    },
  }[status];

  return (
    <div className="flex items-center gap-2 px-2 py-1">
      <div className={`h-2 w-2 rounded-full ${config.color}`} />
      <span className={`text-xs ${config.textColor}`}>{config.text}</span>
    </div>
  );
}
