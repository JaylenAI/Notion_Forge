import { useState, useCallback } from "react";
import type { BlueprintBlock, BlueprintDatabase } from "./notion-renderer.types";
import { getCalloutBg, getHeadingColor } from "./notion-color-utils";
import DatabaseRenderer from "./NotionDatabaseRenderer";

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
      {columns.map((col, ci) => {
        const colBlocks: readonly BlueprintBlock[] = Array.isArray(col) ? col : (col?.blocks ?? []);
        return (
          <div key={ci} className="flex-1 min-w-0">
            {colBlocks.map((childBlock, bi) => (
              <BlockRenderer key={bi} block={childBlock} databases={databases} index={bi + 1} />
            ))}
          </div>
        );
      })}
    </div>
  );
}

let numberedListCounter = 0;

export function resetNumberedListCounter() {
  numberedListCounter = 0;
}

export default function BlockRenderer({
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
