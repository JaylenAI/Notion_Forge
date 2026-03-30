import { useState, useCallback, type FormEvent } from "react";
import { useChatStore } from "../../stores/chatStore";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:9500";

function IntegrationsPage() {
  const settings = useChatStore((s) => s.settings);
  const updateSettings = useChatStore((s) => s.updateSettings);
  const connectionStatus = useChatStore((s) => s.connectionStatus);
  const connectionTested = useChatStore((s) => s.connectionTested);
  const setConnectionTested = useChatStore((s) => s.setConnectionTested);

  const [notionKey, setNotionKey] = useState(settings.notionKey);
  const [pageId, setPageId] = useState(settings.pageId);
  const [showToken, setShowToken] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<"success" | "error" | null>(
    null
  );

  const handleSave = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      updateSettings({ notionKey, pageId });
    },
    [notionKey, pageId, updateSettings]
  );

  const handleTest = useCallback(async () => {
    if (!notionKey.trim()) return;
    setTesting(true);
    setTestResult(null);
    try {
      const response = await fetch(`${API_URL}/api/health`, {
        headers: notionKey ? { "X-Notion-Token": notionKey } : {},
      });
      if (response.ok) {
        setTestResult("success");
        setConnectionTested(true);
      } else {
        setTestResult("error");
        setConnectionTested(false);
      }
    } catch {
      setTestResult("error");
      setConnectionTested(false);
    } finally {
      setTesting(false);
    }
  }, [notionKey, setConnectionTested]);

  const isConnected =
    connectionStatus === "connected" || connectionTested;

  return (
    <div className="flex-1 overflow-y-auto pt-8 pb-20">
      <div className="max-w-6xl mx-auto px-10 py-4">
        {/* Header */}
        <div className="flex justify-between items-end mb-12">
          <div>
            <h2 className="text-4xl font-extrabold font-headline text-[#e5e2e1] tracking-tight mb-2">
              Notion Connection
            </h2>
            <p className="text-[#c2c6d8] max-w-lg">
              Forge a bridge between the AI Alchemist and your Notion workspace
              to automate template generation and data syncing.
            </p>
          </div>
          <div className="flex items-center gap-3 bg-[#1c1b1b] px-4 py-2 rounded-full border border-[#424656]/10">
            <span className="relative flex h-3 w-3">
              {isConnected && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#4edea3] opacity-75" />
              )}
              <span
                className={`relative inline-flex rounded-full h-3 w-3 ${
                  isConnected ? "bg-[#4edea3]" : "bg-[#ffb4ab]"
                }`}
              />
            </span>
            <span
              className={`text-xs font-bold uppercase tracking-widest ${
                isConnected ? "text-[#4edea3]" : "text-[#ffb4ab]"
              }`}
            >
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-8">
          {/* Setup Form */}
          <div className="col-span-12 lg:col-span-7 space-y-6">
            <div className="bg-[#1c1b1b] p-8 rounded-xl relative overflow-hidden group">
              <form onSubmit={handleSave} className="space-y-8 relative z-10">
                {/* Integration Token */}
                <div className="space-y-2">
                  <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-[#adc6ff]">
                    Integration Token
                  </label>
                  <div className="relative group">
                    <input
                      type={showToken ? "text" : "password"}
                      value={notionKey}
                      onChange={(e) => setNotionKey(e.target.value)}
                      className="w-full bg-transparent border-0 border-b border-[#424656]/30 py-3 text-[#e5e2e1] focus:ring-0 focus:border-[#adc6ff] transition-all placeholder:text-[#424656] outline-none"
                      placeholder="secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                    />
                    <button
                      type="button"
                      onClick={() => setShowToken((prev) => !prev)}
                      className="absolute right-0 top-3 material-symbols-outlined text-[#424656] hover:text-[#adc6ff] cursor-pointer transition-colors"
                    >
                      {showToken ? "visibility_off" : "visibility"}
                    </button>
                  </div>
                  <p className="text-[10px] text-[#c2c6d8]/60 italic">
                    Your internal integration secret from the Notion Developers
                    portal.
                  </p>
                </div>

                {/* Workspace / Page URL */}
                <div className="space-y-2">
                  <label className="block text-[10px] font-bold uppercase tracking-[0.2em] text-[#adc6ff]">
                    Workspace / Page URL
                  </label>
                  <input
                    type="text"
                    value={pageId}
                    onChange={(e) => setPageId(e.target.value)}
                    className="w-full bg-transparent border-0 border-b border-[#424656]/30 py-3 text-[#e5e2e1] focus:ring-0 focus:border-[#adc6ff] transition-all placeholder:text-[#424656] outline-none"
                    placeholder="https://www.notion.so/my-workspace/page-id"
                  />
                  <p className="text-[10px] text-[#c2c6d8]/60 italic">
                    The target root page where NotionForge is allowed to create
                    templates.
                  </p>
                </div>

                {/* Buttons */}
                <div className="pt-4 flex items-center gap-4">
                  <button
                    type="submit"
                    className="flex items-center gap-2 bg-gradient-to-r from-[#006de6] to-[#adc6ff] text-[#001a41] px-8 py-3 rounded-lg font-bold text-sm hover:shadow-[0_0_24px_rgba(173,198,255,0.3)] transition-all active:scale-95"
                  >
                    <span className="material-symbols-outlined text-lg">
                      bolt
                    </span>
                    Save &amp; Connect
                  </button>
                  <button
                    type="button"
                    onClick={handleTest}
                    disabled={testing}
                    className="flex items-center gap-2 border border-[#424656]/30 text-[#c2c6d8] px-6 py-3 rounded-lg font-bold text-sm hover:bg-[#3a3939] transition-all disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-lg">
                      sync_alt
                    </span>
                    {testing ? "Testing..." : "Test Connection"}
                  </button>
                </div>

                {/* Test Result Feedback */}
                {testResult === "success" && (
                  <div className="flex items-center gap-2 text-[#4edea3] text-sm animate-fade-in">
                    <span className="material-symbols-outlined text-sm">
                      check_circle
                    </span>
                    Connection successful
                  </div>
                )}
                {testResult === "error" && (
                  <div className="flex items-center gap-2 text-[#ffb4ab] text-sm animate-fade-in">
                    <span className="material-symbols-outlined text-sm">
                      error
                    </span>
                    Connection failed. Please check your credentials.
                  </div>
                )}
              </form>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 gap-4">
              <div className="glass-panel p-6 rounded-xl border border-[#424656]/10 group cursor-pointer hover:border-[#adc6ff]/20 transition-all">
                <span className="material-symbols-outlined text-[#adc6ff] mb-3 block">
                  auto_fix_high
                </span>
                <h4 className="font-bold text-[#e5e2e1] mb-1">Auto-Sync</h4>
                <p className="text-xs text-[#c2c6d8]">
                  Sync changes from Notion back to Forge in real-time.
                </p>
              </div>
              <div className="glass-panel p-6 rounded-xl border border-[#424656]/10 group cursor-pointer hover:border-[#adc6ff]/20 transition-all">
                <span className="material-symbols-outlined text-[#ffb59a] mb-3 block">
                  history
                </span>
                <h4 className="font-bold text-[#e5e2e1] mb-1">Audit Log</h4>
                <p className="text-xs text-[#c2c6d8]">
                  View every template block created by the Alchemist.
                </p>
              </div>
            </div>
          </div>

          {/* Setup Guide */}
          <div className="col-span-12 lg:col-span-5">
            <div className="bg-[#353534]/40 rounded-xl p-8 border border-[#424656]/10">
              <h3 className="font-headline text-xl font-bold mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#adc6ff]">
                  school
                </span>
                Setup Guide
              </h3>
              <div className="space-y-8">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#201f1f] flex items-center justify-center font-bold text-xs text-[#adc6ff] border border-[#adc6ff]/20">
                    1
                  </div>
                  <div>
                    <h5 className="font-bold text-sm text-[#e5e2e1] mb-1">
                      Create Integration
                    </h5>
                    <p className="text-xs text-[#c2c6d8] leading-relaxed">
                      Visit{" "}
                      <a
                        href="https://www.notion.so/my-integrations"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[#ffb59a] underline underline-offset-4 cursor-pointer"
                      >
                        Notion My-Integrations
                      </a>{" "}
                      and click &quot;+ New Integration&quot;.
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#201f1f] flex items-center justify-center font-bold text-xs text-[#adc6ff] border border-[#adc6ff]/20">
                    2
                  </div>
                  <div>
                    <h5 className="font-bold text-sm text-[#e5e2e1] mb-1">
                      Grant Permissions
                    </h5>
                    <p className="text-xs text-[#c2c6d8] leading-relaxed">
                      Select your workspace and ensure &quot;Insert
                      Content&quot; and &quot;Read Content&quot; capabilities are
                      enabled.
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#201f1f] flex items-center justify-center font-bold text-xs text-[#adc6ff] border border-[#adc6ff]/20">
                    3
                  </div>
                  <div>
                    <h5 className="font-bold text-sm text-[#e5e2e1] mb-1">
                      Invite Alchemist
                    </h5>
                    <p className="text-xs text-[#c2c6d8] leading-relaxed">
                      Go to your Notion page, click &quot;...&quot; (top right)
                      &gt; &quot;Add connections&quot; and find your integration
                      name.
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-10 rounded-xl overflow-hidden border border-[#424656]/20 group">
                <div className="w-full h-32 bg-gradient-to-br from-[#006de6]/30 via-[#adc6ff]/10 to-[#131313] group-hover:from-[#006de6]/40 transition-all duration-700" />
                <div className="p-4 bg-[#1c1b1b]">
                  <p className="text-[10px] text-center font-medium uppercase tracking-[0.2em] text-[#c2c6d8]/40">
                    Visualizing Data Bridge
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default IntegrationsPage;
