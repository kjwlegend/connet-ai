# Manual Actions Required by Human

This guide outlines the manual steps that need to be performed by a human to complete the backend setup and deployment process.

## 🔧 Environment Setup

### 1. Environment Variables Configuration
Create or update the `.env` file in the `bff/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/connet_ai_db
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT & Security
JWT_SECRET_KEY=your-256-bit-secret-key-here
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here
ENCRYPTION_SECRET_KEY=your-encryption-secret-key-here

# External APIs
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_AI_API_KEY=your-google-ai-key-here
COHERE_API_KEY=your-cohere-key-here
MISTRAL_API_KEY=your-mistral-key-here
PERPLEXITY_API_KEY=your-perplexity-key-here
TOGETHER_API_KEY=your-together-ai-key-here

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
FROM_EMAIL=noreply@connet.ai

# Storage Configuration
FILE_STORAGE_PROVIDER=supabase  # or 'local', 'aws_s3', 'google_cloud'
AWS_ACCESS_KEY_ID=your-aws-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_BUCKET_NAME=your-s3-bucket

# Application Settings
ENVIRONMENT=development  # or 'production', 'testing', 'staging'
DEBUG=true
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 2. Supabase Project Setup

#### Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and create new project
2. Choose your organization and region
3. Set strong database password
4. Wait for project to be fully provisioned

#### Enable Required Extensions
Execute these SQL commands in Supabase SQL Editor:

```sql
-- Enable vector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for additional encryption functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

#### Configure RLS (Row Level Security)
Run the RLS configuration scripts (will be provided separately).

#### Set up Storage Buckets
1. Go to Storage → Buckets
2. Create buckets:
   - `user-avatars` (public)
   - `conversation-files` (private)
   - `timeline-media` (public)

### 3. Database Migration
Run the migration to create all tables:

```bash
cd bff
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run migration
alembic upgrade head
```

### 4. Redis Setup
Install and start Redis server:

```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Windows
# Download Redis for Windows or use Docker
docker run -d -p 6379:6379 redis:alpine
```

## 🔑 API Keys and Credentials

### Required API Keys
Obtain API keys from these providers:

1. **OpenAI**: https://platform.openai.com/api-keys
2. **Anthropic**: https://console.anthropic.com/
3. **Google AI**: https://makersuite.google.com/app/apikey
4. **Cohere**: https://dashboard.cohere.com/api-keys
5. **Mistral**: https://console.mistral.ai/
6. **Perplexity**: https://www.perplexity.ai/settings/api
7. **Together AI**: https://api.together.xyz/settings/api-keys

### Email Setup
Configure SMTP for transactional emails:
- Use Gmail App Passwords if using Gmail
- Configure SPF, DKIM, DMARC records for custom domains
- Test email delivery in development

## 🚀 Deployment Preparation

### 1. Production Environment Variables
Update environment variables for production:
- Use strong, randomly generated secret keys
- Configure production database URL
- Set `ENVIRONMENT=production`
- Set `DEBUG=false`
- Configure proper CORS origins

### 2. Database Performance Optimization
Create additional indexes if needed:

```sql
-- Add indexes for better query performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_created 
ON messages(conversation_id, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_timeline_posts_author_created 
ON timeline_posts(author_id, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contacts_follower_following 
ON contacts(follower_id, following_id);
```

### 3. Monitoring Setup
Configure monitoring and logging:
- Set up error tracking (Sentry, Rollbar)
- Configure application performance monitoring
- Set up log aggregation
- Configure health check endpoints

## 🧪 Testing & Validation

### 1. Run Unit Tests
```bash
cd bff
pytest tests/ -v --cov=app
```

### 2. Integration Testing
Test key workflows:
- User registration and authentication
- Conversation creation and messaging
- File upload and storage
- AI agent interactions
- Timeline post creation

### 3. Performance Testing
- Load test API endpoints
- Test database query performance
- Validate Redis caching effectiveness
- Test file upload/download speeds

## 📋 Pre-Launch Checklist

### Security
- [ ] All secret keys are randomly generated and secure
- [ ] Database has proper indexes and constraints
- [ ] RLS policies are configured correctly
- [ ] API rate limiting is enabled
- [ ] File upload validation is working
- [ ] CORS is configured properly

### Functionality  
- [ ] User registration and login work
- [ ] Password reset flow works
- [ ] Email delivery is functional
- [ ] AI provider integrations work
- [ ] File storage is operational
- [ ] Real-time features work via Supabase
- [ ] Database migrations run successfully

### Performance
- [ ] API response times are acceptable
- [ ] Database queries are optimized
- [ ] Caching is working effectively
- [ ] File uploads complete successfully
- [ ] Memory usage is within limits

### Monitoring
- [ ] Error tracking is configured
- [ ] Performance monitoring is active
- [ ] Health check endpoints respond
- [ ] Log levels are appropriate for environment

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues
- Verify DATABASE_URL format
- Check network connectivity to database
- Ensure database user has required permissions
- Check if database exists

#### Migration Failures  
- Verify database schema is clean
- Check for conflicting table names
- Ensure user has DDL permissions
- Review migration logs for specific errors

#### API Key Issues
- Verify all required API keys are set
- Test API key validity with direct API calls
- Check rate limits and quotas
- Ensure keys have required permissions

#### File Upload Issues
- Verify storage provider configuration
- Check bucket permissions and policies
- Test file size limits
- Verify MIME type validation

### Getting Help
- Check application logs for specific errors
- Review Supabase dashboard for database issues
- Test individual components in isolation
- Use debugging tools for step-by-step troubleshooting

## 📞 Support Contacts

For technical support:
- Backend Architecture: [Technical Lead]
- Database Issues: [Database Administrator]  
- Infrastructure: [DevOps Team]
- API Integration: [Integration Team]

---

**Note**: This guide assumes basic knowledge of server administration, database management, and API configuration. Ensure all security best practices are followed when setting up production environments.