interface Props {
  step: string;
}

const STEPS = [
  { key: "sending", label: "요청 전송 중" },
  { key: "intent_analysis", label: "요청 분석 중" },
  { key: "blueprint", label: "구조 설계 중" },
  { key: "generating", label: "노션에 생성 중" },
];

export default function ProgressBar({ step }: Props) {
  const currentIndex = STEPS.findIndex((s) => s.key === step);
  const activeIndex = currentIndex >= 0 ? currentIndex : 0;

  return (
    <div className="flex gap-3 rounded-xl bg-zinc-700/50 px-4 py-4">
      {/* Avatar */}
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-600/20">
        <span className="text-sm">⚙️</span>
      </div>

      <div className="min-w-0 flex-1">
        {/* Dots animation */}
        <div className="mb-3 flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse-dot" />
          <div className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse-dot-delay-1" />
          <div className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse-dot-delay-2" />
        </div>

        {/* Step indicators */}
        <div className="flex items-center gap-1">
          {STEPS.map((s, i) => {
            const isActive = i === activeIndex;
            const isDone = i < activeIndex;

            return (
              <div key={s.key} className="flex items-center gap-1">
                {i > 0 && (
                  <div
                    className={`h-px w-4 ${
                      isDone ? "bg-indigo-500" : "bg-zinc-600"
                    }`}
                  />
                )}
                <div className="flex items-center gap-1.5">
                  <div
                    className={`h-2 w-2 rounded-full transition-all ${
                      isActive
                        ? "bg-indigo-400 ring-2 ring-indigo-400/30"
                        : isDone
                          ? "bg-indigo-500"
                          : "bg-zinc-600"
                    }`}
                  />
                  <span
                    className={`text-xs transition-colors ${
                      isActive
                        ? "font-medium text-indigo-300"
                        : isDone
                          ? "text-zinc-400"
                          : "text-zinc-600"
                    }`}
                  >
                    {s.label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
