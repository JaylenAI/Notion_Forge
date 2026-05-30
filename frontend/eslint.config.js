import js from "@eslint/js";
import jsxA11y from "eslint-plugin-jsx-a11y";
import tseslint from "typescript-eslint";

export default tseslint.config(
  // 빌드 산출물·테스트 리포트는 린트 대상에서 제외
  { ignores: ["dist", "playwright-report", "test-results", "coverage", "node_modules"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  jsxA11y.flatConfigs.recommended,
  // 접근성 규칙은 빌드를 막지 않도록 warn으로 (점진 개선 — 회귀 방지용 가시화)
  {
    files: ["**/*.{jsx,tsx}"],
    rules: Object.fromEntries(
      Object.keys(jsxA11y.flatConfigs.recommended.rules || {}).map((r) => [r, "warn"]),
    ),
  },
);
