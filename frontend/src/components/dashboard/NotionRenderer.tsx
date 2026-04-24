import type { NotionBlueprintData, BlueprintSubPage } from "./notion-renderer.types";
import BlockRenderer, { resetNumberedListCounter } from "./NotionBlockRenderers";

export type { NotionBlueprintData };

function SubPageLink({ page }: { readonly page: BlueprintSubPage }) {
  return (
    <div className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-[#252525] transition-colors cursor-pointer group">
      <span className="text-base">{page.icon ?? "📄"}</span>
      <span className="text-sm text-[#d4d4d4] group-hover:text-white transition-colors">
        {page.title ?? "Untitled"}
      </span>
      <span className="material-symbols-outlined text-[#555] text-sm ml-auto opacity-0 group-hover:opacity-100 transition-opacity">
        chevron_right
      </span>
    </div>
  );
}

function NotionRenderer({ blueprint }: { readonly blueprint: NotionBlueprintData }) {
  const mainPage = blueprint.main_page;
  const blocks = blueprint.blocks ?? [];
  const databases = blueprint.databases ?? [];
  const subPages = blueprint.sub_pages ?? [];

  const pageIcon = mainPage?.icon ?? blueprint.metadata?.icon ?? "📄";
  const pageTitle = mainPage?.title ?? blueprint.metadata?.title ?? "Untitled";

  resetNumberedListCounter();

  return (
    <div className="bg-[#191919] rounded-xl overflow-hidden shadow-2xl">
      {mainPage?.cover_url && (
        <div className="h-36 overflow-hidden relative">
          <img
            src={mainPage.cover_url}
            alt="cover"
            className="w-full h-full object-cover opacity-60"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#191919] to-transparent" />
        </div>
      )}

      <div className="px-10 pb-10" style={{ marginTop: mainPage?.cover_url ? "-2rem" : "0" }}>
        <div className="mb-6 pt-4">
          <span className="text-5xl block mb-3">{pageIcon}</span>
          <h1 className="text-3xl font-bold text-white tracking-tight leading-tight">
            {pageTitle}
          </h1>
        </div>

        <div className="space-y-0.5">
          {blocks.map((block, idx) => (
            <BlockRenderer key={idx} block={block} databases={databases} index={idx + 1} />
          ))}
        </div>

        {subPages.length > 0 && (
          <div className="mt-6 pt-4 border-t border-[#333]">
            {subPages.map((page, i) => (
              <SubPageLink key={page.title ?? i} page={page} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default NotionRenderer;
