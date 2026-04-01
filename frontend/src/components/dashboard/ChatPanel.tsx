import { useState, useRef, useEffect, useCallback } from "react";
import { useChatStore } from "../../stores/chatStore";

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

  const handleSend = useCallback(() => {
    const trimmed = input.trim();
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
          <div className="flex flex-col items-center justify-center h-full text-center opacity-40">
            <span
              className="material-symbols-outlined text-4xl text-[#adc6ff] mb-4"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              auto_awesome
            </span>
            <p className="text-sm text-[#c2c6d8]">
              Describe the Notion template you want to create.
            </p>
            <p className="text-xs text-[#c2c6d8]/60 mt-1">
              e.g. &quot;Create a project dashboard with orange theme&quot;
            </p>
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
                    <p className="mb-2 italic text-[#c2c6d8]/70">
                      Transmuting request into structure...
                    </p>
                  )}
                  <p className="whitespace-pre-wrap break-words max-w-full">{msg.content}</p>
                  {msg.metadata?.notionUrl && (
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
            placeholder="어떤 노션 템플릿을 만들어드릴까요? 예: 운동 기록 일지 만들어줘"
            rows={2}
          />
          <button
            type="button"
            onClick={handleSend}
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

function ModelBadge({ model, provider }: { model: string; provider: string }) {
  const providerConfig: Record<string, { emoji: string; color: string; label: string }> = {
    google: { emoji: "🔵", color: "text-blue-400", label: "Gemini" },
    groq: { emoji: "🟠", color: "text-orange-400", label: "Groq" },
    anthropic: { emoji: "🟣", color: "text-purple-400", label: "Claude" },
    openai: { emoji: "🟢", color: "text-green-400", label: "OpenAI" },
  };

  const displayModel = model || "(기본 모델)";
  const config = providerConfig[provider] || { emoji: "⚪", color: "text-gray-400", label: "Mock" };

  return (
    <span className={`inline-flex items-center gap-1 text-[11px] ${config.color} bg-[#353534]/60 px-2 py-0.5 rounded-full`}>
      <span>{config.emoji}</span>
      <span className="font-medium">{displayModel}</span>
    </span>
  );
}

export default ChatPanel;
