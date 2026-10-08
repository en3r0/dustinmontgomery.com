# dustinmontgomery.com

Source for https://dustinmontgomery.com. Plain static HTML: no cookies, no trackers,
no JavaScript. One Python script, `build.py`, generates every file of the site.

## Branches

| Branch     | What it holds                                                    |
|------------|------------------------------------------------------------------|
| `main`     | This: `build.py` and everything it reads. Edit here.             |
| `site`     | The built site. GitHub Pages serves this branch. Never hand-edit. |
| `gh-pages` | The old WordPress site, kept for reference.                      |

## Setup (new machine)

```sh
# 1. tools: Python 3, ffmpeg, and a Chromium (any of these works)
sudo apt install python3 ffmpeg chromium          # Debian/Ubuntu
# or: npx playwright install chromium-headless-shell

# 2. both branches, side by side
git clone https://github.com/en3r0/dustinmontgomery.com.git
git clone -b site https://github.com/en3r0/dustinmontgomery.com.git dustinmontgomery-site
```

`build.py` writes into `../dustinmontgomery-site` by default. Point it elsewhere
with `SITE=/path/to/site-checkout`. Chromium is found automatically (Playwright's
headless shell, or `chromium` / `google-chrome` on `PATH`); override with
`CHROME=/path/to/chrome`. It is only used to render images (`favicon.ico`, the
`og.png` share image, the before/after crops in "How This Site Works").

## Everyday loop

```sh
cd dustinmontgomery.com
python3 build.py                                   # rebuild the whole site; prints "ok"
python3 -m http.server 8080 --directory ../dustinmontgomery-site   # preview
```

Open http://localhost:8080/. When it looks right:

```sh
git add -A && git commit -m "..." && git push        # save the source (main)
cd ../dustinmontgomery-site
git add -A && git commit -m "..." && git push        # publish (site) - live in ~1 minute
```

Pushing `main` never changes the live site; only pushing `site` does.

## Where things are

Everything visible is defined in `build.py`. Search for these:

| To change                         | Look for in `build.py`                                      |
|-----------------------------------|-------------------------------------------------------------|
| The bio under the name            | `BIO =` (also the home page's search description)            |
| Nav links                         | `NAV =`                                                      |
| Site-wide CSS                     | `CSS = r"""`; the hero art's CSS is `ART_CSS`                |
| Head, header, footer of every page| `def page(`                                                  |
| Home page panels and their text   | `# home`: a series of `must_sub(old, new, b)` edits applied to `src/pages/index.html` |
| The /blog/ list                   | `# writing`                                                  |
| The SEO consulting page           | `# consulting`                                               |
| RSS feed                          | `feed.xml`                                                   |
| Sitemap                           | `urls = [`                                                   |
| Plain-text and colour twins       | `def to_text(`, `def to_ansi(`                               |

`must_sub(old, new, text)` replaces exactly one occurrence and stops the build if
`old` isn't found, so a typo in an edit fails loudly instead of silently.

The home, writing, consulting and 404 pages start from the first drafts in
`src/pages/` and are reworked by those `must_sub` edits. Articles migrated from
WordPress are converted from `src/wordpress/`.

## Adding a blog post

Copy what "How This Site Works" does (search `build.py` for `WORKS`):

1. **Write the body** in `src/posts/<slug>.html`: just the article's HTML (`<p>`,
   `<h2>`, `<pre><code>`, `<img>`...), no `<head>`/nav/footer. In code blocks write
   `<` `>` `&` as `&lt;` `&gt;` `&amp;`. No em dashes (brand rule).
2. **Images** for the post go in `src/posts/<slug>/`; they are copied next to the
   page, so reference them by file name (`<img src="photo.webp" ...>`). Use WebP and
   give every `<img>` an `alt`, `width` and `height`.
3. **Register the page** next to `WORKS`: a `(title, one-line summary)` tuple and a
   `wr(f'{SITE}/blog/<slug>/index.html', article('/blog/<slug>/', title, 'YYYY-MM-DD', body, summary))` call.
4. **List it** newest first:
   - on the home page: the `must_sub` under `# home` that builds the writing list;
   - on /blog/: the `must_sub` under `# writing`;
   - in `feed.xml`: a new `<item>` at the top, and update `<lastBuildDate>`;
   - in the sitemap: add `'/blog/<slug>/'` to `urls`.
5. `python3 build.py`, preview, then commit and push both checkouts.

The page title, `<time>` date, `h-entry` markup, share tags, and the `index.txt` /
`index.ansi` twins are all generated for you.

Keep the home page `index.html` under 14 KB (the footer promises it):
`wc -c ../dustinmontgomery-site/index.html`.

## What the build writes

- Every page (`index.html`) with the shared head, nav, footer and CSS.
- `index.txt` (plain) and `index.ansi` (24-bit colour) twins of every page, served to
  curl and terminal browsers by the Cloudflare Worker.
- `feed.xml`, `sitemap.xml`, `robots.txt`, `CNAME`, `.nojekyll`, `favicon.svg`,
  `favicon.ico`, `og.png`, and the WebP images.

The build only adds and overwrites files; if you rename or remove a page, delete
its old folder from `../dustinmontgomery-site` yourself.

## Cloudflare Worker

`cloudflare/worker.js` runs in front of GitHub Pages (terminal twins, old-URL
redirects, headers). It is deployed separately and rarely changes; see the comment
at the top of the file. Script name `dustinmontgomery-com`, route
`dustinmontgomery.com/*`.
