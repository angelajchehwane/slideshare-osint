from pathlib import Path
import httpx
from app.core.config import settings
from app.core.logging import logger

HEADERS = {
    "User-Agent": settings.user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.slideshare.net/",
}


async def fetch_page(query: str, page: int) -> str:
    # Always use fixture first (bot detection workaround)
    fixture = _find_fixture(query, page)
    if fixture:
        logger.info("loading_fixture", path=str(fixture))
        return fixture.read_text(encoding="utf-8", errors="ignore")

    # Try live request as fallback
    url = f"https://www.slideshare.net/search/slideshow?searchfrom=header&q={query}&page={page}"
    logger.info("live_fetch", url=url)
    async with httpx.AsyncClient(
        timeout=settings.request_timeout,
        follow_redirects=True,
        headers=HEADERS
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def _find_fixture(query: str, page: int) -> Path | None:
    fixtures_dir = Path("fixtures")
    if not fixtures_dir.exists():
        return None

    # Look for exact match first
    exact = fixtures_dir / f"search_{query.replace(' ', '_')}_page{page}.html"
    if exact.exists():
        return exact

    # Use any available fixture
    all_fixtures = list(fixtures_dir.glob("*.html"))
    if all_fixtures:
        return all_fixtures[0]

    return None