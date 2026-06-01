import { expect, test } from "@playwright/test";

/**
 * Approval Gate E2E — 실제 제품 UI(DashboardPage → ChatPanel)에서
 * 프롬프트 입력 → 승인 버튼 클릭 → 실제 Notion 생성 완료까지 검증한다.
 * 백엔드(9500)가 실행 중이고 .env에 Notion 키가 있어야 통과한다.
 */
test("프롬프트 → 승인 → Notion 생성 완료 (실제 제품 흐름)", async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors: string[] = [];
  page.on("console", (m) => {
    if (m.type() === "error") consoleErrors.push(m.text());
  });
  await page.goto("/");

  const textarea = page.getByPlaceholder("Describe the template you want to create...");
  await expect(textarea).toBeVisible({ timeout: 15_000 });
  await textarea.fill("간단한 할일 관리 트래커 만들어줘");
  await textarea.press("Enter");

  // 승인 버튼이 떠야 한다
  const approveBtn = page.getByRole("button", { name: /생성하기/ });
  await expect(approveBtn).toBeVisible({ timeout: 90_000 });
  await approveBtn.click();

  // 승인 후 실제 Notion 생성 완료 → "Open in Notion" 링크 (메시지+프리뷰 패널 2곳)
  const notionLink = page.getByRole("link", { name: /Open in Notion/ }).first();
  await expect(notionLink).toBeVisible({ timeout: 120_000 });
  const href = await notionLink.getAttribute("href");
  expect(href).toContain("notion.so");
  console.log("생성된 Notion URL:", href);
});
