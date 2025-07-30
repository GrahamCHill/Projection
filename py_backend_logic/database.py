from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()  # Default to SQLite if not specified
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cv_scanner")
SQLITE_PATH = os.getenv("SQLITE_PATH", "sqlite:///./cv_scanner.db")

# Create the SQLAlchemy Base
Base = declarative_base()

# Define models
class CVDocument(Base):
    __tablename__ = "cv_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CVDocument(id={self.id}, filename='{self.filename}')>"

def get_database_url():
    """
    Generate the database URL based on the configured database type
    """
    if DB_TYPE == "mysql":
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:  # Default to SQLite
        return SQLITE_PATH

def get_engine():
    """
    Create and return a database engine based on the configuration
    """
    db_url = get_database_url()
    return create_engine(db_url, echo=False)

def get_session():
    """
    Create and return a database session
    """
    engine = get_engine()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return Session()

def init_db():
    """
    Initialize the database by creating all tables
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    return engine

def get_db_type():
    """
    Return the currently configured database type
    """
    return DB_TYPE