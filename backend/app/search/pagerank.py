from sqlalchemy.orm import Session
from app.models.document import Document, Link


def build_link_graph(db: Session) -> tuple[dict[int, list[int]], dict[int, int]]:
    """
    Builds two lookup structures from the links table:
    - incoming_links: doc_id -> list of doc_ids that link TO it
    - outbound_counts: doc_id -> how many outbound links that doc has
    """
    documents = db.query(Document).all()
    links = db.query(Link).all()

    incoming_links: dict[int, list[int]] = {doc.id: [] for doc in documents}
    outbound_counts: dict[int, int] = {doc.id: 0 for doc in documents}

    for link in links:
        incoming_links[link.to_document_id].append(link.from_document_id)
        outbound_counts[link.from_document_id] += 1

    return incoming_links, outbound_counts


def compute_pagerank(
    db: Session,
    damping: float = 0.85,
    iterations: int = 20,
) -> dict[int, float]:
    """
    Computes PageRank for every document, using the standard iterative formula:
        PR(P) = (1-d)/N + d * sum(PR(linker) / outbound_links(linker))
    Returns a dict of doc_id -> PageRank score.
    """
    incoming_links, outbound_counts = build_link_graph(db)
    doc_ids = list(incoming_links.keys())
    n = len(doc_ids)

    if n == 0:
        return {}

    # Start every page with equal rank -- 1/N each, so all ranks sum to 1
    ranks: dict[int, float] = {doc_id: 1.0 / n for doc_id in doc_ids}

    for _ in range(iterations):
        new_ranks: dict[int, float] = {}

        for doc_id in doc_ids:
            base = (1 - damping) / n

            contribution = 0.0
            for linker_id in incoming_links[doc_id]:
                linker_outbound = outbound_counts[linker_id]
                if linker_outbound > 0:
                    contribution += ranks[linker_id] / linker_outbound

            new_ranks[doc_id] = base + damping * contribution

        ranks = new_ranks

    return ranks