import { useState, useEffect, useCallback, useRef } from "react";
import ChatPanel from "./ChatPanel";
import LivePreview from "./LivePreview";

function DashboardPage() {
  const [isMobile, setIsMobile] = useState(false);
  const [mobileTab, setMobileTab] = useState<"chat" | "preview">("chat");

  /* Chat panel width as percentage (35% default) */
  const [chatWidth, setChatWidth] = useState(35);
  const containerRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  useEffect(() => {
    function handleResize() {
      setIsMobile(window.innerWidth < 768);
    }
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  useEffect(() => {
    function handleMouseMove(e: MouseEvent) {
      if (!dragging.current || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const pct = (x / rect.width) * 100;
      setChatWidth(Math.min(55, Math.max(25, pct)));
    }

    function handleMouseUp() {
      if (dragging.current) {
        dragging.current = false;
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      }
    }

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  if (isMobile) {
    return (
      <div className="flex-1 overflow-hidden flex flex-col pb-12">
        <div className="flex border-b border-[var(--border-color,#424656)]/20 bg-[var(--bg,#131313)]">
          <button
            type="button"
            onClick={() => setMobileTab("chat")}
            className={`flex-1 py-3 text-xs font-label uppercase tracking-wider text-center transition-colors ${
              mobileTab === "chat"
                ? "text-[#adc6ff] border-b-2 border-[#adc6ff]"
                : "text-[var(--text-muted,#c2c6d8)]/50"
            }`}
          >
            <span className="material-symbols-outlined text-sm align-middle mr-1">chat</span>
            Chat
          </button>
          <button
            type="button"
            onClick={() => setMobileTab("preview")}
            className={`flex-1 py-3 text-xs font-label uppercase tracking-wider text-center transition-colors ${
              mobileTab === "preview"
                ? "text-[#adc6ff] border-b-2 border-[#adc6ff]"
                : "text-[var(--text-muted,#c2c6d8)]/50"
            }`}
          >
            <span className="material-symbols-outlined text-sm align-middle mr-1">preview</span>
            Preview
          </button>
        </div>
        <div className="flex-1 overflow-hidden p-2">
          {mobileTab === "chat" ? <ChatPanel /> : <LivePreview />}
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="flex-1 overflow-hidden p-4 pb-12 flex gap-0">
      {/* Chat Panel */}
      <div style={{ width: `${chatWidth}%` }} className="shrink-0 h-full overflow-hidden">
        <ChatPanel />
      </div>

      {/* Resize Handle */}
      <div
        onMouseDown={handleMouseDown}
        className="group relative w-2 shrink-0 flex items-center justify-center cursor-col-resize hover:bg-[#adc6ff]/5 transition-colors"
      >
        <div className="w-[3px] h-10 rounded-full bg-[#333] group-hover:bg-[#adc6ff]/50 transition-colors" />
      </div>

      {/* Preview Panel — flex container so LivePreview's flex-1 works */}
      <div className="flex-1 h-full min-w-0 flex flex-col overflow-hidden">
        <LivePreview />
      </div>
    </div>
  );
}

export default DashboardPage;
