# PostgreSQL Migration Guide

This document provides information about the migration from MySQL/SQLite to PostgreSQL in the Projection application.

## Overview

The application has been updated to use PostgreSQL as its only supported database backend. This change provides several benefits:

- **Improved Performance**: PostgreSQL offers better performance for complex queries and large datasets
- **Advanced Features**: Support for JSON data types, full-text search, and other advanced features
- **Scalability**: Better support for high concurrency and large databases
- **Reliability**: Strong reputation for data integrity and reliability

## Changes Made

The following changes have been made to migrate from MySQL/SQLite to PostgreSQL:

1. Updated `database.py` to use PostgreSQL connection string
2. Removed SQLite support and simplified database configuration
3. Added PostgreSQL driver (`psycopg2-binary`) to requirements
4. Updated Docker configuration to use PostgreSQL container
5. Updated environment variables and documentation

## Migration Steps for Existing Installations

If you're upgrading an existing installation, follow these steps to migrate your data:

### From MySQL to PostgreSQL

1. **Export MySQL Data**:
   ```bash
   mysqldump -u root -p your_database > mysql_dump.sql
   ```

2. **Convert Data Format** (if needed):
   You may need to modify the SQL dump to be compatible with PostgreSQL. Tools like [pgloader](https://github.com/dimitri/pgloader) can help with this conversion.

3. **Import to PostgreSQL**:
   ```bash
   psql -U postgres -d your_database -f converted_dump.sql
   ```

### From SQLite to PostgreSQL

1. **Export SQLite Data**:
   ```bash
   sqlite3 your_database.db .dump > sqlite_dump.sql
   ```

2. **Convert Data Format**:
   SQLite and PostgreSQL have different SQL dialects. You'll need to convert the dump file to be compatible with PostgreSQL.

3. **Import to PostgreSQL**:
   ```bash
   psql -U postgres -d your_database -f converted_dump.sql
   ```

## Configuration

Update your `.env` file with the following PostgreSQL configuration:

```
# PostgreSQL Configuration
DB_HOST=localhost  # Use 'postgres' if using Docker
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=projection
```

## Testing the Connection

A test script is provided to verify PostgreSQL connectivity:

```bash
python test_postgres.py
```

This script will:
1. Connect to the PostgreSQL database
2. Create a test table
3. Insert and query data
4. Clean up the test table

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Ensure PostgreSQL is running
   - Check that the host and port are correct
   - Verify firewall settings

2. **Authentication Failed**:
   - Verify username and password
   - Check PostgreSQL's `pg_hba.conf` file for authentication settings

3. **Database Does Not Exist**:
   - Create the database: `createdb -U postgres projection`

### Getting Help

If you encounter issues with the PostgreSQL migration, please:
1. Check the application logs for detailed error messages
2. Refer to the PostgreSQL documentation: https://www.postgresql.org/docs/
3. Open an issue in the project repository with details about the problem