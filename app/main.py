from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from app.scraper.orchestrator import scrape
from app.models.slide import SlideResult
from app.core.logging import logger
import time
import json

app = FastAPI(
    title="SlideShare OSINT Extractor",
    description="Extracts structured search results from SlideShare",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SlideShare OSINT Extractor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; color: #333; height: 100vh; display: flex; flex-direction: column; }
        .header { background: #1e3a5f; color: white; padding: 18px 32px; flex-shrink: 0; }
        .header h1 { font-size: 20px; font-weight: 600; }
        .header p { font-size: 12px; opacity: 0.7; margin-top: 2px; }
        .search-bar { background: white; padding: 16px 32px; border-bottom: 1px solid #eee; flex-shrink: 0; display: flex; gap: 12px; align-items: flex-end; flex-wrap: wrap; }
        .form-group { display: flex; flex-direction: column; gap: 5px; }
        label { font-size: 11px; font-weight: 500; color: #888; text-transform: uppercase; }
        input { padding: 9px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
        input:focus { border-color: #1e3a5f; }
        .btn { padding: 9px 20px; border: none; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all .15s; white-space: nowrap; }
        .btn-primary { background: #1e3a5f; color: white; }
        .btn-primary:hover { background: #162d4a; }
        .btn-primary:disabled { background: #aaa; cursor: not-allowed; }
        .btn-download { background: #1a9e6e; color: white; display: none; }
        .btn-download:hover { background: #157a56; }
        .status { font-size: 12px; color: #888; align-self: center; }
        .main { display: flex; flex: 1; overflow: hidden; }
        .left-panel { flex: 1; overflow-y: auto; padding: 20px 24px; }
        .right-panel { width: 420px; background: #1e1e1e; display: flex; flex-direction: column; flex-shrink: 0; }
        .right-header { padding: 14px 18px; background: #2d2d2d; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #444; }
        .right-header span { color: #ccc; font-size: 13px; font-weight: 500; }
        .badge { background: #378add; color: white; font-size: 11px; padding: 2px 8px; border-radius: 20px; }
        .json-content { flex: 1; overflow-y: auto; padding: 16px 18px; }
        .json-content pre { color: #d4d4d4; font-size: 11.5px; line-height: 1.65; white-space: pre-wrap; font-family: 'Cascadia Code', 'Fira Code', monospace; }
        .empty-state { color: #555; font-size: 13px; text-align: center; padding: 40px 20px; }
        .card { background: white; border: 1px solid #eee; border-radius: 10px; padding: 16px 18px; margin-bottom: 12px; transition: border-color .15s, box-shadow .15s; }
        .card:hover { border-color: #b5d4f4; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .card-title { font-size: 14px; font-weight: 500; color: #1e3a5f; margin-bottom: 6px; }
        .card-title a { color: inherit; text-decoration: none; }
        .card-title a:hover { text-decoration: underline; }
        .card-meta { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; color: #999; }
        .card-desc { font-size: 12px; color: #666; line-height: 1.5; margin-top: 8px; border-top: 1px solid #f0f0f0; padding-top: 8px; }
        .spinner { display: inline-block; width: 13px; height: 13px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin .6s linear infinite; vertical-align: middle; margin-right: 6px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .no-results { text-align: center; padding: 60px 20px; color: #aaa; font-size: 14px; }
    </style>
</head>
<body>
<div class="header">
    <h1>SlideShare OSINT Extractor</h1>
    <p>Extract structured search results from SlideShare</p>
</div>

<div class="search-bar">
    <div class="form-group">
        <label>Keyword</label>
        <input type="text" id="query" placeholder="e.g. artificial intelligence" style="width:260px"/>
    </div>
    <div class="form-group">
        <label>Max pages</label>
        <input type="number" id="pages" value="1" min="1" style="width:80px"/>
    </div>
    <button class="btn btn-primary" id="searchBtn" onclick="doSearch()">Search</button>
    <button class="btn btn-download" id="downloadBtn" onclick="downloadJSON()">⬇ Download JSON</button>
    <span class="status" id="status"></span>
</div>

<div class="main">
    <div class="left-panel" id="leftPanel">
        <div class="empty-state">Enter a keyword and click Search to extract results.</div>
    </div>
    <div class="right-panel">
        <div class="right-header">
            <span>JSON Output</span>
            <span class="badge" id="countBadge">0 results</span>
        </div>
        <div class="json-content">
            <pre id="jsonPre"><span style="color:#555">// Results will appear here...</span></pre>
        </div>
    </div>
</div>

<script>
let currentData = [];

async function doSearch() {
    const query = document.getElementById('query').value.trim();
    const pages = document.getElementById('pages').value;
    if (!query) { alert('Please enter a keyword'); return; }

    const btn = document.getElementById('searchBtn');
    const status = document.getElementById('status');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Searching...';
    status.textContent = 'Fetching...';
    document.getElementById('downloadBtn').style.display = 'none';
    document.getElementById('leftPanel').innerHTML = '<div class="empty-state">Loading results...</div>';
    document.getElementById('jsonPre').innerHTML = '<span style="color:#555">// Loading...</span>';

    try {
        const res = await fetch(`/search?query=${encodeURIComponent(query)}&max_pages=${pages}`);
        currentData = await res.json();
        if (!Array.isArray(currentData)) throw new Error('Unexpected response from server');
        status.textContent = `${currentData.length} results`;
        renderCards(currentData, query);
        renderJSON(currentData);
        document.getElementById('downloadBtn').style.display = 'inline-block';
    } catch(e) {
        status.textContent = 'Error: ' + e.message;
        document.getElementById('leftPanel').innerHTML = '<div class="empty-state">Something went wrong.</div>';
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Search';
    }
}

function renderCards(data, query) {
    const panel = document.getElementById('leftPanel');
    if (data.length === 0) {
        panel.innerHTML = '<div class="no-results">No results found for "' + query + '"</div>';
        return;
    }
    panel.innerHTML = data.map((r) => `
        <div class="card">
            <div class="card-title"><a href="${r.url}" target="_blank">${r.title}</a></div>
            <div class="card-meta">
                ${r.author ? `<span>👤 ${r.author}</span>` : ''}
                ${r.views ? `<span>👁 ${Number(r.views).toLocaleString()} views</span>` : ''}
                ${r.slides ? `<span>📑 ${r.slides} slides</span>` : ''}
                <span>📄 Page ${r.page}</span>
            </div>
            ${r.description ? `<div class="card-desc">${r.description}</div>` : ''}
        </div>
    `).join('');
}

function renderJSON(data) {
    document.getElementById('jsonPre').textContent = JSON.stringify(data, null, 2);
    document.getElementById('countBadge').textContent = data.length + ' results';
}

function downloadJSON() {
    const query = document.getElementById('query').value.trim();
    const blob = new Blob([JSON.stringify(currentData, null, 2)], {type: 'application/json'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `slideshare_${query.replace(/\s+/g,'_')}_results.json`;
    a.click();
}

document.getElementById('query').addEventListener('keydown', e => {
    if (e.key === 'Enter') doSearch();
});
</script>
</body>
</html>
"""

@app.get("/search", response_model=list[SlideResult])
async def search_slides(
    query: str = Query(..., min_length=1, description="Search keyword"),
    max_pages: int = Query(default=3, ge=1, description="Max pages")
):
    start = time.time()
    results = await scrape(query, max_pages)
    duration = round(time.time() - start, 2)
    logger.info(
        "search_complete",
        query=query,
        results_count=len(results),
        duration_seconds=duration
    )
    return results

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/metrics")
async def metrics():
    return {
        "status": "ok",
        "endpoints": ["/search", "/health", "/metrics"],
    }
