from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

from database import User, Role, Permission, UserRole, RolePermission, PermissionType, get_session

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Redis client for caching (if enabled)
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
if REDIS_ENABLED:
    try:
        import redis
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD", None),
            decode_responses=True
        )
        print("Redis cache enabled for user-role combinations")
    except ImportError:
        print("Redis package not installed. Caching disabled.")
        REDIS_ENABLED = False
else:
    print("Redis cache disabled")

# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash"""
    return pwd_context.hash(password)

# User management functions
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, username: str, email: str, password: str) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(password)
    db_user = User(username=username, email=email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Role management functions
def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Get a role by name"""
    return db.query(Role).filter(Role.name == name).first()

def create_role(db: Session, name: str, description: str = None) -> Role:
    """Create a new role"""
    db_role = Role(name=name, description=description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def assign_role_to_user(db: Session, user_id: int, role_id: int) -> UserRole:
    """Assign a role to a user"""
    db_user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    
    # Clear cache if Redis is enabled
    if REDIS_ENABLED:
        try:
            redis_client.delete(f"user_roles:{user_id}")
            redis_client.delete(f"user_permissions:{user_id}")
        except Exception as e:
            print(f"Redis cache clearing error: {str(e)}")
    
    return db_user_role

def remove_role_from_user(db: Session, user_id: int, role_id: int) -> bool:
    """Remove a role from a user"""
    db_user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    
    if db_user_role:
        db.delete(db_user_role)
        db.commit()
        
        # Clear cache if Redis is enabled
        if REDIS_ENABLED:
            try:
                redis_client.delete(f"user_roles:{user_id}")
                redis_client.delete(f"user_permissions:{user_id}")
            except Exception as e:
                print(f"Redis cache clearing error: {str(e)}")
        
        return True
    return False

# Permission management functions
def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    """Get a permission by name"""
    return db.query(Permission).filter(Permission.name == name).first()

def create_permission(
    db: Session, 
    name: str, 
    resource: str, 
    action: PermissionType, 
    description: str = None
) -> Permission:
    """Create a new permission"""
    db_permission = Permission(
        name=name,
        resource=resource,
        action=action,
        description=description
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def assign_permission_to_role(db: Session, role_id: int, permission_id: int) -> RolePermission:
    """Assign a permission to a role"""
    db_role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(db_role_permission)
    db.commit()
    db.refresh(db_role_permission)
    
    # Clear all user permission caches if Redis is enabled
    if REDIS_ENABLED:
        try:
            # Get all users with this role
            user_roles = db.query(UserRole).filter(UserRole.role_id == role_id).all()
            for user_role in user_roles:
                redis_client.delete(f"user_permissions:{user_role.user_id}")
        except Exception as e:
            print(f"Redis cache clearing error: {str(e)}")
    
    return db_role_permission

def remove_permission_from_role(db: Session, role_id: int, permission_id: int) -> bool:
    """Remove a permission from a role"""
    db_role_permission = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    
    if db_role_permission:
        db.delete(db_role_permission)
        db.commit()
        
        # Clear all user permission caches if Redis is enabled
        if REDIS_ENABLED:
            try:
                # Get all users with this role
                user_roles = db.query(UserRole).filter(UserRole.role_id == role_id).all()
                for user_role in user_roles:
                    redis_client.delete(f"user_permissions:{user_role.user_id}")
            except Exception as e:
                print(f"Redis cache clearing error: {str(e)}")
        
        return True
    return False

# User role and permission checking
def get_user_roles(db: Session, user_id: int) -> List[Role]:
    """Get all roles assigned to a user"""
    # Try to get from cache first if Redis is enabled
    if REDIS_ENABLED:
        try:
            cached_roles = redis_client.get(f"user_roles:{user_id}")
            if cached_roles:
                import json
                return json.loads(cached_roles)
        except Exception as e:
            print(f"Redis cache retrieval error: {str(e)}")
    
    # Get from database
    user_roles = db.query(Role).join(UserRole).filter(UserRole.user_id == user_id).all()
    
    # Cache the result if Redis is enabled
    if REDIS_ENABLED:
        try:
            import json
            redis_client.setex(
                f"user_roles:{user_id}",
                timedelta(minutes=30),
                json.dumps([{
                    "id": role.id,
                    "name": role.name,
                    "description": role.description
                } for role in user_roles])
            )
        except Exception as e:
            print(f"Redis cache storage error: {str(e)}")
    
    return user_roles

def get_user_permissions(db: Session, user_id: int) -> List[Permission]:
    """Get all permissions assigned to a user through their roles"""
    # Try to get from cache first if Redis is enabled
    if REDIS_ENABLED:
        try:
            cached_permissions = redis_client.get(f"user_permissions:{user_id}")
            if cached_permissions:
                import json
                return json.loads(cached_permissions)
        except Exception as e:
            print(f"Redis cache retrieval error: {str(e)}")
    
    # Get from database
    permissions = db.query(Permission).join(
        RolePermission, RolePermission.permission_id == Permission.id
    ).join(
        Role, Role.id == RolePermission.role_id
    ).join(
        UserRole, UserRole.role_id == Role.id
    ).filter(
        UserRole.user_id == user_id
    ).distinct().all()
    
    # Cache the result if Redis is enabled
    if REDIS_ENABLED:
        try:
            import json
            redis_client.setex(
                f"user_permissions:{user_id}",
                timedelta(minutes=30),
                json.dumps([{
                    "id": permission.id,
                    "name": permission.name,
                    "resource": permission.resource,
                    "action": permission.action.value,
                    "description": permission.description
                } for permission in permissions])
            )
        except Exception as e:
            print(f"Redis cache storage error: {str(e)}")
    
    return permissions

def user_has_permission(
    db: Session, 
    user_id: int, 
    resource: str, 
    action: PermissionType
) -> bool:
    """Check if a user has a specific permission"""
    permissions = get_user_permissions(db, user_id)
    return any(
        p.resource == resource and p.action == action
        for p in permissions
    )

# JWT token functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode a JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Authentication dependency
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    """Get the current authenticated user from the JWT token"""
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Permission dependency
def has_permission(resource: str, action: PermissionType):
    """Dependency to check if the current user has a specific permission"""
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_session)
    ) -> bool:
        if not user_has_permission(db, current_user.id, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions to {action.value} {resource}"
            )
        return True
    return permission_dependency

# Initialize default roles and permissions
def initialize_roles_and_permissions(db: Session):
    """Initialize default roles and permissions"""
    # Create default roles if they don't exist
    admin_role = get_role_by_name(db, "admin")
    if not admin_role:
        admin_role = create_role(db, "admin", "Administrator with full access")
    
    user_role = get_role_by_name(db, "user")
    if not user_role:
        user_role = create_role(db, "user", "Regular user with limited access")
    
    # Create default permissions if they don't exist
    resources = ["user", "cv_document"]
    actions = [PermissionType.VIEW, PermissionType.EDIT, PermissionType.ADD, PermissionType.DELETE]
    
    for resource in resources:
        for action in actions:
            perm_name = f"{resource}_{action.value}"
            permission = get_permission_by_name(db, perm_name)
            if not permission:
                permission = create_permission(
                    db, 
                    perm_name, 
                    resource, 
                    action, 
                    f"Permission to {action.value} {resource}"
                )
            
            # Assign all permissions to admin role
            if admin_role:
                db_role_permission = db.query(RolePermission).filter(
                    RolePermission.role_id == admin_role.id,
                    RolePermission.permission_id == permission.id
                ).first()
                if not db_role_permission:
                    assign_permission_to_role(db, admin_role.id, permission.id)
            
            # Assign view and add permissions to user role for cv_documents
            if user_role and resource == "cv_document" and action in [PermissionType.VIEW, PermissionType.ADD]:
                db_role_permission = db.query(RolePermission).filter(
                    RolePermission.role_id == user_role.id,
                    RolePermission.permission_id == permission.id
                ).first()
                if not db_role_permission:
                    assign_permission_to_role(db, user_role.id, permission.id)
            
            # Assign view permission to user role for users
            if user_role and resource == "user" and action == PermissionType.VIEW:
                db_role_permission = db.query(RolePermission).filter(
                    RolePermission.role_id == user_role.id,
                    RolePermission.permission_id == permission.id
                ).first()
                if not db_role_permission:
                    assign_permission_to_role(db, user_role.id, permission.id)
    
    print("Default roles and permissions initialized")