import { useConnectionStore } from "../../stores/connectionStore";

interface StatusBarProps {
  readonly sidebarWidth: number;
}

function StatusBar({ sidebarWidth }: StatusBarProps) {
  const connectionStatus = useConnectionStore((s) => s.connectionStatus);

  const statusColor =
    connectionStatus === "connected"
      ? "text-[#4edea3]"
      : connectionStatus === "connecting"
        ? "text-[#adc6ff]"
        : "text-[#ffb4ab]";

  const statusText =
    connectionStatus === "connected"
      ? "AI Status: Ready to Build"
      : connectionStatus === "connecting"
        ? "AI Status: Connecting..."
        : "AI Status: Offline";

  return (
    <footer
      className="fixed bottom-0 right-0 z-50 flex items-center px-6 justify-start bg-[var(--surface-low,#1c1b1b)]/80 backdrop-blur-xl h-10 border-t border-[var(--border-color,#424656)]/15 transition-all duration-200 ease-out"
      style={{ left: sidebarWidth }}
    >
      <div className={`flex items-center justify-center gap-2 ${statusColor}`}>
        <span className="material-symbols-outlined text-sm">smart_toy</span>
        <span className="font-mono text-xs uppercase tracking-widest">
          {statusText}
        </span>
      </div>
      <div className="ml-auto flex gap-6">
        <span className="text-[var(--text-primary,#e5e2e1)]/40 font-mono text-[10px] uppercase tracking-tighter hidden sm:inline">
          GPU-Cluster: Beta-09
        </span>
        <span className="text-[var(--text-primary,#e5e2e1)]/40 font-mono text-[10px] uppercase tracking-tighter hidden sm:inline">
          Latency: 24ms
        </span>
      </div>
    </footer>
  );
}

export default StatusBar;
