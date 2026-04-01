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
  readonly language?: string;
  readonly url?: string;
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
  brown_background: "bg-amber-900/30 border-l-4 border-amber-700",
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
  brown_background: "bg-amber-900/20 px-3 py-1 rounded",
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
  brown: "bg-amber-900/50 text-amber-300",
  default: "bg-[#383838] text-gray-300",
};

const STATUS_COLOR_MAP: Record<string, { dot: string; text: string }> = {
  "시작 전": { dot: "bg-gray-400", text: "text-gray-400" },
  "not started": { dot: "bg-gray-400", text: "text-gray-400" },
  "진행 중": { dot: "bg-blue-400", text: "text-blue-400" },
  "in progress": { dot: "bg-blue-400", text: "text-blue-400" },
  "완료": { dot: "bg-green-400", text: "text-green-400" },
  "done": { dot: "bg-green-400", text: "text-green-400" },
  "complete": { dot: "bg-green-400", text: "text-green-400" },
};

function getCalloutBg(color?: string): string {
  if (!color) return COLOR_BG_MAP["default"] ?? "";
  return COLOR_BG_MAP[color] ?? COLOR_BG_MAP["default"] ?? "";
}

function getHeadingColor(color?: string): string {
  if (!color) return "";
  return HEADING_COLOR_MAP[color] ?? "";
}

function getSelectColor(color?: string): string {
  if (!color) return SELECT_COLOR_MAP["default"] ?? "";
  return SELECT_COLOR_MAP[color] ?? SELECT_COLOR_MAP["default"] ?? "";
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
  return (
    <h1 className={`text-2xl font-bold text-white mt-6 mb-2 ${getHeadingColor(block.color)}`}>
      {block.text}
    </h1>
  );
}

function Heading2Block({ block }: { readonly block: BlueprintBlock }) {
  return (
    <h2 className={`text-lg font-semibold text-white mt-4 mb-1.5 ${getHeadingColor(block.color)}`}>
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
        <span className={`text-[#888] text-xs transition-transform duration-150 ${open ? "rotate-90" : ""}`}>
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
  return (
    <p className={`text-sm text-[#d4d4d4] py-0.5 px-1 ${getHeadingColor(block.color)}`}>
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

function NumberedListBlock({ block, index }: { readonly block: BlueprintBlock; readonly index: number }) {
  return (
    <div className="flex items-start gap-2.5 py-0.5 px-1">
      <span className="text-[#888] text-sm min-w-[1.2em] text-right tabular-nums">{index}.</span>
      <span className="text-sm text-[#d4d4d4]">{block.text}</span>
    </div>
  );
}

function QuoteBlock({ block }: { readonly block: BlueprintBlock }) {
  return (
    <blockquote className="border-l-[3px] border-[#adc6ff] pl-4 py-2 my-2">
      <p className="text-sm text-[#d4d4d4] italic leading-relaxed">{block.text}</p>
    </blockquote>
  );
}

function CodeBlock({ block }: { readonly block: BlueprintBlock }) {
  return (
    <div className="my-2 rounded-lg overflow-hidden">
      {block.language && (
        <div className="bg-[#1a1a1a] px-4 py-1.5 text-[10px] text-[#888] uppercase tracking-wider border-b border-[#333]">
          {block.language}
        </div>
      )}
      <pre className="bg-[#1a1a1a] p-4 overflow-x-auto">
        <code className="text-xs text-[#d4d4d4] font-mono leading-relaxed">{block.text}</code>
      </pre>
    </div>
  );
}

function BookmarkBlock({ block }: { readonly block: BlueprintBlock }) {
  const url = block.url ?? block.text ?? "";
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-3 p-3 my-1 rounded-lg border border-[#333] bg-[#1e1e1e] hover:bg-[#252525] transition-colors"
    >
      <span className="material-symbols-outlined text-[#888] text-sm">link</span>
      <span className="text-sm text-[#adc6ff] truncate">{block.text ?? url}</span>
      <span className="material-symbols-outlined text-[#555] text-xs ml-auto">open_in_new</span>
    </a>
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
            <BlockRenderer key={bi} block={childBlock} databases={databases} index={bi + 1} />
          ))}
        </div>
      ))}
    </div>
  );
}

// ============================================================
// Database renderer with multiple view types
// ============================================================

function resolvePropertyType(spec: unknown): { type: string; options?: ReadonlyArray<{ name: string; color?: string }> } {
  if (typeof spec === "string") return { type: spec };
  if (typeof spec === "object" && spec !== null) {
    const obj = spec as Record<string, unknown>;
    return {
      type: (obj.type as string) ?? "text",
      options: obj.options as ReadonlyArray<{ name: string; color?: string }> | undefined,
    };
  }
  return { type: "text" };
}

function findOptionColor(propSpec: unknown, value: string): string | undefined {
  if (typeof propSpec !== "object" || propSpec === null) return undefined;
  const obj = propSpec as Record<string, unknown>;
  const options = obj.options as ReadonlyArray<{ name: string; color?: string }> | undefined;
  return options?.find((o) => o.name === value)?.color;
}

const VIEW_ICON_MAP: Record<string, string> = {
  table: "table_rows",
  calendar: "calendar_month",
  board: "view_kanban",
  gallery: "grid_view",
  timeline: "timeline",
  list: "list",
};

function DatabaseRenderer({ db }: { readonly db: BlueprintDatabase }) {
  const properties = db.properties ?? {};
  const views = db.views ?? [];
  const sampleItems = db.sample_items ?? [];
  const [activeView, setActiveView] = useState(0);

  const propEntries = Object.entries(properties);
  const titlePropName = propEntries.find(([, spec]) => resolvePropertyType(spec).type === "title")?.[0];
  const displayProps = propEntries.filter(([name]) => name !== titlePropName);

  const currentViewType = views[activeView]?.type ?? "table";

  return (
    <div className="my-4">
      {/* Database title bar */}
      <div className="flex items-center gap-2 mb-2 px-1">
        <span className="material-symbols-outlined text-[#adc6ff] text-base">database</span>
        <span className="text-sm font-semibold text-white">{db.title ?? "Database"}</span>
        <span className="text-xs text-[#666] ml-auto">{sampleItems.length} items</span>
      </div>

      {/* View tabs */}
      {views.length > 0 && (
        <div className="flex items-center gap-1 border-b border-[#333] mb-0 px-1">
          {views.map((view, vi) => {
            const viewType = view.type ?? "table";
            const icon = VIEW_ICON_MAP[viewType] ?? "table_rows";
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
                <span className="material-symbols-outlined text-[12px]">{icon}</span>
                <span className="capitalize">{view.title ?? view.name ?? viewType}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* View content */}
      {currentViewType === "board" ? (
        <BoardView db={db} titlePropName={titlePropName} displayProps={displayProps} />
      ) : currentViewType === "calendar" ? (
        <CalendarView db={db} titlePropName={titlePropName} />
      ) : currentViewType === "gallery" ? (
        <GalleryView db={db} titlePropName={titlePropName} displayProps={displayProps} />
      ) : (
        <TableView db={db} titlePropName={titlePropName} displayProps={displayProps} />
      )}
    </div>
  );
}

function TableView({
  db,
  titlePropName,
  displayProps,
}: {
  readonly db: BlueprintDatabase;
  readonly titlePropName?: string;
  readonly displayProps: [string, unknown][];
}) {
  const properties = db.properties ?? {};
  const sampleItems = db.sample_items ?? [];

  return (
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
              <th key={name} className="text-left px-3 py-2.5 text-[#999] font-medium border-r border-[#333] last:border-r-0 min-w-[100px]">
                {name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sampleItems.slice(0, 8).map((row, ri) => (
            <tr key={ri} className="border-t border-[#2a2a2a] hover:bg-[#1a1a1a] transition-colors">
              {titlePropName && (
                <td className="px-3 py-2 border-r border-[#2a2a2a] font-medium text-white">
                  <div className="flex items-center gap-1.5">
                    {row["icon"] ? <span className="text-sm">{String(row["icon"])}</span> : null}
                    <span>{String(row[titlePropName] ?? "")}</span>
                  </div>
                </td>
              )}
              {displayProps.map(([name, spec]) => (
                <td key={name} className="px-3 py-2 border-r border-[#2a2a2a] last:border-r-0">
                  <CellValue value={row[name]} propType={resolvePropertyType(spec).type} propSpec={properties[name]} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function BoardView({
  db,
  titlePropName,
  displayProps,
}: {
  readonly db: BlueprintDatabase;
  readonly titlePropName?: string;
  readonly displayProps: [string, unknown][];
}) {
  const sampleItems = db.sample_items ?? [];
  const properties = db.properties ?? {};

  // Find status/select property to group by
  const groupProp = displayProps.find(([, spec]) => {
    const t = resolvePropertyType(spec).type;
    return t === "status" || t === "select";
  });
  const groupPropName = groupProp?.[0];
  const groupPropSpec = groupProp?.[1];

  if (!groupPropName) {
    return <TableView db={db} titlePropName={titlePropName} displayProps={displayProps} />;
  }

  // Get groups from options or from data
  const resolved = resolvePropertyType(groupPropSpec);
  const groupNames = resolved.options?.map((o) => o.name)
    ?? [...new Set(sampleItems.map((r) => String(r[groupPropName] ?? "")).filter(Boolean))];

  return (
    <div className="flex gap-3 overflow-x-auto p-3 border border-[#333] border-t-0 rounded-b-lg bg-[#161616]">
      {groupNames.map((group) => {
        const items = sampleItems.filter((r) => String(r[groupPropName] ?? "") === group);
        const optionColor = findOptionColor(groupPropSpec, group);
        return (
          <div key={group} className="min-w-[200px] flex-shrink-0">
            <div className="flex items-center gap-2 mb-2 px-1">
              <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${getSelectColor(optionColor)}`}>
                {group}
              </span>
              <span className="text-[10px] text-[#666]">{items.length}</span>
            </div>
            <div className="space-y-2">
              {items.map((row, i) => (
                <div key={i} className="bg-[#1e1e1e] rounded-lg p-3 border border-[#2a2a2a] hover:border-[#444] transition-colors">
                  <div className="flex items-center gap-1.5 mb-1">
                    {row["icon"] ? <span className="text-sm">{String(row["icon"])}</span> : null}
                    <span className="text-xs font-medium text-white truncate">
                      {titlePropName ? String(row[titlePropName] ?? "") : "Untitled"}
                    </span>
                  </div>
                  {displayProps.slice(0, 2).map(([name, spec]) => {
                    if (name === groupPropName) return null;
                    const val = row[name];
                    if (val === null || val === undefined) return null;
                    return (
                      <div key={name} className="text-[10px] text-[#888] mt-1">
                        <CellValue value={val} propType={resolvePropertyType(spec).type} propSpec={properties[name]} />
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CalendarView({
  db,
  titlePropName,
}: {
  readonly db: BlueprintDatabase;
  readonly titlePropName?: string;
}) {
  const sampleItems = db.sample_items ?? [];
  const properties = db.properties ?? {};

  // Find date property
  const datePropName = Object.entries(properties).find(([, spec]) => resolvePropertyType(spec).type === "date")?.[0];

  if (!datePropName) {
    return (
      <div className="border border-[#333] border-t-0 rounded-b-lg p-6 text-center text-xs text-[#666]">
        No date property found for calendar view
      </div>
    );
  }

  // Build a simple month grid
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const monthName = today.toLocaleString("en-US", { month: "long", year: "numeric" });

  // Map items to days
  const dayItems: Record<number, Array<Record<string, unknown>>> = {};
  for (const item of sampleItems) {
    const dateVal = item[datePropName];
    if (!dateVal) continue;
    const d = new Date(String(dateVal));
    if (d.getMonth() === month && d.getFullYear() === year) {
      const day = d.getDate();
      if (!dayItems[day]) dayItems[day] = [];
      dayItems[day].push(item);
    }
  }

  const cells: (number | null)[] = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);

  return (
    <div className="border border-[#333] border-t-0 rounded-b-lg overflow-hidden">
      <div className="bg-[#1e1e1e] px-3 py-2 text-xs text-[#999] font-medium">
        {monthName}
      </div>
      <div className="grid grid-cols-7">
        {DAYS.map((d) => (
          <div key={d} className="px-1 py-1.5 text-center text-[10px] text-[#666] bg-[#1a1a1a] border-b border-[#333]">
            {d}
          </div>
        ))}
        {cells.map((day, i) => (
          <div
            key={i}
            className={`min-h-[60px] p-1 border-b border-r border-[#2a2a2a] ${
              day === today.getDate() ? "bg-blue-900/10" : ""
            }`}
          >
            {day && (
              <>
                <span className={`text-[10px] ${day === today.getDate() ? "text-blue-400 font-bold" : "text-[#888]"}`}>
                  {day}
                </span>
                {dayItems[day]?.slice(0, 2).map((item, ii) => (
                  <div key={ii} className="mt-0.5 px-1 py-0.5 rounded bg-blue-900/30 text-[9px] text-blue-300 truncate">
                    {item["icon"] ? `${String(item["icon"])} ` : ""}
                    {titlePropName ? String(item[titlePropName] ?? "") : ""}
                  </div>
                ))}
                {(dayItems[day]?.length ?? 0) > 2 && (
                  <span className="text-[9px] text-[#666]">+{(dayItems[day]?.length ?? 0) - 2}</span>
                )}
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function GalleryView({
  db,
  titlePropName,
  displayProps,
}: {
  readonly db: BlueprintDatabase;
  readonly titlePropName?: string;
  readonly displayProps: [string, unknown][];
}) {
  const sampleItems = db.sample_items ?? [];
  const properties = db.properties ?? {};

  return (
    <div className="grid grid-cols-3 gap-2 p-3 border border-[#333] border-t-0 rounded-b-lg bg-[#161616]">
      {sampleItems.slice(0, 9).map((row, i) => (
        <div key={i} className="bg-[#1e1e1e] rounded-lg overflow-hidden border border-[#2a2a2a] hover:border-[#444] transition-colors">
          <div className="h-20 bg-gradient-to-br from-[#252525] to-[#1a1a1a] flex items-center justify-center">
            <span className="text-3xl">{row["icon"] ? String(row["icon"]) : "📄"}</span>
          </div>
          <div className="p-3">
            <p className="text-xs font-medium text-white truncate mb-1">
              {titlePropName ? String(row[titlePropName] ?? "") : "Untitled"}
            </p>
            {displayProps.slice(0, 2).map(([name, spec]) => {
              const val = row[name];
              if (val === null || val === undefined) return null;
              return (
                <div key={name} className="text-[10px] text-[#888] mt-0.5">
                  <CellValue value={val} propType={resolvePropertyType(spec).type} propSpec={properties[name]} />
                </div>
              );
            })}
          </div>
        </div>
      ))}
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
    return (
      <span className={`inline-flex items-center justify-center w-4 h-4 rounded-sm border ${value ? "bg-blue-500 border-blue-500" : "border-[#555]"}`}>
        {value && (
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M2 5L4 7L8 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}
      </span>
    );
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
    const strVal = String(value).toLowerCase();
    const statusStyle = STATUS_COLOR_MAP[strVal] ?? STATUS_COLOR_MAP[String(value)] ?? { dot: "bg-gray-400", text: "text-gray-400" };
    return (
      <div className="flex items-center gap-1.5">
        <span className={`w-2 h-2 rounded-full ${statusStyle.dot} flex-shrink-0`} />
        <span className={`${statusStyle.text}`}>{String(value)}</span>
      </div>
    );
  }

  if (propType === "date") {
    return <span className="text-[#999] tabular-nums">{String(value)}</span>;
  }

  if (propType === "number") {
    return <span className="text-[#d4d4d4] tabular-nums">{String(value)}</span>;
  }

  if (propType === "url") {
    return (
      <a href={String(value)} target="_blank" rel="noopener noreferrer" className="text-[#adc6ff] hover:underline truncate block max-w-[120px]">
        {String(value)}
      </a>
    );
  }

  if (propType === "email") {
    return <span className="text-[#adc6ff]">{String(value)}</span>;
  }

  return <span className="text-[#d4d4d4]">{String(value)}</span>;
}

// ============================================================
// Block dispatcher
// ============================================================

let numberedListCounter = 0;

function BlockRenderer({
  block,
  databases,
}: {
  readonly block: BlueprintBlock;
  readonly databases: ReadonlyArray<BlueprintDatabase>;
  readonly index: number;
}) {
  switch (block.type) {
    case "callout":
      return <CalloutBlock block={block} />;
    case "heading_1":
      return <Heading1Block block={block} />;
    case "heading_2":
      return <Heading2Block block={block} />;
    case "divider":
      numberedListCounter = 0;
      return <DividerBlock />;
    case "to_do":
      return <TodoBlock block={block} />;
    case "toggle":
      return <ToggleBlock block={block} />;
    case "paragraph":
      return <ParagraphBlock block={block} />;
    case "bulleted_list":
      return <BulletedListBlock block={block} />;
    case "numbered_list":
      numberedListCounter++;
      return <NumberedListBlock block={block} index={numberedListCounter} />;
    case "quote":
      return <QuoteBlock block={block} />;
    case "code":
      return <CodeBlock block={block} />;
    case "bookmark":
      return <BookmarkBlock block={block} />;
    case "column_list":
      return <ColumnListBlock block={block} databases={databases} />;
    case "database_ref": {
      const dbIdx = block.db_index ?? 0;
      const db = databases[dbIdx];
      if (!db) return null;
      return <DatabaseRenderer db={db} />;
    }
    default:
      if (block.text) {
        return <ParagraphBlock block={block} />;
      }
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

  // Reset counter for each render
  numberedListCounter = 0;

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
            <BlockRenderer key={idx} block={block} databases={databases} index={idx + 1} />
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
