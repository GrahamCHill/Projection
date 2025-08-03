# Database Query Endpoint Documentation

This document provides information about the new database query endpoint added to the Projection application.

## Overview

The query endpoint allows you to retrieve data from any table in the database with filtering capabilities. It supports pagination and provides metadata about the query results.

## Endpoint Details

- **URL**: `/api/db/query/{table_name}`
- **Method**: GET
- **Path Parameters**:
  - `table_name`: The name of the table to query (users, roles, permissions, user_roles, role_permissions, cv_documents)

- **Query Parameters**:
  - `limit`: Maximum number of records to return (default: 100)
  - `offset`: Number of records to skip (default: 0)
  - Any column name from the specified table can be used as a filter parameter

## Filter Syntax

The endpoint supports several filtering options:

1. **Exact match**: `?column_name=value`
2. **NULL check**: `?column_name=null`
3. **NOT NULL check**: `?column_name=not_null`
4. **LIKE query**: `?column_name=like:pattern` (searches for pattern anywhere in the column)
5. **Greater than**: `?column_name=gt:value`
6. **Less than**: `?column_name=lt:value`

## Response Format

The endpoint returns a JSON object with the following structure:

```json
{
  "data": [
    {
      "id": 1,
      "filename": "resume.pdf",
      "content": "Sample content"
    }
  ],
  "metadata": {
    "total_count": 42,
    "limit": 100,
    "offset": 0,
    "available_filters": [
      "id",
      "username",
      "email"
    ]
  }
}
```

The `data` array contains the records matching your query.
The `metadata` object provides information about:
- `total_count`: Total number of records matching the query before pagination
- `limit`: Maximum number of records returned
- `offset`: Number of records skipped
- `available_filters`: List of column names that can be used for filtering

## Examples

### Get all CV documents

```
GET /api/db/query/cv_documents
```

### Get CV documents with pagination

```
GET /api/db/query/cv_documents?limit=10&offset=20
```

### Filter users by username

```
GET /api/db/query/users?username=admin
```

### Find roles with names containing "admin"

```
GET /api/db/query/roles?name=like:admin
```

### Get users with ID greater than 5

```
GET /api/db/query/users?id=gt:5
```

### Get active users

```
GET /api/db/query/users?is_active=true
```

## Error Handling

The endpoint returns appropriate HTTP status codes and error messages:

- **400 Bad Request**: If the table name is invalid
- **500 Internal Server Error**: If there's an error executing the database query

Error responses have the following format:

```json
{
  "error": "Error message"
}
```

## Security Considerations

This endpoint provides direct access to database tables, so it's important to consider security implications:

1. In a production environment, consider adding authentication to this endpoint
2. Consider restricting access to sensitive tables or columns
3. Implement rate limiting to prevent abuse

## Implementation Details

The endpoint is implemented in `main.py` and uses SQLAlchemy to query the database. It dynamically maps table names to SQLAlchemy models and applies filters based on query parameters.