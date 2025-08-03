from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from database import get_session, User, Role, Permission, PermissionType, UserRole
from auth import (
    get_user_by_username, 
    get_user_by_email, 
    create_user, 
    verify_password, 
    create_access_token, 
    get_current_user, 
    has_permission,
    get_role_by_name,
    create_role,
    assign_role_to_user,
    remove_role_from_user,
    get_user_roles,
    get_user_permissions,
    initialize_roles_and_permissions
)

# Create router
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class RoleCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class PermissionResponse(BaseModel):
    id: int
    name: str
    resource: str
    action: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role_id: int

# Initialize roles and permissions
@router.on_event("startup")
async def startup_event():
    db = next(get_session())
    initialize_roles_and_permissions(db)

# Authentication endpoints
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    """Get an access token for authentication"""
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# User management endpoints
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_session)
):
    """Register a new user"""
    # Check if username already exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = create_user(db, user_data.username, user_data.email, user_data.password)
    
    # Assign default user role
    user_role = get_role_by_name(db, "user")
    if user_role:
        assign_role_to_user(db, user.id, user_role.id)
    
    return user

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get information about the current authenticated user"""
    return current_user

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.VIEW))
):
    """Get a list of users (requires user view permission)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.VIEW))
):
    """Get a specific user by ID (requires user view permission)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.DELETE))
):
    """Delete a user (requires user delete permission)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return None

# Role management endpoints
@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_new_role(
    role_data: RoleCreate,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.ADD))
):
    """Create a new role (requires user add permission)"""
    # Check if role already exists
    if get_role_by_name(db, role_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    # Create role
    role = create_role(db, role_data.name, role_data.description)
    return role

@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.VIEW))
):
    """Get a list of roles (requires user view permission)"""
    roles = db.query(Role).all()
    return roles

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.VIEW))
):
    """Get a specific role by ID (requires user view permission)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.DELETE))
):
    """Delete a role (requires user delete permission)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if it's a default role
    if role.name in ["admin", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default roles"
        )
    
    db.delete(role)
    db.commit()
    return None

# User-Role management endpoints
@router.get("/users/{user_id}/roles", response_model=List[RoleResponse])
async def get_user_role_list(
    user_id: int,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.VIEW))
):
    """Get roles assigned to a user (requires user view permission)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    roles = get_user_roles(db, user_id)
    return roles

@router.post("/users/{user_id}/roles", status_code=status.HTTP_200_OK)
async def add_role_to_user(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.EDIT))
):
    """Assign a role to a user (requires user edit permission)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = db.query(Role).filter(Role.id == role_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if user already has this role
    user_roles = get_user_roles(db, user_id)
    if any(r.id == role_data.role_id for r in user_roles):
        return {"message": "User already has this role"}
    
    assign_role_to_user(db, user_id, role_data.role_id)
    return {"message": "Role assigned to user"}

@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_200_OK)
async def remove_role_from_user_endpoint(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.EDIT))
):
    """Remove a role from a user (requires user edit permission)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if it's the only admin role for an admin user
    if role.name == "admin":
        admin_users = db.query(User).join(
            User.user_roles
        ).join(
            Role, Role.id == UserRole.role_id
        ).filter(
            Role.name == "admin"
        ).all()
        
        if len(admin_users) == 1 and admin_users[0].id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the only admin role from the only admin user"
            )
    
    result = remove_role_from_user(db, user_id, role_id)
    if not result:
        return {"message": "User does not have this role"}
    
    return {"message": "Role removed from user"}

# Permission endpoints
@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.VIEW))
):
    """Get a list of all permissions (requires user view permission)"""
    permissions = db.query(Permission).all()
    return permissions

@router.get("/users/{user_id}/permissions", response_model=List[PermissionResponse])
async def get_user_permission_list(
    user_id: int,
    db: Session = Depends(get_session),
    _: bool = Depends(has_permission("user", PermissionType.VIEW))
):
    """Get permissions assigned to a user through their roles (requires user view permission)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    permissions = get_user_permissions(db, user_id)
    return permissions

# Create admin user if none exists
@router.on_event("startup")
async def create_admin_user():
    """Create an admin user if none exists"""
    db = next(get_session())
    
    # Check if admin role exists
    admin_role = get_role_by_name(db, "admin")
    if not admin_role:
        return
    
    # Check if any admin user exists
    admin_users = db.query(User).join(
        User.user_roles
    ).join(
        Role, Role.id == UserRole.role_id
    ).filter(
        Role.name == "admin"
    ).all()
    
    if not admin_users:
        # Create admin user
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_password = "adminpassword"  # This should be changed immediately
        
        # Check if username already exists
        if get_user_by_username(db, admin_username):
            return
        
        # Create user
        admin_user = create_user(db, admin_username, admin_email, admin_password)
        
        # Assign admin role
        assign_role_to_user(db, admin_user.id, admin_role.id)
        
        print(f"Created admin user: {admin_username} (please change password immediately)")