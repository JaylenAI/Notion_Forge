import type { Message } from "../../types";

interface Props {
  message: Message;
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const metaType = message.metadata?.type;

  if (isUser) {
    return (
      <div className="mb-5 flex justify-end animate-fade-in">
        <div className="max-w-[75%] rounded-2xl rounded-br-md bg-indigo-600 px-4 py-3">
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-white">
            {message.content}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-5 animate-fade-in">
      <div className="flex gap-3">
        {/* Avatar */}
        <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-600/20">
          <BotIcon type={metaType} />
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          {/* Type badge */}
          {metaType && metaType !== "system" && (
            <TypeBadge type={metaType} />
          )}

          {/* Message body */}
          <div className={getBodyClass(metaType)}>
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {message.content}
            </div>

            {/* Notion URL */}
            {message.metadata?.notionUrl && (
              <a
                href={message.metadata.notionUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-indigo-600/20 px-3 py-2 text-xs font-medium text-indigo-300 transition hover:bg-indigo-600/30"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
                Notion에서 열기
              </a>
            )}

            {/* Blueprint preview */}
            {message.metadata?.blueprint && (
              <details className="mt-3">
                <summary className="cursor-pointer text-xs text-zinc-500 hover:text-zinc-300 transition">
                  Blueprint JSON 보기
                </summary>
                <pre className="mt-2 max-h-48 overflow-auto rounded-lg bg-zinc-900 p-3 text-xs text-zinc-400 leading-relaxed">
                  {JSON.stringify(message.metadata.blueprint, null, 2)}
                </pre>
              </details>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function BotIcon({ type }: { type?: string }) {
  const icon =
    type === "progress"
      ? "⚙️"
      : type === "complete"
        ? "✅"
        : type === "error"
          ? "❌"
          : type === "blueprint_preview"
            ? "📋"
            : type === "question"
              ? "❓"
              : "⚡";
  return <span className="text-sm">{icon}</span>;
}

function TypeBadge({ type }: { type: string }) {
  const config: Record<string, { label: string; color: string }> = {
    progress: { label: "처리 중", color: "text-blue-400" },
    blueprint_preview: { label: "구조 미리보기", color: "text-purple-400" },
    complete: { label: "완료", color: "text-emerald-400" },
    question: { label: "추가 정보 필요", color: "text-amber-400" },
    error: { label: "오류", color: "text-red-400" },
    system: { label: "시스템", color: "text-zinc-400" },
  };

  const c = config[type] ?? { label: type, color: "text-zinc-400" };

  return (
    <span className={`mb-1 inline-block text-xs font-medium ${c.color}`}>
      {c.label}
    </span>
  );
}

function getBodyClass(type?: string): string {
  const base = "rounded-2xl rounded-tl-md px-4 py-3 ";
  switch (type) {
    case "error":
      return base + "bg-red-900/20 border border-red-800/30 text-red-200";
    case "complete":
      return base + "bg-emerald-900/20 border border-emerald-800/30 text-emerald-200";
    case "blueprint_preview":
      return base + "bg-purple-900/20 border border-purple-800/30 text-purple-200";
    case "progress":
      return base + "bg-zinc-700/50 text-zinc-300";
    case "question":
      return base + "bg-amber-900/20 border border-amber-800/30 text-amber-200";
    default:
      return base + "bg-zinc-700/50 text-zinc-200";
  }
}
