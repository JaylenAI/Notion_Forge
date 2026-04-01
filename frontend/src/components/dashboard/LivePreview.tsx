import { useMemo, useState, useCallback } from "react";
import toast from "react-hot-toast";
import { useChatStore } from "../../stores/chatStore";
import NotionRenderer, { type NotionBlueprintData } from "./NotionRenderer";

interface BlueprintData {
  readonly metadata?: {
    readonly title?: string;
    readonly icon?: string;
    readonly template_type?: string;
    readonly color_theme?: string;
    readonly description?: string;
  };
  readonly databases?: ReadonlyArray<{
    readonly name?: string;
    readonly properties?: Record<string, { type?: string }>;
    readonly views?: ReadonlyArray<{ name?: string; type?: string }>;
    readonly sample_data?: ReadonlyArray<Record<string, unknown>>;
  }>;
  readonly sub_pages?: ReadonlyArray<{
    readonly title?: string;
    readonly icon?: string;
    readonly type?: string;
  }>;
}

const ZOOM_LEVELS = [50, 75, 100, 125, 150] as const;

function BlueprintPreview({ blueprint }: { readonly blueprint: BlueprintData }) {
  const meta = blueprint.metadata;
  const databases = blueprint.databases ?? [];
  const subPages = blueprint.sub_pages ?? [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-[#1e1e1e] rounded-2xl p-6 border border-[#333]">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-3xl">{meta?.icon ?? "\u{1F4C4}"}</span>
          <div>
            <h2 className="text-2xl font-extrabold tracking-tight text-white">
              {meta?.title ?? "Untitled"}
            </h2>
            {meta?.template_type && (
              <span className="text-xs text-[#adc6ff] uppercase tracking-wider">
                {meta.template_type}
              </span>
            )}
          </div>
        </div>
        {meta?.description && (
          <p className="text-gray-400 text-sm">{meta.description}</p>
        )}
        {meta?.color_theme && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-[10px] uppercase tracking-wider text-gray-500">
              Theme
            </span>
            <span className="px-2 py-0.5 rounded bg-[#2a2a2a] text-xs text-[#ffb59a] border border-[#333]">
              {meta.color_theme}
            </span>
          </div>
        )}
      </div>

      {/* Databases */}
      {databases.map((db, i) => (
        <div
          key={db.name ?? i}
          className="bg-[#1e1e1e] rounded-2xl p-6 border border-[#333]"
        >
          <div className="flex items-center gap-2 mb-4">
            <span className="material-symbols-outlined text-[#adc6ff] text-base">
              database
            </span>
            <h3 className="font-bold text-white text-sm">
              {db.name ?? `Database ${i + 1}`}
            </h3>
          </div>

          {/* Properties */}
          {db.properties && (
            <div className="mb-4">
              <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">
                Properties
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(db.properties).map(([name, prop]) => (
                  <span
                    key={name}
                    className="px-2 py-1 rounded bg-[#252525] text-xs text-gray-300 border border-[#333]"
                  >
                    <span className="text-[#adc6ff]">{name}</span>
                    <span className="text-gray-500 ml-1">
                      : {prop.type ?? "text"}
                    </span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Views */}
          {db.views && db.views.length > 0 && (
            <div className="mb-4">
              <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">
                Views
              </p>
              <div className="flex flex-wrap gap-2">
                {db.views.map((view, vi) => (
                  <span
                    key={view.name ?? vi}
                    className="flex items-center gap-1 px-2 py-1 rounded bg-[#252525] text-xs text-gray-300 border border-[#333]"
                  >
                    <span className="material-symbols-outlined text-[10px] text-[#ffb59a]">
                      {view.type === "board"
                        ? "view_kanban"
                        : view.type === "calendar"
                          ? "calendar_month"
                          : view.type === "gallery"
                            ? "grid_view"
                            : view.type === "timeline"
                              ? "timeline"
                              : "table_rows"}
                    </span>
                    {view.name ?? view.type ?? "View"}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Sample Data Table */}
          {db.sample_data && db.sample_data.length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">
                Sample Data
              </p>
              <div className="overflow-x-auto rounded-lg border border-[#333]">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-[#252525]">
                      {Object.keys(db.sample_data[0] ?? {}).map((key) => (
                        <th
                          key={key}
                          className="text-left px-3 py-2 text-gray-400 font-medium border-b border-[#333]"
                        >
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {db.sample_data.slice(0, 5).map((row, ri) => (
                      <tr
                        key={ri}
                        className="border-b border-[#333]/50 last:border-0"
                      >
                        {Object.values(row).map((val, ci) => (
                          <td
                            key={ci}
                            className="px-3 py-2 text-gray-300 max-w-[150px] truncate"
                          >
                            {String(val ?? "")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ))}

      {/* Sub-pages */}
      {subPages.length > 0 && (
        <div className="bg-[#1e1e1e] rounded-2xl p-6 border border-[#333]">
          <p className="text-[10px] uppercase tracking-wider text-gray-500 mb-3">
            Sub-pages
          </p>
          <div className="space-y-2">
            {subPages.map((page, i) => (
              <div
                key={page.title ?? i}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[#252525] border border-[#333]"
              >
                <span className="text-sm">{page.icon ?? "\u{1F4C4}"}</span>
                <span className="text-sm text-gray-300">
                  {page.title ?? "Untitled"}
                </span>
                {page.type && (
                  <span className="text-[10px] text-gray-500 ml-auto">
                    {page.type}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center py-20">
      <div className="w-16 h-16 rounded-2xl bg-[#1e1e1e] border border-[#333] flex items-center justify-center mb-6">
        <span className="material-symbols-outlined text-3xl text-[#adc6ff]/40">
          preview
        </span>
      </div>
      <p className="text-gray-400 text-sm mb-2">
        Template preview will appear here once AI designs it
      </p>
      <p className="text-gray-500 text-xs">
        Describe the Notion template you want in the chat
      </p>
    </div>
  );
}

function CompleteBanner({ notionUrl }: { readonly notionUrl: string }) {
  const handleCopy = () => {
    navigator.clipboard.writeText(notionUrl).then(() => {
      toast.success("URL copied!");
    });
  };

  return (
    <div className="bg-[#1e1e1e] rounded-2xl p-6 border border-[#4edea3]/30">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-xl bg-[#4edea3]/20 flex items-center justify-center">
          <span className="material-symbols-outlined text-[#4edea3]">
            check_circle
          </span>
        </div>
        <div>
          <h3 className="font-bold text-white">Template Created</h3>
          <p className="text-xs text-gray-400">
            Your Notion page has been successfully generated
          </p>
        </div>
      </div>
      <div className="flex gap-2 mt-3">
        <a
          href={notionUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-2 bg-[#4edea3] text-[#003824] font-bold text-sm py-3 rounded-xl hover:opacity-90 transition-opacity"
        >
          <span className="material-symbols-outlined text-sm">open_in_new</span>
          Notion\uC5D0\uC11C \uC5F4\uAE30
        </a>
        <button
          type="button"
          onClick={handleCopy}
          className="px-4 py-3 rounded-xl bg-[#2a2a2a] text-[#c2c6d8] hover:bg-[#353534] transition-colors flex items-center gap-2"
          title="Copy URL"
        >
          <span className="material-symbols-outlined text-sm">content_copy</span>
        </button>
      </div>
    </div>
  );
}

function CreationStepper() {
  const isLoading = useChatStore((s) => s.isLoading);
  const messages = useChatStore((s) => s.messages);

  const hasBlueprint = messages.some((m) => m.metadata?.blueprint);

  const steps = [
    { label: "Creating Page", done: hasBlueprint || messages.length > 0 },
    { label: "Adding Database", done: hasBlueprint },
    { label: "Populating Rows", done: !isLoading && hasBlueprint },
  ];

  return (
    <div className="bg-[#1e1e1e] rounded-xl p-4 border border-[#333]/30">
      <div className="flex items-center gap-3 flex-wrap">
        {steps.map((step, i) => (
          <div key={step.label} className="flex items-center gap-2">
            {i > 0 && <div className="w-6 h-px bg-[#333]" />}
            <div
              className={`w-2 h-2 rounded-full flex-shrink-0 ${
                step.done
                  ? "bg-[#4edea3]"
                  : isLoading && i === steps.findIndex((s) => !s.done)
                    ? "bg-[#adc6ff] animate-pulse"
                    : "bg-[#444]"
              }`}
            />
            <span
              className={`text-xs font-bold uppercase tracking-tighter whitespace-nowrap ${
                step.done
                  ? "text-[#4edea3]"
                  : isLoading && i === steps.findIndex((s) => !s.done)
                    ? "text-[#adc6ff]"
                    : "text-gray-500"
              }`}
            >
              {step.label}
              {step.done && (
                <span className="material-symbols-outlined text-[10px] ml-1 align-middle">
                  check_circle
                </span>
              )}
              {isLoading && !step.done && i === steps.findIndex((s) => !s.done) && (
                <span className="inline-block ml-1 w-3 h-3 border-2 border-[#adc6ff] border-t-transparent rounded-full animate-spin align-middle" />
              )}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function LivePreview() {
  const messages = useChatStore((s) => s.messages);
  const [previewMode, setPreviewMode] = useState(true);
  const [zoomIndex, setZoomIndex] = useState(2); // Default 100%

  const zoomLevel = ZOOM_LEVELS[zoomIndex] ?? 100;

  const zoomIn = useCallback(() => {
    setZoomIndex((prev) => Math.min(prev + 1, ZOOM_LEVELS.length - 1));
  }, []);

  const zoomOut = useCallback(() => {
    setZoomIndex((prev) => Math.max(prev - 1, 0));
  }, []);

  const resetZoom = useCallback(() => {
    setZoomIndex(2);
  }, []);

  const { blueprint, notionUrl, isComplete } = useMemo(() => {
    const reversed = [...messages].reverse();
    const blueprintMsg = reversed.find((m) => m.metadata?.blueprint);
    const urlMsg = reversed.find((m) => m.metadata?.notionUrl);
    const completeMsg = reversed.find((m) => m.metadata?.type === "complete");
    return {
      blueprint: blueprintMsg?.metadata?.blueprint as BlueprintData | undefined,
      notionUrl: urlMsg?.metadata?.notionUrl,
      isComplete: !!completeMsg,
    };
  }, [messages]);

  const hasBlueprint = !!blueprint;
  const isLoading = useChatStore((s) => s.isLoading);
  const showStepper = isLoading || hasBlueprint;

  return (
    <section className="flex-1 flex flex-col bg-[var(--preview-bg,#131313)] rounded-2xl border border-[#333]/30 overflow-hidden relative">
      {/* Toolbar — nowrap to prevent line-break on narrow panels */}
      <div className="h-14 flex items-center justify-between px-3 sm:px-6 bg-[#1e1e1e]/80 border-b border-[#333]/30 backdrop-blur-md overflow-hidden shrink-0">
        <div className="flex items-center gap-2 sm:gap-4 min-w-0 overflow-hidden">
          <span className="material-symbols-outlined text-[#ffb59a] shrink-0">
            description
          </span>
          <span className="text-sm font-semibold tracking-wide text-white whitespace-nowrap hidden lg:inline">
            Live Preview
          </span>
          <span className="h-4 w-px bg-[#333] hidden lg:block shrink-0" />
          <div className="hidden lg:flex items-center gap-2 text-xs text-gray-500 whitespace-nowrap">
            <span className="material-symbols-outlined text-xs">
              {hasBlueprint ? "cloud_done" : "cloud_off"}
            </span>
            {hasBlueprint ? "Blueprint loaded" : "Waiting"}
          </div>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
          {/* Zoom controls */}
          <div className="flex items-center gap-1 bg-[#252525] rounded-lg border border-[#333]/50 px-1">
            <button
              type="button"
              onClick={zoomOut}
              disabled={zoomIndex === 0}
              className="w-7 h-7 flex items-center justify-center text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Zoom Out"
            >
              <span className="material-symbols-outlined text-sm">remove</span>
            </button>
            <button
              type="button"
              onClick={resetZoom}
              className="px-2 h-7 text-[10px] text-gray-400 hover:text-white font-mono transition-colors"
              title="Reset Zoom"
            >
              {zoomLevel}%
            </button>
            <button
              type="button"
              onClick={zoomIn}
              disabled={zoomIndex === ZOOM_LEVELS.length - 1}
              className="w-7 h-7 flex items-center justify-center text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Zoom In"
            >
              <span className="material-symbols-outlined text-sm">add</span>
            </button>
          </div>

          <button
            type="button"
            onClick={() => setPreviewMode((prev) => !prev)}
            className={`px-3 sm:px-4 py-1.5 rounded-lg border text-xs font-label uppercase tracking-wider transition-colors whitespace-nowrap ${
              previewMode && hasBlueprint
                ? "border-[#adc6ff] text-[#adc6ff] bg-[#adc6ff]/10"
                : "border-[#333] text-gray-400 hover:bg-[#2a2a2a]"
            }`}
          >
            Preview
          </button>
          {notionUrl ? (
            <a
              href={notionUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 sm:px-4 py-1.5 rounded-lg bg-[#4edea3] text-[#003824] text-xs font-label font-bold uppercase tracking-wider hover:opacity-90 transition-opacity inline-flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-xs">
                open_in_new
              </span>
              <span className="hidden sm:inline">Open in Notion</span>
            </a>
          ) : null}
        </div>
      </div>

      {/* Live Canvas Area */}
      <div className="flex-1 blueprint-bg p-4 sm:p-8 overflow-auto">
        <div
          className="max-w-4xl mx-auto space-y-6 transition-transform duration-200 origin-top-left"
          style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: "top center" }}
        >
          {isComplete && notionUrl && <CompleteBanner notionUrl={notionUrl} />}

          {hasBlueprint ? (
            <>
              {previewMode ? (
                <NotionRenderer blueprint={blueprint as unknown as NotionBlueprintData} />
              ) : (
                <BlueprintPreview blueprint={blueprint} />
              )}
              {showStepper && <CreationStepper />}
            </>
          ) : showStepper ? (
            <CreationStepper />
          ) : (
            <EmptyState />
          )}
        </div>
      </div>
    </section>
  );
}

export default LivePreview;
