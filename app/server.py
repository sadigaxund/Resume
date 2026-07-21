import asyncio
import hashlib
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import httpx

app = FastAPI(title="Resume Server")

OWNER = "sadigaxund"
REPO = "Resume"
BRANCH = "main"
API = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

ROOT = Path(__file__).parent.parent
CACHE = ROOT / "_cache"
ARCHIVE = ROOT / "Archive"

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sadig Akhund - Resume</title>
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
    <h1>Sadig Akhund — Resume</h1>
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


def _parse_date(name: str) -> str:
    stem = name.removesuffix(".pdf")
    return stem.replace("Template_Resumé_", "")


def _label(name: str, date: str) -> str:
    return "Latest" if date == "_latest_" else date


def _find_sources() -> dict:
    seen: dict[str, Path] = {}

    if CACHE.is_dir():
        for f in CACHE.iterdir():
            if f.suffix == ".pdf":
                seen[f.name] = f

    archive = ROOT / "Archive"
    if archive.is_dir():
        for f in sorted(archive.iterdir(), reverse=True):
            if f.suffix == ".pdf" and f.name not in seen:
                seen[f.name] = f

    by_date: dict[str, tuple[str, Path]] = {}
    for name, path in seen.items():
        date = _parse_date(name)
        if date not in by_date:
            by_date[date] = (name, path)

    dates = sorted(by_date.keys(), reverse=True)
    if not dates:
        return {}

    latest_name, latest_path = by_date[dates[0]]
    latest_hash = _hash_file(latest_path)

    versions: dict = {}
    versions["latest"] = {"name": latest_name, "url": f"/pdf/{latest_name}",
                          "sha256": latest_hash, "date": "_latest_"}

    for date in dates[1:]:
        name, path = by_date[date]
        h = _hash_file(path)
        if h == latest_hash:
            continue
        versions[name] = {"name": name, "url": f"/pdf/{name}", "sha256": h, "date": date}

    return versions


async def _sync():
    CACHE.mkdir(exist_ok=True)
    cached = {f.name for f in CACHE.iterdir() if f.suffix == ".pdf"}

    async with httpx.AsyncClient(follow_redirects=True, timeout=httpx.Timeout(10, connect=5)) as client:
        try:
            resp = await client.get(f"{API}/Archive",
                                    headers={"Accept": "application/vnd.github.v3+json"})
            if resp.status_code == 200:
                for item in resp.json():
                    name = item["name"]
                    if name.endswith(".pdf") and name not in cached:
                        url = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/Archive/{name}"
                        try:
                            r = await client.get(url)
                            r.raise_for_status()
                            (CACHE / name).write_bytes(r.content)
                            print(f"[resume-server] cached: {name}")
                        except Exception as e:
                            print(f"[resume-server] failed to fetch {name}: {e}")
        except Exception as e:
            print(f"[resume-server] couldn't list Archive from GitHub: {e}")

    files = [(f, _parse_date(f.name)) for f in CACHE.iterdir() if f.suffix == ".pdf"]
    if not files:
        return

    files.sort(key=lambda x: x[1], reverse=True)
    latest_path, latest_date = files[0]
    latest_hash = _hash_file(latest_path)

    for path, _ in files[1:]:
        if _hash_file(path) == latest_hash:
            path.unlink()
            print(f"[resume-server] dedup: removed {path.name} (identical to latest {latest_path.name})")


@app.on_event("startup")
async def startup():
    asyncio.create_task(_sync())


@app.get("/", response_class=HTMLResponse)
async def index():
    v = _find_sources()
    options = "\n".join(
        f'<option value="{k}">{_label(v["name"], v.get("date", ""))}</option>'
        for k, v in v.items()
    )
    return INDEX_TEMPLATE.replace("{OPTIONS}", options).replace("{VERSIONS}", json.dumps(v))


@app.get("/sync")
async def sync():
    await _sync()
    return {"status": "ok"}


@app.get("/pdf/{filename:path}")
async def serve_pdf(filename: str):
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    path = (CACHE / filename).resolve()
    if not path.is_file():
        path = (ROOT / "Archive" / filename).resolve()
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    if not str(path).startswith(str(ROOT.resolve())):
        raise HTTPException(status_code=403, detail="Invalid path")
    return FileResponse(str(path), media_type="application/pdf", filename=path.name,
                        headers={"Content-Disposition": f'inline; filename="{path.name}"',
                                   "Cache-Control": "no-cache, no-store, must-revalidate"})


@app.get("/api/versions")
async def api_versions():
    return _find_sources()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.server:app", host="0.0.0.0", port=8000)
