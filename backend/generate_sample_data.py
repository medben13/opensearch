import random
from app.core.database import SessionLocal
from app.services.document_service import save_document

# A pool of topic-relevant words to build varied, realistic-length documents from.
# Real vocabulary, real sentence structure -- just generated in bulk instead of
# hand-written one by one, so we can reach the document counts the blueprint asks for.
TOPICS = [
    "computer science", "machine learning", "artificial intelligence", "data structures",
    "algorithms", "web development", "databases", "operating systems", "networking",
    "software engineering", "cybersecurity", "cloud computing", "distributed systems",
    "compilers", "computer architecture", "programming languages", "data science",
    "computer graphics", "robotics", "quantum computing",
]

SENTENCE_TEMPLATES = [
    "{topic} is a fundamental area of study in modern computing.",
    "Understanding {topic} requires strong foundations in mathematics and logic.",
    "Many companies rely heavily on {topic} to build their products.",
    "Researchers continue to make progress in {topic} every year.",
    "Students learning {topic} often start with basic examples before tackling harder problems.",
    "The history of {topic} dates back several decades of innovation.",
    "Applying {topic} effectively requires both theory and hands-on practice.",
    "Recent advances in {topic} have changed how engineers approach problems.",
]


def generate_document(doc_number: int) -> tuple[str, str, str]:
    topic = random.choice(TOPICS)
    num_sentences = random.randint(3, 8)
    sentences = [
        random.choice(SENTENCE_TEMPLATES).format(topic=topic)
        for _ in range(num_sentences)
    ]
    content = " ".join(sentences)
    title = f"{topic.title()} - Article {doc_number}"
    url = f"https://example.com/articles/{doc_number}"
    return title, url, content


def generate_and_save(count: int):
    db = SessionLocal()
    added = 0
    skipped = 0

    for i in range(count):
        title, url, content = generate_document(i)
        result = save_document(db, title=title, url=url, content=content)
        if result is None:
            skipped += 1
        else:
            added += 1

        if (i + 1) % 100 == 0:
            print(f"Progress: {i + 1}/{count}")

    db.close()
    print(f"Done. Added {added} documents, skipped {skipped} duplicates.")


if __name__ == "__main__":
    generate_and_save(1000)