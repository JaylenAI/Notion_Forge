import { describe, expect, it } from "vitest";
import { bandTone } from "../QualityPanel";

describe("bandTone (Phase 2 — 품질 밴드 색)", () => {
  it("알려진 밴드를 구분되는 색으로 매핑", () => {
    expect(bandTone("$100+")).toBe("#ffd166");
    expect(bandTone("$50-99")).toBe("#4edea3");
    expect(bandTone("$20-49")).toBe("#adc6ff");
    expect(bandTone("$5-15")).toBe("#c2c6d8");
  });

  it("미상/미지정은 폴백 색", () => {
    expect(bandTone(undefined)).toBe("#8a8a8a");
    expect(bandTone("$0")).toBe("#8a8a8a");
    expect(bandTone("weird")).toBe("#8a8a8a");
  });
});
