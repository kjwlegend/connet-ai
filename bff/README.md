# Connet.AI BFF Service

Backend for Frontend (BFF) service for the Connet.AI platform, providing APIs for the frontend application.

## 🏗️ Architecture

The BFF service is built using:
- **FastAPI** - Modern, fast web framework for Python APIs
- **SQLModel** - SQL databases with Python type hints
- **Supabase** - Database and authentication backend
- **Redis** - Caching and session storage
- **LangChain** - AI agent orchestration
- **Pydantic** - Data validation and serialization

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (via Supabase)
- Redis
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/connet-ai/xiaoguang-next-gen.git
cd xiaoguang-next-gen/bff
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the development server**
```bash
python -m app.main
# or
uvicorn app.main:create_app --factory --reload
```

The API will be available at `http://localhost:8000`

## 📁 Project Structure

```
bff/
├── app/                              # Application code
│   ├── __init__.py
│   ├── main.py                       # FastAPI app factory
│   ├── config/                       # Configuration
│   │   ├── settings.py               # App settings
│   │   └── ...
│   ├── api/                          # API layer
│   │   ├── dependencies.py           # FastAPI dependencies
│   │   ├── middleware.py             # Custom middleware
│   │   └── v1/                       # API version 1
│   │       ├── router.py             # Main router
│   │       └── endpoints/            # API endpoints
│   ├── core/                         # Business logic
│   │   ├── domain/                   # Domain models
│   │   ├── use_cases/                # Use case implementations
│   │   └── interfaces/               # Abstract interfaces
│   ├── infrastructure/               # Infrastructure layer
│   │   ├── database/                 # Database models & repos
│   │   ├── cache/                    # Redis caching
│   │   ├── external/                 # External service clients
│   │   └── security/                 # Auth & security
│   ├── services/                     # Application services
│   ├── schemas/                      # Pydantic schemas
│   ├── utils/                        # Utilities
│   └── tests/                        # Test files
├── alembic/                          # Database migrations
├── scripts/                          # Utility scripts
├── pyproject.toml                    # Project configuration
├── requirements.txt                  # Dependencies
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Application
APP_NAME="Connet.AI BFF Service"
APP_ENV="development"
DEBUG=true

# Database (Supabase)
SUPABASE_URL="your-supabase-url"
SUPABASE_ANON_KEY="your-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
DATABASE_URL="postgresql+asyncpg://..."

# Redis
REDIS_URL="redis://localhost:6379/0"

# Security
SECRET_KEY="your-secret-key"

# AI Services
OPENAI_API_KEY="your-openai-key"
```

### Development Setup

1. **Database Setup**
```bash
# Run Alembic migrations
alembic upgrade head
```

2. **Redis Setup**
```bash
# Start Redis (if running locally)
redis-server
```

3. **Run Tests**
```bash
pytest
```

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API docs**: `http://localhost:8000/docs`
- **Alternative docs**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/v1/openapi.json`

## 🔒 Authentication

The API uses JWT-based authentication:

1. **Register/Login** to get access tokens
2. **Include token** in Authorization header: `Bearer <token>`
3. **Refresh tokens** when they expire

## 🚀 Deployment

### Docker (Recommended)

```bash
# Build image
docker build -t connet-ai-bff .

# Run container
docker run -p 8000:8000 --env-file .env connet-ai-bff
```

### Production

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn app.main:create_app --factory --workers 4 --bind 0.0.0.0:8000
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_users.py

# Run tests with markers
pytest -m "unit"  # or "integration", "e2e"
```

## 📊 Monitoring

### Health Checks

- **Basic health**: `GET /health`
- **Detailed health**: `GET /api/v1/health/detailed`
- **Readiness**: `GET /api/v1/health/readiness`
- **Liveness**: `GET /api/v1/health/liveness`

### Metrics

Prometheus metrics available at `/metrics` (if enabled)

### Logging

Structured logging with correlation IDs for request tracing.

## 🔄 Development Workflow

1. **Create feature branch**
2. **Make changes**
3. **Run tests**: `pytest`
4. **Format code**: `black . && isort .`
5. **Lint code**: `flake8`
6. **Type check**: `mypy`
7. **Commit and push**
8. **Create pull request**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions and support:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

---

**Note**: This service is part of the Connet.AI platform. For frontend integration, see the `frontend/` directory in the main repository.