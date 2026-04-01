import { useState, useRef, useEffect, useCallback } from "react";
import { useChatStore } from "../../stores/chatStore";

const STARTER_PROMPTS = [
  { icon: "🏋️", title: "Workout Tracker", prompt: "운동 기록 일지 만들어줘", color: "orange" },
  { icon: "📊", title: "Project Board", prompt: "프로젝트 관리 대시보드 만들어줘", color: "blue" },
  { icon: "📚", title: "Reading Log", prompt: "독서 기록장 만들어줘", color: "green" },
  { icon: "💰", title: "Budget Manager", prompt: "가계부 만들어줘", color: "yellow" },
  { icon: "📝", title: "Content Calendar", prompt: "콘텐츠 캘린더 만들어줘", color: "purple" },
  { icon: "✈️", title: "Travel Planner", prompt: "여행 계획표 만들어줘", color: "red" },
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

  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (connectionStatus === "disconnected") {
      connect();
    }
  }, [connectionStatus, connect]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback((text?: string) => {
    const trimmed = (text ?? input).trim();
    if (!trimmed || isLoading) return;
    sendMessage(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [input, isLoading, sendMessage]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
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
    <section className="w-1/3 min-w-[320px] flex flex-col bg-[#0e0e0e] rounded-2xl overflow-hidden border border-[#424656]/10">
      {/* Header */}
      <div className="p-6 border-b border-[#424656]/10 flex items-center justify-between">
        <div>
          <h3 className="font-headline font-bold text-lg">Alchemist Chat</h3>
          <div className="flex items-center gap-1.5 mt-0.5">
            <ModelBadge model={settings.aiModel} provider={aiProvider} />
          </div>
        </div>
        <span
          className={`flex h-2 w-2 rounded-full ${
            connectionStatus === "connected"
              ? "bg-[#4edea3] animate-pulse"
              : connectionStatus === "connecting"
                ? "bg-[#adc6ff] animate-pulse"
                : "bg-[#ffb4ab]"
          }`}
        />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {!hasMessages && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <span
              className="material-symbols-outlined text-4xl text-[#adc6ff] mb-4 opacity-40"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              auto_awesome
            </span>
            <p className="text-sm text-[#c2c6d8] opacity-60 mb-1">
              Describe the Notion template you want to create.
            </p>
            <p className="text-xs text-[#c2c6d8]/40 mb-6">
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
                  <span className="text-xs text-[#c2c6d8] font-medium truncate">{s.title}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-col gap-4">
          {messages.map((msg) =>
            msg.role === "user" ? (
              <div key={msg.id} className="flex justify-end animate-fade-in">
                <div className="bg-[#2a2a2a] text-[#e5e2e1] max-w-[85%] rounded-2xl rounded-tr-none px-4 py-3 text-sm break-words overflow-hidden">
                  <p className="whitespace-pre-wrap break-words max-w-full">{msg.content}</p>
                </div>
              </div>
            ) : (
              <div
                key={msg.id}
                className="flex justify-start gap-3 animate-fade-in"
              >
                <div className="w-8 h-8 rounded-lg bg-[#adc6ff]/20 flex items-center justify-center shrink-0">
                  <span
                    className="material-symbols-outlined text-[#adc6ff] text-sm"
                    style={{ fontVariationSettings: "'FILL' 1" }}
                  >
                    auto_awesome
                  </span>
                </div>
                <div className="glass-panel text-[#c2c6d8] max-w-[85%] rounded-2xl rounded-tl-none px-4 py-3 text-sm border-l-2 border-[#adc6ff] break-words overflow-hidden">
                  {msg.metadata?.type === "progress" && (
                    <ProgressIndicator step={msg.metadata.step} />
                  )}
                  {msg.metadata?.type === "error" && (
                    <div className="flex items-center gap-1.5 mb-2 text-[#ffb4ab]">
                      <span className="material-symbols-outlined text-xs">error</span>
                      <span className="text-xs font-medium">Error</span>
                    </div>
                  )}
                  <p className="whitespace-pre-wrap break-words max-w-full">{msg.content}</p>
                  {msg.metadata?.type === "complete" && msg.metadata.notionUrl && (
                    <CompletionActions notionUrl={msg.metadata.notionUrl} />
                  )}
                  {msg.metadata?.notionUrl && msg.metadata?.type !== "complete" && (
                    <a
                      href={msg.metadata.notionUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 inline-flex items-center gap-1 text-xs text-[#adc6ff] hover:underline max-w-full"
                      title={msg.metadata.notionUrl}
                    >
                      <span className="material-symbols-outlined text-xs shrink-0">
                        open_in_new
                      </span>
                      <span className="truncate">
                        {msg.metadata.notionUrl.length > 40
                          ? `${msg.metadata.notionUrl.slice(0, 40)}...`
                          : msg.metadata.notionUrl}
                      </span>
                    </a>
                  )}
                </div>
              </div>
            )
          )}

          {isLoading && (
            <div className="flex justify-start gap-3 animate-fade-in">
              <div className="w-8 h-8 rounded-lg bg-[#adc6ff]/20 flex items-center justify-center shrink-0">
                <span
                  className="material-symbols-outlined text-[#adc6ff] text-sm"
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  auto_awesome
                </span>
              </div>
              <div className="glass-panel text-[#c2c6d8] rounded-2xl rounded-tl-none px-4 py-3 text-sm border-l-2 border-[#adc6ff]">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-[#adc6ff] animate-pulse-dot" />
                  <div className="w-2 h-2 rounded-full bg-[#adc6ff] animate-pulse-dot-delay-1" />
                  <div className="w-2 h-2 rounded-full bg-[#adc6ff] animate-pulse-dot-delay-2" />
                  <span className="ml-2 text-xs italic text-[#c2c6d8]/60">
                    Transmuting...
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-[#1c1b1b] border-t border-[#424656]/10">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            className="w-full bg-[#353534] border-none rounded-xl text-sm text-[#e5e2e1] placeholder:text-[#c2c6d8]/40 focus:ring-1 focus:ring-[#adc6ff] py-3 pl-4 pr-12 resize-none outline-none"
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
    </section>
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

function CompletionActions({ notionUrl }: { readonly notionUrl: string }) {
  const clearMessages = useChatStore((s) => s.clearMessages);

  return (
    <div className="flex items-center gap-2 mt-3 pt-3 border-t border-[#424656]/20">
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
        onClick={clearMessages}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#353534] text-[#c2c6d8] text-xs font-medium hover:bg-[#424656] transition-colors"
      >
        <span className="material-symbols-outlined text-xs">add</span>
        Create Another
      </button>
    </div>
  );
}

function ModelBadge({ model, provider }: { readonly model: string; readonly provider: string }) {
  const providerConfig: Record<string, { emoji: string; color: string }> = {
    google: { emoji: "G", color: "text-blue-400 bg-blue-400/10" },
    groq: { emoji: "G", color: "text-orange-400 bg-orange-400/10" },
    anthropic: { emoji: "A", color: "text-purple-400 bg-purple-400/10" },
    openai: { emoji: "O", color: "text-green-400 bg-green-400/10" },
  };

  const displayModel = model || "(default)";
  const config = providerConfig[provider] ?? { emoji: "?", color: "text-gray-400 bg-gray-400/10" };

  return (
    <span className={`inline-flex items-center gap-1 text-[11px] ${config.color} px-2 py-0.5 rounded-full`}>
      <span className="font-bold text-[10px]">{config.emoji}</span>
      <span className="font-medium">{displayModel}</span>
    </span>
  );
}

export default ChatPanel;
