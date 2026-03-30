import { useState, useCallback } from "react";

// ============================================================
// Types
// ============================================================

interface BlueprintBlock {
  readonly type: string;
  readonly text?: string;
  readonly icon?: string;
  readonly color?: string;
  readonly columns?: ReadonlyArray<{ blocks: ReadonlyArray<BlueprintBlock> }>;
  readonly children_text?: string;
  readonly db_index?: number;
  readonly checked?: boolean;
}

interface BlueprintDatabase {
  readonly title?: string;
  readonly is_inline?: boolean;
  readonly properties?: Record<string, unknown>;
  readonly views?: ReadonlyArray<{ type?: string; title?: string; name?: string }>;
  readonly sample_items?: ReadonlyArray<Record<string, unknown>>;
}

interface BlueprintSubPage {
  readonly title?: string;
  readonly icon?: string;
  readonly blocks?: ReadonlyArray<BlueprintBlock>;
}

interface BlueprintMainPage {
  readonly title?: string;
  readonly icon?: string;
  readonly cover_url?: string;
}

interface BlueprintMetadata {
  readonly title?: string;
  readonly template_type?: string;
  readonly color_theme?: string;
  readonly description?: string;
  readonly icon?: string;
}

export interface NotionBlueprintData {
  readonly main_page?: BlueprintMainPage;
  readonly metadata?: BlueprintMetadata;
  readonly blocks?: ReadonlyArray<BlueprintBlock>;
  readonly databases?: ReadonlyArray<BlueprintDatabase>;
  readonly sub_pages?: ReadonlyArray<BlueprintSubPage>;
}

// ============================================================
// Color utilities
// ============================================================

const COLOR_BG_MAP: Record<string, string> = {
  blue_background: "bg-blue-900/30 border-l-4 border-blue-500",
  orange_background: "bg-orange-900/30 border-l-4 border-orange-500",
  green_background: "bg-green-900/30 border-l-4 border-green-500",
  red_background: "bg-red-900/30 border-l-4 border-red-500",
  purple_background: "bg-purple-900/30 border-l-4 border-purple-500",
  pink_background: "bg-pink-900/30 border-l-4 border-pink-500",
  yellow_background: "bg-yellow-900/30 border-l-4 border-yellow-500",
  gray_background: "bg-gray-700/30 border-l-4 border-gray-500",
  default: "bg-[#2f2f2f] border-l-4 border-[#555]",
};

const HEADING_COLOR_MAP: Record<string, string> = {
  blue_background: "bg-blue-900/20 px-3 py-1 rounded",
  orange_background: "bg-orange-900/20 px-3 py-1 rounded",
  green_background: "bg-green-900/20 px-3 py-1 rounded",
  red_background: "bg-red-900/20 px-3 py-1 rounded",
  purple_background: "bg-purple-900/20 px-3 py-1 rounded",
  pink_background: "bg-pink-900/20 px-3 py-1 rounded",
  yellow_background: "bg-yellow-900/20 px-3 py-1 rounded",
  gray_background: "bg-gray-700/20 px-3 py-1 rounded",
};

const SELECT_COLOR_MAP: Record<string, string> = {
  blue: "bg-blue-900/50 text-blue-300",
  green: "bg-green-900/50 text-green-300",
  red: "bg-red-900/50 text-red-300",
  orange: "bg-orange-900/50 text-orange-300",
  purple: "bg-purple-900/50 text-purple-300",
  pink: "bg-pink-900/50 text-pink-300",
  yellow: "bg-yellow-900/50 text-yellow-300",
  gray: "bg-gray-700/50 text-gray-300",
  default: "bg-[#383838] text-gray-300",
};

function getCalloutBg(color?: string): string {
  const fallback = COLOR_BG_MAP["default"] ?? "";
  if (!color) return fallback;
  return COLOR_BG_MAP[color] ?? fallback;
}

function getHeadingColor(color?: string): string {
  if (!color) return "";
  return HEADING_COLOR_MAP[color] ?? "";
}

function getSelectColor(color?: string): string {
  const fallback = SELECT_COLOR_MAP["default"] ?? "";
  if (!color) return fallback;
  return SELECT_COLOR_MAP[color] ?? fallback;
}

// ============================================================
// Block renderers
// ============================================================

function CalloutBlock({ block }: { readonly block: BlueprintBlock }) {
  return (
    <div className={`flex items-start gap-3 rounded-lg p-4 my-1 ${getCalloutBg(block.color)}`}>
      <span className="text-xl flex-shrink-0 mt-0.5">{block.icon ?? "💡"}</span>
      <p className="text-sm text-[#d4d4d4] leading-relaxed">{block.text}</p>
    </div>
  );
}

function Heading1Block({ block }: { readonly block: BlueprintBlock }) {
  const colorClass = getHeadingColor(block.color);
  return (
    <h1 className={`text-2xl font-bold text-white mt-6 mb-2 ${colorClass}`}>
      {block.text}
    </h1>
  );
}

function Heading2Block({ block }: { readonly block: BlueprintBlock }) {
  const colorClass = getHeadingColor(block.color);
  return (
    <h2 className={`text-lg font-semibold text-white mt-4 mb-1.5 ${colorClass}`}>
      {block.text}
    </h2>
  );
}

function DividerBlock() {
  return <hr className="border-t border-[#333] my-3" />;
}

function TodoBlock({ block }: { readonly block: BlueprintBlock }) {
  const [checked, setChecked] = useState(!!block.checked);
  const toggle = useCallback(() => setChecked((prev) => !prev), []);

  return (
    <div className="flex items-center gap-2.5 py-1 px-1 group">
      <button
        type="button"
        onClick={toggle}
        className={`w-4 h-4 rounded-sm border flex items-center justify-center flex-shrink-0 transition-colors ${
          checked
            ? "bg-blue-500 border-blue-500"
            : "border-[#555] hover:border-[#888]"
        }`}
      >
        {checked && (
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M2 5L4 7L8 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}
      </button>
      <span className={`text-sm ${checked ? "line-through text-[#666]" : "text-[#d4d4d4]"}`}>
        {block.text}
      </span>
    </div>
  );
}

function ToggleBlock({ block }: { readonly block: BlueprintBlock }) {
  const [open, setOpen] = useState(false);
  const toggle = useCallback(() => setOpen((prev) => !prev), []);

  return (
    <div className="py-0.5">
      <button
        type="button"
        onClick={toggle}
        className="flex items-center gap-2 w-full text-left group py-1 px-1 rounded hover:bg-[#252525] transition-colors"
      >
        <span
          className={`text-[#888] text-xs transition-transform duration-150 ${open ? "rotate-90" : ""}`}
        >
          &#9654;
        </span>
        <span className="text-sm text-[#d4d4d4]">{block.text}</span>
      </button>
      {open && block.children_text && (
        <div className="ml-6 pl-3 border-l border-[#333] py-1">
          <p className="text-sm text-[#999]">{block.children_text}</p>
        </div>
      )}
    </div>
  );
}

function ParagraphBlock({ block }: { readonly block: BlueprintBlock }) {
  const colorClass = getHeadingColor(block.color);
  return (
    <p className={`text-sm text-[#d4d4d4] py-0.5 px-1 ${colorClass}`}>
      {block.text}
    </p>
  );
}

function BulletedListBlock({ block }: { readonly block: BlueprintBlock }) {
  return (
    <div className="flex items-start gap-2.5 py-0.5 px-1">
      <span className="text-[#888] mt-1.5 text-[6px]">&#9679;</span>
      <span className="text-sm text-[#d4d4d4]">{block.text}</span>
    </div>
  );
}

function ColumnListBlock({
  block,
  databases,
}: {
  readonly block: BlueprintBlock;
  readonly databases: ReadonlyArray<BlueprintDatabase>;
}) {
  const columns = block.columns ?? [];
  return (
    <div className="flex gap-4 my-2" style={{ alignItems: "flex-start" }}>
      {columns.map((col, ci) => (
        <div key={ci} className="flex-1 min-w-0">
          {col.blocks.map((childBlock, bi) => (
            <BlockRenderer key={bi} block={childBlock} databases={databases} />
          ))}
        </div>
      ))}
    </div>
  );
}

// ============================================================
// Database renderer
// ============================================================

function resolvePropertyType(spec: unknown): { type: string; options?: ReadonlyArray<{ name: string; color?: string }> } {
  if (typeof spec === "string") {
    return { type: spec };
  }
  if (typeof spec === "object" && spec !== null) {
    const obj = spec as Record<string, unknown>;
    return {
      type: (obj.type as string) ?? "text",
      options: obj.options as ReadonlyArray<{ name: string; color?: string }> | undefined,
    };
  }
  return { type: "text" };
}

function findOptionColor(
  propSpec: unknown,
  value: string
): string | undefined {
  if (typeof propSpec !== "object" || propSpec === null) return undefined;
  const obj = propSpec as Record<string, unknown>;
  const options = obj.options as ReadonlyArray<{ name: string; color?: string }> | undefined;
  if (!options) return undefined;
  const match = options.find((o) => o.name === value);
  return match?.color;
}

const VIEW_ICON_MAP: Record<string, string> = {
  table: "📊",
  calendar: "📅",
  board: "📋",
  gallery: "🖼️",
  timeline: "📈",
  list: "📝",
};

function DatabaseRenderer({ db }: { readonly db: BlueprintDatabase }) {
  const properties = db.properties ?? {};
  const views = db.views ?? [];
  const sampleItems = db.sample_items ?? [];
  const [activeView, setActiveView] = useState(0);

  const propEntries = Object.entries(properties);
  const titlePropName = propEntries.find(([, spec]) => {
    const resolved = resolvePropertyType(spec);
    return resolved.type === "title";
  })?.[0];

  const displayProps = propEntries.filter(([name]) => name !== titlePropName);

  return (
    <div className="my-4">
      {/* Database title bar */}
      <div className="flex items-center gap-2 mb-2 px-1">
        <span className="text-base">📊</span>
        <span className="text-sm font-semibold text-white">{db.title ?? "Database"}</span>
        <span className="text-xs text-[#666] ml-auto">{sampleItems.length} items</span>
      </div>

      {/* View tabs */}
      {views.length > 0 && (
        <div className="flex items-center gap-1 border-b border-[#333] mb-0 px-1">
          {views.map((view, vi) => {
            const viewType = view.type ?? view.title ?? "table";
            const icon = VIEW_ICON_MAP[viewType] ?? "📊";
            return (
              <button
                key={vi}
                type="button"
                onClick={() => setActiveView(vi)}
                className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
                  activeView === vi
                    ? "border-blue-500 text-white"
                    : "border-transparent text-[#888] hover:text-[#bbb]"
                }`}
              >
                <span>{icon}</span>
                <span className="capitalize">{view.title ?? view.name ?? viewType}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-b-lg border border-[#333] border-t-0">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-[#1e1e1e]">
              {titlePropName && (
                <th className="text-left px-3 py-2.5 text-[#999] font-medium border-r border-[#333] min-w-[160px]">
                  {titlePropName}
                </th>
              )}
              {displayProps.map(([name]) => (
                <th
                  key={name}
                  className="text-left px-3 py-2.5 text-[#999] font-medium border-r border-[#333] last:border-r-0 min-w-[100px]"
                >
                  {name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sampleItems.slice(0, 8).map((row, ri) => (
              <tr
                key={ri}
                className="border-t border-[#2a2a2a] hover:bg-[#1a1a1a] transition-colors"
              >
                {titlePropName && (
                  <td className="px-3 py-2 border-r border-[#2a2a2a] font-medium text-white">
                    <div className="flex items-center gap-1.5">
                      {row["icon"] ? <span className="text-sm">{String(row["icon"])}</span> : null}
                      <span>{String(row[titlePropName] ?? "")}</span>
                    </div>
                  </td>
                )}
                {displayProps.map(([name, spec]) => {
                  const resolved = resolvePropertyType(spec);
                  const cellVal = row[name];
                  return (
                    <td
                      key={name}
                      className="px-3 py-2 border-r border-[#2a2a2a] last:border-r-0"
                    >
                      <CellValue
                        value={cellVal}
                        propType={resolved.type}
                        propSpec={spec}
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CellValue({
  value,
  propType,
  propSpec,
}: {
  readonly value: unknown;
  readonly propType: string;
  readonly propSpec: unknown;
}) {
  if (value === null || value === undefined) {
    return <span className="text-[#555]">-</span>;
  }

  if (propType === "checkbox" || typeof value === "boolean") {
    return <span>{value ? "✅" : "⬜"}</span>;
  }

  if (propType === "select" || propType === "multi_select") {
    const strVal = String(value);
    const optionColor = findOptionColor(propSpec, strVal);
    return (
      <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${getSelectColor(optionColor)}`}>
        {strVal}
      </span>
    );
  }

  if (propType === "status") {
    const strVal = String(value);
    return (
      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-blue-400 flex-shrink-0" />
        <span className="text-[#d4d4d4]">{strVal}</span>
      </div>
    );
  }

  if (propType === "date") {
    return <span className="text-[#999]">{String(value)}</span>;
  }

  if (propType === "number") {
    return <span className="text-[#d4d4d4] tabular-nums">{String(value)}</span>;
  }

  return <span className="text-[#d4d4d4]">{String(value)}</span>;
}

// ============================================================
// Block dispatcher
// ============================================================

function BlockRenderer({
  block,
  databases,
}: {
  readonly block: BlueprintBlock;
  readonly databases: ReadonlyArray<BlueprintDatabase>;
}) {
  switch (block.type) {
    case "callout":
      return <CalloutBlock block={block} />;
    case "heading_1":
      return <Heading1Block block={block} />;
    case "heading_2":
      return <Heading2Block block={block} />;
    case "divider":
      return <DividerBlock />;
    case "to_do":
      return <TodoBlock block={block} />;
    case "toggle":
      return <ToggleBlock block={block} />;
    case "paragraph":
      return <ParagraphBlock block={block} />;
    case "bulleted_list":
      return <BulletedListBlock block={block} />;
    case "column_list":
      return <ColumnListBlock block={block} databases={databases} />;
    case "database_ref": {
      const dbIdx = block.db_index ?? 0;
      const db = databases[dbIdx];
      if (!db) return null;
      return <DatabaseRenderer db={db} />;
    }
    default:
      return null;
  }
}

// ============================================================
// Sub-page links
// ============================================================

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

// ============================================================
// Main renderer
// ============================================================

function NotionRenderer({ blueprint }: { readonly blueprint: NotionBlueprintData }) {
  const mainPage = blueprint.main_page;
  const blocks = blueprint.blocks ?? [];
  const databases = blueprint.databases ?? [];
  const subPages = blueprint.sub_pages ?? [];

  const pageIcon = mainPage?.icon ?? blueprint.metadata?.icon ?? "📄";
  const pageTitle = mainPage?.title ?? blueprint.metadata?.title ?? "Untitled";

  return (
    <div className="bg-[#191919] rounded-xl overflow-hidden shadow-2xl">
      {/* Cover image area */}
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

      {/* Page content */}
      <div className="px-10 pb-10" style={{ marginTop: mainPage?.cover_url ? "-2rem" : "0" }}>
        {/* Icon + Title */}
        <div className="mb-6 pt-4">
          <span className="text-5xl block mb-3">{pageIcon}</span>
          <h1 className="text-3xl font-bold text-white tracking-tight leading-tight">
            {pageTitle}
          </h1>
        </div>

        {/* Blocks */}
        <div className="space-y-0.5">
          {blocks.map((block, idx) => (
            <BlockRenderer key={idx} block={block} databases={databases} />
          ))}
        </div>

        {/* Sub-pages */}
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
