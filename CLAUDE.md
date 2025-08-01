# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Connet.AI** - an AI collaboration platform that enables human-AI cooperation and multi-agent autonomous collaboration for complex task completion. The project focuses on creating a social-media-like interface for AI agent interaction through @ mentions, with future development towards autonomous AI task planning and execution.

## Common Development Commands

### Frontend (Next.js)
```bash
cd frontend
pnpm dev          # Start development server (localhost:3000)
pnpm build        # Build for production
pnpm start        # Start production server
pnpm lint         # Run ESLint
```

### Testing
- Frontend uses Jest and React Testing Library (setup needs to be verified)
- Backend uses Pytest (backend not yet implemented)

## Architecture Overview

### Tech Stack
- **Frontend**: Next.js 15.3.2 with App Router, TypeScript, Tailwind CSS, shadcn/ui
- **Package Manager**: pnpm (not npm)
- **State Management**: Zustand
- **Authentication**: NextAuth.js (planned integration with FastAPI backend)
- **Internationalization**: next-international (English/Chinese support)
- **Theme System**: next-themes with class-based dark mode
- **Backend** (planned): Local FastAPI + Supabase integration, LangChain/LangGraph for AI

### Frontend Architecture

**Three-Panel Layout Design**:
- Left sidebar (60-120px): Main navigation (Chat, Contacts, Files, Timeline, Plugins, Settings)
- Middle panel (300-400px): Content lists (conversations, contacts, files, etc.)
- Right panel (adaptive width): Main content area (chat interface, details, etc.)

**Route Structure** (Next.js App Router):
```
app/
├── (auth)/           # Authentication pages
│   ├── login/
│   └── register/
├── (main)/           # Main application with three-panel layout
│   ├── layout.tsx    # Main layout wrapper
│   ├── chat/         # Chat functionality
│   ├── dashboard/    # Dashboard page
│   └── ...
├── api/              # API routes (NextAuth, webhooks)
└── globals.css       # Global styles
```

**Component Organization**:
- `components/ui/`: shadcn/ui components (Avatar, Badge, Button, Card, etc.)
- `components/layout/`: Layout components (ThemeProvider, etc.)
- `components/chat/`: Chat-specific components
- `components/contacts/`: Contact/agent management components
- `lib/`: Utilities and configurations
- `store/`: Zustand state management
- `types/`: TypeScript type definitions

### Key Features
1. **AI Agent Social Network**: Treat AI agents as "virtual contacts" with profiles, capabilities, and personalities
2. **@ Mention System**: Dynamic AI agent integration in conversations
3. **Multi-modal Support**: Text, images, files, code blocks, charts
4. **Real-time Collaboration**: WebSocket-based communication
5. **Plugin Ecosystem**: Extensible tool and plugin architecture
6. **Timeline/Feed**: Social media-like content sharing by AI agents

## Development Guidelines

### Code Preferences (from .cursor/rules/)
- Always prefer simple solutions
- Avoid code duplication - check existing codebase for similar functionality
- Keep files under 200-300 lines - refactor beyond that
- Never mock data for dev/prod environments (only for tests)
- Don't overwrite .env files without confirmation
- Keep codebase clean and organized

### Styling & UI
- Uses Tailwind CSS with class-based dark mode (`darkMode: 'class'`)
- shadcn/ui for consistent UI components
- Theme system with next-themes provider
- Tailwind animate plugin for animations

### Internationalization
- Supports English (`en`) and Chinese (`zh`) locales
- Default locale: English
- Uses next-international for i18n
- Configuration in `lib/i18n/config.ts`

### State Management
- Zustand for client-side state management
- Store slices in `store/slices/` (authSlice.ts, settingsSlice.ts)
- Types defined in `store/types.ts`

## Development Environment Setup

1. **Frontend Setup**:
   ```bash
   cd frontend
   pnpm install   # Use pnpm as package manager
   pnpm dev
   ```

2. **Environment Variables**:
   - Uses `.env.local` for Next.js environment variables
   - Don't overwrite existing .env files without confirmation

3. **Project Structure Notes**:
   - Currently only `frontend/` directory exists
   - Future: Will add `bff/` (Backend for Frontend) and `backend-web/` directories
   - Current route structure is placeholder and will be completely refactored

## Future Implementation Notes

- **Backend**: Local FastAPI + Supabase integration, vector database (pgvector), LangChain/LangGraph
- **Authentication**: Integration between NextAuth.js and FastAPI backend
- **Real-time**: Supabase Realtime for chat and presence
- **Payments**: Planned integration with Creem.io (initial) then Stripe (scale)
- **AI Integration**: LangGraph for multi-agent orchestration
- **Plugin System**: Dynamic loading of AI tools and external integrations

## Important References

- **Design System**: See `Design-system.md` for comprehensive UI/UX guidelines, color schemes, component specifications
- **Product Requirements**: See `README.md` for detailed product requirements, architecture plans, and technical specifications
- **Coding Preferences**: See `.cursor/rules/` for development guidelines and tech stack details

## File Structure Conventions

- Components are organized by feature/domain
- UI components use shadcn/ui patterns
- Types are centralized in `types/` directory
- Utilities and configurations in `lib/`
- Store management follows Zustand slice pattern

## Important Notes

- This is a bilingual platform with both English and Chinese support
- Focus on clean, maintainable code following established patterns
- The project is in early development with many components being newly added
- Pay attention to existing coding preferences and maintain consistency