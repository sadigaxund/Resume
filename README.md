# Sadig Akhund — Resume

Data Engineer · Baku, Azerbaijan

[**Download latest PDF →**](SadigAkhund_Resume.pdf)

<!-- LAST_UPDATED -->_Last updated: 2026-07-12_<!-- /LAST_UPDATED -->

![Resume preview](preview.png)

---

## Repository

| What | Where |
|------|-------|
| Source | [`SadigAkhund_Resume.tex`](SadigAkhund_Resume.tex) |
| Latest PDF | [`SadigAkhund_Resume.pdf`](SadigAkhund_Resume.pdf) |
| Version history | [`Archive/`](Archive/) |
| Build scripts | [`scripts/`](scripts/) |

## Build

```bash
./scripts/install-deps.sh   # one-time: install LaTeX packages (Fedora)
./scripts/build.sh          # compile PDF + regenerate preview.png
./scripts/version-commit.sh # archive current PDF with date suffix + commit
```

Compiler: `xelatex` via `latexmk`. Ubuntu font is vendored under [`fonts/`](fonts/), so the build is self-contained.

> On every push that changes `SadigAkhund_Resume.tex`, GitHub Actions rebuilds the PDF, regenerates the preview, archives a dated copy into [`Archive/`](Archive/), and commits the results back.

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

Stops the service, removes the systemd unit, and optionally deletes the cloned repo.

### Manual run

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
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

On startup, `server.py` fetches the PDF archive from `raw.githubusercontent.com`, caches files in `_cache/`, and deduplicates entries that are identical to the latest. No local PDFs are required after the initial sync.

## Contact

- Email: sadigaxund@gmail.com
- LinkedIn: [/in/sakhund](https://linkedin.com/in/sakhund)
