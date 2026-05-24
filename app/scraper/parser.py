import re
from bs4 import BeautifulSoup
from app.models.slide import SlideResult
from app.core.logging import logger


def parse_results(html: str, page: int) -> list[SlideResult]:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    cards = soup.find_all("a", attrs={"data-cy": "slideshow-card-link"})
    logger.info("cards_found", count=len(cards), page=page)

    for card in cards:
        try:
            # URL
            url = card.get("href", "")
            if not url.startswith("http"):
                url = "https://www.slideshare.net" + url

            # aria-label contains everything:
            # "Title by Author, has X slides with Y views."
            aria = card.get("aria-label", "")

            # Extract title and author from aria-label
            # Format: "Title by Author, has..."
            title = aria
            author = None
            views = None

            by_match = re.split(r'\s+by\s+', aria, maxsplit=1)
            if len(by_match) == 2:
                title = by_match[0].strip()
                rest = by_match[1]

                # Extract author (before the comma)
                author_match = re.match(r'^(.+?),\s+has', rest)
                if author_match:
                    author = author_match.group(1).strip()

            # Extract slide count from aria-label
            # Format: "has 25 slides"
            slides = None
            slides_match = re.search(r'has\s+(\d+)\s+slides', aria)
            if slides_match:
                slides = int(slides_match.group(1))
            # Extract views from aria-label
            # Format: "with 22.6K views"
            views_match = re.search(r'with\s+([\d,.]+[KMB]?)\s+views', aria)
            if views_match:
                views_str = views_match.group(1).replace(',', '')
                # Convert K/M to numbers
                if views_str.endswith('K'):
                    views = int(float(views_str[:-1]) * 1000)
                elif views_str.endswith('M'):
                    views = int(float(views_str[:-1]) * 1000000)
                else:
                    views = int(views_str) if views_str.isdigit() else None

            # Description from the card content
            desc_el = card.find("p", attrs={"data-cy": "document-description"})
            description = desc_el.get_text(strip=True) if desc_el else None

            if not title:
                continue

            results.append(SlideResult(
                title=title,
                url=url,
                author=author,
                description=description,
                views=views,
                slides=slides,
                page=page
            ))

        except Exception as e:
            logger.warning("parse_error", error=str(e))
            continue

    return results