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

# Alternative development commands using Makefile
make dev           # Start development server locally
make install       # Install Python dependencies
make debug-start   # Start debug environment (PostgreSQL + Redis only)
make test          # Run tests with pytest
make test-cov      # Run tests with coverage
make lint          # Run linting (flake8 + mypy)
make format        # Format code (black + isort)
make docker-start  # Start all services with Docker
make docker-stop   # Stop Docker services
make db-upgrade    # Run database migrations with Alembic
```

### Testing
```bash
# Frontend testing
cd frontend
pnpm test          # Run Jest tests
pnpm test:watch    # Run tests in watch mode
pnpm test:coverage # Run tests with coverage

# Backend testing  
cd bff
pytest             # Run all tests
pytest -v          # Run tests with verbose output
make test          # Run tests via Makefile
make test-cov      # Run tests with coverage report
```

## Architecture Overview

### Tech Stack
- **Frontend**: Next.js 15.3.2 with App Router, TypeScript, Tailwind CSS 4.x, shadcn/ui
- **Package Manager**: pnpm (not npm)
- **State Management**: Zustand
- **Authentication**: Supabase Auth integration
- **Internationalization**: next-intl (English/Chinese support)
- **Theme System**: next-themes with class-based dark mode
- **Backend**: FastAPI BFF service with comprehensive DDD architecture
- **Database**: PostgreSQL with SQLModel ORM and Alembic migrations
- **AI Integration**: LangChain + LangGraph for multi-agent orchestration
- **Python Package Management**: pip with requirements.txt and pyproject.toml (hatchling build system)

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
- **Always prefer simple solutions**
- **Avoid code duplication** - check existing codebase for similar functionality before creating new code
- **Environment awareness** - write code that works across dev, test, and prod environments
- **Careful changes** - only make changes that are requested or well understood and related to the request
- **Fix without introducing new patterns** - exhaust existing implementation options before introducing new tech/patterns
- **Keep codebase clean and organized**
- **File size limits** - keep files under 200-300 lines, refactor beyond that
- **No mocking in non-test environments** - mocking data is only for tests, never for dev or prod
- **Environment file protection** - never overwrite .env files without confirmation
- **Remove old implementations** - when introducing new patterns, remove old duplicate logic

### Styling & UI
- Uses Tailwind CSS 4.x with class-based dark mode (`darkMode: 'class'`)
- shadcn/ui for consistent UI components with Radix UI primitives
- Theme system with next-themes provider
- Framer Motion for advanced animations
- Additional packages: tw-animate-css, class-variance-authority for component variants

### Internationalization
- Supports English (`en`) and Chinese (`zh`) locales
- Default locale: English
- Uses next-intl for i18n
- Configuration in `lib/i18n/config.ts`
- **重要**: Translation files are located in both directories:
  - Primary: `lib/i18n/messages/` (en.json, zh.json)
  - Fallback: `lib/i18n/locales/` (en.json, zh.json)

### State Management
- Zustand for client-side state management
- Store slices organized by feature in `store/slices/`:
  - `auth/authSlice.ts` - Authentication state
  - `chat/conversationSlice.ts` - Chat and conversation state
  - `contacts/contactsSlice.ts` - Contact management
  - `agents/agentsSlice.ts` - AI agent state
  - `ui/` - UI-related state (layout, notifications, preferences)
- Types defined in `store/types/` with feature-based organization
- Middleware for persistence and hydration in `store/middleware/`

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
- **Core Architecture**: FastAPI application with Domain-Driven Design (DDD) structure
- **Application Structure**:
  - `app/api/v1/endpoints/` - API endpoint modules (auth, users, ai_agents, conversations, contacts, etc.)
  - `app/core/` - Core configuration and interfaces
  - `app/infrastructure/` - External integrations (database, cache, supabase, security)
  - `app/services/` - Business logic layer with LangGraph integration
  - `app/schemas/` - Pydantic models for request/response validation
- **Database Models**: 17+ comprehensive SQLModel classes in `app/infrastructure/database/models/`:
  - User system (User, UserInvitation, UserRegistrationSource, UserLLMSettings, UserPromptLibrary, UserSubscription)
  - AI agent system (Agent, Knowledge models)  
  - Conversation system (Conversation, ConversationParticipant, Message, etc.)
  - File system (File, FilePermission)
  - Social system (Contact, TimelinePost, TimelineComment, TimelineLike)
- **Infrastructure**: Complete setup with Redis caching, Supabase integration, security middleware
- **API Framework**: FastAPI with comprehensive middleware stack and 12+ endpoint modules
- **AI Services**: Full LangChain/LangGraph integration with multi-agent orchestration

### 🚧 In Progress
- **Database Migrations**: Alembic setup and schema deployment
- **Frontend-Backend Integration**: API service integration with Zustand stores
- **Real-time Features**: WebSocket implementation for chat functionality

### 📋 Future Implementation
- **Authentication**: Complete Supabase Auth integration across frontend/backend
- **Real-time**: Enhanced WebSocket and Supabase Realtime for chat and presence
- **Plugin System**: Dynamic loading of AI tools and external integrations
- **Payments**: Integration with payment providers for subscription management

## Important References

- **Design System**: See `Design-system.md` for comprehensive UI/UX guidelines, color schemes, component specifications
- **Product Requirements**: See `README.md` for detailed product requirements, architecture plans, and technical specifications
- **Database Schema**: See `bff/database_schema_design.md` for comprehensive schema documentation
- **Coding Preferences**: See `.cursor/rules/` for development guidelines and tech stack details
- **Architecture Documentation**: See `docs/` directory for detailed architecture plans and implementation guides

## Key Project Structure

### Frontend (`frontend/`)
```
src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Authentication pages (login, register)
│   ├── (main)/            # Main application routes
│   ├── (test)/            # Test pages for development
│   └── api/               # API routes and webhooks
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── features/          # Feature-specific components
│   │   ├── chat/          # Chat interface components
│   │   ├── contacts/      # Contact management
│   │   ├── settings/      # Settings pages
│   │   └── timeline/      # Social timeline features
│   └── layout/            # Layout components
├── lib/                   # Utilities and configurations
│   ├── i18n/             # Internationalization setup
│   ├── design-system/    # Design tokens and theme system
│   └── seo/              # SEO configuration
├── store/                 # Zustand state management
│   ├── slices/           # Feature-based state slices
│   └── middleware/       # Store middleware (persistence, logging)
└── services/             # API client services
```

### Backend (`bff/`)
```
app/
├── api/v1/               # Versioned API endpoints
├── core/                 # Core configuration
├── infrastructure/       # External integrations
│   ├── database/        # SQLModel models and repositories
│   ├── cache/           # Redis cache implementation
│   ├── external/        # Supabase and other external services
│   └── security/        # Authentication and security
├── services/            # Business logic layer
│   └── langgraph/       # LangGraph AI orchestration
├── schemas/             # Pydantic request/response models
└── utils/               # Utility functions
```

## Important Notes

- This is a bilingual platform with both English and Chinese support
- Focus on clean, maintainable code following established patterns in `.cursor/rules/`
- The project uses Domain-Driven Design (DDD) architecture in the backend
- Pay attention to existing coding preferences and maintain consistency
- Always leverage i18n for globalization (English/Chinese) using next-intl
- Backend uses pip with requirements.txt and pyproject.toml (hatchling build system)
- Frontend uses pnpm as the package manager (not npm)
- Follow the three-panel layout design pattern for UI consistency
- Use feature-based organization for components and state management
- Prefer existing solutions and patterns over introducing new ones
- Test coverage is important - use Jest for frontend and pytest for backend