from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Association tables for many-to-many relationships
repository_tag = Table(
    'repository_tag',
    Base.metadata,
    Column('repository_id', Integer, ForeignKey('github_repositories.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('repository_tags.id'), primary_key=True)
)

repository_project = Table(
    'repository_project',
    Base.metadata,
    Column('repository_id', Integer, ForeignKey('github_repositories.id'), primary_key=True),
    Column('project_id', Integer, ForeignKey('repository_projects.id'), primary_key=True)
)

class GitHubRepository(Base):
    """
    Model for GitHub repositories
    """
    __tablename__ = "github_repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    full_name = Column(String(255), index=True, unique=True)
    url = Column(String(255))
    html_url = Column(String(255))
    description = Column(Text, nullable=True)
    is_private = Column(Boolean, default=False)
    owner_name = Column(String(255))
    owner_type = Column(String(50))  # User or Organization
    last_polled = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tags = relationship("RepositoryTag", secondary=repository_tag, back_populates="repositories")
    projects = relationship("RepositoryProject", secondary=repository_project, back_populates="repositories")
    
    def __repr__(self):
        return f"<GitHubRepository(id={self.id}, full_name='{self.full_name}')>"

class RepositoryTag(Base):
    """
    Model for repository tags
    """
    __tablename__ = "repository_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#CCCCCC")  # Hex color code
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repositories = relationship("GitHubRepository", secondary=repository_tag, back_populates="tags")
    
    def __repr__(self):
        return f"<RepositoryTag(id={self.id}, name='{self.name}')>"

class RepositoryProject(Base):
    """
    Model for repository projects
    """
    __tablename__ = "repository_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repositories = relationship("GitHubRepository", secondary=repository_project, back_populates="projects")
    
    def __repr__(self):
        return f"<RepositoryProject(id={self.id}, name='{self.name}')>"