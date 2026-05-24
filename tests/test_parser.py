from app.scraper.parser import parse_results
from pathlib import Path

def test_parse_fixture_returns_results():
    html = Path("fixtures/search_python_page1.html").read_text(encoding="utf-8", errors="ignore")
    results = parse_results(html, page=1)
    assert len(results) > 0

def test_parse_fixture_has_required_fields():
    html = Path("fixtures/search_python_page1.html").read_text(encoding="utf-8", errors="ignore")
    results = parse_results(html, page=1)
    for r in results:
        assert r.title
        assert r.url.startswith("http")
        assert r.page == 1
        assert r.extracted_at

def test_parse_fixture_views_are_numbers():
    html = Path("fixtures/search_python_page1.html").read_text(encoding="utf-8", errors="ignore")
    results = parse_results(html, page=1)
    for r in results:
        if r.views is not None:
            assert isinstance(r.views, int)

def test_parse_empty_html_returns_empty_list():
    results = parse_results("<html></html>", page=1)
    assert results == []