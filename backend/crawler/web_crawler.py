import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.services.document_service import save_document


def can_fetch(url: str, user_agent: str = "OpenSearchBot") -> bool:
    """
    Checks the site's robots.txt to see if we're allowed to visit this URL.
    Returns True if allowed (or if no robots.txt exists), False if disallowed.
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # If robots.txt can't be fetched at all (site has none, or it's down),
        # we default to allowing -- this matches robots.txt's own convention:
        # absence of the file means no restrictions were declared.
        return True

    return rp.can_fetch(user_agent, url)


def extract_text_and_links(html: str, base_url: str) -> tuple[str, list[str]]:
    """
    Parses raw HTML into (visible text, list of absolute links found on the page).
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove script/style tags entirely -- their contents aren't real page text
    # and would pollute the indexed content with JavaScript/CSS code.
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    links = []
    for a_tag in soup.find_all("a", href=True):
        # href might be relative (e.g. "/about") -- urljoin resolves it into
        # a full, absolute URL relative to the page we found it on.
        absolute_url = urljoin(base_url, a_tag["href"])
        links.append(absolute_url)

    return text, links


def crawl(seed_url: str, max_pages: int = 20, delay_seconds: float = 1.0):
    """
    Crawls starting from seed_url using breadth-first traversal,
    respecting robots.txt and rate limits, stopping at max_pages.
    """
    db = SessionLocal()

    queue = [seed_url]
    visited = set()
    pages_saved = 0

    while queue and pages_saved < max_pages:
        url = queue.pop(0)  # take from the FRONT of the queue -- this is what makes it BFS

        if url in visited:
            continue
        visited.add(url)

        if not can_fetch(url):
            print(f"Skipping (robots.txt disallows): {url}")
            continue

        try:
            response = requests.get(url, timeout=5, headers={"User-Agent": "OpenSearchBot"})
            response.raise_for_status()  # raises an error for 4xx/5xx status codes
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        text, links = extract_text_and_links(response.text, url)

        title = url  # simple fallback; real title extraction is a nice later improvement
        result = save_document(db, title=title, url=url, content=text)

        if result is not None:
            pages_saved += 1
            print(f"[{pages_saved}/{max_pages}] Saved: {url}")
        else:
            print(f"Duplicate content, skipped: {url}")

        # Only queue NEW links we haven't seen, keeping the same domain
        # to avoid the crawler wandering off across the entire internet
        seed_domain = urlparse(seed_url).netloc
        for link in links:
            if urlparse(link).netloc == seed_domain and link not in visited:
                queue.append(link)

        # Rate limiting: pause between requests, being a polite, non-disruptive visitor
        time.sleep(delay_seconds)

    db.close()
    print(f"\nCrawl complete. Saved {pages_saved} pages.")


if __name__ == "__main__":
    crawl("https://example.com", max_pages=5)