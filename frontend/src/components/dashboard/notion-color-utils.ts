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

export const STATUS_COLOR_MAP: Record<string, { dot: string; text: string }> = {
  "시작 전": { dot: "bg-gray-400", text: "text-gray-400" },
  "not started": { dot: "bg-gray-400", text: "text-gray-400" },
  "진행 중": { dot: "bg-blue-400", text: "text-blue-400" },
  "in progress": { dot: "bg-blue-400", text: "text-blue-400" },
  "완료": { dot: "bg-green-400", text: "text-green-400" },
  "done": { dot: "bg-green-400", text: "text-green-400" },
  "complete": { dot: "bg-green-400", text: "text-green-400" },
};

export const VIEW_ICON_MAP: Record<string, string> = {
  table: "table_rows",
  calendar: "calendar_month",
  board: "view_kanban",
  gallery: "grid_view",
  timeline: "timeline",
  list: "list",
};

export function getCalloutBg(color?: string): string {
  if (!color) return COLOR_BG_MAP["default"] ?? "";
  return COLOR_BG_MAP[color] ?? COLOR_BG_MAP["default"] ?? "";
}

export function getHeadingColor(color?: string): string {
  if (!color) return "";
  return HEADING_COLOR_MAP[color] ?? "";
}

export function getSelectColor(color?: string): string {
  if (!color) return SELECT_COLOR_MAP["default"] ?? "";
  return SELECT_COLOR_MAP[color] ?? SELECT_COLOR_MAP["default"] ?? "";
}

export function resolvePropertyType(spec: unknown): { type: string; options?: ReadonlyArray<{ name: string; color?: string }> } {
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

export function findOptionColor(propSpec: unknown, value: string): string | undefined {
  if (typeof propSpec !== "object" || propSpec === null) return undefined;
  const obj = propSpec as Record<string, unknown>;
  const options = obj.options as ReadonlyArray<{ name: string; color?: string }> | undefined;
  return options?.find((o) => o.name === value)?.color;
}
