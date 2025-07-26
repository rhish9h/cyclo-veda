# Cyclo Veda Frontend

A modern, maintainable React TypeScript application built with clean code principles and best practices for long-term maintainability.

## 🏗️ Architecture Overview

This frontend is designed with maintainability as the top priority, following clean code principles and industry best practices:

- **Clean Architecture**: Separation of concerns with clear boundaries
- **Type Safety**: Full TypeScript coverage with strict configuration
- **Error Handling**: Centralized error management system
- **Code Quality**: ESLint + Prettier with strict rules
- **Developer Experience**: VSCode workspace settings and extensions

## 📁 Project Structure

])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
