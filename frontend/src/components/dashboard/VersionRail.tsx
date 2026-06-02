// 버전 히스토리 레일 (Phase 4/B2) — 세션 내 blueprint 리비전을 칩으로 표시, 클릭해 이전 버전 열람.
import type { Revision } from "../../lib/revisions";

interface VersionRailProps {
  readonly revisions: ReadonlyArray<Revision>;
  readonly selected: number;
  readonly onSelect: (index: number) => void;
}

function VersionRail({ revisions, selected, onSelect }: VersionRailProps) {
  if (revisions.length < 2) return null;

  return (
    <div className="bg-[#1e1e1e] rounded-2xl p-3 border border-[#333] flex items-center gap-2 flex-wrap">
      <span className="material-symbols-outlined text-sm text-[#adc6ff]">history</span>
      <span className="text-xs font-bold text-white mr-1">버전 히스토리</span>
      {revisions.map((r, i) => {
        const isLatest = i === revisions.length - 1;
        const active = i === selected;
        return (
          <button
            key={r.index}
            type="button"
            onClick={() => onSelect(i)}
            title={r.label}
            className={`px-2.5 py-1 rounded-lg text-[11px] border transition-colors max-w-[160px] truncate ${
              active
                ? "border-[#adc6ff] text-[#adc6ff] bg-[#adc6ff]/10"
                : "border-[#333] text-gray-400 hover:bg-[#2a2a2a]"
            }`}
          >
            v{i + 1}
            {isLatest ? " · 최신" : ""}
          </button>
        );
      })}
      {selected !== revisions.length - 1 && (
        <span className="text-[10px] text-[#ffb59a] ml-1">← 이전 버전 보는 중</span>
      )}
    </div>
  );
}

export default VersionRail;
