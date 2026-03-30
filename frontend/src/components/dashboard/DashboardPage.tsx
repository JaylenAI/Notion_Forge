import ChatPanel from "./ChatPanel";
import LivePreview from "./LivePreview";

function DashboardPage() {
  return (
    <div className="flex flex-1 overflow-hidden p-6 gap-6 pb-16">
      <ChatPanel />
      <LivePreview />
    </div>
  );
}

export default DashboardPage;
