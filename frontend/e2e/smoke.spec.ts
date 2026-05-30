import { expect, test } from "@playwright/test";

test.describe("스모크 — 앱 로드", () => {
  test("홈이 렌더되고 NotionForge 브랜딩이 보인다", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/NotionForge/);
    // 레이아웃 헤딩은 백엔드 없이도 즉시 렌더됨
    await expect(page.getByText("NotionForge").first()).toBeVisible();
  });

  test("크리티컬 JS 에러 없이 로드된다", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");
    expect(errors).toEqual([]);
  });
});
