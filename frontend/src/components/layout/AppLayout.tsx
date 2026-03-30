import { type ReactNode, useCallback, useState, useRef, useEffect } from "react";
import { useChatStore, type PageName } from "../../stores/chatStore";
import StatusBar from "../common/StatusBar";

interface SideNavItem {
  readonly id: PageName | "new-template";
  readonly icon: string;
  readonly label: string;
  readonly filled?: boolean;
}

const NAV_ITEMS: readonly SideNavItem[] = [
  { id: "new-template", icon: "auto_awesome", label: "New Template" },
  { id: "library", icon: "grid_view", label: "Library" },
  { id: "integrations", icon: "api", label: "Integrations" },
  { id: "profile", icon: "person", label: "Profile" },
];

const TOP_NAV: readonly { id: PageName; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "library", label: "Library" },
  { id: "integrations", label: "Integrations" },
];

function HeaderActions({ setPage }: { readonly setPage: (page: PageName) => void }) {
  const [showNotifDropdown, setShowNotifDropdown] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setShowNotifDropdown(false);
      }
    }
    if (showNotifDropdown) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showNotifDropdown]);

  return (
    <div className="flex items-center gap-4">
      {/* Notifications */}
      <div className="relative" ref={notifRef}>
        <button
          type="button"
          onClick={() => setShowNotifDropdown((prev) => !prev)}
          className="text-[#e5e2e1]/60 hover:text-[#adc6ff] transition-colors"
        >
          <span className="material-symbols-outlined">notifications</span>
        </button>
        {showNotifDropdown && (
          <div className="absolute right-0 top-full mt-2 w-64 bg-[#1e1e1e] border border-[#333] rounded-xl shadow-2xl p-4 z-50">
            <p className="text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">
              Notifications
            </p>
            <div className="flex flex-col items-center justify-center py-6">
              <span className="material-symbols-outlined text-2xl text-gray-500 mb-2">
                notifications_off
              </span>
              <p className="text-sm text-gray-500">알림이 없습니다</p>
            </div>
          </div>
        )}
      </div>
      {/* Settings */}
      <button
        type="button"
        onClick={() => setPage("integrations")}
        className="text-[#e5e2e1]/60 hover:text-[#adc6ff] transition-colors"
      >
        <span className="material-symbols-outlined">settings</span>
      </button>
      {/* Profile */}
      <button
        type="button"
        onClick={() => setPage("profile")}
        className="w-8 h-8 rounded-full overflow-hidden border border-[#424656]/30 bg-[#353534] flex items-center justify-center hover:border-[#adc6ff]/50 transition-colors"
      >
        <span className="material-symbols-outlined text-[#c2c6d8] text-sm">
          person
        </span>
      </button>
    </div>
  );
}

interface AppLayoutProps {
  readonly children: ReactNode;
}

function AppLayout({ children }: AppLayoutProps) {
  const currentPage = useChatStore((s) => s.currentPage);
  const setPage = useChatStore((s) => s.setPage);
  const clearMessages = useChatStore((s) => s.clearMessages);

  const handleSideNav = useCallback(
    (id: SideNavItem["id"]) => {
      if (id === "new-template") {
        clearMessages();
        setPage("dashboard");
        return;
      }
      setPage(id);
    },
    [setPage, clearMessages]
  );

  const getActiveClass = useCallback(
    (id: SideNavItem["id"]) => {
      if (id === "new-template" && currentPage === "dashboard") {
        return "flex items-center gap-3 bg-[#1c1b1b] text-[#adc6ff] rounded-lg px-4 py-3 transition-all duration-200 translate-x-1";
      }
      if (id === currentPage) {
        return "flex items-center gap-3 bg-[#1c1b1b] text-[#adc6ff] rounded-lg px-4 py-3 transition-all duration-200 translate-x-1";
      }
      return "flex items-center gap-3 text-[#e5e2e1]/50 px-4 py-3 hover:bg-[#1c1b1b] hover:text-[#e5e2e1] transition-all rounded-lg cursor-pointer";
    },
    [currentPage]
  );

  const isItemFilled = useCallback(
    (id: SideNavItem["id"]) => {
      if (id === "new-template" && currentPage === "dashboard") return true;
      return id === currentPage;
    },
    [currentPage]
  );

  return (
    <div className="min-h-screen bg-[#131313] text-[#e5e2e1] font-body selection:bg-[#adc6ff] selection:text-[#002e69]">
      {/* TopNavBar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 h-16 bg-[#131313] shadow-[0_0_48px_0_rgba(173,198,255,0.06)]">
        <div className="flex items-center gap-8">
          <span className="text-xl font-bold tracking-tighter text-[#e5e2e1] font-headline">
            NotionForge
          </span>
          <nav className="hidden md:flex gap-6 items-center">
            {TOP_NAV.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setPage(item.id)}
                className={
                  currentPage === item.id
                    ? "text-[#adc6ff] border-b-2 border-[#adc6ff] pb-1 font-label text-sm uppercase tracking-widest"
                    : "text-[#e5e2e1]/60 hover:text-[#adc6ff] transition-colors duration-200 font-label text-sm uppercase tracking-widest"
                }
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
        <HeaderActions setPage={setPage} />
      </header>

      {/* SideNavBar */}
      <aside className="fixed left-0 top-0 h-full flex flex-col py-8 z-40 bg-[#0e0e0e] w-64 pt-20">
        <div className="px-6 mb-8">
          <button
            type="button"
            onClick={() => setPage("dashboard")}
            className="flex items-center gap-3 w-full text-left hover:opacity-80 transition-opacity"
          >
            <div className="w-10 h-10 bg-[#006de6] rounded-xl flex items-center justify-center">
              <span
                className="material-symbols-outlined text-white"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                auto_awesome
              </span>
            </div>
            <div>
              <h2 className="text-lg font-black text-[#adc6ff] font-headline leading-tight">
                NotionForge
              </h2>
              <p className="text-[10px] uppercase tracking-[0.2em] text-[#c2c6d8]/50">
                AI Alchemist
              </p>
            </div>
          </button>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => handleSideNav(item.id)}
              className={getActiveClass(item.id)}
            >
              <span
                className="material-symbols-outlined"
                style={
                  isItemFilled(item.id)
                    ? { fontVariationSettings: "'FILL' 1" }
                    : undefined
                }
              >
                {item.icon}
              </span>
              <span className="font-label text-sm uppercase tracking-wider">
                {item.label}
              </span>
            </button>
          ))}
        </nav>

        <div className="px-4 mt-auto space-y-4">
          <div className="bg-[#2a2a2a] rounded-xl p-4 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-[#ffb59a]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <p className="text-xs text-[#ffb59a] font-bold mb-1">PRO PLAN</p>
            <p className="text-[10px] text-[#c2c6d8] mb-3">
              Unlock unlimited AI alchemy.
            </p>
            <button
              type="button"
              className="w-full py-2 bg-[#ffb59a] text-[#5a1b00] font-bold text-xs rounded-lg transition-transform active:scale-95"
            >
              Upgrade to Pro
            </button>
          </div>
          <div className="space-y-1">
            <button
              type="button"
              onClick={() => setPage("support")}
              className="flex items-center gap-3 text-[#e5e2e1]/30 px-4 py-2 hover:text-[#e5e2e1] transition-all text-xs w-full"
            >
              <span className="material-symbols-outlined scale-75">help</span>
              <span>Support</span>
            </button>
            <button
              type="button"
              onClick={() => setPage("support")}
              className="flex items-center gap-3 text-[#e5e2e1]/30 px-4 py-2 hover:text-[#e5e2e1] transition-all text-xs w-full"
            >
              <span className="material-symbols-outlined scale-75">
                description
              </span>
              <span>Documentation</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="pl-64 pt-16 h-screen flex flex-col">
        {children}
      </main>

      {/* StatusBar */}
      <StatusBar />
    </div>
  );
}

export default AppLayout;
