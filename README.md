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
2. **Set environment variables** so the server and scripts know your identity:

```bash
export AUTHOR="Your Name"
export GITHUB_OWNER="your-github-username"
export GITHUB_REPO="your-repo-name"
```

### Build

```bash
./scripts/build.sh template/YourResume.tex
```

### Serve with systemd

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/install.sh | bash
```

Prompts for host, port, service name. Or set `GITHUB_OWNER`/`GITHUB_REPO` in advance for a non-interactive install.

### Manual server

```bash
pip install -r app/requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

### Version commit

```bash
./scripts/version-commit.sh template/YourResume.tex
```

## CI

The GitHub Actions workflow (`.github/workflows/build-resume.yml`) compiles the template on every push to `template/`. Set `AUTHOR` as a repository variable in your fork's GitHub settings.

## License

Feel free to fork and adapt for your own use.
