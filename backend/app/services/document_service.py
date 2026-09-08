import hashlib
from sqlalchemy.orm import Session
from app.models.document import Document


def compute_content_hash(content: str) -> str:
    """
    Creates a short fixed-length fingerprint of the content.
    Two documents with identical content will always produce the same hash,
    which is how we detect duplicates (blueprint Step 17).
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def save_document(db: Session, title: str, url: str, content: str) -> Document | None:
    """
    Saves a new document to the database.
    Returns None if a document with identical content already exists (duplicate).
    """
    content_hash = compute_content_hash(content)

    # Check if this exact content was already saved
    existing = db.query(Document).filter(Document.content_hash == content_hash).first()
    if existing:
        return None

    document = Document(
        title=title,
        url=url,
        content=content,
        content_hash=content_hash,
    )
    db.add(document)
    db.commit()
    db.refresh(document)  # reloads the object with DB-generated fields (like id, created_at)
    return document


def get_all_documents(db: Session) -> list[Document]:
    """
    Retrieves every document currently stored.
    """
    return db.query(Document).all()