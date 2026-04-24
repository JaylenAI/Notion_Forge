import { useState } from "react";
import type { BlueprintDatabase } from "./notion-renderer.types";
import {
  VIEW_ICON_MAP,
  STATUS_COLOR_MAP,
  getSelectColor,
  resolvePropertyType,
  findOptionColor,
} from "./notion-color-utils";

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

  const groupProp = displayProps.find(([, spec]) => {
    const t = resolvePropertyType(spec).type;
    return t === "status" || t === "select";
  });
  const groupPropName = groupProp?.[0];
  const groupPropSpec = groupProp?.[1];

  if (!groupPropName) {
    return <TableView db={db} titlePropName={titlePropName} displayProps={displayProps} />;
  }

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

  const datePropName = Object.entries(properties).find(([, spec]) => resolvePropertyType(spec).type === "date")?.[0];

  if (!datePropName) {
    return (
      <div className="border border-[#333] border-t-0 rounded-b-lg p-6 text-center text-xs text-[#666]">
        No date property found for calendar view
      </div>
    );
  }

  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const monthName = today.toLocaleString("en-US", { month: "long", year: "numeric" });

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

export default function DatabaseRenderer({ db }: { readonly db: BlueprintDatabase }) {
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
      <div className="flex items-center gap-2 mb-2 px-1">
        <span className="material-symbols-outlined text-[#adc6ff] text-base">database</span>
        <span className="text-sm font-semibold text-white">{db.title ?? "Database"}</span>
        <span className="text-xs text-[#666] ml-auto">{sampleItems.length} items</span>
      </div>

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
