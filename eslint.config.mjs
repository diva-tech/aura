import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [
      "**/dist/**",
      "**/dist-electron/**",
      "**/node_modules/**",
      "**/.vite/**"
    ]
  },
  js.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  {
    files: ["apps/desktop/src/**/*.{ts,tsx}"],
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname
      },
      globals: {
        ...globals.browser,
        ...globals.node
      }
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true }
      ]
    }
  },
  {
    files: [
      "apps/desktop/electron/*.ts",
      "apps/desktop/vite.config.ts",
      "apps/desktop/tailwind.config.ts",
      "apps/desktop/vitest.config.ts",
      "apps/desktop/playwright.config.ts"
    ],
    languageOptions: {
      parserOptions: {
        projectService: false,
        project: "./apps/desktop/tsconfig.eslint.json",
        tsconfigRootDir: import.meta.dirname
      }
    }
  },
  {
    files: ["packages/shared/src/**/*.{ts,tsx}"],
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname
      },
      globals: {
        ...globals.node
      }
    }
  }
);
