import { useChatStore } from "../../stores/chatStore";

function ProfilePage() {
  const settings = useChatStore((s) => s.settings);
  const templates = useChatStore((s) => s.generatedTemplates);
  const aiProvider = useChatStore((s) => s.aiProvider);
  const connectionStatus = useChatStore((s) => s.connectionStatus);
  const setPage = useChatStore((s) => s.setPage);

  const templateCount = templates.length;
  const starredCount = templates.filter((t) => t.starred).length;
  const hasNotion = !!settings.notionKey;
  const hasAi = !!settings.aiKey;

  return (
    <div className="flex-1 overflow-y-auto pt-8 pb-20">
      <div className="max-w-4xl mx-auto px-10 py-4">
        {/* Header */}
        <div className="mb-10">
          <h2 className="text-4xl font-extrabold font-headline text-[#e5e2e1] tracking-tight mb-2">
            Profile
          </h2>
          <p className="text-[#c2c6d8] max-w-lg">
            Your account overview and connection status.
          </p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Connection Status */}
          <div className="col-span-12 lg:col-span-7 space-y-6">
            {/* Notion Connection */}
            <div className="bg-[#1c1b1b] rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm text-[#adc6ff]">link</span>
                  Notion Connection
                </h3>
                <span className={`flex items-center gap-1.5 text-xs ${hasNotion ? "text-[#4edea3]" : "text-[#ffb4ab]"}`}>
                  <span className={`w-2 h-2 rounded-full ${hasNotion ? "bg-[#4edea3]" : "bg-[#ffb4ab]"}`} />
                  {hasNotion ? "Connected" : "Not Connected"}
                </span>
              </div>
              {hasNotion ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[#888]">Token</span>
                    <span className="text-[#d4d4d4] font-mono">{settings.notionKey.slice(0, 8)}...{settings.notionKey.slice(-4)}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[#888]">WebSocket</span>
                    <span className={connectionStatus === "connected" ? "text-[#4edea3]" : "text-[#ffb4ab]"}>
                      {connectionStatus}
                    </span>
                  </div>
                  {settings.pageId && (
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-[#888]">Target Page</span>
                      <span className="text-[#d4d4d4] font-mono truncate ml-4 max-w-[200px]">{settings.pageId}</span>
                    </div>
                  )}
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => setPage("integrations")}
                  className="text-xs text-[#adc6ff] hover:underline"
                >
                  Set up Notion connection
                </button>
              )}
            </div>

            {/* AI Provider */}
            <div className="bg-[#1c1b1b] rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm text-[#adc6ff]">smart_toy</span>
                  AI Provider
                </h3>
                <span className={`flex items-center gap-1.5 text-xs ${hasAi ? "text-[#4edea3]" : "text-[#888]"}`}>
                  <span className={`w-2 h-2 rounded-full ${hasAi ? "bg-[#4edea3]" : "bg-[#555]"}`} />
                  {hasAi ? (aiProvider || "Configured") : "Using Default"}
                </span>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-[#888]">Model</span>
                  <span className="text-[#d4d4d4]">{settings.aiModel || "(default)"}</span>
                </div>
                {hasAi && (
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[#888]">API Key</span>
                    <span className="text-[#d4d4d4] font-mono">{settings.aiKey.slice(0, 8)}...{settings.aiKey.slice(-4)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Skills Available */}
            <div className="bg-[#1c1b1b] rounded-xl p-6">
              <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-sm text-[#adc6ff]">category</span>
                Available Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {["Track", "Collect", "Manage", "Plan", "Organize", "Guide", "Hub", "Finance", "Journal", "Content", "Learn", "CRM"].map((skill) => (
                  <span key={skill} className="px-2.5 py-1 rounded-lg bg-[#252525] text-[10px] text-[#c2c6d8] border border-[#333]">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="col-span-12 lg:col-span-5 space-y-6">
            <div className="bg-[#353534]/40 rounded-xl p-8 border border-[#424656]/10">
              <h3 className="font-headline text-lg font-bold mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#adc6ff]">analytics</span>
                Usage
              </h3>
              <div className="space-y-6">
                <StatItem label="Templates Created" value={templateCount} color="#ffb59a" />
                <StatItem label="Starred" value={starredCount} color="#adc6ff" />
              </div>
            </div>

            {/* Data Management */}
            <div className="bg-[#1c1b1b] rounded-xl p-6 space-y-4">
              <h3 className="font-headline text-sm font-bold flex items-center gap-2 text-white">
                <span className="material-symbols-outlined text-sm text-gray-400">storage</span>
                Data
              </h3>
              <div className="space-y-2">
                <button
                  type="button"
                  onClick={() => setPage("integrations")}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-gray-400 hover:bg-[#2a2a2a] hover:text-white transition-all"
                >
                  <span className="material-symbols-outlined text-sm">settings</span>
                  Manage Integrations
                </button>
                <button
                  type="button"
                  onClick={() => {
                    localStorage.removeItem("notionforge_templates");
                    window.location.reload();
                  }}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-[#ffb4ab] hover:bg-[#ffb4ab]/10 transition-all"
                >
                  <span className="material-symbols-outlined text-sm">delete_sweep</span>
                  Clear Template History
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatItem({ label, value, color }: { readonly label: string; readonly value: number; readonly color: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-gray-400 uppercase tracking-wider">{label}</span>
      <span className="text-2xl font-bold" style={{ color }}>{value}</span>
    </div>
  );
}

export default ProfilePage;
