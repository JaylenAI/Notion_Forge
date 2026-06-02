// 판매 품질 신호 표시 (Phase 2) — 백엔드 metadata의 premium_*·listing_kit를 시각화.
// 엔진이 만든 유료급 가치를 사용자에게 보이게 한다(도착해도 렌더 0이던 갭 해소).

interface ListingKitView {
  readonly tagline?: string;
  readonly features?: ReadonlyArray<string>;
  readonly suggested_price_band?: string;
}

export interface QualityMetadata {
  readonly premium_score?: number;
  readonly premium_band?: string;
  readonly premium_band_label?: string;
  readonly premium_ready?: boolean;
  readonly listing_kit?: ListingKitView;
}

// 가격 밴드 → 표시 색 (순수 함수, 테스트 대상)
export function bandTone(band?: string): string {
  switch (band) {
    case "$100+":
      return "#ffd166"; // gold (플래그십)
    case "$50-99":
      return "#4edea3"; // green (프리미엄)
    case "$20-49":
      return "#adc6ff"; // blue (판매 가능)
    case "$5-15":
      return "#c2c6d8"; // gray-blue (심플)
    default:
      return "#8a8a8a"; // $0 / 미상
  }
}

function QualityPanel({ metadata }: { readonly metadata?: QualityMetadata }) {
  if (!metadata || typeof metadata.premium_score !== "number") return null;

  const score = Math.round(metadata.premium_score);
  const band = metadata.premium_band ?? "";
  const ready = metadata.premium_ready === true;
  const tone = bandTone(band);
  const kit = metadata.listing_kit;

  return (
    <div className="bg-[#1e1e1e] rounded-2xl p-5 border border-[#333]">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-sm" style={{ color: tone }}>
            verified
          </span>
          <span className="text-sm font-bold text-white">판매 품질</span>
        </div>
        <div className="flex items-center gap-2">
          {band && (
            <span
              className="px-2.5 py-1 rounded-lg text-xs font-bold"
              style={{ color: tone, border: `1px solid ${tone}`, backgroundColor: `${tone}1a` }}
            >
              {band}
              {metadata.premium_band_label ? ` · ${metadata.premium_band_label}` : ""}
            </span>
          )}
          <span
            className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${
              ready
                ? "text-[#4edea3] border-[#4edea3]/40 bg-[#4edea3]/10"
                : "text-[#ffb4ab] border-[#ffb4ab]/40 bg-[#ffb4ab]/10"
            }`}
          >
            {ready ? "판매 준비 완료" : "기준 미달"}
          </span>
        </div>
      </div>

      {/* 유료급 점수 바 */}
      <div className="mt-3">
        <div className="flex justify-between text-[10px] text-gray-500 mb-1">
          <span>유료급 점수</span>
          <span>{score}/100</span>
        </div>
        <div className="h-1.5 rounded-full bg-[#2a2a2a] overflow-hidden">
          <div className="h-full rounded-full" style={{ width: `${score}%`, backgroundColor: tone }} />
        </div>
      </div>

      {/* 리스팅 초안 */}
      {kit && (kit.tagline || (kit.features && kit.features.length > 0)) && (
        <div className="mt-4 pt-4 border-t border-[#333]">
          <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">
            리스팅 초안{kit.suggested_price_band ? ` · 추천가 ${kit.suggested_price_band}` : ""}
          </div>
          {kit.tagline && <p className="text-sm text-gray-300 mb-2">{kit.tagline}</p>}
          {kit.features && kit.features.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {kit.features.slice(0, 5).map((f) => (
                <span
                  key={f}
                  className="px-2 py-0.5 rounded bg-[#252525] text-[10px] text-[#c2c6d8] border border-[#333]"
                >
                  {f}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default QualityPanel;
