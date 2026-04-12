import { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import toast from "react-hot-toast";
import { useChatStore } from "../../stores/chatStore";
import { timeAgo } from "../../lib/timeago";
import PromptLibrary from "./PromptLibrary";

const STARTER_PROMPTS = [
  { icon: "\u{1F3CB}\uFE0F", title: "Workout Tracker", prompt: "\uC6B4\uB3D9 \uAE30\uB85D \uC77C\uC9C0 \uB9CC\uB4E4\uC5B4\uC918", color: "orange" },
  { icon: "\u{1F4CA}", title: "Project Board", prompt: "\uD504\uB85C\uC81D\uD2B8 \uAD00\uB9AC \uB300\uC2DC\uBCF4\uB4DC \uB9CC\uB4E4\uC5B4\uC918", color: "blue" },
  { icon: "\u{1F4DA}", title: "Reading Log", prompt: "\uB3C5\uC11C \uAE30\uB85D\uC7A5 \uB9CC\uB4E4\uC5B4\uC918", color: "green" },
  { icon: "\u{1F4B0}", title: "Budget Manager", prompt: "\uAC00\uACC4\uBD80 \uB9CC\uB4E4\uC5B4\uC918", color: "yellow" },
  { icon: "\u{1F4DD}", title: "Content Calendar", prompt: "\uCF58\uD150\uCE20 \uCE98\uB9B0\uB354 \uB9CC\uB4E4\uC5B4\uC918", color: "purple" },
  { icon: "\u2708\uFE0F", title: "Travel Planner", prompt: "\uC5EC\uD589 \uACC4\uD68D\uD45C \uB9CC\uB4E4\uC5B4\uC918", color: "red" },
];

const STARTER_COLOR_MAP: Record<string, string> = {
  orange: "border-orange-500/30 hover:border-orange-500/60 hover:bg-orange-500/5",
  blue: "border-blue-500/30 hover:border-blue-500/60 hover:bg-blue-500/5",
  green: "border-green-500/30 hover:border-green-500/60 hover:bg-green-500/5",
  yellow: "border-yellow-500/30 hover:border-yellow-500/60 hover:bg-yellow-500/5",
  purple: "border-purple-500/30 hover:border-purple-500/60 hover:bg-purple-500/5",
  red: "border-red-500/30 hover:border-red-500/60 hover:bg-red-500/5",
};

function ChatPanel() {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const sendMessage = useChatStore((s) => s.sendMessage);
  const connectionStatus = useChatStore((s) => s.connectionStatus);
  const connect = useChatStore((s) => s.connect);
  const settings = useChatStore((s) => s.settings);
  const aiProvider = useChatStore((s) => s.aiProvider);
  const copilotStatus = useChatStore((s) => s.copilotStatus);
  const fetchCopilotStatus = useChatStore((s) => s.fetchCopilotStatus);
  const sessions = useChatStore((s) => s.sessions);
  const loadSession = useChatStore((s) => s.loadSession);
  const deleteSession = useChatStore((s) => s.deleteSession);
  const newSession = useChatStore((s) => s.newSession);

  const complexity = useChatStore((s) => s.complexity);
  const language = useChatStore((s) => s.language);
  const setComplexity = useChatStore((s) => s.setComplexity);
  const setLanguage = useChatStore((s) => s.setLanguage);

  const [input, setInput] = useState("");
  const [showHistory, setShowHistory] = useState(false);
  const [showPromptLibrary, setShowPromptLibrary] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Connect once on mount, not on every status change
  const connectCalledRef = useRef(false);
  useEffect(() => {
    if (!connectCalledRef.current) {
      connectCalledRef.current = true;
      connect();
      fetchCopilotStatus();
    }
  }, [connect, fetchCopilotStatus]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback((text?: string) => {
    const trimmed = (text ?? input).trim();
    if (!trimmed || isLoading) return;
    sendMessage(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.value = "";
      textareaRef.current.style.height = "auto";
    }
  }, [input, isLoading, sendMessage]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // 한글 IME 조합 중이면 무시 (조합 완료 후 Enter에만 반응)
      if (e.nativeEvent.isComposing) return;
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleTextareaChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setInput(e.target.value);
      const el = e.target;
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
    },
    []
  );

  const hasMessages = messages.length > 0;

  return (
    <section className="h-full flex flex-col bg-[var(--chat-bg,#0e0e0e)] rounded-2xl overflow-hidden border border-[var(--border-color,#424656)]/10">
      {/* Header */}
      <div className="p-4 sm:p-6 border-b border-[var(--border-color,#424656)]/10 flex items-center justify-between">
        <div className="min-w-0">
          <h3 className="font-headline font-bold text-base sm:text-lg">Alchemist Chat</h3>
          <div className="flex items-center gap-1.5 mt-0.5">
            <ModelBadge model={settings.aiModel} provider={aiProvider} copilotModel={copilotStatus?.available ? copilotStatus.model : undefined} />
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Session history toggle */}
          <button
            type="button"
            onClick={() => setShowHistory((p) => !p)}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-[var(--text-muted,#c2c6d8)]/60 hover:text-[#adc6ff] hover:bg-[#adc6ff]/10 transition-colors"
            title="Chat History"
          >
            <span className="material-symbols-outlined text-sm">history</span>
          </button>
          {/* New session */}
          <button
            type="button"
            onClick={newSession}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-[var(--text-muted,#c2c6d8)]/60 hover:text-[#adc6ff] hover:bg-[#adc6ff]/10 transition-colors"
            title="New Chat"
          >
            <span className="material-symbols-outlined text-sm">add</span>
          </button>
          <span
            className={`flex h-2 w-2 rounded-full shrink-0 ${
              connectionStatus === "connected"
                ? "bg-[#4edea3] animate-pulse"
                : connectionStatus === "connecting"
                  ? "bg-[#adc6ff] animate-pulse"
                  : "bg-[#ffb4ab]"
            }`}
          />
        </div>
      </div>

      {/* Session History Drawer */}
      {showHistory && (
        <div className="border-b border-[var(--border-color,#424656)]/10 bg-[var(--surface-low,#1c1b1b)] max-h-52 overflow-y-auto animate-fade-in">
          <div className="p-3">
            <p className="text-[10px] uppercase tracking-wider text-[var(--text-muted,#c2c6d8)]/50 mb-2 font-bold">
              Recent Sessions ({sessions.length})
            </p>
            {sessions.length === 0 ? (
              <p className="text-xs text-[var(--text-muted,#c2c6d8)]/40 py-2">No saved sessions</p>
            ) : (
              <div className="space-y-1">
                {sessions.slice(0, 20).map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-[var(--surface-container,#2a2a2a)] transition-colors group"
                  >
                    <button
                      type="button"
                      onClick={() => { loadSession(session.id); setShowHistory(false); }}
                      className="flex-1 text-left min-w-0"
                    >
                      <p className="text-xs text-[var(--text-primary,#e5e2e1)] truncate">{session.title}</p>
                      <p className="text-[10px] text-[var(--text-muted,#c2c6d8)]/40">
                        {timeAgo(session.updatedAt)} · {session.messages.length} messages
                      </p>
                    </button>
                    <button
                      type="button"
                      onClick={() => deleteSession(session.id)}
                      className="opacity-0 group-hover:opacity-100 text-[#ffb4ab] hover:bg-[#ffb4ab]/10 rounded p-1 transition-all"
                    >
                      <span className="material-symbols-outlined text-xs">delete</span>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 flex flex-col">
        {!hasMessages && (
          <div className="flex flex-col items-center justify-center flex-1 text-center">
            <span
              className="material-symbols-outlined text-4xl text-[#adc6ff] mb-4 opacity-40"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              auto_awesome
            </span>
            <p className="text-sm text-[var(--text-muted,#c2c6d8)] opacity-60 mb-1">
              Describe the Notion template you want to create.
            </p>
            <p className="text-xs text-[var(--text-muted,#c2c6d8)]/40 mb-6">
              Or pick a starter below
            </p>

            {/* Starter prompt cards */}
            <div className="grid grid-cols-2 gap-2 w-full max-w-[280px]">
              {STARTER_PROMPTS.map((s) => (
                <button
                  key={s.prompt}
                  type="button"
                  onClick={() => handleSend(s.prompt)}
                  disabled={isLoading}
                  className={`flex items-center gap-2 px-3 py-2.5 rounded-xl border bg-transparent text-left transition-all duration-200 disabled:opacity-40 ${STARTER_COLOR_MAP[s.color] ?? ""}`}
                >
                  <span className="text-lg">{s.icon}</span>
                  <span className="text-xs text-[var(--text-muted,#c2c6d8)] font-medium truncate">{s.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-col gap-4 mt-auto">
          {messages.map((msg) =>
            msg.role === "user" ? (
              <div key={msg.id} className="flex justify-end animate-fade-in group">
                <div className="bg-[var(--surface-container,#2a2a2a)] text-[var(--text-primary,#e5e2e1)] max-w-[85%] rounded-2xl rounded-tr-none px-4 py-3 text-sm break-words overflow-hidden">
                  <p className="whitespace-pre-wrap break-words max-w-full">{msg.content}</p>
                  <p className="text-[10px] text-[var(--text-muted,#c2c6d8)]/30 mt-1.5 text-right opacity-0 group-hover:opacity-100 transition-opacity">
                    {timeAgo(msg.timestamp)}
                  </p>
                </div>
              </div>
            ) : (
              <div
                key={msg.id}
                className="flex justify-start gap-3 animate-fade-in group"
              >
                <div className="w-8 h-8 rounded-lg bg-[#adc6ff]/20 flex items-center justify-center shrink-0">
                  <span
                    className="material-symbols-outlined text-[#adc6ff] text-sm"
                    style={{ fontVariationSettings: "'FILL' 1" }}
                  >
                    auto_awesome
                  </span>
                </div>
                <div className="glass-panel text-[var(--text-muted,#c2c6d8)] max-w-[85%] rounded-2xl rounded-tl-none px-4 py-3 text-sm border-l-2 border-[#adc6ff] break-words overflow-hidden">
                  {msg.metadata?.type === "progress" && (
                    <ProgressIndicator step={msg.metadata.step} />
                  )}
                  {msg.metadata?.type === "error" && (
                    <div className="flex items-center gap-1.5 mb-2 text-[#ffb4ab]">
                      <span className="material-symbols-outlined text-xs">error</span>
                      <span className="text-xs font-medium">Error</span>
                    </div>
                  )}
                  {/* Markdown rendering for assistant messages */}
                  {msg.content ? (
                    <div className="markdown-body">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  ) : null}
                  {msg.metadata?.type === "approval_request" && (
                    <ApprovalActions />
                  )}
                  {msg.metadata?.type === "complete" && msg.metadata.notionUrl && (
                    <CompletionActions notionUrl={msg.metadata.notionUrl} />
                  )}
                  {msg.metadata?.notionUrl && msg.metadata?.type !== "complete" && (
                    <NotionUrlLink url={msg.metadata.notionUrl} />
                  )}
                  <p className="text-[10px] text-[var(--text-muted,#c2c6d8)]/30 mt-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    {timeAgo(msg.timestamp)}
                  </p>
                </div>
              </div>
            )
          )}

          {isLoading && <ProgressStream />}
        </div>
        <div ref={messagesEndRef} />
      </div>

      {/* Prompt Library Modal */}
      <PromptLibrary
        open={showPromptLibrary}
        onClose={() => setShowPromptLibrary(false)}
        onSelect={handleSend}
      />

      {/* Complexity & Language & Model Selector */}
      <div className="px-3 sm:px-4 pt-2 pb-0 bg-[var(--surface-low,#1c1b1b)] border-t border-[var(--border-color,#424656)]/10 flex items-center gap-3 text-xs flex-wrap">
        <div className="flex items-center gap-1">
          <span className="text-[var(--text-muted,#c2c6d8)]/50">Complexity:</span>
          {(["simple", "standard", "advanced"] as const).map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setComplexity(c)}
              className={`px-2 py-0.5 rounded-md transition-colors ${
                complexity === c
                  ? "bg-[#adc6ff]/20 text-[#adc6ff]"
                  : "text-[var(--text-muted,#c2c6d8)]/40 hover:text-[var(--text-muted,#c2c6d8)]/70"
              }`}
            >
              {c === "simple" ? "Simple" : c === "standard" ? "Standard" : "Advanced"}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1">
          <span className="text-[var(--text-muted,#c2c6d8)]/50">Lang:</span>
          {(["ko", "en", "ja"] as const).map((l) => (
            <button
              key={l}
              type="button"
              onClick={() => setLanguage(l)}
              className={`px-2 py-0.5 rounded-md transition-colors ${
                language === l
                  ? "bg-[#adc6ff]/20 text-[#adc6ff]"
                  : "text-[var(--text-muted,#c2c6d8)]/40 hover:text-[var(--text-muted,#c2c6d8)]/70"
              }`}
            >
              {l === "ko" ? "KR" : l === "en" ? "EN" : "JP"}
            </button>
          ))}
        </div>
        {/* Model Quick Display */}
        <ModelBadgeInline />
      </div>

      {/* Input Area */}
      <div className="p-3 sm:p-4 bg-[var(--surface-low,#1c1b1b)] border-b-0 border-t-0">
        <div className="flex items-end gap-2">
          <button
            type="button"
            onClick={() => setShowPromptLibrary(true)}
            className="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-[var(--text-muted,#c2c6d8)]/50 hover:text-[#adc6ff] hover:bg-[#adc6ff]/10 transition-colors mb-0.5"
            title="Prompt Library"
          >
            <span className="material-symbols-outlined text-lg">library_books</span>
          </button>
          <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            className="w-full bg-[var(--surface-variant,#353534)] border-none rounded-xl text-sm text-[var(--text-primary,#e5e2e1)] placeholder:text-[var(--text-muted,#c2c6d8)]/40 focus:ring-1 focus:ring-[#adc6ff] py-3 pl-4 pr-12 resize-none outline-none"
            placeholder="Describe the template you want to create..."
            rows={2}
          />
          <button
            type="button"
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="absolute right-3 bottom-3 w-8 h-8 bg-[#adc6ff] text-[#002e69] rounded-lg flex items-center justify-center hover:scale-105 transition-transform active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined text-sm">send</span>
          </button>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─── Sub-components ─── */

function ProgressStream() {
  const progressLog = useChatStore((s) => s.progressLog);
  const cancelGeneration = useChatStore((s) => s.cancelGeneration);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [progressLog]);

  return (
    <div className="flex justify-start gap-3 animate-fade-in">
      <div className="w-8 h-8 rounded-lg bg-[#adc6ff]/20 flex items-center justify-center shrink-0 mt-1">
        <span
          className="material-symbols-outlined text-[#adc6ff] text-sm"
          style={{ fontVariationSettings: "'FILL' 1" }}
        >
          auto_awesome
        </span>
      </div>
      <div className="glass-panel text-[var(--text-muted,#c2c6d8)] max-w-[85%] rounded-2xl rounded-tl-none px-4 py-3 text-sm border-l-2 border-[#adc6ff] min-w-[200px]">
        {/* Progress log stream */}
        {progressLog.length > 0 ? (
          <div className="space-y-1 mb-2 max-h-40 overflow-y-auto">
            {progressLog.map((log, i) => (
              <p key={i} className={`text-xs ${i === progressLog.length - 1 ? "text-[#adc6ff]" : "text-[var(--text-muted,#c2c6d8)]/40"} transition-colors`}>
                {log}
              </p>
            ))}
            <div ref={logEndRef} />
          </div>
        ) : null}
        {/* Pulse dots + cancel */}
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-[#adc6ff] animate-pulse-dot" />
          <div className="w-1.5 h-1.5 rounded-full bg-[#adc6ff] animate-pulse-dot-delay-1" />
          <div className="w-1.5 h-1.5 rounded-full bg-[#adc6ff] animate-pulse-dot-delay-2" />
          <span className="ml-1 text-[10px] italic text-[var(--text-muted,#c2c6d8)]/40">
            {progressLog.length > 0 ? progressLog[progressLog.length - 1]?.slice(0, 30) : "Transmuting..."}
          </span>
          <button
            type="button"
            onClick={cancelGeneration}
            className="ml-auto px-2 py-0.5 rounded-lg bg-[#ffb4ab]/15 text-[#ffb4ab] text-[10px] font-medium hover:bg-[#ffb4ab]/25 transition-colors flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-xs">close</span>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

function ProgressIndicator({ step }: { readonly step?: string }) {
  const STEP_ICONS: Record<string, string> = {
    intent: "psychology",
    skill: "category",
    design: "architecture",
    creating_page: "note_add",
    creating_db: "database",
    adding_items: "playlist_add",
    adding_views: "grid_view",
    complete: "check_circle",
  };
  const icon = (step && STEP_ICONS[step]) ?? "pending";

  return (
    <div className="flex items-center gap-1.5 mb-2 text-[#adc6ff]/70">
      <span className="material-symbols-outlined text-xs animate-pulse">{icon}</span>
      <span className="text-[11px] italic">In progress...</span>
    </div>
  );
}

function NotionUrlLink({ url }: { readonly url: string }) {
  const handleCopy = () => {
    navigator.clipboard.writeText(url).then(() => {
      toast.success("URL copied!");
    });
  };

  return (
    <div className="mt-2 flex items-center gap-1.5 max-w-full">
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 text-xs text-[#adc6ff] hover:underline min-w-0"
        title={url}
      >
        <span className="material-symbols-outlined text-xs shrink-0">open_in_new</span>
        <span className="truncate">
          {url.length > 35 ? `${url.slice(0, 35)}...` : url}
        </span>
      </a>
      <button
        type="button"
        onClick={handleCopy}
        className="shrink-0 w-6 h-6 rounded flex items-center justify-center text-[#adc6ff]/60 hover:text-[#adc6ff] hover:bg-[#adc6ff]/10 transition-colors"
        title="Copy URL"
      >
        <span className="material-symbols-outlined text-xs">content_copy</span>
      </button>
    </div>
  );
}

function ApprovalActions() {
  const pendingApproval = useChatStore((s) => s.pendingApproval);
  const confirmCreate = useChatStore((s) => s.confirmCreate);
  const cancelCreate = useChatStore((s) => s.cancelCreate);

  if (!pendingApproval) {
    return (
      <div className="mt-3 text-xs text-[var(--text-muted,#c2c6d8)]/50">
        (응답 완료)
      </div>
    );
  }

  return (
    <div className="mt-3 flex gap-2">
      <button
        type="button"
        onClick={confirmCreate}
        className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#adc6ff]/20 text-[#adc6ff] hover:bg-[#adc6ff]/30 transition-colors text-sm font-medium"
      >
        <span className="material-symbols-outlined text-sm">check_circle</span>
        생성하기
      </button>
      <button
        type="button"
        onClick={cancelCreate}
        className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#ffb4ab]/10 text-[#ffb4ab] hover:bg-[#ffb4ab]/20 transition-colors text-sm font-medium"
      >
        <span className="material-symbols-outlined text-sm">cancel</span>
        취소
      </button>
    </div>
  );
}

function CompletionActions({ notionUrl }: { readonly notionUrl: string }) {
  const clearMessages = useChatStore((s) => s.clearMessages);
  const saveToLibrary = useChatStore((s) => s.saveToLibrary);
  const templates = useChatStore((s) => s.generatedTemplates);
  const alreadySaved = templates.some((t) => t.notionUrl === notionUrl);

  const handleCopy = () => {
    navigator.clipboard.writeText(notionUrl).then(() => {
      toast.success("Notion URL copied!");
    });
  };

  const handleSaveToLibrary = () => {
    const saved = saveToLibrary();
    if (saved) {
      toast.success("Library에 저장됨!");
    } else {
      toast.error("이미 저장된 템플릿입니다");
    }
  };

  return (
    <div className="flex items-center gap-2 mt-3 pt-3 border-t border-[var(--border-color,#424656)]/20 flex-wrap">
      <a
        href={notionUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#4edea3]/20 text-[#4edea3] text-xs font-medium hover:bg-[#4edea3]/30 transition-colors"
      >
        <span className="material-symbols-outlined text-xs">open_in_new</span>
        Open in Notion
      </a>
      <button
        type="button"
        onClick={handleSaveToLibrary}
        disabled={alreadySaved}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
          alreadySaved
            ? "bg-[var(--surface-variant,#353534)] text-[var(--text-muted,#c2c6d8)]/40 cursor-not-allowed"
            : "bg-[#ffb59a]/20 text-[#ffb59a] hover:bg-[#ffb59a]/30"
        }`}
      >
        <span className="material-symbols-outlined text-xs">{alreadySaved ? "check" : "bookmark_add"}</span>
        {alreadySaved ? "Saved" : "Save to Library"}
      </button>
      <button
        type="button"
        onClick={handleCopy}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#adc6ff]/10 text-[#adc6ff] text-xs font-medium hover:bg-[#adc6ff]/20 transition-colors"
      >
        <span className="material-symbols-outlined text-xs">content_copy</span>
        Copy URL
      </button>
      <button
        type="button"
        onClick={clearMessages}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--surface-variant,#353534)] text-[var(--text-muted,#c2c6d8)] text-xs font-medium hover:bg-[var(--border-color,#424656)] transition-colors"
      >
        <span className="material-symbols-outlined text-xs">add</span>
        Create Another
      </button>
    </div>
  );
}

function ModelBadgeInline() {
  const settings = useChatStore((s) => s.settings);
  const aiProvider = useChatStore((s) => s.aiProvider);
  const copilotStatus = useChatStore((s) => s.copilotStatus);

  const provider = copilotStatus?.available ? "copilot" : aiProvider;
  const model = copilotStatus?.available ? copilotStatus.model : (settings.aiModel || "default");

  const providerConfig: Record<string, { emoji: string; color: string }> = {
    copilot: { emoji: "C", color: "text-cyan-400 bg-cyan-400/10" },
    google: { emoji: "G", color: "text-blue-400 bg-blue-400/10" },
    groq: { emoji: "G", color: "text-orange-400 bg-orange-400/10" },
    anthropic: { emoji: "A", color: "text-purple-400 bg-purple-400/10" },
    openai: { emoji: "O", color: "text-green-400 bg-green-400/10" },
  };
  const config = providerConfig[provider] ?? { emoji: "?", color: "text-gray-400 bg-gray-400/10" };

  return (
    <span className={`inline-flex items-center gap-1 text-[11px] ${config.color} px-2 py-0.5 rounded-full ml-auto`}>
      <span className="font-bold text-[10px]">{config.emoji}</span>
      <span className="font-medium truncate max-w-[100px]">{model}</span>
    </span>
  );
}

function ModelBadge({ model, provider, copilotModel }: { readonly model: string; readonly provider: string; readonly copilotModel?: string }) {
  const providerConfig: Record<string, { emoji: string; color: string }> = {
    copilot: { emoji: "C", color: "text-cyan-400 bg-cyan-400/10" },
    google: { emoji: "G", color: "text-blue-400 bg-blue-400/10" },
    groq: { emoji: "G", color: "text-orange-400 bg-orange-400/10" },
    anthropic: { emoji: "A", color: "text-purple-400 bg-purple-400/10" },
    openai: { emoji: "O", color: "text-green-400 bg-green-400/10" },
  };

  // Copilot이 활성이면 Copilot 모델을 우선 표시
  const activeCopilot = !!copilotModel;
  const displayProvider = activeCopilot ? "copilot" : provider;
  const displayModel = activeCopilot ? copilotModel : (model || "(default)");
  const config = providerConfig[displayProvider] ?? { emoji: "?", color: "text-gray-400 bg-gray-400/10" };

  return (
    <span className={`inline-flex items-center gap-1 text-[11px] ${config.color} px-2 py-0.5 rounded-full`}>
      <span className="font-bold text-[10px]">{config.emoji}</span>
      <span className="font-medium">{displayModel}</span>
    </span>
  );
}

export default ChatPanel;
