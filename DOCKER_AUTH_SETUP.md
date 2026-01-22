# Docker Setup for Authentication

This document outlines the changes made to support authentication in the Docker setup.

## Changes Made

### 1. Backend Dockerfile (`Dockerfile`)
- ✅ Added `python3-dev` and `libffi-dev` for bcrypt compilation
- ✅ Added `DATABASE_URL` environment variable
- ✅ Ensured `/app/data` directory exists for database storage

### 2. Backend docker-compose.yml
- ✅ Added `SECRET_KEY` environment variable (with fallback)
- ✅ Database volume mount: `./data:/app/data`
- ✅ Database URL: `sqlite:///./data/sql.db`

### 3. Database Configuration (`auth/database.py`)
- ✅ Updated to use `DATABASE_URL` environment variable
- ✅ Fallback to `sqlite:///./sql.db` for local development
- ✅ Added `check_same_thread=False` for SQLite in multi-threaded environments

### 4. Service Configuration (`auth/service.py`)
- ✅ Updated to use `SECRET_KEY` from environment variable
- ✅ Fallback to default for development

### 5. Frontend docker-compose.yml
- ✅ Added `NEXT_PUBLIC_API_URL` environment variable
- ✅ Default: `http://localhost:8000`

## Environment Variables

### Backend (.env or docker-compose.yml)
```bash
DATABASE_URL=sqlite:///./data/sql.db
SECRET_KEY=your-secret-key-here  # Change in production!
```

### Frontend (.env.local or docker-compose.yml)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database Location

- **Local Development**: `./sql.db` (in project root)
- **Docker**: `/app/data/sql.db` (mounted to `./data/sql.db` on host)

## Security Notes

⚠️ **IMPORTANT**: 
- Change `SECRET_KEY` in production! Use a strong random key.
- Generate a secure key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Never commit `.env` files with real secrets to version control

## Dependencies Added

The following dependencies were added to `requirements.txt`:
- `python-jose[cryptography]==3.3.0` - JWT token handling
- `passlib[bcrypt]==1.7.4` - Password hashing (though we use bcrypt directly)
- `bcrypt==4.0.1` - Password hashing library
- `sqlalchemy==2.0.23` - Database ORM

## Building and Running

### Backend
```bash
cd /home/mhki/sanctum/improved-carnival
docker-compose build
docker-compose up -d
```

### Frontend
```bash
cd /home/mhki/pesabu/my-app
docker-compose build
docker-compose up -d
```

## Database Initialization

The database tables are automatically created when the application starts via:
```python
Base.metadata.create_all(bind=engine)
```
This happens in `app/main.py` on startup.

## Troubleshooting

1. **Database not persisting**: Ensure `./data` directory exists and is writable
2. **bcrypt compilation errors**: Ensure `python3-dev` and `libffi-dev` are installed (already in Dockerfile)
3. **Connection issues**: Check that `NEXT_PUBLIC_API_URL` matches your backend URL
4. **Auth endpoints 404**: Ensure the auth router is included in `app/main.py` (already done)
