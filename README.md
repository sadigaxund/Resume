# Resume

| What | Where |
|------|-------|
| Template | [`template/Template_Resumé.tex`](template/Template_Resumé.tex) |
| Latest PDF | [`Template_Resumé.pdf`](Template_Resumé.pdf) |
| Archive | [`Archive/`](Archive/) |
| Server | [`app/`](app/) |
| LaTeX deps | [`tex-packages.txt`](tex-packages.txt) |

## Build

```bash
./scripts/install-deps.sh   # install deps from tex-packages.txt (Fedora)
# or: sudo dnf install texlive-scheme-full
./scripts/build.sh          # compile PDF
```

CI rebuilds on every push to `template/`.

## Serve

```bash
curl -fsSL https://raw.githubusercontent.com/sadigaxund/Resume/main/install.sh | bash
```

Creates a `systemd --user` service. Prompts for host/port.

### Manual

```bash
pip install -r app/requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/sadigaxund/Resume/main/uninstall.sh | bash
```
