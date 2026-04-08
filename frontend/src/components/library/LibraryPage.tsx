import { useState, useMemo, useCallback, lazy, Suspense } from "react";
import { useChatStore } from "../../stores/chatStore";

const RecipeGallery = lazy(() => import("./RecipeGallery"));

const SKILL_LABELS: Record<string, { label: string; color: string }> = {
  track: { label: "Track", color: "bg-orange-900/50 text-orange-300" },
  collect: { label: "Collect", color: "bg-green-900/50 text-green-300" },
  manage: { label: "Manage", color: "bg-blue-900/50 text-blue-300" },
  plan: { label: "Plan", color: "bg-purple-900/50 text-purple-300" },
  organize: { label: "Organize", color: "bg-yellow-900/50 text-yellow-300" },
  guide: { label: "Guide", color: "bg-pink-900/50 text-pink-300" },
  hub: { label: "Hub", color: "bg-red-900/50 text-red-300" },
  finance: { label: "Finance", color: "bg-emerald-900/50 text-emerald-300" },
  journal: { label: "Journal", color: "bg-indigo-900/50 text-indigo-300" },
  content: { label: "Content", color: "bg-cyan-900/50 text-cyan-300" },
  learn: { label: "Learn", color: "bg-amber-900/50 text-amber-300" },
  crm: { label: "CRM", color: "bg-rose-900/50 text-rose-300" },
  custom: { label: "Custom", color: "bg-gray-700/50 text-gray-300" },
};

type SortMode = "newest" | "oldest" | "name" | "starred";

function LibraryPage() {
  const templates = useChatStore((s) => s.generatedTemplates);
  const toggleStar = useChatStore((s) => s.toggleTemplateStar);
  const deleteTemplate = useChatStore((s) => s.deleteTemplate);
  const setPage = useChatStore((s) => s.setPage);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterSkill, setFilterSkill] = useState<string>("all");
  const [sortMode, setSortMode] = useState<SortMode>("newest");
  const [showSortMenu, setShowSortMenu] = useState(false);
  const [activeTab, setActiveTab] = useState<"my" | "recipes">("my");

  const availableSkills = useMemo(() => {
    const skills = new Set(templates.map((t) => t.skill));
    return [...skills].sort();
  }, [templates]);

  const filteredTemplates = useMemo(() => {
    let result = [...templates];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (t) =>
          t.title.toLowerCase().includes(q) ||
          t.skill.toLowerCase().includes(q) ||
          t.description.toLowerCase().includes(q)
      );
    }

    if (filterSkill !== "all") {
      result = result.filter((t) => t.skill === filterSkill);
    }

    switch (sortMode) {
      case "newest":
        result.sort((a, b) => b.date.localeCompare(a.date));
        break;
      case "oldest":
        result.sort((a, b) => a.date.localeCompare(b.date));
        break;
      case "name":
        result.sort((a, b) => a.title.localeCompare(b.title));
        break;
      case "starred":
        result.sort((a, b) => (b.starred ? 1 : 0) - (a.starred ? 1 : 0));
        break;
    }

    return result;
  }, [templates, searchQuery, filterSkill, sortMode]);

  const handleNewTemplate = useCallback(() => {
    setPage("dashboard");
  }, [setPage]);

  const isEmpty = templates.length === 0;

  return (
    <section className="flex-1 overflow-y-auto pt-8 pb-20 px-10">
      {/* Header */}
      <div className="relative mb-10">
        <div className="max-w-4xl">
          <h2 className="text-4xl font-extrabold font-headline tracking-tighter text-[#e5e2e1] mb-3">
            Template Library
          </h2>
          <p className="text-[#c2c6d8] text-base max-w-2xl font-body leading-relaxed">
            Your templates and community recipes.
          </p>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex gap-1 mb-6 bg-[var(--surface-variant,#1e1e1e)] rounded-xl p-1 w-fit">
        <button
          type="button"
          onClick={() => setActiveTab("my")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === "my"
              ? "bg-[#adc6ff]/15 text-[#adc6ff]"
              : "text-gray-400 hover:text-gray-200"
          }`}
        >
          My Templates ({templates.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("recipes")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === "recipes"
              ? "bg-[#adc6ff]/15 text-[#adc6ff]"
              : "text-gray-400 hover:text-gray-200"
          }`}
        >
          Community Recipes
        </button>
      </div>

      {activeTab === "recipes" ? (
        <Suspense fallback={<div className="text-gray-500 text-center py-12">Loading...</div>}>
          <RecipeGallery />
        </Suspense>
      ) : isEmpty ? (
        <EmptyLibrary onCreateNew={handleNewTemplate} />
      ) : (
        <>
          {/* Search and Filter */}
          <div className="mb-8 flex flex-wrap items-center gap-3">
            <div className="flex-1 min-w-[280px] relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-[#8c90a1] text-sm">
                search
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#1c1b1b] border border-[#333] text-[#e5e2e1] py-2.5 pl-10 pr-4 focus:outline-none focus:border-[#adc6ff] transition-all rounded-xl text-sm"
                placeholder="Search templates..."
              />
            </div>

            {/* Skill filter */}
            <select
              value={filterSkill}
              onChange={(e) => setFilterSkill(e.target.value)}
              className="bg-[#1c1b1b] border border-[#333] text-[#c2c6d8] rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:border-[#adc6ff]"
            >
              <option value="all">All Skills</option>
              {availableSkills.map((s) => (
                <option key={s} value={s}>
                  {SKILL_LABELS[s]?.label ?? s}
                </option>
              ))}
            </select>

            {/* Sort */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowSortMenu((prev) => !prev)}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#1c1b1b] border border-[#333] text-[#c2c6d8] text-xs hover:border-[#555] transition-colors"
              >
                <span className="material-symbols-outlined text-sm">sort</span>
                {sortMode === "newest" ? "Newest" : sortMode === "oldest" ? "Oldest" : sortMode === "name" ? "Name" : "Starred"}
              </button>
              {showSortMenu && (
                <div className="absolute right-0 top-full mt-1 bg-[#1e1e1e] border border-[#333] rounded-xl overflow-hidden shadow-xl z-10">
                  {(["newest", "oldest", "name", "starred"] as SortMode[]).map((mode) => (
                    <button
                      key={mode}
                      type="button"
                      onClick={() => { setSortMode(mode); setShowSortMenu(false); }}
                      className={`block w-full text-left px-4 py-2 text-xs hover:bg-[#252525] transition-colors ${sortMode === mode ? "text-[#adc6ff]" : "text-[#c2c6d8]"}`}
                    >
                      {mode === "newest" ? "Newest First" : mode === "oldest" ? "Oldest First" : mode === "name" ? "By Name" : "Starred First"}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <span className="text-xs text-[#666]">{filteredTemplates.length} templates</span>
          </div>

          {/* Template Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => {
              const skillStyle = SKILL_LABELS[template.skill] ?? SKILL_LABELS["custom"] ?? { label: template.skill, color: "text-[#888]" };
              return (
                <div
                  key={template.id}
                  className="group relative bg-[#1c1b1b] rounded-xl overflow-hidden hover:ring-1 hover:ring-[#424656]/40 transition-all duration-200"
                >
                  {/* Card header */}
                  <div className="p-5">
                    <div className="flex items-start justify-between mb-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${skillStyle.color}`}>
                        {skillStyle.label}
                      </span>
                      <div className="flex items-center gap-1">
                        <button
                          type="button"
                          onClick={() => toggleStar(template.id)}
                          className="p-1 rounded hover:bg-[#333] transition-colors"
                        >
                          <span
                            className={`material-symbols-outlined text-sm ${template.starred ? "text-[#ffb59a]" : "text-[#555] hover:text-[#888]"}`}
                            style={template.starred ? { fontVariationSettings: "'FILL' 1" } : undefined}
                          >
                            star
                          </span>
                        </button>
                        <button
                          type="button"
                          onClick={() => deleteTemplate(template.id)}
                          className="p-1 rounded hover:bg-[#333] transition-colors opacity-0 group-hover:opacity-100"
                        >
                          <span className="material-symbols-outlined text-sm text-[#555] hover:text-[#ffb4ab]">
                            delete
                          </span>
                        </button>
                      </div>
                    </div>

                    <h3 className="text-base font-bold text-[#e5e2e1] mb-1 truncate">
                      {template.title}
                    </h3>
                    <p className="text-[#888] text-xs line-clamp-2 mb-3 min-h-[2rem]">
                      {template.description}
                    </p>

                    <div className="flex items-center justify-between">
                      <span className="text-[10px] text-[#666]">
                        {formatDate(template.date)}
                      </span>
                      {template.notionUrl ? (
                        <a
                          href={template.notionUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-[#adc6ff] text-xs hover:underline"
                        >
                          <span className="material-symbols-outlined text-xs">open_in_new</span>
                          Open
                        </a>
                      ) : (
                        <span className="text-[10px] text-[#555]">No link</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* New Template Card */}
            <button
              type="button"
              onClick={handleNewTemplate}
              className="h-full min-h-[180px] flex flex-col justify-center items-center p-6 rounded-xl border border-dashed border-[#333] bg-[#0e0e0e]/50 group hover:bg-[#1c1b1b] transition-all cursor-pointer"
            >
              <div className="w-12 h-12 rounded-full bg-[#252525] flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-[#adc6ff] text-xl">add</span>
              </div>
              <h4 className="text-sm text-[#c2c6d8] font-medium">Create New Template</h4>
            </button>
          </div>
        </>
      )}
    </section>
  );
}

function EmptyLibrary({ onCreateNew }: { readonly onCreateNew: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-20 h-20 rounded-2xl bg-[#1e1e1e] border border-[#333] flex items-center justify-center mb-6">
        <span className="material-symbols-outlined text-4xl text-[#adc6ff]/30">
          inventory_2
        </span>
      </div>
      <h3 className="text-lg font-bold text-[#e5e2e1] mb-2">No templates yet</h3>
      <p className="text-sm text-[#888] mb-6 max-w-md">
        Templates you create through the chat will automatically appear here.
      </p>
      <button
        type="button"
        onClick={onCreateNew}
        className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#adc6ff] text-[#002e69] text-sm font-bold hover:opacity-90 transition-opacity"
      >
        <span className="material-symbols-outlined text-sm">add</span>
        Create Your First Template
      </button>
    </div>
  );
}

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  } catch {
    return dateStr;
  }
}

export default LibraryPage;
