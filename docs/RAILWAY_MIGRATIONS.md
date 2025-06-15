# Railway Migrations Guide

## Overview
This guide explains how to handle database migrations when deploying to Railway, covering both development and production environments.

## Current Setup

### Railway Configuration
- **Backend**: `railway.toml` in project root
- **Frontend**: `frontend/railway.toml` for React SPA
- **Database**: PostgreSQL managed by Railway

### Migration Strategy
We use **manual migrations** instead of automatic migrations on every deploy for better control and reliability.

## Migration Workflow

### 1. Development Environment

#### Creating New Migrations
```bash
# Navigate to project root
cd /path/to/wingman

# Create a new migration
flask db migrate -m "Description of changes"

# Review the generated migration file in migrations/versions/
# Edit if necessary to ensure correctness

# Apply migration locally
flask db upgrade
```

#### Testing Migrations
```bash
# Test rollback (optional)
flask db downgrade

# Re-apply to ensure it works
flask db upgrade
```

### 2. Production Deployment

#### Before Deploying Code Changes
1. **Commit your migration files** to git
2. **Deploy to Railway** (code will deploy without running migrations)
3. **Manually run migrations** via Railway CLI or console

#### Running Migrations on Railway

**Option A: Railway CLI**
```bash
# Connect to your Railway project
railway login
railway link

# Run migrations
railway run flask db upgrade
```

**Option B: Railway Console**
1. Go to your Railway dashboard
2. Open your backend service
3. Go to "Deploy" → "Command"
4. Run: `flask db upgrade`

**Option C: Temporary Deploy Command**
If you need to run migrations as part of a specific deploy:
```bash
# Temporarily modify railway.toml
startCommand = "flask db upgrade && gunicorn -w 4 -b 0.0.0.0:$PORT backend.wsgi:application"

# Deploy, then revert railway.toml to:
startCommand = "gunicorn -w 4 -b 0.0.0.0:$PORT backend.wsgi:application"
```

### 3. Emergency Procedures

#### Rolling Back Migrations
```bash
# Check current migration
railway run flask db current

# Rollback to specific revision
railway run flask db downgrade <revision_id>
```

#### Migration Conflicts
If you encounter migration conflicts:
1. **Don't panic** - Railway keeps database backups
2. **Check migration history**: `railway run flask db history`
3. **Resolve conflicts** in migration files
4. **Test locally** before applying to production

## Best Practices

### ✅ Do's
- Always review generated migration files before applying
- Test migrations on a copy of production data when possible
- Keep migration descriptions clear and descriptive
- Commit migration files with the code changes that require them
- Run migrations during low-traffic periods
- Monitor application logs after applying migrations

### ❌ Don'ts
- Don't run automatic migrations on every deploy
- Don't edit applied migration files (create new ones instead)
- Don't skip testing migrations locally
- Don't apply untested migrations directly to production
- Don't forget to backup before major schema changes

## Troubleshooting

### Common Issues

#### "Migration already applied"
```bash
# Check what's applied
railway run flask db current
railway run flask db history

# If migration is already applied, you're good to go
```

#### "Migration conflicts"
```bash
# Resolve conflicts in migration files
# Then run
railway run flask db stamp head
railway run flask db upgrade
```

#### "Database connection issues"
- Check Railway database credentials
- Verify DATABASE_URL environment variable
- Check Railway service logs for connection errors

### Getting Help
- Check Railway logs: Dashboard → Service → Deployments → View Logs
- Review Flask-Migrate documentation
- Check migration files in `migrations/versions/`

## Migration History
Keep track of important migrations:

- `20250615_companion`: Added companion app tables (GoalTemplate, UserGoal, Badge, UserBadge)
- `20250608_add_chat_message`: Added chat message persistence
- `20250607_seed_skills`: Initial skills seeding
- `20250529_add_product_images`: Product image support

## Environment Variables
Ensure these are set in Railway:
- `DATABASE_URL`: Automatically provided by Railway PostgreSQL
- `FLASK_APP`: Should be set to `backend.wsgi:application`
- `FLASK_ENV`: `production` for production deployments
