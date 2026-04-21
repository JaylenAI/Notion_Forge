import { type ReactNode, useCallback, useState, useRef, useEffect } from "react";
import toast from "react-hot-toast";
import { useChatStore } from "../../stores/chatStore";
import { useSettingsStore, type PageName } from "../../stores/settingsStore";
import { useThemeStore } from "../../stores/themeStore";
import StatusBar from "../common/StatusBar";

interface SideNavItem {
  readonly id: PageName | "new-template";
  readonly icon: string;
  readonly label: string;
}

const NAV_ITEMS: readonly SideNavItem[] = [
  { id: "new-template", icon: "auto_awesome", label: "New Template" },
  { id: "library", icon: "grid_view", label: "Library" },
  { id: "integrations", icon: "api", label: "Integrations" },
  { id: "profile", icon: "person", label: "Profile" },
  { id: "support", icon: "help", label: "Support" },
];

const TOP_NAV: readonly { id: PageName; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "library", label: "Library" },
  { id: "integrations", label: "Integrations" },
];

function HeaderActions({ setPage }: { readonly setPage: (page: PageName) => void }) {
  const [showNotifDropdown, setShowNotifDropdown] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const theme = useThemeStore((s) => s.theme);
  const toggleTheme = useThemeStore((s) => s.toggleTheme);

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
    <div className="flex items-center gap-2 sm:gap-4">
      {/* Theme toggle */}
      <button
        type="button"
        onClick={toggleTheme}
        className="text-[var(--text-primary,#e5e2e1)]/60 hover:text-[#adc6ff] transition-colors"
        title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
      >
        <span className="material-symbols-outlined">
          {theme === "dark" ? "light_mode" : "dark_mode"}
        </span>
      </button>

      <div className="relative" ref={notifRef}>
        <button
          type="button"
          onClick={() => setShowNotifDropdown((prev) => !prev)}
          className="text-[var(--text-primary,#e5e2e1)]/60 hover:text-[#adc6ff] transition-colors"
        >
          <span className="material-symbols-outlined">notifications</span>
        </button>
        {showNotifDropdown && (
          <div className="absolute right-0 top-full mt-2 w-64 bg-[var(--surface-container-low,#1e1e1e)] border border-[var(--border-color,#333)] rounded-xl shadow-2xl p-4 z-50">
            <p className="text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">
              Notifications
            </p>
            <div className="flex flex-col items-center justify-center py-6">
              <span className="material-symbols-outlined text-2xl text-gray-500 mb-2">
                notifications_off
              </span>
              <p className="text-sm text-gray-500">No notifications</p>
            </div>
          </div>
        )}
      </div>
      <button
        type="button"
        onClick={() => setPage("integrations")}
        className="text-[var(--text-primary,#e5e2e1)]/60 hover:text-[#adc6ff] transition-colors hidden sm:block"
      >
        <span className="material-symbols-outlined">settings</span>
      </button>
      <button
        type="button"
        onClick={() => setPage("profile")}
        className="w-8 h-8 rounded-full overflow-hidden border border-[var(--border-color,#424656)]/30 bg-[var(--surface-variant,#353534)] flex items-center justify-center hover:border-[#adc6ff]/50 transition-colors"
      >
        <span className="material-symbols-outlined text-[var(--text-muted,#c2c6d8)] text-sm">
          person
        </span>
      </button>
    </div>
  );
}

/* ─── Command Palette (Cmd+K) ─── */
function CommandPalette({ open, onClose }: { readonly open: boolean; readonly onClose: () => void }) {
  const setPage = useSettingsStore((s) => s.setPage);
  const newSession = useChatStore((s) => s.newSession);
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setQuery("");
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  const commands = [
    { icon: "auto_awesome", label: "New Template", shortcut: "\u2318N", action: () => { newSession(); setPage("dashboard"); } },
    { icon: "grid_view", label: "Library", action: () => setPage("library") },
    { icon: "api", label: "Integrations", action: () => setPage("integrations") },
    { icon: "person", label: "Profile", action: () => setPage("profile") },
    { icon: "help", label: "Support", action: () => setPage("support") },
    { icon: "dashboard", label: "Dashboard", action: () => setPage("dashboard") },
  ];

  const filtered = query
    ? commands.filter((c) => c.label.toLowerCase().includes(query.toLowerCase()))
    : commands;

  const handleSelect = (action: () => void) => {
    action();
    onClose();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[20vh]" onClick={onClose}>
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-md bg-[var(--surface-container,#201f1f)] border border-[var(--border-color,#424656)] rounded-2xl shadow-2xl overflow-hidden animate-fade-in"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border-color,#424656)]/30">
          <span className="material-symbols-outlined text-[var(--text-muted,#c2c6d8)]/40 text-lg">search</span>
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent text-sm text-[var(--text-primary,#e5e2e1)] placeholder:text-[var(--text-muted,#c2c6d8)]/40 outline-none"
            placeholder="Search commands..."
            onKeyDown={(e) => {
              if (e.key === "Escape") onClose();
              if (e.key === "Enter" && filtered.length > 0 && filtered[0]) handleSelect(filtered[0].action);
            }}
          />
          <kbd className="text-[10px] text-[var(--text-muted,#c2c6d8)]/30 border border-[var(--border-color,#424656)]/30 rounded px-1.5 py-0.5">ESC</kbd>
        </div>
        <div className="py-2 max-h-64 overflow-y-auto">
          {filtered.map((cmd) => (
            <button
              key={cmd.label}
              type="button"
              onClick={() => handleSelect(cmd.action)}
              className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-[var(--surface-container-high,#2a2a2a)] transition-colors text-left"
            >
              <span className="material-symbols-outlined text-[var(--text-muted,#c2c6d8)]/60 text-lg">{cmd.icon}</span>
              <span className="text-sm text-[var(--text-primary,#e5e2e1)]">{cmd.label}</span>
              {cmd.shortcut && (
                <kbd className="ml-auto text-[10px] text-[var(--text-muted,#c2c6d8)]/30 border border-[var(--border-color,#424656)]/30 rounded px-1.5 py-0.5">
                  {cmd.shortcut}
                </kbd>
              )}
            </button>
          ))}
          {filtered.length === 0 && (
            <p className="px-4 py-6 text-sm text-[var(--text-muted,#c2c6d8)]/40 text-center">No results</p>
          )}
        </div>
      </div>
    </div>
  );
}

interface AppLayoutProps {
  readonly children: ReactNode;
}

function AppLayout({ children }: AppLayoutProps) {
  const currentPage = useSettingsStore((s) => s.currentPage);
  const setPage = useSettingsStore((s) => s.setPage);
  const clearMessages = useChatStore((s) => s.clearMessages);
  const newSession = useChatStore((s) => s.newSession);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(typeof window !== "undefined" && window.innerWidth < 768);

  /* ─── Keyboard Shortcuts ─── */
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const meta = e.metaKey || e.ctrlKey;

      // Cmd+K — Command palette
      if (meta && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen((prev) => !prev);
      }
      // Cmd+N — New template
      if (meta && e.key === "n") {
        e.preventDefault();
        newSession();
        setPage("dashboard");
        toast.success("New template session started");
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [newSession, setPage]);

  /* Track screen size + auto-collapse sidebar on small screens */
  useEffect(() => {
    function handleResize() {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarCollapsed(true);
      }
    }
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleSideNav = useCallback(
    (id: SideNavItem["id"]) => {
      if (id === "new-template") {
        clearMessages();
        setPage("dashboard");
        setMobileMenuOpen(false);
        return;
      }
      setPage(id);
      setMobileMenuOpen(false);
    },
    [setPage, clearMessages]
  );

  const isActive = useCallback(
    (id: SideNavItem["id"]) => {
      if (id === "new-template" && currentPage === "dashboard") return true;
      return id === currentPage;
    },
    [currentPage]
  );

  /* Determine if we're showing expanded labels in sidebar */
  const showLabels = mobileMenuOpen || !sidebarCollapsed;

  /* Compute sidebar pixel width for main content offset */
  const sidebarPx = sidebarCollapsed ? 68 : 256;

  return (
    <div className="min-h-screen bg-[var(--bg,#131313)] text-[var(--text-primary,#e5e2e1)] font-body selection:bg-[#adc6ff] selection:text-[#002e69]">
      {/* TopNavBar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-4 sm:px-6 h-14 bg-[var(--bg,#131313)]/95 backdrop-blur-sm border-b border-[var(--border-color,#333)]/20">
        <div className="flex items-center gap-3 sm:gap-6">
          <button
            type="button"
            onClick={() => {
              if (isMobile) {
                setMobileMenuOpen((p) => !p);
              } else {
                setSidebarCollapsed((prev) => !prev);
              }
            }}
            className="text-[var(--text-primary,#e5e2e1)]/50 hover:text-[#adc6ff] transition-colors"
          >
            <span className="material-symbols-outlined text-xl">
              {mobileMenuOpen ? "close" : sidebarCollapsed ? "menu" : "menu_open"}
            </span>
          </button>
          <span className="text-lg font-bold tracking-tighter text-[var(--text-primary,#e5e2e1)] font-headline">
            NotionForge
          </span>
          <nav className="hidden md:flex gap-5 items-center">
            {TOP_NAV.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setPage(item.id)}
                className={
                  currentPage === item.id
                    ? "text-[#adc6ff] border-b-2 border-[#adc6ff] pb-0.5 font-label text-xs uppercase tracking-widest"
                    : "text-[var(--text-primary,#e5e2e1)]/50 hover:text-[#adc6ff] transition-colors duration-200 font-label text-xs uppercase tracking-widest"
                }
              >
                {item.label}
              </button>
            ))}
          </nav>
          {/* Keyboard shortcut hint */}
          <button
            type="button"
            onClick={() => setCommandPaletteOpen(true)}
            className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--surface-container,#201f1f)] border border-[var(--border-color,#424656)]/20 text-[var(--text-muted,#c2c6d8)]/30 hover:text-[var(--text-muted,#c2c6d8)]/60 hover:border-[var(--border-color,#424656)]/40 transition-colors"
          >
            <span className="material-symbols-outlined text-sm">search</span>
            <span className="text-xs">Search</span>
            <kbd className="text-[10px] border border-[var(--border-color,#424656)]/20 rounded px-1 py-0.5 ml-2">{"\u2318K"}</kbd>
          </button>
        </div>
        <HeaderActions setPage={setPage} />
      </header>

      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* SideNavBar — always flex, translate to show/hide on mobile */}
      <aside
        className="fixed left-0 top-0 h-full flex flex-col z-40 bg-[var(--sidebar-bg,#0e0e0e)] pt-14 transition-all duration-200 ease-out"
        style={{
          width: mobileMenuOpen ? 256 : sidebarPx,
          transform: isMobile && !mobileMenuOpen ? "translateX(-100%)" : "translateX(0)",
        }}
      >
        {/* Logo */}
        <div className={`${showLabels ? "px-5" : "px-3"} py-5`}>
          <button
            type="button"
            onClick={() => { setPage("dashboard"); setMobileMenuOpen(false); }}
            className="flex items-center gap-3 w-full text-left hover:opacity-80 transition-opacity"
          >
            <div className="w-9 h-9 bg-[#006de6] rounded-xl flex items-center justify-center shrink-0">
              <span
                className="material-symbols-outlined text-white text-lg"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                auto_awesome
              </span>
            </div>
            {showLabels && (
              <div className="overflow-hidden">
                <h2 className="text-base font-black text-[#adc6ff] font-headline leading-tight">
                  NotionForge
                </h2>
                <p className="text-[9px] uppercase tracking-[0.15em] text-[var(--text-muted,#c2c6d8)]/40">
                  AI Alchemist
                </p>
              </div>
            )}
          </button>
        </div>

        {/* Nav — flex-1 pushes footer down */}
        <nav className={`flex-1 ${showLabels ? "px-3" : "px-2"} space-y-1`}>
          {NAV_ITEMS.map((item) => {
            const active = isActive(item.id);
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleSideNav(item.id)}
                title={!showLabels ? item.label : undefined}
                className={`flex items-center gap-3 w-full rounded-lg transition-all duration-150 ${
                  !showLabels ? "justify-center px-2 py-2.5" : "px-3 py-2.5"
                } ${
                  active
                    ? "bg-[var(--surface-container-low,#1c1b1b)] text-[#adc6ff]"
                    : "text-[var(--text-primary,#e5e2e1)]/40 hover:bg-[var(--surface-container-low,#1c1b1b)] hover:text-[var(--text-primary,#e5e2e1)]"
                }`}
              >
                <span
                  className="material-symbols-outlined text-xl"
                  style={active ? { fontVariationSettings: "'FILL' 1" } : undefined}
                >
                  {item.icon}
                </span>
                {showLabels && (
                  <span className="font-label text-xs uppercase tracking-wider truncate">
                    {item.label}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom spacer for StatusBar */}
        <div className="pb-14" />
      </aside>

      {/* Main Content — offset by sidebar width on desktop */}
      <main
        className="pt-14 h-screen flex flex-col transition-all duration-200 ease-out"
        style={{ paddingLeft: isMobile ? 0 : sidebarPx }}
      >
        {children}
      </main>

      {/* StatusBar — offset by sidebar width so it doesn't hide behind sidebar */}
      <StatusBar sidebarWidth={isMobile ? 0 : sidebarPx} />

      {/* Command Palette */}
      <CommandPalette open={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />
    </div>
  );
}

export default AppLayout;
