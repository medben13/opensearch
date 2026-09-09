from app.core.database import SessionLocal
from app.services.document_service import save_document
from app.models.document import Link

# A small, deliberately-designed link graph so PageRank's behavior is
# predictable and explainable: Hub is linked-to by everyone, so it should
# end up with the highest PageRank.
PAGES = {
    "hub": ("The Hub Page", "https://test.local/hub", "This is the central hub page that many others link to."),
    "a": ("Page A", "https://test.local/a", "Page A discusses computer science topics and links elsewhere."),
    "b": ("Page B", "https://test.local/b", "Page B covers software engineering practices."),
    "c": ("Page C", "https://test.local/c", "Page C is a small, less-linked page about databases."),
}

# (from, to) pairs -- notice hub is linked to by a, b, AND c, while
# c is linked to by no one -- this should show up clearly in the results.
LINKS = [
    ("a", "hub"),
    ("b", "hub"),
    ("c", "hub"),
    ("hub", "a"),
    ("a", "b"),
]


def generate_linked_data():
    db = SessionLocal()
    doc_ids = {}

    for key, (title, url, content) in PAGES.items():
        doc = save_document(db, title=title, url=url, content=content)
        if doc is None:
            # Already exists from a previous run -- look it up instead
            from app.models.document import Document
            doc = db.query(Document).filter(Document.url == url).first()
        doc_ids[key] = doc.id

    for from_key, to_key in LINKS:
        link = Link(from_document_id=doc_ids[from_key], to_document_id=doc_ids[to_key])
        db.add(link)

    db.commit()
    db.close()
    print(f"Created {len(PAGES)} pages and {len(LINKS)} links.")


if __name__ == "__main__":
    generate_linked_data()