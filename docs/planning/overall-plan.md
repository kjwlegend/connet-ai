# Connet.AI - Overall Development Plan

## Project Overview
Connet.AI is an AI collaboration platform designed as a social-media-like interface for human-AI interaction. The platform enables users to interact with AI agents as "virtual contacts" through @ mentions, group chats, and a timeline-based content sharing system.

## Development Phases

### Phase 1: Foundation Setup (Current)
**Goal**: Establish basic project structure and core infrastructure

**Key Deliverables**:
- ✅ Frontend foundation (Next.js + TypeScript + Tailwind + shadcn/ui)
- ✅ Design system documentation
- ✅ Project requirements documentation
- ⏳ Backend setup (Local FastAPI + Supabase)
- ⏳ Database schema design and implementation
- ⏳ Authentication system (NextAuth.js + Supabase Auth)

### Phase 2: Core Features (Q1 2025)
**Goal**: Implement basic chat functionality and AI agent system

**Key Deliverables**:
- User registration and authentication
- Basic AI agent management
- One-on-one chat with AI agents
- @ mention system for dynamic agent inclusion
- Message history and context management
- Real-time chat via Supabase Realtime

### Phase 3: Advanced Features (Q2 2025)
**Goal**: Expand collaboration capabilities and social features

**Key Deliverables**:
- Group chat with multiple AI agents
- Timeline/Feed system for AI agent content sharing
- File sharing and management
- Agent discovery and recommendation system
- Basic plugin system architecture

### Phase 4: Autonomous Collaboration (Q3 2025)
**Goal**: Enable AI-to-AI collaboration and task planning

**Key Deliverables**:
- Task planning AI agent
- Multi-agent autonomous collaboration
- Human intervention checkpoints
- Advanced context and memory management

### Phase 5: Scale & Monetization (Q4 2025)
**Goal**: Commercial features and platform scaling

**Key Deliverables**:
- Payment integration (Creem.io → Stripe)
- Subscription management
- Advanced plugin marketplace
- Enterprise features
- Performance optimization

## Architecture Overview

### Current Structure
```
connet-ai/
├── frontend/           # Next.js application (EXISTS)
├── todo/              # Project planning (EXISTS)
├── Design-system.md   # UI/UX guidelines (EXISTS)
├── README.md          # Product requirements (EXISTS)
└── CLAUDE.md          # Development guide (EXISTS)
```

### Target Structure
```
connet-ai/
├── frontend/          # Next.js client application
├── bff/              # Backend-for-Frontend (API gateway)
├── backend-web/       # FastAPI + Supabase integration
├── shared/           # Shared types and utilities
├── docs/             # Documentation
└── todo/             # Project planning and task management
```

## Technical Stack

### Frontend
- **Framework**: Next.js 15.3.2 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **Package Manager**: pnpm
- **Authentication**: NextAuth.js
- **Internationalization**: next-international (EN/ZH)

### Backend
- **API Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Real-time**: Supabase Realtime
- **AI Framework**: LangChain + LangGraph
- **Task Queue**: ARQ (Async Redis Queue)
- **Vector Search**: pgvector extension

### Infrastructure
- **Hosting**: Vercel (Frontend) + Supabase (Backend services)
- **File Storage**: Supabase Storage
- **Payments**: Creem.io (initial) → Stripe (scale)
- **Monitoring**: Supabase Analytics + Vercel Analytics

## Key Design Principles

### 1. Social-First Design
- AI agents as "virtual contacts"
- Familiar chat-based interface (like WeChat/Slack)
- Timeline/feed for content discovery
- Group collaboration features

### 2. Three-Panel Layout
- **Left Panel (60-120px)**: Navigation (Chat, Contacts, Files, Timeline, Plugins)
- **Middle Panel (300-400px)**: Content lists and search
- **Right Panel (flexible)**: Main content area and details

### 3. Progressive Enhancement
- Start with basic chat functionality
- Gradually add advanced AI collaboration features
- Maintain backwards compatibility
- Focus on user experience at each stage

## Success Metrics

### Phase 1 (Foundation)
- [ ] Frontend development environment fully functional
- [ ] Backend API endpoints responding
- [ ] Database schema deployed
- [ ] Authentication flow working

### Phase 2 (Core Features)
- [ ] Users can register and authenticate
- [ ] Basic AI chat functionality working
- [ ] @ mention system functional
- [ ] Real-time messaging working

### Phase 3 (Advanced Features)
- [ ] Group chat with multiple agents
- [ ] Timeline/feed system operational
- [ ] File sharing working
- [ ] Agent discovery system functional

### Phase 4 (Autonomous Collaboration)
- [ ] Task planning agent operational
- [ ] Multi-agent collaboration working
- [ ] Human checkpoints functional

### Phase 5 (Scale & Monetization)
- [ ] Payment system integrated
- [ ] Subscription tiers operational
- [ ] Plugin marketplace functional
- [ ] Performance targets met

## Risk Mitigation

### Technical Risks
- **AI API Cost Control**: Implement usage limits and caching
- **Real-time Performance**: Use Supabase Realtime efficiently
- **Database Scaling**: Proper indexing and partitioning strategies

### Business Risks
- **User Adoption**: Focus on intuitive social interface
- **Competition**: Rapid MVP development and unique features
- **Monetization**: Clear value proposition and pricing strategy

## Next Steps (Immediate)

1. **Setup Backend Infrastructure**
   - Initialize FastAPI project structure
   - Configure Supabase integration
   - Set up database schema

2. **Implement Authentication**
   - Configure NextAuth.js with Supabase
   - Create user registration flow
   - Set up session management

3. **Basic AI Integration**
   - Set up LangChain/LangGraph foundation
   - Create basic AI agent system
   - Implement simple chat functionality

4. **Real-time Features**
   - Configure Supabase Realtime
   - Implement live chat updates
   - Add presence indicators

---

**Last Updated**: 2025-01-08
**Next Review**: Weekly (every Wednesday)
**Status**: Phase 1 - Foundation Setup