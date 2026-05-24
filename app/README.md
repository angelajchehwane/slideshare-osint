# SlideShare OSINT Extraction Module

A production-grade REST API for extracting structured search results from SlideShare based on a user-provided keyword query, with multi-page navigation and a built-in web interface.


## Description

This module is an OSINT (Open Source Intelligence) extraction tool that automates the retrieval of structured data from SlideShare search results. Given a keyword and a maximum page count, it navigates through SlideShare's paginated search results, extracts metadata from each presentation card, normalizes it into structured JSON objects and returns the aggregated results via a REST API.

## Getting Started

### Dependencies

* Windows 10 / macOS / Linux
* Python 3.11 or higher
* pip (Python package manager)
* Git
* Docker & Docker Compose (optional, for containerized run)
* Google Chrome or any modern browser (for saving HTML fixtures)

### Installing

**Clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/slideshare-osint
cd slideshare-osint
```

**Create and activate a virtual environment:**

```bash
# Create virtual environment
python -m venv venv
```

# Activate — Windows
```bash
venv\Scripts\activate
```

# Activate — Mac/Linux
```bash
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

* [https://www.slideshare.net/search/slideshow?searchfrom=header&q=python&page=1](https://www.slideshare.net/search/slideshow?searchfrom=header&q=python&page=1)

2. Press `Ctrl + S` → Save as **"Webpage, Complete"**
3. Save the `.html` file inside the `fixtures/` folder
4. Name it `search_python_page1.html`

> **Note:** SlideShare detects and blocks automated HTTP requests. The fixture file acts as a reliable fallback. This is the expected behavior as noted in the assessment brief.


### Executing program

**Run locally:**

```bash
uvicorn app.main:app --reload
```

**Run with Docker:**

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

## Help

**Getting an empty result `[]`:**

SlideShare blocks automated HTTP requests and returns empty pages. Make sure you have saved a fixture HTML file in the `fixtures/` folder as described in the Installing section above.

**`ModuleNotFoundError: No module named 'app'` when running tests:**

Make sure `conftest.py` exists in the project root and your virtual environment is activated before running pytest.

**Playwright `NotImplementedError` on Windows:**

This is a known Windows async subprocess limitation. The solution automatically falls back to the fixture file, no action needed.

**Port 8000 already in use:**

```bash
uvicorn app.main:app --reload --port 8001
```

**Virtual environment not activated:**

You should see `(venv)` at the start of your terminal line. If not, run:

```bash
venv\Scripts\activate
```

---

## Environment Variables

All settings can be configured via a .env file in the project root. 
Create a .env file and set any of the following:
```bash
env MAX_RETRIES=3
RATE_LIMIT_DELAY=1.5
REQUEST_TIMEOUT=30
LOG_LEVEL=INFO
```

**MAX_RETRIES:** number of retry attempts per page before giving up (default: 3)

**RATE_LIMIT_DELAY:** seconds to wait between page requests to avoid bot detection (default: 1.5)

**REQUEST_TIMEOUT**: maximum seconds to wait for a response before timing out (default: 30)

**LOG_LEVEL:** logging verbosity, one of DEBUG, INFO, WARNING, ERROR (default: INFO)

## Authors

Angela Chehwane
[GitHub](https://github.com/angelajchehwane)


## Version History

* **1.0.0**
    * Initial release
    * REST API with FastAPI
    * Multi-page pagination
    * Fixture-based fallback for bot detection
    * Structured JSON logging with structlog
    * Interactive web UI with JSON download
    * Docker and docker-compose support
    * Unit tests with pytest


## Acknowledgments

* [FastAPI](https://fastapi.tiangolo.com/) — modern, async Python web framework
* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — HTML parsing
* [httpx](https://www.python-httpx.org/) — async HTTP client
* [Pydantic](https://docs.pydantic.dev/) — data validation and serialization
* [structlog](https://www.structlog.org/) — structured logging
* [Playwright](https://playwright.dev/python/) — browser automation fallback
* [tenacity](https://tenacity.readthedocs.io/) — retry logic
