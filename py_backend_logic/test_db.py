#!/usr/bin/env python3
"""
Test script to verify database functionality.
This script tests both SQLite and MySQL database connections if configured.
"""

import os
from dotenv import load_dotenv
import sys
from database import init_db, get_session, get_db_type, CVDocument

def test_database():
    """Test database connection and basic CRUD operations"""
    print("Testing database functionality...")
    
    # Initialize database
    try:
        engine = init_db()
        print(f"✅ Database initialized successfully with type: {get_db_type()}")
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False
    
    # Test session creation
    try:
        session = get_session()
        print("✅ Database session created successfully")
    except Exception as e:
        print(f"❌ Database session creation failed: {str(e)}")
        return False
    
    # Test CRUD operations
    try:
        # Create
        test_doc = CVDocument(
            filename="test_cv.pdf",
            content="This is a test CV document content."
        )
        session.add(test_doc)
        session.commit()
        print(f"✅ Created test document with ID: {test_doc.id}")
        
        # Read
        retrieved_doc = session.query(CVDocument).filter(CVDocument.id == test_doc.id).first()
        if retrieved_doc and retrieved_doc.filename == "test_cv.pdf":
            print(f"✅ Retrieved test document successfully: {retrieved_doc}")
        else:
            print("❌ Failed to retrieve test document")
            return False
        
        # Update
        retrieved_doc.content = "Updated test content"
        session.commit()
        updated_doc = session.query(CVDocument).filter(CVDocument.id == test_doc.id).first()
        if updated_doc and updated_doc.content == "Updated test content":
            print("✅ Updated test document successfully")
        else:
            print("❌ Failed to update test document")
            return False
        
        # Delete
        session.delete(retrieved_doc)
        session.commit()
        deleted_check = session.query(CVDocument).filter(CVDocument.id == test_doc.id).first()
        if deleted_check is None:
            print("✅ Deleted test document successfully")
        else:
            print("❌ Failed to delete test document")
            return False
        
        print("✅ All database operations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database operations failed: {str(e)}")
        return False
    finally:
        session.close()

def test_sqlite():
    """Test SQLite database"""
    print("\n=== Testing SQLite Database ===")
    os.environ["DB_TYPE"] = "sqlite"
    return test_database()

def test_mysql():
    """Test MySQL database if configured"""
    print("\n=== Testing MySQL Database ===")
    # Check if MySQL credentials are available
    if not all([
        os.getenv("DB_HOST"),
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_NAME")
    ]):
        print("❌ MySQL credentials not fully configured, skipping MySQL test")
        return False
    
    os.environ["DB_TYPE"] = "mysql"
    return test_database()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    print("CV Quality Scanner Database Test")
    print("================================")
    
    # Test SQLite by default
    sqlite_result = test_sqlite()
    
    # Test MySQL only if explicitly requested
    mysql_result = False
    if len(sys.argv) > 1 and sys.argv[1] == "--mysql":
        mysql_result = test_mysql()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"SQLite Test: {'✅ Passed' if sqlite_result else '❌ Failed'}")
    if len(sys.argv) > 1 and sys.argv[1] == "--mysql":
        print(f"MySQL Test: {'✅ Passed' if mysql_result else '❌ Failed'}")
    
    # Exit with appropriate status code
    if not sqlite_result or (len(sys.argv) > 1 and sys.argv[1] == "--mysql" and not mysql_result):
        sys.exit(1)
    sys.exit(0)