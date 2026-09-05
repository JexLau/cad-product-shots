# cad-product-shots

Static service landing: **STEP / IGES in → geometry-faithful product shots out**.

This is a marketing page, not an upload product. No accounts, no app shell.

## Local preview

From the repo root (any static server):

```bash
python3 -m http.server 8080
```

Then open [http://localhost:8080](http://localhost:8080).

Alternatives:

```bash
npx --yes serve -l 8080
```

There is no build step and no environment variables.

## Deploy

### GitHub Pages

1. Repo Settings → Pages.
2. Source: **Deploy from a branch**.
3. Branch: `main` / folder: `/ (root)`.
4. Site will serve `index.html` at `https://<user>.github.io/cad-product-shots/` (or the custom domain you attach).

`.nojekyll` is committed so Pages does not run Jekyll on the static files.

### Vercel

1. Import `JexLau/cad-product-shots`.
2. Framework Preset: **Other**.
3. Build Command: empty. Output Directory: `.` (root).
4. `vercel.json` enables clean URLs. No secrets required.

## Contact (TODO)

Primary CTA is `mailto:todo@example.com?subject=Free%20test%20frame%20STEP`. Replace the address and the footer `X` / email placeholders before a public launch.

## Docs

See [DESIGN.md](./DESIGN.md) for IA and the N=5 / ghost-perspective / free test still / no public price assumptions.
