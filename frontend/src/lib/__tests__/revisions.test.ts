import { describe, expect, it } from "vitest";
import { extractRevisions } from "../revisions";

describe("extractRevisions (Phase 4 — 버전 히스토리)", () => {
  it("blueprint 메시지만 리비전으로 추출하고 순서·라벨 부여", () => {
    const messages = [
      {},
      { metadata: { blueprint: { metadata: { title: "CRM v1" } } } },
      { metadata: {} },
      { metadata: { blueprint: { metadata: { title: "CRM v2" } } } },
    ];
    const revs = extractRevisions(messages);
    expect(revs.length).toBe(2);
    expect(revs[0]?.label).toBe("CRM v1");
    expect(revs[1]?.label).toBe("CRM v2");
    expect(revs[0]?.index).toBe(0);
    expect(revs[1]?.index).toBe(1);
  });

  it("title 없으면 '버전 N' 라벨", () => {
    const revs = extractRevisions([{ metadata: { blueprint: {} } }, { metadata: { blueprint: { metadata: {} } } }]);
    expect(revs[0]?.label).toBe("버전 1");
    expect(revs[1]?.label).toBe("버전 2");
  });

  it("blueprint 없으면 빈 배열", () => {
    expect(extractRevisions([{}, { metadata: {} }])).toEqual([]);
  });
});
