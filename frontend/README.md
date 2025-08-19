# Cyclo Veda Frontend

> Modern React TypeScript application with authentication, routing, and responsive design.

[![React 19+](https://img.shields.io/badge/react-19+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.8+-green.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/vite-7.0+-purple.svg)](https://vitejs.dev/)

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Application Available:** http://localhost:5173  
**Backend API:** http://localhost:8000

## 🛠️ Development Scripts

```bash
# Development
npm run dev              # Start dev server with hot reload
npm run build            # Build for production
npm run preview          # Preview production build

# Code Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix ESLint issues
npm run format           # Format code with Prettier
npm run format:check     # Check code formatting
npm run type-check       # TypeScript type checking
npm run check-all        # Run all checks (type, lint, format)

# Maintenance
npm run clean            # Clean build artifacts
```

## 📁 Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Page components
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API services
│   ├── types/          # TypeScript type definitions
│   ├── utils/          # Utility functions
│   ├── constants/      # Application constants
│   ├── App.tsx         # Main application component
│   └── main.tsx        # Application entry point
├── index.html          # HTML template
├── package.json        # Dependencies & scripts
├── vite.config.ts      # Vite configuration
└── tsconfig.json       # TypeScript configuration
```

## 🔧 Environment Setup

Create `.env` file:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Optional: Enable development features
VITE_DEV_MODE=true
```

## 🏗️ Architecture

- **React 19**: Latest React with concurrent features
- **TypeScript**: Full type safety with strict configuration
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **ESLint + Prettier**: Code quality and formatting
- **Responsive Design**: Mobile-first approach

## 🔐 Authentication

The frontend integrates with the backend JWT authentication system:

- Login/logout functionality
- Protected routes
- Automatic token refresh
- Persistent authentication state

## 🎨 Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: React and TypeScript rules
- **Prettier**: Consistent code formatting
- **File Naming**: kebab-case for files, PascalCase for components

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines and coding standards.

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.
