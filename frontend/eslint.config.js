import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  // 빌드 산출물·테스트 리포트는 린트 대상에서 제외
  { ignores: ["dist", "playwright-report", "test-results", "coverage", "node_modules"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
);
