import { useChatStore } from "../../stores/chatStore";

function StatusBar() {
  const connectionStatus = useChatStore((s) => s.connectionStatus);

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
    <footer className="fixed bottom-0 left-0 w-full z-50 flex items-center px-6 justify-start bg-[#1c1b1b]/80 backdrop-blur-xl h-10 border-t border-[#424656]/15">
      <div className={`flex items-center justify-center gap-2 ${statusColor}`}>
        <span className="material-symbols-outlined text-sm">smart_toy</span>
        <span className="font-mono text-xs uppercase tracking-widest">
          {statusText}
        </span>
      </div>
      <div className="ml-auto flex gap-6">
        <span className="text-[#e5e2e1]/40 font-mono text-[10px] uppercase tracking-tighter">
          GPU-Cluster: Beta-09
        </span>
        <span className="text-[#e5e2e1]/40 font-mono text-[10px] uppercase tracking-tighter">
          Latency: 24ms
        </span>
      </div>
    </footer>
  );
}

export default StatusBar;
