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

### Backend (BFF Service)
```bash
cd bff
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Start development server

# Alternative development commands
make dev           # Start with Docker Compose
make setup         # Setup local environment
make migrate       # Run database migrations
make test          # Run tests
make lint          # Run code quality checks
```

### Testing
```bash
# Frontend testing
cd frontend
pnpm test          # Run Jest tests
pnpm test:watch    # Run tests in watch mode

# Backend testing  
cd bff
pytest             # Run all tests
pytest tests/unit  # Run unit tests only
pytest -v          # Verbose output
make test          # Run tests via Makefile
```

## Architecture Overview

### Tech Stack
- **Frontend**: Next.js 15.3.2 with App Router, TypeScript, Tailwind CSS, shadcn/ui
- **Package Manager**: pnpm (not npm)
- **State Management**: Zustand
- **Authentication**: NextAuth.js (planned integration with FastAPI backend)
- **Internationalization**: next-international (English/Chinese support)
- **Theme System**: next-themes with class-based dark mode
- **Backend**: FastAPI BFF service + Supabase integration, LangChain/LangGraph for AI
- **Python Package Management**: pip with requirements.txt and pyproject.toml

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
- `components/layout/`: Layout components (AppLayout, Sidebar, MiddlePanel, ContentArea)
- `components/features/`: Feature-specific components organized by domain
  - `chat/`: Chat interface, message bubbles, conversation management
  - `contacts/`: Contact/agent management, dialogs, forms
  - `files/`: File management, upload, preview components
  - `plugins/`: Plugin marketplace, configuration, cards
  - `settings/`: Settings pages (Account, LLM, Membership, etc.)
  - `timeline/`: Social feed, timeline posts
- `lib/`: Utilities, configurations, and service integrations
- `store/`: Zustand state management with slices pattern
- `types/`: TypeScript type definitions
- `services/`: API clients and data fetching logic

### Key Features
1. **AI Agent Social Network**: Treat AI agents as "virtual contacts" with profiles, capabilities, and personalities
2. **@ Mention System**: Dynamic AI agent integration in conversations
3. **Multi-modal Support**: Text, images, files, code blocks, charts
4. **Real-time Collaboration**: WebSocket-based communication
5. **Plugin Ecosystem**: Extensible tool and plugin architecture
6. **Timeline/Feed**: Social media-like content sharing by AI agents
7. **Conversation Management**: 
   - Pin/unpin conversations with visual indicators (pinned conversations appear first with special styling)
   - Export conversations as Markdown files with full message history and metadata
   - Delete conversations with modern shadcn/ui dialog confirmation (replaces window.confirm)
   - Right-click context menu for conversation actions with dark/light theme support
8. **Chat Right Panel System**:
   - **Expandable Chat Details**: Right panel with smooth animations for conversation management
   - **Participants Management**: View all conversation participants with online status, add new participants via dialog
   - **Group Files**: List shared files with forward functionality, no icons for clean design
   - **Conversation Memory**: Core summary display with expandable details dialog
   - **Interactive TODO System**: AI-generated + human-editable TODO lists with add/check/delete functionality
   - **Responsive Design**: Overlay on mobile, sidebar on desktop with conditional rendering
9. **Theme System**: 
   - Complete dark/light mode support across all UI components
   - Context menus, panels, chat interface, and input areas all support theme switching
   - Consistent styling using CSS variables and Tailwind dark: classes

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
- **重要**: 翻译文件位于 `lib/i18n/messages/` 目录，不是 `locales/` 目录
  - 英文翻译: `lib/i18n/messages/en.json`
  - 中文翻译: `lib/i18n/messages/zh.json`

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
   - `frontend/` directory contains Next.js application  
   - `bff/` directory contains FastAPI Backend for Frontend service (in development)
   - Future: Will add `backend-web/` directory for admin panel
   - Current route structure is placeholder and will be completely refactored

## Backend Development Status

### ✅ Completed (BFF Service)
- **Core Architecture**: FastAPI application with DDD structure
- **Database Models**: 17+ comprehensive SQLModel classes supporting human-AI hybrid community:
  - User system (User, UserInvitation, UserRegistrationSource, UserLLMSettings, UserPromptLibrary, UserSubscription)
  - AI agent system (Agent, AgentKnowledgeBase)  
  - Conversation system (Conversation, ConversationParticipant, ConversationTopic, ConversationUserSetting, Message)
  - File system (File, FilePermission)
  - Social system (Contact, TimelinePost, TimelineComment, TimelineLike)
- **Infrastructure**: Database connection, caching (Redis), security (JWT), Supabase integration
- **API Framework**: Complete FastAPI setup with 12 endpoint modules including AI services
- **AI Services**: Agent management, chat, documents, tools endpoints with LangChain integration

### 🚧 In Progress
- **Database Migrations**: Alembic setup and initial schema deployment
- **Supabase Integration**: Project setup with pgvector for semantic search

### 📋 Future Implementation
- **Authentication**: Complete NextAuth.js and FastAPI backend integration
- **Real-time**: Supabase Realtime for chat and presence
- **AI Integration**: LangGraph for multi-agent orchestration
- **Plugin System**: Dynamic loading of AI tools and external integrations
- **Payments**: Integration with Creem.io (initial) then Stripe (scale)

## Important References

- **Design System**: See `Design-system.md` for comprehensive UI/UX guidelines, color schemes, component specifications
- **Product Requirements**: See `README.md` for detailed product requirements, architecture plans, and technical specifications
- **Backend Progress**: See `docs/bff-progress-tracker.md` for detailed BFF service development status
- **Database Schema**: See `bff/database_schema_design.md` for comprehensive schema documentation
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
- Always remember to leverage i18n for globalization (English/Chinese)
- Backend uses pip with requirements.txt and pyproject.toml for dependency management
- Frontend uses pnpm as the package manager (not npm)