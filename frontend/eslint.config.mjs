import parser from '@typescript-eslint/parser';
import typescript from '@typescript-eslint/eslint-plugin';
import react from 'eslint-plugin-react';
import hooks from 'eslint-plugin-react-hooks';

export default [
 {ignores:['.next/**','node_modules/**','next-env.d.ts']},
 {files:['**/*.ts','**/*.tsx'],languageOptions:{parser,parserOptions:{ecmaVersion:'latest',sourceType:'module',ecmaFeatures:{jsx:true}}},
  plugins:{'@typescript-eslint':typescript,react,'react-hooks':hooks},settings:{react:{version:'detect'}},
  rules:{...typescript.configs.recommended.rules,...hooks.configs.recommended.rules,
   'react/jsx-key':'error','react/jsx-no-target-blank':'error','react/no-danger':'error',
  }},
];
