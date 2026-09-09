from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    content_hash = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Link(Base):
    """
    Represents a link FROM one document TO another.
    This is the raw data PageRank needs -- who links to whom.
    """
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    from_document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    to_document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)