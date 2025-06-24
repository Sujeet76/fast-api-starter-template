# FastAPI Template Project

A production-ready FastAPI template with best practices, proper structure, and essential tools for building scalable web APIs.

## 🚀 Features

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy 2.0** - Async ORM with type hints
- **PostgreSQL** - Production-ready database
- **Alembic** - Database migrations
- **Pydantic Settings** - Environment variable management
- **JWT Authentication** - Secure token-based auth
- **Docker Compose** - Easy development setup
- **UV** - Fast Python package manager
- **Ruff** - Lightning-fast linting and formatting
- **Pre-commit** - Code quality hooks
- **Structured Logging** - JSON and pretty console logging with `structlog`

## 📁 Project Structure

```
fastapi_project/
│
├── app/
│   ├── main.py               # FastAPI application factory
│   ├── api/
│   │   └── v1/
│   │       └── routes/
│   │           └── users.py  # User endpoints
│   ├── models/               # Pydantic & SQLAlchemy models
│   │   └── user.py
│   ├── services/             # Business logic
│   │   └── user_service.py
│   ├── core/                 # App settings, config
│   │   └── config.py
│   ├── db/                   # Database setup
│   │   └── database.py
│   └── utils/                # Helper functions
│       └── helpers.py
│
├── alembic/                  # Database migrations
├── docker-compose.yml        # PostgreSQL & Redis setup
├── .env.example             # Environment variables template
├── pyproject.toml           # Dependencies and tool config
└── README.md               # This file
```

## 🛠 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd py-backend

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional, defaults work for development)
```

### 2. Start Database

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Install Dependencies

```bash
# Install all dependencies
uv sync

# Or if you don't have uv installed:
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Create your first migration
uv run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
uv run alembic upgrade head
```

### 5. Run the Application

```bash
# Development server
uv run fastapi dev app/main.py

# Or using uvicorn directly
uv run uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## � Logging

The application includes a comprehensive logging system with:
- **Pretty Console Logging** - Colored, readable logs for development
- **Structured JSON Logging** - Machine-readable logs for production
- **File Rotation** - Automatic log file management
- **Performance Monitoring** - Request timing and slow query detection

```bash
# View logs in real-time (pretty format)
tail -f logs/app.log

# For different log formats, set environment variables:
export CONSOLE_LOG_FORMAT=pretty  # For colored console (default)
export LOG_FORMAT=json           # For file logging format
```

See [LOGGING.md](LOGGING.md) for detailed documentation.

## �🔧 Development

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Fix linting issues
uv run ruff check --fix
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

### Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Add new table"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1

# Migration history
uv run alembic history --verbose
```

## 🐳 Docker

### Development with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up (removes volumes)
docker-compose down -v
```

### Production Docker Build

```bash
# Build production image
docker build -t fastapi-app .

# Run production container
docker run -p 8000:8000 fastapi-app
```

## 📝 API Documentation

### Available Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/docs` - Interactive API documentation
- `GET /api/v1/users` - List all users
- `POST /api/v1/users` - Create new user
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Example API Usage

```bash
# Create a user
curl -X POST "http://localhost:8000/api/v1/users" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "first_name": "John",
       "last_name": "Doe"
     }'

# Get all users
curl "http://localhost:8000/api/v1/users"
```

## ⚙️ Configuration

### Environment Variables

All configuration is managed through environment variables. See `.env.example` for all available options.

Key settings:
- `DEBUG` - Enable debug mode
- `SECRET_KEY` - JWT secret key (change in production!)
- `POSTGRES_*` - Database connection settings
- `CORS_ORIGINS` - Allowed CORS origins

### Database Configuration

The project uses PostgreSQL by default. Connection settings:
- Host: `localhost`
- Port: `5432`
- Database: `fastapi_template`
- User: `postgres`
- Password: `password`

## 🚀 Deployment

### Production Checklist

1. **Security**:
   - [ ] Change `SECRET_KEY` to a secure random value
   - [ ] Set `DEBUG=False`
   - [ ] Configure proper CORS origins
   - [ ] Use environment variables for sensitive data

2. **Database**:
   - [ ] Use a managed PostgreSQL service
   - [ ] Run migrations: `alembic upgrade head`
   - [ ] Set up database backups

3. **Infrastructure**:
   - [ ] Use a proper WSGI server (Gunicorn + Uvicorn)
   - [ ] Set up reverse proxy (Nginx)
   - [ ] Configure logging
   - [ ] Set up monitoring

### Example Production Deployment

```bash
# Install production dependencies
uv sync --no-dev

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🧪 Testing

The template is ready for testing. Add your tests in the `tests/` directory.

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio httpx

# Run tests
uv run pytest
```

## 📦 Adding New Features

### Adding a New Model

1. Create model in `app/models/`
2. Import in `app/models/__init__.py`
3. Create migration: `alembic revision --autogenerate -m "Add new model"`
4. Apply migration: `alembic upgrade head`

### Adding New Routes

1. Create route file in `app/api/v1/routes/`
2. Create service in `app/services/`
3. Add router to `app/main.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- FastAPI team for the amazing framework
- SQLAlchemy team for the excellent ORM
- All the open-source contributors who made this possible
