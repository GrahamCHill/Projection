# Database System Documentation

This document provides information about the database system implemented in the Projection application.

## Overview

The application supports two database backends:
1. **SQLite** (default) - A file-based database that requires no additional setup
2. **MySQL** - A more robust database system for production environments

The system is designed to allow easy switching between these database types when initially setting up an instance.

## Configuration

Database configuration is managed through environment variables, which can be set in a `.env` file in the project root.

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `DB_TYPE` | Database type (`sqlite` or `mysql`) | `sqlite` |
| `SQLITE_PATH` | SQLite database file path | `sqlite:///./cv_scanner.db` |
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | `password` |
| `DB_NAME` | MySQL database name | `cv_scanner` |

### Example .env Configuration

```
# Database Configuration
# Options: sqlite, mysql
DB_TYPE=sqlite

# SQLite Configuration (used when DB_TYPE=sqlite)
SQLITE_PATH=sqlite:///./cv_scanner.db

# MySQL Configuration (used when DB_TYPE=mysql)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=cv_scanner
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
# Test SQLite (default)
python test_db.py

# Test MySQL (if configured)
python test_db.py --mysql
```

## Docker Setup

When using Docker, the database configuration is managed through environment variables in the `docker-compose.yml` file.

### Using SQLite with Docker

To use SQLite (default), no additional configuration is needed. You may want to comment out the `depends_on` section for the MySQL service in the backend service configuration.

### Using MySQL with Docker

To use MySQL:
1. Set `DB_TYPE=mysql` in your `.env` file
2. Ensure the MySQL service is uncommented in `docker-compose.yml`
3. Make sure the backend service has the `depends_on` section for MySQL uncommented

## Switching Database Types

To switch between database types:

1. Update the `DB_TYPE` environment variable in your `.env` file
2. If using Docker, adjust the `docker-compose.yml` file as needed
3. Restart the application

Note that data is not automatically migrated between database types. If you need to migrate data, you'll need to implement a custom migration script.