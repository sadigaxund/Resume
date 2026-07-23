# Resume

| What | Where |
|------|-------|
| Template | [`template/`](template/) |
| Viewer | [sadigaxund.github.io/Resume](https://sadigaxund.github.io/Resume) |
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

3. **Push** — CI builds the PDF, uploads to Releases, and deploys the HTML viewer to GitHub Pages.

## Viewer

The resume is served as a static GitHub Pages site at `https://YOUR_USER.github.io/YOUR_REPO/` with a version selector and embedded PDF viewer. All versions are fetched directly from GitHub Releases.

## CI

The workflow (`.github/workflows/build-resume.yml`) runs on every push to `template/`:

1. Reads `template/resume.yml` → gets your name and template filename
2. Builds the PDF with XeLaTeX
3. Uploads the PDF to a `latest` release (always) and creates `resume-YYYY-MM-DD` releases on content change
4. Deploys the HTML viewer to GitHub Pages

## License

Feel free to fork and adapt for your own use.
