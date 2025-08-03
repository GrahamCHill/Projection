"""
Test script to verify multi-tenancy functionality.
This script tests user authentication, role management, and permission checks.
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from main import app
from database import init_db, get_session, User, Role, Permission, PermissionType, UserRole, RolePermission
from auth import get_password_hash, create_user, create_role, assign_role_to_user, create_permission, assign_permission_to_role

# Create test client
client = TestClient(app)

class TestMultiTenancy(unittest.TestCase):
    """Test multi-tenancy functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database and create test users"""
        # Initialize database
        init_db()
        
        # Get database session
        cls.db = next(get_session())
        
        # Create test roles
        cls.admin_role = cls.db.query(Role).filter(Role.name == "admin").first()
        if not cls.admin_role:
            cls.admin_role = create_role(cls.db, "admin", "Administrator with full access")
        
        cls.user_role = cls.db.query(Role).filter(Role.name == "user").first()
        if not cls.user_role:
            cls.user_role = create_role(cls.db, "user", "Regular user with limited access")
        
        cls.editor_role = cls.db.query(Role).filter(Role.name == "editor").first()
        if not cls.editor_role:
            cls.editor_role = create_role(cls.db, "editor", "Editor with edit permissions")
        
        # Create test permissions
        resources = ["user", "cv_document"]
        actions = [PermissionType.VIEW, PermissionType.EDIT, PermissionType.ADD, PermissionType.DELETE]
        
        for resource in resources:
            for action in actions:
                perm_name = f"{resource}_{action.value}"
                permission = cls.db.query(Permission).filter(Permission.name == perm_name).first()
                if not permission:
                    permission = create_permission(
                        cls.db, 
                        perm_name, 
                        resource, 
                        action, 
                        f"Permission to {action.value} {resource}"
                    )
                
                # Assign all permissions to admin role
                if cls.admin_role:
                    db_role_permission = cls.db.query(RolePermission).filter(
                        RolePermission.role_id == cls.admin_role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    if not db_role_permission:
                        assign_permission_to_role(cls.db, cls.admin_role.id, permission.id)
                
                # Assign view and add permissions to user role for cv_documents
                if cls.user_role and resource == "cv_document" and action in [PermissionType.VIEW, PermissionType.ADD]:
                    db_role_permission = cls.db.query(RolePermission).filter(
                        RolePermission.role_id == cls.user_role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    if not db_role_permission:
                        assign_permission_to_role(cls.db, cls.user_role.id, permission.id)
                
                # Assign view permission to user role for users
                if cls.user_role and resource == "user" and action == PermissionType.VIEW:
                    db_role_permission = cls.db.query(RolePermission).filter(
                        RolePermission.role_id == cls.user_role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    if not db_role_permission:
                        assign_permission_to_role(cls.db, cls.user_role.id, permission.id)
                
                # Assign edit permissions to editor role
                if cls.editor_role and action == PermissionType.EDIT:
                    db_role_permission = cls.db.query(RolePermission).filter(
                        RolePermission.role_id == cls.editor_role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    if not db_role_permission:
                        assign_permission_to_role(cls.db, cls.editor_role.id, permission.id)
                
                # Assign view permissions to editor role
                if cls.editor_role and action == PermissionType.VIEW:
                    db_role_permission = cls.db.query(RolePermission).filter(
                        RolePermission.role_id == cls.editor_role.id,
                        RolePermission.permission_id == permission.id
                    ).first()
                    if not db_role_permission:
                        assign_permission_to_role(cls.db, cls.editor_role.id, permission.id)
        
        # Create test users
        cls.admin_user = cls.db.query(User).filter(User.username == "test_admin").first()
        if not cls.admin_user:
            cls.admin_user = create_user(cls.db, "test_admin", "admin@test.com", "adminpass")
            assign_role_to_user(cls.db, cls.admin_user.id, cls.admin_role.id)
        
        cls.regular_user = cls.db.query(User).filter(User.username == "test_user").first()
        if not cls.regular_user:
            cls.regular_user = create_user(cls.db, "test_user", "user@test.com", "userpass")
            assign_role_to_user(cls.db, cls.regular_user.id, cls.user_role.id)
        
        cls.editor_user = cls.db.query(User).filter(User.username == "test_editor").first()
        if not cls.editor_user:
            cls.editor_user = create_user(cls.db, "test_editor", "editor@test.com", "editorpass")
            assign_role_to_user(cls.db, cls.editor_user.id, cls.editor_role.id)
        
        print("Test setup completed")
    
    def get_token(self, username, password):
        """Helper method to get authentication token"""
        response = client.post(
            "/api/auth/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    
    def test_01_user_authentication(self):
        """Test user authentication"""
        print("\n=== Testing User Authentication ===")
        
        # Test valid login
        response = client.post(
            "/api/auth/token",
            data={"username": "test_admin", "password": "adminpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertIn("token_type", response.json())
        print("✅ Admin login successful")
        
        # Test invalid login
        response = client.post(
            "/api/auth/token",
            data={"username": "test_admin", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 401)
        print("✅ Invalid login rejected")
    
    def test_02_user_registration(self):
        """Test user registration"""
        print("\n=== Testing User Registration ===")
        
        # Test user registration
        response = client.post(
            "/api/auth/users",
            json={
                "username": "new_test_user",
                "email": "newuser@test.com",
                "password": "newuserpass"
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "new_test_user")
        self.assertEqual(response.json()["email"], "newuser@test.com")
        print("✅ User registration successful")
        
        # Test duplicate username
        response = client.post(
            "/api/auth/users",
            json={
                "username": "new_test_user",
                "email": "another@test.com",
                "password": "anotherpass"
            }
        )
        self.assertEqual(response.status_code, 400)
        print("✅ Duplicate username rejected")
    
    def test_03_role_management(self):
        """Test role management"""
        print("\n=== Testing Role Management ===")
        
        # Get admin token
        admin_token = self.get_token("test_admin", "adminpass")
        self.assertIsNotNone(admin_token)
        
        # Test creating a new role
        response = client.post(
            "/api/auth/roles",
            json={"name": "tester", "description": "Role for testers"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "tester")
        print("✅ Role creation successful")
        
        # Test getting roles
        response = client.get(
            "/api/auth/roles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        roles = response.json()
        self.assertTrue(len(roles) >= 4)  # admin, user, editor, tester
        print(f"✅ Retrieved {len(roles)} roles")
    
    def test_04_permission_checks(self):
        """Test permission checks"""
        print("\n=== Testing Permission Checks ===")
        
        # Get tokens
        admin_token = self.get_token("test_admin", "adminpass")
        user_token = self.get_token("test_user", "userpass")
        editor_token = self.get_token("test_editor", "editorpass")
        
        self.assertIsNotNone(admin_token)
        self.assertIsNotNone(user_token)
        self.assertIsNotNone(editor_token)
        
        # Test admin permissions (can view users)
        response = client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        print("✅ Admin can view users")
        
        # Test regular user permissions (can view users)
        response = client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        self.assertEqual(response.status_code, 200)
        print("✅ Regular user can view users")
        
        # Test editor permissions (can view users)
        response = client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {editor_token}"}
        )
        self.assertEqual(response.status_code, 200)
        print("✅ Editor can view users")
        
        # Test admin permissions (can create roles)
        response = client.post(
            "/api/auth/roles",
            json={"name": "viewer", "description": "Role for viewers"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 201)
        print("✅ Admin can create roles")
        
        # Test regular user permissions (cannot create roles)
        response = client.post(
            "/api/auth/roles",
            json={"name": "invalid_role", "description": "This should fail"},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        self.assertEqual(response.status_code, 403)
        print("✅ Regular user cannot create roles")
    
    def test_05_user_role_assignment(self):
        """Test user-role assignment"""
        print("\n=== Testing User-Role Assignment ===")
        
        # Get admin token
        admin_token = self.get_token("test_admin", "adminpass")
        self.assertIsNotNone(admin_token)
        
        # Get the tester role ID
        response = client.get(
            "/api/auth/roles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        roles = response.json()
        tester_role = next((r for r in roles if r["name"] == "tester"), None)
        self.assertIsNotNone(tester_role)
        
        # Assign tester role to regular user
        response = client.post(
            f"/api/auth/users/{self.regular_user.id}/roles",
            json={"role_id": tester_role["id"]},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        print("✅ Role assignment successful")
        
        # Check user roles
        response = client.get(
            f"/api/auth/users/{self.regular_user.id}/roles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        roles = response.json()
        role_names = [r["name"] for r in roles]
        self.assertIn("user", role_names)
        self.assertIn("tester", role_names)
        print(f"✅ User has roles: {', '.join(role_names)}")
    
    def test_06_document_access_control(self):
        """Test document access control"""
        print("\n=== Testing Document Access Control ===")
        
        # Get tokens
        admin_token = self.get_token("test_admin", "adminpass")
        user_token = self.get_token("test_user", "userpass")
        
        # Admin creates a document
        response = client.post(
            "/api/db/documents",
            params={"filename": "admin_doc.txt", "content": "This is an admin document"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        admin_doc_id = response.json()["id"]
        print("✅ Admin created document")
        
        # User creates a document
        response = client.post(
            "/api/db/documents",
            params={"filename": "user_doc.txt", "content": "This is a user document"},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        self.assertEqual(response.status_code, 200)
        user_doc_id = response.json()["id"]
        print("✅ User created document")
        
        # Admin can view all documents
        response = client.get(
            "/api/db/documents",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        docs = response.json()
        self.assertTrue(len(docs) >= 2)
        print(f"✅ Admin can view all documents ({len(docs)} documents)")
        
        # User can view all documents
        response = client.get(
            "/api/db/documents",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        self.assertEqual(response.status_code, 200)
        docs = response.json()
        self.assertTrue(len(docs) >= 2)
        print(f"✅ User can view all documents ({len(docs)} documents)")
        
        # Admin can delete any document
        response = client.delete(
            f"/api/db/documents/{user_doc_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        print("✅ Admin can delete user's document")
        
        # Clean up admin's document
        response = client.delete(
            f"/api/db/documents/{admin_doc_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        print("✅ Admin deleted own document")

def test_multi_tenancy():
    """Run multi-tenancy tests"""
    print("Multi-Tenancy Test Suite")
    print("========================")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    test_multi_tenancy()