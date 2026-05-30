import { describe, expect, it } from "vitest";

import { cn } from "../utils";
import { timeAgo } from "../timeago";

describe("cn", () => {
  it("falsy 값을 걸러내고 공백으로 합친다", () => {
    expect(cn("a", "b")).toBe("a b");
    expect(cn("a", false, undefined, "b")).toBe("a b");
    expect(cn()).toBe("");
  });
});

describe("timeAgo", () => {
  it("5초 미만은 '방금 전'", () => {
    expect(timeAgo(new Date())).toBe("방금 전");
  });

  it("분/시간/일 단위를 한국어로 표기", () => {
    const now = Date.now();
    expect(timeAgo(new Date(now - 120 * 1000))).toBe("2분 전");
    expect(timeAgo(new Date(now - 3 * 3600 * 1000))).toBe("3시간 전");
    expect(timeAgo(new Date(now - 2 * 86400 * 1000))).toBe("2일 전");
  });

  it("문자열 날짜도 처리", () => {
    const iso = new Date(Date.now() - 60 * 1000).toISOString();
    expect(timeAgo(iso)).toBe("1분 전");
  });
});
