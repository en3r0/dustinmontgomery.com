// Cloudflare Worker in front of dustinmontgomery.com (origin: GitHub Pages).
//
// Runs on Cloudflare's servers only. Visitors' browsers never receive or run it,
// so the site's "no JavaScript" claim is unaffected.
//
// It does four things:
//   1. Redirects the old WordPress URLs to their new homes (301), and answers 410
//      for WordPress machinery that has no new home.
//   2. Serves the plain-text twin (index.txt) or colour twin (index.ansi) of a page
//      to terminal clients. curl, HTTPie and xh print to a terminal, so they get
//      colour; wget saves to a file and the text browsers can't show escapes, so
//      they get plain text. ?html forces HTML, ?plain drops the colour.
//   3. Adds the Speculation-Rules header to HTML pages (Chrome prerenders a page
//      when a link to it is hovered), and serves the rules file it points to.
//   4. Gives images a longer browser cache than GitHub Pages' 10 minutes.
//
// Source of truth: this file on the `main` branch. Deploy notes: README.md.

// ---------------------------------------------------------------- 1. redirects

// Old path (no trailing slash) -> new URL. Case-study anchors are sections of
// /seo-consulting/.
const MOVED = {
  // the pages that rank
  "/dtc-ecommerce-case-study": "/seo-consulting/#dtc-ecommerce",
  "/fortune-500-company-case-study": "/seo-consulting/#fortune-500",
  "/startup-case-study": "/seo-consulting/#startup",
  "/manufacturing-case-study": "/seo-consulting/#manufacturing",
  "/manufacturing-client-case-study": "/seo-consulting/#manufacturing", // older slug (?p=511)
  "/internal-linking-case-study": "/seo-consulting/#internal-linking",
  "/direct-to-consumer-seo": "/seo-consulting/direct-to-consumer-seo/",
  "/what-is-dtc-ecommerce": "/seo-consulting/what-is-dtc-ecommerce/",
  "/pros-and-cons-of-selling-direct-to-customers": "/seo-consulting/pros-and-cons-of-selling-direct-to-customers/",
  "/how-manufacturers-can-successfully-sell-direct-to-consumers": "/seo-consulting/manufacturers-selling-direct/",
  "/note-taking-applications": "/blog/note-taking-applications/",
  "/seedless-torrents.html": "/blog/seedless-torrents/",
  // old consulting pages
  "/seo": "/seo-consulting/",
  "/welcome": "/seo-consulting/",
  "/anchored-networks-consult": "/seo-consulting/",
  "/author/dustinauthor": "/",
  // WordPress listings collapse to the blog
  "/blog-2": "/blog/",
  "/blog-3": "/blog/",
  "/blog-3/page/2": "/blog/",
  "/page/1": "/blog/",
  "/page/2": "/blog/",
  "/category/blog": "/blog/",
  "/category/blog/page/1": "/blog/",
  "/category/case-studies": "/seo-consulting/",
  "/category/case-studies/page/1": "/seo-consulting/",
  "/category/uncategorized": "/blog/",
  "/category/uncategorized/page/1": "/blog/",
  // feeds and sitemaps
  "/feed": "/feed.xml",
  "/category/blog/feed": "/feed.xml",
  "/category/case-studies/feed": "/feed.xml",
  "/category/uncategorized/feed": "/feed.xml",
  "/sitemap_index.xml": "/sitemap.xml",
  "/post-sitemap.xml": "/sitemap.xml",
  "/page-sitemap.xml": "/sitemap.xml",
};

// WordPress short links: /?p=N and /?page_id=N, from the old feeds and sitemap.
const SHORTLINKS = {
  "p=1361": "/seo-consulting/#startup",
  "p=1380": "/seo-consulting/#fortune-500",
  "p=1395": "/seo-consulting/#internal-linking",
  "p=1402": "/seo-consulting/direct-to-consumer-seo/",
  "p=1410": "/seo-consulting/pros-and-cons-of-selling-direct-to-customers/",
  "p=1428": "/seo-consulting/what-is-dtc-ecommerce/",
  "p=1439": "/seo-consulting/manufacturers-selling-direct/",
  "p=1453": "/seo-consulting/#dtc-ecommerce",
  "p=511": "/seo-consulting/#manufacturing",
  "page_id=1198": "/",
};

// Gone for good: answer 410 so search engines drop them.
const GONE = [/^\/wp-(content|includes|admin)(\/|$)/, /^\/wp-login\.php$/, /^\/xmlrpc\.php$/, /^\/comments\/feed\/?$/];

function redirect(url) {
  if (url.pathname === "/") {
    for (const key of ["p", "page_id"]) {
      const id = url.searchParams.get(key);
      if (id && SHORTLINKS[`${key}=${id}`]) return SHORTLINKS[`${key}=${id}`];
    }
    return null;
  }
  const path = url.pathname.replace(/\/index\.html$/, "").replace(/\/+$/, "");
  return MOVED[path] || null;
}

// ------------------------------------------------------- 2. terminal clients

const TEXT_CLIENTS = /\b(curl|wget|httpie|xh|lynx|w3m|links|elinks)\b/i;
const COLOUR_CLIENTS = /\b(curl|httpie|xh)\b/i;

async function terminalTwin(request, url, ua) {
  const colour = COLOUR_CLIENTS.test(ua) && !url.searchParams.has("plain");
  for (const name of colour ? ["index.ansi", "index.txt"] : ["index.txt"]) {
    const res = await fetch(new URL(url.pathname + name, url.origin), { method: request.method });
    if (res.ok) {
      const headers = new Headers(res.headers);
      headers.set("content-type", "text/plain; charset=utf-8");
      headers.set("vary", "User-Agent");
      headers.set("link", `<${url.origin}${url.pathname}>; rel="alternate"; type="text/html"`);
      return new Response(res.body, { status: 200, headers });
    }
  }
  return null; // no twin for this path
}

// ---------------------------------------------------- 3. speculation rules

const RULES_PATH = "/speculationrules.json";
const RULES = JSON.stringify({
  prerender: [{ where: { href_matches: "/*" }, eagerness: "moderate" }],
});

// ------------------------------------------------------------- 4. caching

const IMAGE = /\.(webp|png|ico|svg)$/;

// --------------------------------------------------------------------------

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const ua = request.headers.get("user-agent") || "";
    const readOnly = request.method === "GET" || request.method === "HEAD";

    if (readOnly) {
      const to = redirect(url);
      if (to) {
        return Response.redirect(new URL(to, url.origin).toString(), 301);
      }
      if (GONE.some((re) => re.test(url.pathname))) {
        return new Response("Gone. This was part of the old WordPress site.\n", {
          status: 410,
          headers: { "content-type": "text/plain; charset=utf-8" },
        });
      }
      if (url.pathname === RULES_PATH) {
        return new Response(request.method === "HEAD" ? null : RULES, {
          headers: {
            "content-type": "application/speculationrules+json",
            "cache-control": "public, max-age=86400",
          },
        });
      }
      if (url.pathname.endsWith("/") && !url.searchParams.has("html") && TEXT_CLIENTS.test(ua)) {
        const twin = await terminalTwin(request, url, ua);
        if (twin) return twin;
      }
    }

    const res = await fetch(request);
    const type = res.headers.get("content-type") || "";
    if (res.ok && type.startsWith("text/html")) {
      const out = new Response(res.body, res);
      out.headers.set("speculation-rules", `"${RULES_PATH}"`);
      return out;
    }
    if (res.ok && IMAGE.test(url.pathname)) {
      const out = new Response(res.body, res);
      out.headers.set("cache-control", "public, max-age=604800");
      return out;
    }
    return res;
  },
};
