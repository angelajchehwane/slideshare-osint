import asyncio
from app.scraper import parser
from app.scraper.browser import fetch_page
from app.models.slide import SlideResult
from app.core.config import settings
from app.core.logging import logger


async def scrape(query: str, max_pages: int) -> list[SlideResult]:
    results = []
    seen_urls = set()

    for page in range(1, max_pages + 1):
        try:
            logger.info("scraping_page", page=page, query=query)
            html = await fetch_page(query, page)
            items = parser.parse_results(html, page)

            for item in items:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    results.append(item)

            logger.info("page_done", page=page, found=len(items))
            await asyncio.sleep(settings.rate_limit_delay)

        except Exception as e:
            logger.error("page_failed", page=page, error=str(e))

    return results