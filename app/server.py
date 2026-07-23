import hashlib
import json
import os
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
import httpx

ROOT = Path(__file__).parent.parent
_CONFIG_PATH = ROOT / "app" / "config.json"

def _load_config() -> dict:
    if _CONFIG_PATH.is_file():
        try:
            return json.loads(_CONFIG_PATH.read_text())
        except Exception:
            pass
    return {}

CONFIG = _load_config()

AUTHOR = CONFIG.get("author") or os.getenv("AUTHOR") or ""

def _git_remote_owner() -> str:
    try:
        out = subprocess.run(["git", "config", "--get", "remote.origin.url"],
                             capture_output=True, text=True, timeout=2).stdout.strip()
        m = re.match(r"(?:https://github\.com/|git@github\.com:)([^/]+)/([^/.]+)", out)
        return m.group(1) if m else ""
    except Exception:
        return ""

def _git_remote_repo() -> str:
    try:
        out = subprocess.run(["git", "config", "--get", "remote.origin.url"],
                             capture_output=True, text=True, timeout=2).stdout.strip()
        m = re.match(r"(?:https://github\.com/|git@github\.com:)([^/]+)/([^/.]+)", out)
        return m.group(2) if m else ""
    except Exception:
        return ""

OWNER = CONFIG.get("owner") or os.getenv("GITHUB_OWNER") or _git_remote_owner() or ""
REPO = CONFIG.get("repo") or os.getenv("GITHUB_REPO") or _git_remote_repo() or ""

CACHE = Path.home() / ".cache" / "resume-server"
MAX_FILENAME_BYTES = 200

# --- rate limiter ---
_RATE: dict[str, list[float]] = defaultdict(list)
_RATE_LIMITS: list[tuple[str, int, int]] = [
    ("/pdf",          30, 60),
    ("/",             60, 60),
]

def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    ip = request.client
    return ip.host if ip else "unknown"

def _check_rate(request: Request):
    ip = _client_ip(request)
    path = request.url.path
    now = time.time()
    for prefix, max_req, window in _RATE_LIMITS:
        if not path.startswith(prefix):
            continue
        hits = _RATE[ip]
        cutoff = now - window
        hits[:] = [t for t in hits if t > cutoff]
        if len(hits) >= max_req:
            raise HTTPException(429, "Too many requests")
        hits.append(now)
        break

app = FastAPI(title="Resume Server")

@app.middleware("http")
async def _middleware(request: Request, call_next):
    try:
        _check_rate(request)
    except HTTPException as e:
        from starlette.responses import JSONResponse
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    response = await call_next(request)
    ct = response.headers.get("content-type", "")
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "interest-cohort=()"
    if ct.startswith("text/html"):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "object-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:"
        )
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE}</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #525659;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  .toolbar {
    background: #1a1a1a;
    color: #fff;
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    gap: 0.75rem;
    flex-shrink: 0;
  }
  .toolbar h1 {
    font-size: 1rem;
    font-weight: 500;
  }
  .btn {
    display: inline-block;
    padding: 0.4rem 1rem;
    background: #2563eb;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    text-decoration: none;
    line-height: 1.4;
  }
  .btn:hover { background: #1d4ed8; }
  select {
    padding: 0.4rem 0.5rem;
    border-radius: 4px;
    border: 1px solid #555;
    background: #333;
    color: #fff;
    font-size: 0.875rem;
    cursor: pointer;
  }
  select:focus { outline: none; border-color: #2563eb; }
  .hash-group {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.75rem;
    color: #999;
    margin-right: auto;
  }
  .hash-group code {
    font-size: 0.65rem;
    background: #333;
    padding: 0.15rem 0.4rem;
    border-radius: 3px;
    max-width: 30ch;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: pointer;
  }
  .hash-group .label {
    color: #777;
    font-size: 0.7rem;
  }
  .copy-btn {
    background: none;
    border: 1px solid #555;
    color: #aaa;
    font-size: 0.7rem;
    padding: 0.1rem 0.4rem;
    border-radius: 3px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.15s;
  }
  .hash-group:hover .copy-btn { opacity: 1; }
  .copy-btn:hover { border-color: #888; color: #fff; }
  .copy-btn.copied { border-color: #22c55e; color: #22c55e; opacity: 1; }
  .viewer {
    flex: 1;
    display: flex;
    justify-content: center;
    overflow: auto;
  }
  .viewer object {
    width: 100%;
    height: 100%;
  }
</style>
</head>
<body>
  <div class="toolbar">
    <h1>{TITLE}</h1>
    <span class="hash-group">
      <span class="label">SHA:</span>
      <code id="hashDisplay"></code>
      <button class="copy-btn" id="copyBtn">Copy</button>
    </span>
    <a class="btn" id="downloadBtn" href="#" download>Download</a>
    <select id="versionSelect">{OPTIONS}</select>
  </div>
  <div class="viewer">
    <object id="pdfViewer" type="application/pdf">
      <p>Your browser doesn't support PDF viewing. <a id="fallbackLink" href="#">Download the resume</a>.</p>
    </object>
  </div>
  <script>
    const viewer = document.getElementById("pdfViewer");
    const downloadBtn = document.getElementById("downloadBtn");
    const fallbackLink = document.getElementById("fallbackLink");
    const select = document.getElementById("versionSelect");
    const hashDisplay = document.getElementById("hashDisplay");
    const copyBtn = document.getElementById("copyBtn");
    const versions = {VERSIONS};
    function loadVersion(key) {
      const v = versions[key];
      viewer.data = v.url;
      downloadBtn.href = v.url;
      downloadBtn.download = v.name;
      if (fallbackLink) fallbackLink.href = v.url;
      hashDisplay.textContent = v.sha256;
      copyBtn.textContent = "Copy";
      copyBtn.className = "copy-btn";
    }
    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(hashDisplay.textContent).then(() => {
        copyBtn.textContent = "Copied!";
        copyBtn.className = "copy-btn copied";
        setTimeout(() => { copyBtn.textContent = "Copy"; copyBtn.className = "copy-btn"; }, 2000);
      });
    });
    const first = Object.keys(versions)[0];
    if (first) loadVersion(first);
    select.addEventListener("change", () => loadVersion(select.value));
  </script>
</body>
</html>"""


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


_DATE_RE = re.compile(r"_(\d{4}-\d{2}-\d{2})\.pdf$")

def _parse_date(name: str) -> str:
    m = _DATE_RE.search(name)
    return m.group(1) if m else ""


def _label(name: str, date: str) -> str:
    return "Latest" if date == "_latest_" else date


_MANIFEST: list[dict] = []
_MANIFEST_TS: float = 0
_MANIFEST_TTL: float = 300

async def _fetch_manifest() -> list[dict]:
    global _MANIFEST, _MANIFEST_TS
    now = time.time()
    if now - _MANIFEST_TS < _MANIFEST_TTL:
        return _MANIFEST
    if not OWNER or not REPO:
        return []
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/resume"
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            r = await client.get(url, headers={"Accept": "application/vnd.github.v3+json"})
            if r.status_code == 200:
                data = r.json()
                _MANIFEST = [
                    {"name": a["name"], "url": a["browser_download_url"]}
                    for a in data.get("assets", [])
                    if a["name"].endswith(".pdf")
                ]
                _MANIFEST.sort(key=lambda a: a["name"], reverse=True)
                _MANIFEST_TS = now
    except Exception:
        pass
    return _MANIFEST


MAX_CACHED = 10

def _evict():
    if not CACHE.is_dir():
        return
    pdfs = sorted(
        [f for f in CACHE.iterdir() if f.suffix == ".pdf"],
        key=lambda f: f.stat().st_mtime
    )
    while len(pdfs) > MAX_CACHED:
        pdfs[0].unlink(missing_ok=True)
        pdfs.pop(0)


@app.get("/", response_class=HTMLResponse)
async def index():
    title = f"{AUTHOR} — Resume" if AUTHOR else "Resume"
    manifest = await _fetch_manifest()

    cached_sha: dict[str, str] = {}
    if CACHE.is_dir():
        for f in CACHE.iterdir():
            if f.suffix == ".pdf":
                cached_sha[f.name] = _hash_file(f)

    versions: dict = {}
    for a in manifest:
        key = a["name"]
        date = _parse_date(key)
        versions[key] = {
            "name": key,
            "url": f"/pdf/{key}",
            "sha256": cached_sha.get(key, ""),
            "date": "_latest_" if not date else date,
        }

    options = "\n".join(
        f'<option value="{k}">{_label(v["name"], v["date"])}</option>'
        for k, v in versions.items()
    )
    html = INDEX_TEMPLATE.replace("{TITLE}", title)
    html = html.replace("{OPTIONS}", options).replace("{VERSIONS}", json.dumps(versions))
    return html


@app.get("/pdf/{filename:path}")
async def serve_pdf(filename: str):
    if len(filename.encode()) > MAX_FILENAME_BYTES or not filename.endswith(".pdf"):
        raise HTTPException(status_code=400)

    try:
        path = (CACHE / filename).resolve(strict=False)
        path.relative_to(CACHE.resolve())
    except (ValueError, OSError):
        raise HTTPException(status_code=403)

    if path.is_file():
        path.touch()
        return FileResponse(str(path), media_type="application/pdf", filename=path.name,
                            headers={"Content-Disposition": f'inline; filename="{path.name}"',
                                     "Cache-Control": "no-cache, no-store, must-revalidate"})

    manifest = await _fetch_manifest()
    asset = next((a for a in manifest if a["name"] == filename), None)
    if not asset:
        raise HTTPException(status_code=404)

    CACHE.mkdir(exist_ok=True)
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(asset["url"])
            r.raise_for_status()
            path.write_bytes(r.content)
    except Exception:
        raise HTTPException(status_code=502)

    _evict()
    return FileResponse(str(path), media_type="application/pdf", filename=path.name,
                        headers={"Content-Disposition": f'inline; filename="{path.name}"',
                                 "Cache-Control": "no-cache, no-store, must-revalidate"})


@app.head("/")
async def head_root():
    return Response(headers={"Content-Type": "text/html; charset=utf-8"})

@app.head("/pdf/{filename:path}")
async def head_pdf(filename: str):
    return Response()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.server:app", host="0.0.0.0", port=8000)
