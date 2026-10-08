# dustinmontgomery.com

Source for https://dustinmontgomery.com. Plain static HTML: no cookies, no trackers,
no JavaScript.

## Branches

| Branch     | What it holds                                               |
|------------|-------------------------------------------------------------|
| `main`     | This: the generator and its sources.                        |
| `site`     | The built site. GitHub Pages serves this branch.            |
| `gh-pages` | The old WordPress site, kept as-is for reference/rollback.  |

## Build

```sh
python3 build.py            # writes into $SITE (default: ../dustinmontgomery-site)
```

`$SITE` should be a checkout of the `site` branch. After a build, commit and push
that checkout to publish.

Requirements: Python 3, `ffmpeg` (WebP images) and Playwright's headless Chromium
(`~/.cache/ms-playwright/chromium_headless_shell-1243/...`, for `favicon.ico` and the
`og.png` share image).

## What the build writes

- Every page (`index.html`), with the shared head, nav, footer and CSS.
- `index.txt` (plain text) and `index.ansi` (24-bit colour) twins of every page,
  for curl and terminal browsers.
- `feed.xml`, `sitemap.xml`, `robots.txt`, `CNAME`, `.nojekyll`, `favicon.svg`,
  `favicon.ico`, `og.png`.

## Sources

- `src/pages/` - the first hand-written drafts of the home, writing, consulting and
  404 pages; `build.py` reworks them into the current pages.
- `src/wordpress/` - the pages and images migrated from the old WordPress site.
- `cloudflare/worker.js` - the Cloudflare Worker that sits in front of GitHub Pages
  (text twins for terminal clients, old-URL redirects, headers).

The URL migration plan and the Cloudflare cutover steps are in
`dm-reference/redirect-map.md` (outside this repo).
