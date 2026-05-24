import httpx
from app.core.config import settings
from app.core.logging import logger

HEADERS = {"User-Agent": settings.user_agent}

async def fetch_page(query: str, page: int) -> str:
    url = f"https://www.slideshare.net/search/slideshow?searchfrom=header&q={query}&page={page}"
    logger.info("fetching_page", url=url, page=page)
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        response = await client.get(url, headers=HEADERS, follow_redirects=True)
        response.raise_for_status()
        return response.text