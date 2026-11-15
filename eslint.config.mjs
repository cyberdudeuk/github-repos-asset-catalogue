// JavaScript linter (OpenSSF warnings criterion; secure development standing rule, 15 Nov 2026).
// CI installs the pinned versions below and runs `npx eslint .`, which fails on any finding.
// eslint@9.39.5, @eslint/js@9.39.5, globals@16.5.0
import js from "@eslint/js";
import globals from "globals";

export default [
  {ignores: ["node_modules/**", "**/vendor/**", "**/*.min.js", "dist/**"]},
  js.configs.recommended,
  {files: ["**/*.js", "**/*.cjs"], languageOptions: {ecmaVersion: 2024, sourceType: "script", globals: {...globals.browser}}},
  {files: ["**/*.mjs"], languageOptions: {ecmaVersion: 2024, sourceType: "module", globals: {...globals.node}}},
  // Node test harnesses (jsdom, Playwright), run with node in the private companion build.
  {files: ["build/jt/**/*.js"], languageOptions: {sourceType: "commonjs", globals: {...globals.node, ...globals.browser}}},
];
