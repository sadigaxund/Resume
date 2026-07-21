# Sadig Akhund — Resume

---

## Repository

| What | Where |
|------|-------|
| Template source | [`template/Template_Resumé.tex`](template/Template_Resumé.tex) |
| Latest PDF | [`Template_Resumé.pdf`](Template_Resumé.pdf) |
| Version history | [`Archive/`](Archive/) |
| Build scripts | [`scripts/`](scripts/) |
| Server | [`app/`](app/) |
| LaTeX deps | [`tex-packages.txt`](tex-packages.txt) |

## Build

### Dependencies

**Minimal** — install only the packages listed in `tex-packages.txt`:

```bash
./scripts/install-deps.sh          # Fedora: reads tex-packages.txt
```

**Full TeX Live** (slower download, but guaranteed to have everything):

```bash
sudo dnf install texlive-scheme-full   # Fedora
# or your distro's equivalent
```

### Compile

```bash
./scripts/build.sh                # compiles template/Template_Resumé.tex
./scripts/version-commit.sh       # archives + commits
```

The PDF is written to the repo root as `Template_Resumé.pdf`. Template assets (icons, fonts) live in [`template/`](template/).

> On every push that touches `template/`, GitHub Actions rebuilds the PDF, archives a dated copy into [`Archive/`](Archive/), and commits the results back.

## Serve

A FastAPI server serves the latest and archived PDFs with a native PDF viewer, version switcher, and SHA-256 integrity display.

### One‑line install

```bash
curl -fsSL https://raw.githubusercontent.com/sadigaxund/Resume/main/install.sh | bash
```

Prompts for host/port interactively; defaults to `0.0.0.0:8000`. Creates a `systemd --user` service named `resume-server` that auto‑starts and survives reboots.

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/sadigaxund/Resume/main/uninstall.sh | bash
```

### Manual run

```bash
pip install -r app/requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8000
# or
./scripts/serve.sh
```

### What it does

| Endpoint | Description |
|----------|-------------|
| `/` | Web UI with embedded PDF viewer + version dropdown |
| `/pdf/<filename>` | Serves a PDF inline (browser‑native viewer) |
| `/sync` | Triggers a re‑sync from GitHub |
| `/api/versions` | JSON list of available versions + SHA‑256 hashes |

On startup, the server fetches the PDF archive from `raw.githubusercontent.com`, caches files in `_cache/`, and deduplicates entries that are identical to the latest. No local PDFs are required after the initial sync.
