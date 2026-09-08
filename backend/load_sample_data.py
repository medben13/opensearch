from app.core.database import SessionLocal
from app.services.document_service import save_document

# A small set of varied sample documents. In a real run you'd generate or
# scrape many more (the blueprint eventually wants 5,000-10,000), but this
# is enough to demonstrate the loading pattern and get non-trivial TF-IDF/BM25 scores.
SAMPLE_DOCUMENTS = [
    ("Introduction to Computer Science", "https://example.com/1",
     "Computer science is the study of algorithms, data structures, and computation."),
    ("Machine Learning Basics", "https://example.com/2",
     "Machine learning is a subset of artificial intelligence focused on learning from data."),
    ("Web Development Guide", "https://example.com/3",
     "Web development involves building websites using HTML, CSS, and JavaScript."),
    ("Database Systems", "https://example.com/4",
     "A database stores structured data and allows efficient querying using SQL."),
    ("Operating Systems Overview", "https://example.com/5",
     "An operating system manages hardware resources and provides services to programs."),
    ("Introduction to Networking", "https://example.com/6",
     "Computer networks allow devices to communicate and share data across distances."),
    ("Software Engineering Principles", "https://example.com/7",
     "Software engineering applies engineering principles to designing reliable software systems."),
    ("Data Structures Explained", "https://example.com/8",
     "Data structures such as arrays, trees, and graphs organize data for efficient access."),
    ("Introduction to Algorithms", "https://example.com/9",
     "An algorithm is a step by step procedure for solving a problem or performing a computation."),
    ("Cybersecurity Fundamentals", "https://example.com/10",
     "Cybersecurity protects computer systems and networks from digital attacks and unauthorized access."),
]


def load_sample_data():
    db = SessionLocal()
    added = 0
    skipped = 0

    for title, url, content in SAMPLE_DOCUMENTS:
        result = save_document(db, title=title, url=url, content=content)
        if result is None:
            skipped += 1
        else:
            added += 1

    db.close()
    print(f"Added {added} documents, skipped {skipped} duplicates.")


if __name__ == "__main__":
    load_sample_data()