# Database System Documentation

This document provides information about the database system implemented in the Projection application.

## Overview

The application uses PostgreSQL as its database backend:
- **PostgreSQL** - A powerful, open-source object-relational database system with over 30 years of active development
- Provides robustness, performance, and advanced features for production environments
- Supports complex queries, foreign keys, and many other features

## Configuration

Database configuration is managed through environment variables, which can be set in a `.env` file in the project root.

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `password` |
| `DB_NAME` | PostgreSQL database name | `projection` |

### Example .env Configuration

```
# Database Configuration
# PostgreSQL is the only supported database

# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=projection
```

## Database Models

The application currently has the following database models:

### CVDocument

Stores CV documents with the following fields:
- `id` (Integer, Primary Key): Unique identifier
- `filename` (String): Name of the CV file
- `content` (Text): Content of the CV
- `created_at` (DateTime): When the record was created
- `updated_at` (DateTime): When the record was last updated

## API Endpoints

The following API endpoints are available for database operations:

### Database Information
- `GET /api/db/info`: Get information about the current database configuration

### CV Documents
- `POST /api/db/documents`: Create a new CV document
  - Parameters: `filename` (string), `content` (string)
- `GET /api/db/documents`: List all CV documents
- `GET /api/db/documents/{doc_id}`: Get a specific CV document by ID
- `DELETE /api/db/documents/{doc_id}`: Delete a CV document by ID

## Testing

A test script is provided to verify database functionality:

```bash
# Test PostgreSQL connection and operations
python test_db.py
```

## Docker Setup

When using Docker, the database configuration is managed through environment variables in the `docker-compose.yml` file.

### PostgreSQL with Docker

The application is configured to use PostgreSQL by default:

1. The PostgreSQL service is defined in `docker-compose.yml`
2. The backend service depends on the PostgreSQL service
3. Data is persisted in a Docker volume named `postgres_data`

You can customize the PostgreSQL configuration by setting the following environment variables:

```
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=your_database_name
```

## Database Migration

If you're migrating from MySQL or SQLite to PostgreSQL, you'll need to:

1. Export your data from the previous database
2. Transform the data to match PostgreSQL's format if necessary
3. Import the data into PostgreSQL

PostgreSQL provides tools like `pg_dump` and `psql` for data migration. For complex migrations, consider using a dedicated migration tool or writing custom migration scripts.