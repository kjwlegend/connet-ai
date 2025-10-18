# Environment Management Guide

This guide explains how to manage multiple environment files for different deployment stages in the Connet.AI BFF service.

## Overview

The BFF service supports multiple environment configurations through a flexible environment file system:

- **Environment-specific files**: `.env.local`, `.env.uat`, `.env.prod`, `.env.test`
- **Dynamic selection**: Based on `APP_ENV` or `BFF_ENV_FILE` environment variables
- **Fallback mechanism**: Graceful fallback to default `.env` file
- **Management tools**: Helper scripts for creating and managing environment files

## Environment File Priority

The system loads environment files in the following priority order:

1. **`BFF_ENV_FILE`** environment variable (highest priority)
2. **Environment-specific files** based on `APP_ENV`:
   - `development` → `.env.local`
   - `staging` → `.env.uat`
   - `production` → `.env.prod`
3. **Default `.env`** file (lowest priority)

## Quick Start

### 1. Create Environment Files

```bash
# List available environments and their status
python scripts/manage_env.py list

# Create environment files from template
python scripts/manage_env.py create local
python scripts/manage_env.py create uat
python scripts/manage_env.py create prod
python scripts/manage_env.py create test
```

### 2. Customize Environment Files

Edit the created files to match your environment:

```bash
# Local development
nano .env.local

# UAT environment  
nano .env.uat

# Production environment
nano .env.prod
```

### 3. Set Active Environment

```bash
# Set active environment (creates .env symlink)
python scripts/manage_env.py set local
```

### 4. Validate Configuration

```bash
# Validate environment file
python scripts/manage_env.py validate local
```

## Environment-Specific Configurations

### Local Development (`.env.local`)

```bash
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/connet_ai_local
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### UAT Environment (`.env.uat`)

```bash
APP_ENV=staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://user:pass@uat-db:5432/connet_ai_uat
REDIS_URL=redis://uat-redis:6379/0
CORS_ORIGINS=https://uat.connet.ai
```

### Production Environment (`.env.prod`)

```bash
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/connet_ai_prod
REDIS_URL=redis://prod-redis:6379/0
CORS_ORIGINS=https://connet.ai,https://app.connet.ai
```

### Test Environment (`.env.test`)

```bash
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/connet_ai_test
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/connet_ai_test
REDIS_URL=redis://localhost:6379/1
```

## Starting the Service

### Using Startup Scripts (Recommended)

```bash
# Local development
python scripts/start_dev.py

# UAT environment
python scripts/start_uat.py

# Production environment
python scripts/start_prod.py
```

### Using Environment Variables

```bash
# Method 1: Set BFF_ENV_FILE
export BFF_ENV_FILE="/path/to/.env.local"
python -m uvicorn app.main:create_app --factory

# Method 2: Set APP_ENV (auto-selects env file)
export APP_ENV=development
python -m uvicorn app.main:create_app --factory
```

### Using Docker

```bash
# Local development
docker-compose -f docker-compose.local.yml up

# UAT environment
docker-compose -f docker-compose.yml up

# Production environment
docker-compose -f docker-compose.yml up
```

## Environment File Management Commands

### List All Environment Files

```bash
python scripts/manage_env.py list
```

Output:
```
📁 Environment Files Status:
==================================================
local    | .env.local    | ✅ Exists
uat      | .env.uat      | ❌ Missing
prod     | .env.prod     | ✅ Exists
test     | .env.test     | ❌ Missing
```

### Create Environment File

```bash
# Create from template
python scripts/manage_env.py create local

# Overwrite existing file
python scripts/manage_env.py create local --force
```

### Validate Environment File

```bash
python scripts/manage_env.py validate local
```

Output:
```
✅ Environment file .env.local is valid
   App: Connet.AI BFF Service v0.1.0
   Environment: development
   Debug: True
   Log Level: DEBUG
```

### Set Active Environment

```bash
# Set active environment (creates .env symlink)
python scripts/manage_env.py set local
```

## Best Practices

### 1. Environment File Security

- **Never commit sensitive files**: Add `.env*` to `.gitignore`
- **Use environment-specific secrets**: Each environment should have its own API keys
- **Rotate secrets regularly**: Especially in production environments
- **Use secret management**: Consider using tools like HashiCorp Vault for production

### 2. Environment File Organization

- **Keep templates updated**: Maintain `env.example` with all required variables
- **Document environment differences**: Add comments explaining environment-specific settings
- **Use consistent naming**: Follow the established naming convention
- **Validate configurations**: Use the validation command before deployment

### 3. Development Workflow

- **Start with local**: Always begin development with local environment
- **Test in UAT**: Validate changes in UAT before production
- **Use feature flags**: Implement feature flags for environment-specific behavior
- **Monitor logs**: Use appropriate log levels for each environment

### 4. Deployment Considerations

- **Environment variables**: Override file settings with environment variables in containers
- **Health checks**: Implement health checks that verify environment configuration
- **Rollback strategy**: Keep previous environment configurations for quick rollback
- **Configuration drift**: Regularly audit configurations for consistency

## Troubleshooting

### Common Issues

1. **Environment file not found**
   ```
   ❌ Environment file .env.local not found.
   ```
   **Solution**: Create the environment file using `python scripts/manage_env.py create local`

2. **Invalid configuration**
   ```
   ❌ Error loading environment file .env.local: ValidationError
   ```
   **Solution**: Check the environment file syntax and required variables

3. **Wrong environment loaded**
   ```
   Environment: production (expected: development)
   ```
   **Solution**: Check `APP_ENV` or `BFF_ENV_FILE` environment variables

### Debug Commands

```bash
# Check current environment
echo $APP_ENV
echo $BFF_ENV_FILE

# Validate all environment files
python scripts/manage_env.py validate local
python scripts/manage_env.py validate uat
python scripts/manage_env.py validate prod

# Check environment file priority
python -c "from app.config.settings import get_settings; print(get_settings().app_env)"
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Deploy to UAT
on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up environment
        run: |
          export APP_ENV=staging
          python scripts/manage_env.py validate uat
      - name: Deploy
        run: |
          python scripts/start_uat.py
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  bff:
    build: .
    environment:
      - APP_ENV=production
    env_file:
      - .env.prod
    ports:
      - "8000:8000"
```

## Migration from Single .env File

If you're migrating from a single `.env` file:

1. **Backup existing file**: `cp .env .env.backup`
2. **Create environment files**: Use the management script
3. **Update startup scripts**: Ensure they use the new environment system
4. **Test each environment**: Validate configurations before deployment
5. **Update documentation**: Update deployment and development guides

## Security Considerations

- **File permissions**: Set appropriate file permissions (600) for environment files
- **Secret rotation**: Implement regular secret rotation for production
- **Audit logging**: Log environment file access and changes
- **Access control**: Limit access to production environment files
- **Encryption**: Consider encrypting sensitive environment files at rest
