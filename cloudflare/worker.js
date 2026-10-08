// Cloudflare Worker for dustinmontgomery.com: serve the plain-text twin of a page
// (index.txt, which the site generator writes next to every index.html) to
// terminal clients, and the normal HTML to everyone else.
//
// Runs on Cloudflare's servers only. Visitors' browsers never receive or run it,
// so the site's "no JavaScript" claim is unaffected.
//
// Not deployed yet: it needs DNS on Cloudflare first (see redirect-map.md,
// "When DNS moves to Cloudflare, also do this").
//
// The generator writes two twins per page: index.txt (plain) and index.ansi (the
// same text with 24-bit colour escapes: the ASCII art in the site's green stripes,
// green headings). curl, HTTPie and xh print straight to a terminal, so they get
// the colour one; wget saves to a file and the text browsers can't show escapes,
// so they get plain text.
//
// Escape hatches:
//   curl https://dustinmontgomery.com/?html    -> HTML even for curl
//   curl https://dustinmontgomery.com/?plain   -> plain text, no colour
//   https://dustinmontgomery.com/blog/index.txt -> text in any browser

// curl, wget, HTTPie/xh and the terminal browsers. Lynx and w3m render HTML fine
// apart from the ASCII-art header, so they get text too; drop them from this list
// to give them the HTML instead.
const TEXT_CLIENTS = /\b(curl|wget|httpie|xh|lynx|w3m|links|elinks)\b/i;
const COLOUR_CLIENTS = /\b(curl|httpie|xh)\b/i;

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const ua = request.headers.get("user-agent") || "";

    const isPage = url.pathname.endsWith("/"); // every page is a directory index
    const wantsText =
      (request.method === "GET" || request.method === "HEAD") &&
      isPage &&
      !url.searchParams.has("html") &&
      TEXT_CLIENTS.test(ua);

    if (!wantsText) {
      return fetch(request);
    }

    const colour = COLOUR_CLIENTS.test(ua) && !url.searchParams.has("plain");
    let text = null;
    for (const name of colour ? ["index.ansi", "index.txt"] : ["index.txt"]) {
      const res = await fetch(new URL(url.pathname + name, url.origin), { method: request.method });
      if (res.ok) {
        text = res;
        break;
      }
    }
    if (!text) {
      return fetch(request); // no twin for this path: fall back to the page
    }

    const headers = new Headers(text.headers);
    headers.set("content-type", "text/plain; charset=utf-8");
    headers.set("vary", "User-Agent");
    headers.set("link", `<${url.origin}${url.pathname}>; rel="alternate"; type="text/html"`);
    return new Response(text.body, { status: 200, headers });
  },
};
