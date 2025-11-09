# ProjectBoard

A collaborative project management API with document storage capabilities. Built with FastAPI, PostgreSQL, and AWS S3.

## 🚀 Features

- **User Authentication & Authorization**
  - JWT-based authentication
  - Secure password hashing with bcrypt
  - Token-based API access

- **Project Management**
  - Create and manage projects
  - Invite collaborators to projects
  - Owner and member access control
  - Track project metadata and storage usage

- **Document Storage**
  - Upload documents to projects (stored in AWS S3)
  - Download documents via presigned URLs
  - Replace and delete documents
  - Search and filter documents by filename
  - Automatic storage quota tracking

- **AWS Lambda Integration**
  - Automated S3 event processing
  - Real-time storage size tracking

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0
- **Authentication:** JWT (python-jose)
- **Cloud Storage:** AWS S3
- **Containerization:** Docker & Docker Compose
- **Database Migrations:** Alembic
- **Python:** 3.10+

## 📋 Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- PostgreSQL 16 (or use the provided Docker setup)
- AWS Account with S3 access
- Poetry (Python package manager)

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/ahkazak23/projectboard.git
cd projectboard
```

### 2. Set up environment variables

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` and update the following variables:

```env
# PostgreSQL Configuration
POSTGRES_USER=appuser
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=projectboard
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql+psycopg://appuser:your-secure-password@db:5432/projectboard

# JWT Configuration
JWT_SECRET=your-long-random-secret-key
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Server Configuration
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000

# AWS Configuration
AWS_REGION=us-east-1
S3_BUCKET=your-s3-bucket-name
```

Create `.awsenv` file for AWS credentials:

```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

### 3. Using Docker (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Run database migrations
docker-compose exec api poetry run alembic upgrade head

# Check logs
docker-compose logs -f api
```

The API will be available at `http://localhost:80`

### 4. Local Development Setup

```bash
# Install dependencies with Poetry
poetry install

# Run database migrations
poetry run alembic upgrade head

# Start the development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 🗄️ Database Migrations

Create a new migration:

```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
poetry run alembic upgrade head
```

Rollback migrations:

```bash
poetry run alembic downgrade -1
```

## 📚 API Endpoints

### Health Check
- `GET /health` - Check API status

### Authentication
- `POST /auth` - Register a new user
- `POST /auth/login` - Login and get JWT token

### Projects
- `POST /projects` - Create a new project
- `GET /projects` - List all accessible projects
- `GET /project/{project_id}/info` - Get project details
- `PUT /project/{project_id}/info` - Update project details
- `DELETE /project/{project_id}` - Delete project (owner only)
- `POST /project/{project_id}/invite?user={login}` - Invite user to project

### Documents
- `POST /projects/{project_id}/documents` - Upload a document
- `GET /projects/{project_id}/documents` - List project documents (with pagination and search)
- `GET /document/{doc_id}?ttl={seconds}` - Get presigned download URL
- `PUT /document/{doc_id}` - Replace a document
- `DELETE /document/{doc_id}` - Delete a document (owner only)

## 📖 API Documentation

When the server is running, you can access:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test markers
poetry run pytest -m api
poetry run pytest -m auth
```

## 🧹 Code Quality

The project uses several tools to maintain code quality:

```bash
# Format code with Black
poetry run black app

# Sort imports with isort
poetry run isort app

# Lint with Ruff
poetry run ruff check app

# Check for unused dependencies
poetry run deptry app
```

## 📁 Project Structure

```
projectboard/
├── app/
│   ├── api/
│   │   └── routers/          # API route handlers
│   │       ├── auth.py       # Authentication endpoints
│   │       ├── project.py    # Project management endpoints
│   │       └── document.py   # Document management endpoints
│   ├── core/
│   │   ├── config.py         # Configuration settings
│   │   ├── deps.py           # Dependency injection
│   │   ├── errors.py         # Error handlers
│   │   ├── security.py       # Security utilities
│   │   └── storage_s3.py     # S3 integration
│   ├── db/
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── document.py
│   │   │   └── project_access.py
│   │   └── session.py        # Database session management
│   ├── migrations/           # Alembic migrations
│   ├── schemas/              # Pydantic schemas
│   │   ├── auth.py
│   │   ├── project.py
│   │   └── document.py
│   ├── services/             # Business logic
│   │   ├── auth.py
│   │   ├── project.py
│   │   └── document.py
│   ├── tests/                # Test suite
│   └── main.py               # Application entry point
├── lambdas/
│   └── s3_size_updater/      # AWS Lambda for S3 event handling
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # API container definition
├── pyproject.toml            # Poetry dependencies and configuration
├── alembic.ini               # Alembic configuration
└── README.md
```

## 🔐 Security Considerations

- All passwords are hashed using bcrypt
- JWT tokens expire after the configured time (default: 60 minutes)
- API endpoints require authentication (except `/health`, `/auth`, and `/auth/login`)
- Project access is controlled via owner and member permissions
- S3 presigned URLs are time-limited (default: 600 seconds, max: 3600 seconds)
- Environment variables are used for sensitive configuration

## 🚀 AWS Lambda Setup

The project includes a Lambda function for tracking S3 storage usage:

1. Navigate to the lambda directory:
   ```bash
   cd lambdas/s3_size_updater
   ```

2. Build and deploy using Docker:
   ```bash
   docker build -t s3-size-updater .
   ```

3. Configure the Lambda to trigger on S3 events (ObjectCreated, ObjectRemoved)

4. Set environment variables:
   - `DB_SECRET_NAME`: AWS Secrets Manager secret containing database URL

## 🐛 Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `docker-compose ps`
- Check connection string in `.env`
- Verify database exists: `docker-compose exec db psql -U appuser -d projectboard`

### S3 Upload/Download Issues
- Verify AWS credentials in `.awsenv`
- Check S3 bucket name and region in `.env`
- Ensure bucket permissions allow read/write operations

### Migration Issues
- Reset database: `docker-compose down -v && docker-compose up -d`
- Run migrations: `docker-compose exec api poetry run alembic upgrade head`

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Alihan Kazak**
- Email: ahkazak23@gmail.com
- GitHub: [@ahkazak23](https://github.com/ahkazak23)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Notes

- Default project size limit: 10 MB
- Maximum page size for document listing: 200 items
- PostgreSQL runs on port 5433 (mapped from container's 5432)
- API runs on port 80 (mapped from container's 8000)
