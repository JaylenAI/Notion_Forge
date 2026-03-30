import { useState, useCallback } from "react";
import { useChatStore } from "../../stores/chatStore";

const TAG_COLORS: Record<string, { bg: string; text: string }> = {
  tertiary: { bg: "bg-[#4edea3]/20", text: "text-[#4edea3]" },
  secondary: { bg: "bg-[#ffb59a]/20", text: "text-[#ffb59a]" },
  primary: { bg: "bg-[#adc6ff]/20", text: "text-[#adc6ff]" },
};

function LibraryPage() {
  const templates = useChatStore((s) => s.generatedTemplates);
  const toggleStar = useChatStore((s) => s.toggleTemplateStar);
  const setPage = useChatStore((s) => s.setPage);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredTemplates = searchQuery.trim()
    ? templates.filter(
        (t) =>
          t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          t.tag.toLowerCase().includes(searchQuery.toLowerCase()) ||
          t.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : templates;

  const handleNewTemplate = useCallback(() => {
    setPage("dashboard");
  }, [setPage]);

  return (
    <section className="flex-1 overflow-y-auto pt-8 pb-20 px-10">
      {/* Header */}
      <div className="relative mb-12">
        <div className="max-w-4xl">
          <h2 className="text-5xl font-extrabold font-headline tracking-tighter text-[#e5e2e1] mb-4">
            Template Vault
          </h2>
          <p className="text-[#c2c6d8] text-lg max-w-2xl font-body leading-relaxed">
            Access and refine your AI-transmuted Notion architectures. Every
            generation is preserved with high-fidelity structural metadata.
          </p>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="mb-10 flex flex-wrap items-center gap-4">
        <div className="flex-1 min-w-[300px] relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-[#8c90a1]">
            search
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#1c1b1b] border-b border-[#424656]/30 text-[#e5e2e1] py-3 pl-12 pr-4 focus:outline-none focus:border-[#adc6ff] transition-all rounded-t-xl"
            placeholder="Search templates by name, tags, or focus..."
          />
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#2a2a2a] text-[#c2c6d8] hover:text-[#e5e2e1] transition-all border border-transparent hover:border-[#424656]/30"
          >
            <span className="material-symbols-outlined text-sm">
              filter_list
            </span>
            <span className="text-xs font-label uppercase tracking-widest">
              Filter
            </span>
          </button>
          <button
            type="button"
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#2a2a2a] text-[#c2c6d8] hover:text-[#e5e2e1] transition-all border border-transparent hover:border-[#424656]/30"
          >
            <span className="material-symbols-outlined text-sm">sort</span>
            <span className="text-xs font-label uppercase tracking-widest">
              Sort: Newest
            </span>
          </button>
        </div>
      </div>

      {/* Template Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {filteredTemplates.map((template) => {
          const colors = TAG_COLORS[template.tagColor] ?? { bg: "bg-[#adc6ff]/20", text: "text-[#adc6ff]" };
          return (
            <div
              key={template.id}
              className="group relative bg-[#1c1b1b] rounded-xl overflow-hidden shadow-[0_0_48px_0_rgba(173,198,255,0.06)] hover:scale-[1.01] transition-all duration-300"
            >
              <div className="h-48 overflow-hidden relative bg-gradient-to-br from-[#2a2a2a] to-[#131313]">
                <div className="absolute inset-0 bg-gradient-to-t from-[#1c1b1b] to-transparent" />
                <div className="absolute inset-0 flex items-center justify-center opacity-20 group-hover:opacity-30 transition-opacity">
                  <span className="material-symbols-outlined text-7xl text-[#adc6ff]">
                    description
                  </span>
                </div>
                <div className="absolute top-4 left-4 flex gap-2">
                  <span
                    className={`px-2 py-1 rounded ${colors.bg} ${colors.text} text-[10px] font-bold uppercase tracking-widest`}
                  >
                    {template.tag}
                  </span>
                </div>
              </div>
              <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xl font-bold font-headline text-[#e5e2e1]">
                    {template.title}
                  </h3>
                  <span className="text-[10px] font-label text-[#8c90a1] uppercase tracking-widest">
                    {template.date}
                  </span>
                </div>
                <p className="text-[#c2c6d8] text-sm font-body mb-6 line-clamp-2">
                  {template.description}
                </p>
                <div className="flex items-center justify-between">
                  <button
                    type="button"
                    className="text-[#adc6ff] text-xs font-bold uppercase tracking-widest flex items-center gap-2 hover:gap-3 transition-all"
                  >
                    Open in Notion
                    <span className="material-symbols-outlined text-sm">
                      open_in_new
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={() => toggleStar(template.id)}
                    className="transition-colors"
                  >
                    <span
                      className={`material-symbols-outlined ${
                        template.starred
                          ? "text-[#ffb59a]"
                          : "text-[#8c90a1] cursor-pointer hover:text-[#ffb59a]"
                      }`}
                      style={
                        template.starred
                          ? { fontVariationSettings: "'FILL' 1" }
                          : undefined
                      }
                    >
                      star
                    </span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}

        {/* New Architecture Card */}
        <button
          type="button"
          onClick={handleNewTemplate}
          className="lg:col-span-1 h-full min-h-[340px] flex flex-col justify-center items-center p-8 rounded-xl border border-dashed border-[#424656]/20 bg-[#0e0e0e]/50 group hover:bg-[#1c1b1b] transition-all cursor-pointer"
        >
          <div className="w-16 h-16 rounded-full bg-[#353534] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-[#adc6ff] text-3xl">
              add
            </span>
          </div>
          <h4 className="text-[#e5e2e1] font-headline font-bold mb-2">
            New Architecture?
          </h4>
          <p className="text-[#c2c6d8] text-xs font-label uppercase tracking-tighter text-center">
            Spawn a new template in seconds
          </p>
        </button>
      </div>
    </section>
  );
}

export default LibraryPage;
