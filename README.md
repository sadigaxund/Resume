# Resume

| What | Where |
|------|-------|
| Template | [`template/`](template/) |
| Server | [`app/`](app/) |
| LaTeX deps | [`tex-packages.txt`](tex-packages.txt) |

## Fork & use

```bash
git clone https://github.com/YOUR_USER/YOUR_REPO.git
cd YOUR_REPO
```

1. **Replace** the `.tex` file in `template/` with your own resume
2. **Edit** `template/resume.yml` with your name and template filename:

```yaml
author: "Your Name"
template: "YourResume.tex"
```

3. **Push** — CI reads the config, builds the PDF, generates server config, and commits everything.

### Build

```bash
./scripts/build.sh template/YourResume.tex
```

### Serve with systemd

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/install.sh | bash
```

The installer auto-detects the repo URL (CI updates it on each build). Prompts for host, port, service name.

### Manual server

```bash
pip install -r app/requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

## CI

The GitHub Actions workflow (`.github/workflows/build-resume.yml`) runs on every push to `template/`:

1. Reads `template/resume.yml` → gets your name and template filename
2. Builds the PDF with XeLaTeX
3. Generates `app/config.json` with your name + GitHub owner/repo/branch (from context)
4. Updates `install.sh` with the correct clone URL
5. Archives a dated copy: `Archive/YourName_2026-07-22.pdf`
6. Commits everything

## License

Feel free to fork and adapt for your own use.
