"""
Test script to verify PostgreSQL connectivity and basic operations.
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "projection")

# Create database URL
db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def test_postgres_connection():
    """Test connection to PostgreSQL database"""
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Successfully connected to PostgreSQL database")
            
            # Get PostgreSQL version
            version = connection.execute(text("SELECT version()")).scalar()
            print(f"PostgreSQL version: {version}")
            
            # Test query execution
            connection.execute(text("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR(50))"))
            print("✅ Successfully created test table")
            
            # Insert data
            connection.execute(text("INSERT INTO test_table (name) VALUES ('Test Record')"))
            connection.commit()
            print("✅ Successfully inserted test record")
            
            # Query data
            result = connection.execute(text("SELECT * FROM test_table")).fetchall()
            print(f"✅ Successfully queried test table: {result}")
            
            # Clean up
            connection.execute(text("DROP TABLE test_table"))
            connection.commit()
            print("✅ Successfully cleaned up test table")
            
        return True
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL database: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing PostgreSQL connectivity...")
    success = test_postgres_connection()
    
    if success:
        print("\n🎉 All PostgreSQL tests passed!")
    else:
        print("\n❌ PostgreSQL tests failed. Please check your configuration.")