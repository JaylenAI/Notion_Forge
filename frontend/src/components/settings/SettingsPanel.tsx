import { useState } from "react";
import { useChatStore } from "../../stores/chatStore";

export default function SettingsPanel() {
  const { settings, updateSettings, toggleSettings, connectionStatus } =
    useChatStore();

  const [notionKey, setNotionKey] = useState(settings.notionKey);
  const [pageId, setPageId] = useState(settings.pageId);
  const [showKey, setShowKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<
    { ok: boolean; message: string } | null
  >(null);

  const handleSave = () => {
    updateSettings({ ...settings, notionKey, pageId });
    toggleSettings();
  };

  const handleTest = async () => {
    if (!notionKey) {
      setTestResult({ ok: false, message: "API 키를 입력해주세요." });
      return;
    }
    setTesting(true);
    setTestResult(null);

    try {
      const API_URL =
        import.meta.env.VITE_API_URL ?? "http://localhost:9500";
      const resp = await fetch(`${API_URL}/health`);
      if (resp.ok) {
        setTestResult({ ok: true, message: "서버 연결 성공!" });
      } else {
        setTestResult({
          ok: false,
          message: `서버 응답 오류 (${resp.status})`,
        });
      }
    } catch {
      setTestResult({
        ok: false,
        message: "서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해주세요.",
      });
    } finally {
      setTesting(false);
    }
  };

  const maskedKey = notionKey
    ? notionKey.substring(0, 8) + "..." + notionKey.substring(notionKey.length - 4)
    : "";

  return (
    <div className="w-full max-w-md animate-fade-in rounded-2xl border border-zinc-700 bg-zinc-800 p-6 shadow-2xl">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">설정</h2>
        <button
          onClick={toggleSettings}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-400 transition hover:bg-zinc-700 hover:text-white"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      {/* Connection status */}
      <div className="mb-5 flex items-center gap-2 rounded-lg bg-zinc-900/50 px-3 py-2.5">
        <div
          className={`h-2.5 w-2.5 rounded-full ${
            connectionStatus === "connected"
              ? "bg-emerald-500"
              : connectionStatus === "connecting"
                ? "bg-yellow-500"
                : "bg-red-500"
          }`}
        />
        <span className="text-sm text-zinc-300">
          {connectionStatus === "connected"
            ? "WebSocket 연결됨"
            : connectionStatus === "connecting"
              ? "연결 중..."
              : "연결 끊김 (REST 모드)"}
        </span>
      </div>

      {/* Notion API Key */}
      <div className="mb-4">
        <label className="mb-1.5 block text-sm font-medium text-zinc-300">
          Notion API 키
        </label>
        <div className="relative">
          <input
            type={showKey ? "text" : "password"}
            value={notionKey}
            onChange={(e) => setNotionKey(e.target.value)}
            placeholder="ntn_xxxxxxxxxxxxxxxx"
            className="w-full rounded-lg border border-zinc-600 bg-zinc-900/50 px-3 py-2.5 pr-10 text-sm text-white placeholder-zinc-600 outline-none transition focus:border-indigo-500"
          />
          <button
            onClick={() => setShowKey((v) => !v)}
            type="button"
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-zinc-500 hover:text-zinc-300"
          >
            {showKey ? (
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
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                <line x1="1" y1="1" x2="23" y2="23" />
              </svg>
            ) : (
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
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            )}
          </button>
        </div>
        {notionKey && !showKey && (
          <p className="mt-1 text-xs text-zinc-500">{maskedKey}</p>
        )}
        <p className="mt-1 text-xs text-zinc-500">
          <a
            href="https://www.notion.so/my-integrations"
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-400 hover:underline"
          >
            Notion Integrations
          </a>
          에서 발급받을 수 있습니다.
        </p>
      </div>

      {/* Parent Page ID */}
      <div className="mb-5">
        <label className="mb-1.5 block text-sm font-medium text-zinc-300">
          부모 페이지 ID
        </label>
        <input
          type="text"
          value={pageId}
          onChange={(e) => setPageId(e.target.value)}
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          className="w-full rounded-lg border border-zinc-600 bg-zinc-900/50 px-3 py-2.5 text-sm text-white placeholder-zinc-600 outline-none transition focus:border-indigo-500"
        />
        <p className="mt-1 text-xs text-zinc-500">
          템플릿이 생성될 상위 페이지의 ID (페이지 URL에서 복사)
        </p>
      </div>

      {/* Test result */}
      {testResult && (
        <div
          className={`mb-4 rounded-lg px-3 py-2.5 text-sm ${
            testResult.ok
              ? "bg-emerald-900/30 text-emerald-300"
              : "bg-red-900/30 text-red-300"
          }`}
        >
          {testResult.message}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleTest}
          disabled={testing}
          className="flex-1 rounded-lg border border-zinc-600 px-4 py-2.5 text-sm font-medium text-zinc-300 transition hover:border-zinc-500 hover:bg-zinc-700 disabled:opacity-50"
        >
          {testing ? "테스트 중..." : "연결 테스트"}
        </button>
        <button
          onClick={handleSave}
          className="flex-1 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-500"
        >
          저장
        </button>
      </div>
    </div>
  );
}
