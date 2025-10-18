import { createRequire } from "module";
import path, { dirname } from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const nextPackagePath = require.resolve("eslint-config-next/package.json");
const nextNodeModules = path.join(path.dirname(nextPackagePath), "..");

const resolveFromNext = (specifier) =>
  require.resolve(specifier, { paths: [nextNodeModules] });

const globals = require("globals");
const reactPlugin = require(resolveFromNext("eslint-plugin-react"));
const reactHooksPlugin = require(resolveFromNext("eslint-plugin-react-hooks"));
const jsxA11yPlugin = require(resolveFromNext("eslint-plugin-jsx-a11y"));
const importPlugin = require(resolveFromNext("eslint-plugin-import"));
const tsPlugin = require(resolveFromNext("@typescript-eslint/eslint-plugin"));
const tsParser = require(resolveFromNext("@typescript-eslint/parser"));
const nextPlugin = require(resolveFromNext("@next/eslint-plugin-next"));
const nextParser = require(require.resolve("eslint-config-next/parser.js"));

const baseRules = {
  ...reactPlugin.configs.recommended?.rules,
  ...reactHooksPlugin.configs.recommended?.rules,
  ...jsxA11yPlugin.configs.recommended?.rules,
  ...importPlugin.configs.recommended?.rules,
  ...nextPlugin.configs?.recommended?.rules,
  ...nextPlugin.configs?.["core-web-vitals"]?.rules,
  "import/no-anonymous-default-export": "warn",
  "react/no-unknown-property": "off",
  "react/react-in-jsx-scope": "off",
  "react/prop-types": "off",
  "jsx-a11y/alt-text": [
    "warn",
    {
      elements: ["img"],
      img: ["Image"],
    },
  ],
  "jsx-a11y/aria-props": "warn",
  "jsx-a11y/aria-proptypes": "warn",
  "jsx-a11y/aria-unsupported-elements": "warn",
  "jsx-a11y/role-has-required-aria-props": "warn",
  "jsx-a11y/role-supports-aria-props": "warn",
  "react/jsx-no-target-blank": "off",
};

const tsRecommendedRules = tsPlugin.configs.recommended?.rules ?? {};

export default [
  {
    ignores: ["node_modules/**", ".next/**", "out/**", "build/**", "next-env.d.ts"],
  },
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    plugins: {
      "@next/next": nextPlugin,
      import: importPlugin,
      "jsx-a11y": jsxA11yPlugin,
      react: reactPlugin,
      "react-hooks": reactHooksPlugin,
    },
    languageOptions: {
      parser: nextParser,
      parserOptions: {
        requireConfigFile: false,
        sourceType: "module",
        allowImportExportEverywhere: true,
        babelOptions: {
          presets: ["next/babel"],
          caller: {
            supportsTopLevelAwait: true,
          },
        },
      },
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    settings: {
      react: {
        version: "detect",
      },
      next: {
        rootDir: __dirname,
      },
      "import/parsers": {
        [resolveFromNext("@typescript-eslint/parser")]: [
          ".ts",
          ".mts",
          ".cts",
          ".tsx",
          ".d.ts",
        ],
      },
      "import/resolver": {
        [resolveFromNext("eslint-import-resolver-node")]: {
          extensions: [".js", ".jsx", ".ts", ".tsx"],
        },
        [resolveFromNext("eslint-import-resolver-typescript")]: {
          alwaysTryTypes: true,
        },
      },
    },
    rules: baseRules,
  },
  {
    files: ["**/*.{ts,tsx}"],
    plugins: {
      "@typescript-eslint": tsPlugin,
    },
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: "module",
        projectService: true,
        tsconfigRootDir: __dirname,
      },
    },
    rules: tsRecommendedRules,
  },
];
