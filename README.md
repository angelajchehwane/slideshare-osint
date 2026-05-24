# SlideShare OSINT Extraction Module

A REST API that searches SlideShare and returns structured results as JSON.

## Description

This tool lets you search SlideShare automatically. You give it a keyword like "python" and it goes through multiple pages of SlideShare search results, collects information about each presentation and gives you back a clean JSON list with the title, author, views, slide count and link for each result.

It also has a simple web interface where you can type your keyword, see the results as cards on the left and the raw JSON on the right and download the results as a file.

## Getting Started

### Dependencies

* Windows 10 / macOS / Linux
* Python 3.11 or higher
* pip (Python package manager)
* Git
* Docker and Docker Compose (optional, for containerized run)
* Google Chrome or any modern browser (for saving HTML fixtures)

### Installing

**Clone the repository:**

```bash
git clone https://github.com/angelajchehwane/slideshare-osint
cd slideshare-osint
```

**Create and activate a virtual environment:**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**Install all dependencies:**

```bash
pip install -r requirements.txt
```

**Install Playwright browser:**

```bash
playwright install chromium
```

**Save a fixture file (required for offline/fallback mode):**

1. Open your browser and go to:
```
https://www.slideshare.net/search/slideshow?searchfrom=header&q=python&page=1
```
2. Press Ctrl + S and save as "Webpage, Complete"
3. Save the .html file inside the fixtures/ folder
4. Name it search_python_page1.html

Note: SlideShare detects and blocks automated HTTP requests. The fixture file acts as a reliable fallback. This is the expected behavior as noted in the assessment brief.

### Executing program

**Run locally:**

```bash
uvicorn app.main:app --reload
```

**Run with Docker (preferred):**

```bash
docker-compose up
```

**Access the web interface:**

```
http://localhost:8000
```

**Access the interactive API docs:**

```
http://localhost:8000/docs
```

**Make an API request directly:**

```bash
curl "http://localhost:8000/search?query=machine+learning&max_pages=2"
```

**Run the tests:**

```bash
pytest tests/ -v
```

**Check the health endpoint:**

```bash
curl "http://localhost:8000/health"
```

## Docker Setup

**Build and run with Dockerfile:**

```bash
docker build -t slideshare-osint .
docker run -p 8000:8000 slideshare-osint
```

**Run with docker-compose (preferred):**

```bash
docker-compose up
```

The docker-compose.yml exposes port 8000 and passes environment variables automatically:

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MAX_RETRIES=3
      - RATE_LIMIT_DELAY=1.5
      - LOG_LEVEL=INFO
```

## Sample Output JSON

The /search endpoint returns a JSON array. Example output:

```json
[
  {
    "title": "Artificial Intelligence",
    "url": "https://www.slideshare.net/slideshow/artificial-intelligence-185776428/185776428",
    "author": "gayathrysatheesan1",
    "description": null,
    "views": 22600,
    "slides": 25,
    "upload_date": null,
    "page": 1,
    "extracted_at": "2026-05-24T08:50:31.155432"
  },
  {
    "title": "ARTIFICIAL INTELLIGENCE",
    "url": "https://www.slideshare.net/slideshow/artificial-intelligence-88505942/88505942",
    "author": "Omkar Shinde",
    "description": null,
    "views": 23300,
    "slides": 14,
    "upload_date": null,
    "page": 1,
    "extracted_at": "2026-05-24T08:50:31.156093"
  }
]
```

A full sample output file is included in sample_output.json.

## Design Decisions

**httpx + BeautifulSoup with fixture fallback**

SlideShare blocks automated requests by returning empty pages. The tool first tries a direct HTTP request using httpx. If SlideShare blocks it the tool loads a saved HTML file from the fixtures folder instead. This way the tool always works even when SlideShare fights back.

**aria-label as primary data source**

SlideShare loads most card content using JavaScript so the raw HTML is almost empty. But the aria-label on each card always contains the key info in a consistent format: "Title by Author, has X slides with Y views." The tool reads this to extract all the data it needs.

**Separation of concerns**

Each file has one job. browser.py fetches HTML. parser.py reads the HTML. orchestrator.py coordinates the pages. None of them know about each other's details. This makes the code easy to change and maintain.

**Pydantic models**

Every result is validated against a strict model before it goes out. If a field is missing or the wrong type it gets caught automatically.

**Config via environment variables**

All settings like timeouts and delays are in one place and can be changed without touching the code.

**Structured logging**

Every action is logged as a JSON line so logs are easy to read and search in production tools.

**Deduplication**

The tool keeps track of URLs it has already seen and skips duplicates across pages.

**Rate limiting**

The tool waits 1.5 seconds between page requests so SlideShare does not block it for making too many requests too fast.

## Assumptions and Limitations

* SlideShare detects automated requests and returns empty pages. The fixture fallback handles this. Production deployments would need proxy rotation.
* upload_date and description are not available in SlideShare's search results page because they are loaded by JavaScript. Getting them would require visiting each slide's individual page separately.
* If SlideShare changes their website design the parser selectors would need to be updated.
* Pages are fetched one at a time to avoid triggering bot detection.

## Possible Future Improvements

* Proxy pool rotation to bypass bot detection at scale
* Redis caching to avoid re-fetching the same query within a short time window
* Fetch multiple pages at the same time instead of one by one
* Visit each slide's individual page to get upload_date and full description
* Add support for other sources like SpeakerDeck and Scribd
* CI/CD pipeline with GitHub Actions for automated testing on every push

## Help

**Getting an empty result []:**
SlideShare blocks automated requests. Save a fixture HTML file in the fixtures/ folder as described above.

**ModuleNotFoundError: No module named app when running tests:**
Make sure conftest.py exists in the project root and your virtual environment is activated.

**Playwright NotImplementedError on Windows:**
Known Windows async subprocess limitation. The solution automatically falls back to the fixture file.

**Port 8000 already in use:**

```bash
uvicorn app.main:app --reload --port 8001
```

## Environment Variables

Create a .env file in the project root:

```env
MAX_RETRIES=3
RATE_LIMIT_DELAY=1.5
REQUEST_TIMEOUT=30
LOG_LEVEL=INFO
```

* MAX_RETRIES: how many times to retry if a request fails (default: 3)
* RATE_LIMIT_DELAY: how many seconds to wait between pages (default: 1.5)
* REQUEST_TIMEOUT: how many seconds to wait for a response before giving up (default: 30)
* LOG_LEVEL: one of DEBUG, INFO, WARNING or ERROR (default: INFO)

## Authors

Angela Chehwane
[GitHub](https://github.com/angelajchehwane)

## Version History

* 1.0.0
    * Initial release
    * REST API with FastAPI
    * Multi-page pagination
    * Fixture-based fallback for bot detection
    * Structured JSON logging with structlog
    * Interactive web UI with JSON download
    * Docker and docker-compose support
    * Unit tests with pytest

## License

This project is licensed under the MIT License.

## Acknowledgments

* [FastAPI](https://fastapi.tiangolo.com/) - modern async Python web framework
* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
* [httpx](https://www.python-httpx.org/) - async HTTP client
* [Pydantic](https://docs.pydantic.dev/) - data validation and serialization
* [structlog](https://www.structlog.org/) - structured logging
* [Playwright](https://playwright.dev/python/) - browser automation fallback
* [tenacity](https://tenacity.readthedocs.io/) - retry logic
