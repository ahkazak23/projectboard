# ProjectBoard

A FastAPI-based project management application with document storage using AWS S3.

## Features

- User authentication with JWT
- Project and task management
- Document upload and storage in AWS S3
- PostgreSQL database
- Docker containerization

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Storage**: AWS S3
- **Authentication**: JWT with bcrypt
- **Testing**: pytest
- **Containerization**: Docker, Docker Compose

## Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- Docker and Docker Compose (for containerized deployment)
- AWS account with S3 bucket (for document storage)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ahkazak23/projectboard.git
cd projectboard
```

### 2. Install Dependencies

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 3. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` and configure:
- Database credentials
- JWT secret
- AWS credentials (see [AWS Configuration](#aws-configuration))

### 4. Run with Docker Compose

```bash
docker-compose up -d
```

The API will be available at `http://localhost:80`

### 5. Run Tests

```bash
poetry run pytest
```

### 6. Lint and Format Code

```bash
# Run linter
poetry run ruff check . --fix

# Format code
poetry run black .
poetry run isort .

# Verify formatting
poetry run black --check .
poetry run isort --check-only .
```

## AWS Configuration

This application uses AWS S3 for document storage. You have two options for AWS authentication:

### Option 1: Using AWS Access Keys (Traditional)

Set the following environment variables in `.env`:

```bash
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
```

### Option 2: Using OIDC for GitHub Actions (Recommended)

For GitHub Actions workflows, use OpenID Connect (OIDC) instead of long-lived credentials for enhanced security.

**📖 See [AWS_OIDC_SETUP.md](./AWS_OIDC_SETUP.md) for detailed configuration guide**

**Quick answer**: Do you need to configure anything on the GitHub side for OIDC? **NO** - All configuration is done in AWS IAM.

Benefits of OIDC:
- ✅ No credential rotation needed
- ✅ Short-lived, auto-expiring tokens
- ✅ Better security and audit trails
- ✅ No secrets stored in GitHub

## Project Structure

```
projectboard/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core functionality (config, security, S3)
│   ├── db/            # Database models and migrations
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── tests/         # Test suite
├── .github/
│   └── workflows/     # GitHub Actions CI/CD
├── docker-compose.yml # Container orchestration
├── Dockerfile         # Container image definition
├── pyproject.toml     # Poetry dependencies and config
└── env.example        # Environment variables template
```

## API Endpoints

The API documentation is available at:
- Swagger UI: `http://localhost:80/docs`
- ReDoc: `http://localhost:80/redoc`

## CI/CD

This project uses GitHub Actions for continuous integration:

- **Linting**: Ruff, Black, isort
- **Testing**: pytest
- **Branch Protection**: Runs on `main` and `sprint-3` branches

See [AWS_OIDC_SETUP.md](./AWS_OIDC_SETUP.md) for configuring AWS authentication in GitHub Actions workflows.

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `POSTGRES_USER` | PostgreSQL username | Yes | - |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes | - |
| `POSTGRES_DB` | Database name | Yes | - |
| `DB_HOST` | Database host | Yes | `localhost` |
| `DB_PORT` | Database port | Yes | `5432` |
| `DATABASE_URL` | Full database connection string | Yes | - |
| `JWT_SECRET` | Secret key for JWT tokens | Yes | - |
| `JWT_ALG` | JWT algorithm | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | No | `60` |
| `AWS_REGION` | AWS region for S3 | Yes | - |
| `S3_BUCKET` | S3 bucket name | Yes | - |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes* | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes* | - |

\* Not required when using OIDC authentication in GitHub Actions

## Troubleshooting

### S3 Connection Issues

If you encounter S3 connection errors:

1. Verify AWS credentials are correct
2. Ensure the S3 bucket exists and is in the correct region
3. Check IAM permissions for S3 access
4. Test S3 connectivity: `aws s3 ls s3://your-bucket-name`

For OIDC-related issues, see the troubleshooting section in [AWS_OIDC_SETUP.md](./AWS_OIDC_SETUP.md).

### Database Connection Issues

If the application can't connect to the database:

1. Ensure PostgreSQL is running: `docker-compose ps`
2. Check database credentials in `.env`
3. Verify the database host is correct (`db` in Docker, `localhost` otherwise)
4. Check logs: `docker-compose logs db`

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Ensure tests pass: `poetry run pytest`
4. Ensure code is formatted: `poetry run black . && poetry run isort .`
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Author

Alihan Kazak - [ahkazak23@gmail.com](mailto:ahkazak23@gmail.com)
