# Multi-Tenancy Implementation

This document provides information about the multi-tenancy system implemented in the CV Quality Scanner application.

## Overview

The application now supports a comprehensive multi-tenancy setup with the following features:

1. **User Management**: Create, read, update, and delete users
2. **Role-Based Access Control (RBAC)**: Assign customizable roles to users
3. **Permission System**: Fine-grained permissions for different resources and actions
4. **Redis Caching**: Optional caching for user-role combinations to improve performance

## Database Models

The multi-tenancy implementation adds the following database models:

### User

Stores user information with the following fields:
- `id` (Integer, Primary Key): Unique identifier
- `username` (String): Unique username
- `email` (String): Unique email address
- `password_hash` (String): Hashed password
- `is_active` (Boolean): Whether the user is active
- `created_at` (DateTime): When the record was created
- `updated_at` (DateTime): When the record was last updated

### Role

Defines roles that can be assigned to users:
- `id` (Integer, Primary Key): Unique identifier
- `name` (String): Unique role name
- `description` (String): Description of the role
- `created_at` (DateTime): When the record was created
- `updated_at` (DateTime): When the record was last updated

### Permission

Defines permissions that can be assigned to roles:
- `id` (Integer, Primary Key): Unique identifier
- `name` (String): Unique permission name
- `resource` (String): Resource type (e.g., 'user', 'cv_document')
- `action` (Enum): Action type (VIEW, EDIT, ADD, DELETE)
- `description` (String): Description of the permission
- `created_at` (DateTime): When the record was created
- `updated_at` (DateTime): When the record was last updated

### UserRole

Many-to-many relationship between users and roles:
- `id` (Integer, Primary Key): Unique identifier
- `user_id` (Integer, Foreign Key): Reference to User
- `role_id` (Integer, Foreign Key): Reference to Role
- `created_at` (DateTime): When the record was created

### RolePermission

Many-to-many relationship between roles and permissions:
- `id` (Integer, Primary Key): Unique identifier
- `role_id` (Integer, Foreign Key): Reference to Role
- `permission_id` (Integer, Foreign Key): Reference to Permission
- `created_at` (DateTime): When the record was created

## Default Roles and Permissions

The system initializes with two default roles:

1. **Admin**: Has full access to all resources and actions
2. **User**: Has limited access based on predefined permissions

The following permissions are created by default:

- `user_view`: View user information
- `user_edit`: Edit user information
- `user_add`: Add new users
- `user_delete`: Delete users
- `cv_document_view`: View CV documents
- `cv_document_edit`: Edit CV documents
- `cv_document_add`: Add new CV documents
- `cv_document_delete`: Delete CV documents

## API Endpoints

The following API endpoints are available for multi-tenancy operations:

### Authentication
- `POST /api/auth/token`: Get an access token (login)
- `POST /api/auth/users`: Register a new user
- `GET /api/auth/users/me`: Get current user information

### User Management
- `GET /api/auth/users`: List all users
- `GET /api/auth/users/{user_id}`: Get a specific user
- `DELETE /api/auth/users/{user_id}`: Delete a user

### Role Management
- `POST /api/auth/roles`: Create a new role
- `GET /api/auth/roles`: List all roles
- `GET /api/auth/roles/{role_id}`: Get a specific role
- `DELETE /api/auth/roles/{role_id}`: Delete a role

### User-Role Management
- `GET /api/auth/users/{user_id}/roles`: Get roles assigned to a user
- `POST /api/auth/users/{user_id}/roles`: Assign a role to a user
- `DELETE /api/auth/users/{user_id}/roles/{role_id}`: Remove a role from a user

### Permission Management
- `GET /api/auth/permissions`: List all permissions
- `GET /api/auth/users/{user_id}/permissions`: Get permissions assigned to a user

## Redis Caching

The application includes optional Redis caching for user-role combinations to improve performance. When enabled, the system caches:

1. **User Roles**: The roles assigned to each user
2. **User Permissions**: The permissions assigned to each user through their roles

### Benefits of Redis Caching

Redis caching provides several benefits for the multi-tenancy implementation:

1. **Reduced Database Load**: Fewer database queries are needed to check user permissions
2. **Improved Response Time**: Permission checks are faster, especially for users with many roles
3. **Scalability**: The system can handle more concurrent users without database performance degradation
4. **Reduced Latency**: Critical permission checks have lower latency, improving user experience

### When to Enable Redis Caching

Redis caching is particularly beneficial in the following scenarios:

1. **High User Count**: Systems with many users (thousands or more)
2. **Complex Role Structures**: Users with multiple roles and many permissions
3. **High Traffic**: Applications with many concurrent users
4. **Distributed Deployment**: When the application is deployed across multiple servers

### Configuration

Redis caching can be enabled by setting the following environment variables:

```
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password  # Optional
```

## Usage Examples

### Creating a New Role

```python
import requests

# Login to get token
response = requests.post(
    "http://localhost:8000/api/auth/token",
    data={"username": "admin", "password": "adminpassword"}
)
token = response.json()["access_token"]

# Create a new role
response = requests.post(
    "http://localhost:8000/api/auth/roles",
    json={"name": "editor", "description": "Can edit but not delete"},
    headers={"Authorization": f"Bearer {token}"}
)
```

### Assigning a Role to a User

```python
import requests

# Login to get token
response = requests.post(
    "http://localhost:8000/api/auth/token",
    data={"username": "admin", "password": "adminpassword"}
)
token = response.json()["access_token"]

# Assign a role to a user
response = requests.post(
    "http://localhost:8000/api/auth/users/2/roles",
    json={"role_id": 3},  # Assign role with ID 3 to user with ID 2
    headers={"Authorization": f"Bearer {token}"}
)
```

## Security Considerations

1. **Password Hashing**: All passwords are hashed using bcrypt
2. **JWT Authentication**: JSON Web Tokens are used for authentication
3. **Permission Checks**: All protected endpoints verify appropriate permissions
4. **Role Separation**: Clear separation between admin and regular user roles
5. **Data Isolation**: Users can only delete their own documents unless they have admin privileges

## Conclusion

The multi-tenancy implementation provides a robust foundation for user management, role-based access control, and permission management. The optional Redis caching enhances performance and scalability for larger deployments.

By using this system, the application can support multiple users with customizable roles and permissions, ensuring that users only have access to the features and data they are authorized to use.