#!/usr/bin/env python3
"""Generator for dustinmontgomery.com: shared head/nav/footer/CSS on every page,
the WordPress articles and case studies migrated from src/wordpress, and the
plain-text and colour twins. Run `python3 build.py`; see README.md."""
import re, html, os, subprocess

REPO = os.path.dirname(os.path.abspath(__file__))
# built site: a checkout of the `site` branch (what GitHub Pages serves)
SITE = os.environ.get('SITE', '/home/en3r0/Projects/dustinmontgomery-site')
WP = f'{REPO}/src/wordpress'   # the old WordPress pages and images this site migrated
SRC = f'{REPO}/src/pages'      # the hand-written first draft of the section pages
BASE = 'https://dustinmontgomery.com'
NEWSLETTER = 'https://dustin-montgomery.beehiiv.com/subscribe'
BIO = "A Christ follower who's been building websites for 25+ years. Still excited about technology."
BIO_DESC = BIO  # short enough to be the search description too

def rd(p): return open(p, encoding='utf-8').read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)

# ---------------------------------------------------------------- CSS
CSS = r"""*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#0a0e0a;color:#e7f1e2;overflow-x:hidden;
  font:13.5px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.wrap{max-width:1120px;margin:0 auto;padding:20px 16px 56px;
  position:relative;z-index:1}
.desk{display:grid;gap:13px;
  grid-template-columns:repeat(auto-fit,minmax(min(400px,100%),1fr))}
.desk>.win{margin:0}
.desk>.win.hero,.desk>.win.wide{grid-column:1/-1}
/* one-column regime: auto-fit can hand a panel the full 1120px wrap, which puts
   the measure back over 90 characters. Cap the wrap until two columns fit. */
@media (max-width:864px){.wrap{max-width:660px}}
.grid{position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:radial-gradient(#0f170f 1px,transparent 1px);
  background-size:14px 14px}
@media (max-width:700px){.grid{display:none}}
.vh{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;
  clip:rect(0 0 0 0);white-space:nowrap}
a{color:#a5eba0;text-decoration:none}
a:hover{text-decoration:underline}
/* links in running content are underlined, not told apart by colour alone */
.bd a{text-decoration:underline;text-decoration-color:#2f4a2b;
  text-underline-offset:3px}
.bd a:hover{text-decoration-color:currentColor}
nav{display:flex;flex-wrap:wrap;gap:3px 13px;align-items:baseline;
  border-bottom:1px solid #1d291b;padding:9px 0;margin-bottom:20px;font-size:12.5px}
nav a,nav .site{color:#7e8f78}
nav a.on{color:#a5eba0}
nav a:hover{color:#a5eba0}
nav .sp{flex:1;min-width:8px}
.win{background:#101710;border:1px solid #1d291b;margin:0 0 13px;
  container-type:inline-size}
.win>.bar{display:flex;align-items:center;gap:8px;background:#0c130c;
  border-bottom:1px solid #1d291b;padding:6px 10px}
/* a panel reached by an #anchor (nav projects / expert witness / elsewhere, the
   case-study list) flashes, then keeps a quiet highlight, so it is clear where the
   click went even when the page barely scrolls */
.win{scroll-margin-top:16px}
.win:target{border-color:#4d6a47}
.win:target>.bar h2,.win:target>.bar b{color:#a5eba0}
@media (prefers-reduced-motion:no-preference){
  .win:target{animation:hl 1.6s ease-out}
  .win:target>.bar{animation:hlbar 1.6s ease-out}
}
@keyframes hl{0%{border-color:#a5eba0;box-shadow:0 0 0 3px #a5eba055,0 0 18px #6ec95f66}
  100%{border-color:#4d6a47;box-shadow:0 0 0 0 transparent}}
@keyframes hlbar{0%{background:#1f3a1c}100%{background:#0c130c}}
.win>.bar i{width:7px;height:7px;border-radius:1px;background:#2b3a28;display:block;flex:none}
.win>.bar b,.win>.bar h2{margin:0 0 0 auto;color:#7e8f78;font-size:11.5px;letter-spacing:.06em;
  font-weight:400;line-height:inherit}
.win>.bd{padding:13px 14px 15px}
.win.hero>.bd{padding:16px 14px 18px;text-align:center}
h1,h2,h3,h4{font-size:13.5px;font-weight:400;margin:0 0 9px}
h1{color:#a5eba0}
p{margin:0 0 9px}
p:last-child,ul:last-child{margin-bottom:0}
p.more{margin-top:9px}
ul{margin:0;padding:0;list-style:none}
li{padding:6px 0;border-bottom:1px solid #1d291b}
li:last-child{border-bottom:0}
li .m{color:#7e8f78;font-size:11.5px;display:block;margin-top:2px}
.hero .bio{color:#e7f1e2;max-width:62ch;margin:14px auto 0}
.tag{color:#7e8f78;font-size:11.5px;letter-spacing:.06em}
.more+.tag{margin-top:18px}
.foot{border-top:1px solid #1d291b;margin-top:26px;padding-top:12px;
  color:#7e8f78;font-size:11.5px}
.cols{display:grid;grid-template-columns:1fr;gap:0 18px}
.cols li{padding:6px 0;border-bottom:1px solid #1d291b}
.cols li:last-child{border-bottom:1px solid #1d291b}
.cols li a{display:flex;justify-content:space-between;gap:10px}
.cols li a .m{display:inline;margin:0;font-size:11.5px;color:#7e8f78}
@container (min-width:490px){.cols{grid-template-columns:1fr 1fr}}
/* long-form: articles and case studies */
.prose{max-width:72ch}
/* long-form panels shrink to the 72ch measure (+ .bd padding and border) and
   sit centred, rather than a full-width window with the text against the left */
.desk>.win.doc{justify-self:center;width:100%;max-width:calc(72ch + 30px)}
.prose h2,.prose h3,.prose h4{margin:22px 0 9px}
.prose h2,.case h3{color:#a5eba0}
.prose h2::before{content:"## ";color:#4d6a47}
.prose h3::before,.case h4::before{content:"### ";color:#4d6a47}
.case h3::before{content:"## "}
.prose>:first-child{margin-top:0}
.prose ul,.prose ol{margin:0 0 9px;padding-left:2ch}
.prose ol{padding-left:3.5ch}
.prose ul{list-style:"- "}
.prose li{padding:2px 0;border:0}
.prose img{display:block;max-width:100%;height:auto;margin:4px 0 13px;
  border:1px solid #1d291b}
.prose .meta{color:#7e8f78;font-size:11.5px;margin-bottom:16px}
"""

ART_CSS = r"""
.artband{max-width:1058px;margin:0 auto}
pre.art{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  line-height:1;white-space:pre;margin:0 auto;display:block;
  width:fit-content;max-width:100%;position:relative;
  color:#dcfcd2;text-shadow:0 0 0 #dcfcd2,0 0 0 #dcfcd2,0 0 0 #dcfcd2,0 0 0 #dcfcd2}
/* background-clip:text leaves hairline seams between block glyphs, and text-shadow
   can't carry a gradient (it paints over a clipped background). So the glyphs are
   drawn solid in the lightest stop with 4 stacked 0-blur shadows, which closes the
   seams, and ::after lays the gradient on with mix-blend-mode:darken (per-channel
   min). #dcfcd2 is >= every stop and every stop is >= the #101710 card, so glyphs
   take the exact gradient and the card shows through untouched. Nothing between
   here and the card may isolate (filter, opacity, isolation), or the overlay
   paints as a solid block. Glyphs overhang the line box slightly, so the overlay
   reaches .3em past it; the gradient stays sized to the box. */
pre.art::after{content:"";position:absolute;inset:-.3em;pointer-events:none;
  background:
    linear-gradient(#1d3718,#1d3718) 0 100%/100% .3em no-repeat,
    linear-gradient(#dcfcd2 0%,#b4f1a6 26%,#84d876 27%,#6ec95f 50%,#3f7a35 51%,
      #33632a 76%,#27491f 77%,#1d3718 100%) 0 .3em/100% calc(100% - .6em) no-repeat,
    #dcfcd2;
  mix-blend-mode:darken}
pre.art-dust{font-size:min(2.0013vw,28.818px)}
pre.art-mont{font-size:min(0.9842vw,14.172px)}
"""

PREFETCH = ['/', '/blog/', '/seo-consulting/']

NAV = [('/', 'home'), ('/blog/', 'writing'), ('/#projects', 'projects'),
       ('/seo-consulting/', 'seo consulting'), ('/#expert-witness', 'expert witness'),
       ('/#elsewhere', 'elsewhere')]

def headings(body):
    """Panel titles become h2s so screen readers can jump between sections. A panel
    that holds the page's h1 (hero, article, 404) keeps a plain <b>, so no h2 comes
    before the h1."""
    parts = re.split(r'(?=<(?:div|section) class="win)', body)
    return ''.join(p if '<h1' in p else
                   re.sub(r'(<div class="bar"><i></i><i></i><i></i>)<b>(.*?)</b>', r'\1<h2>\2</h2>', p, count=1)
                   for p in parts)

def strip_css_comments(css):
    """The CSS comments document the generator; visitors don't need them."""
    return re.sub(r'/\*.*?\*/\n?', '', css, flags=re.S)

def page(path, title, desc, body, on=None, extra_css='', og_type='website', main_attrs='',
         home=False, canonical=True, noindex=False, extra_head='', main_class=''):
    url = BASE + path
    links = ''.join(f'<a href="{h}"{" class=\"on\" aria-current=\"page\"" if h == on else ""}>{t}</a>'
                    for h, t in NAV)
    size = (' This page is one file, under 14 KB.' if home else '')
    e = html.escape
    # the top-level pages are tiny and every nav link lands on one of them, so
    # fetch them at idle (anchors like /#projects resolve to /)
    prefetch = ''.join(f'<link rel="prefetch" href="{u}">\n' for u in PREFETCH if u != path)
    head_canon = (f'<link rel="canonical" href="{url}">\n'
                  f'<meta property="og:url" content="{url}">\n') if canonical else ''
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{'<meta name="robots" content="noindex">' + chr(10) if noindex else ''}{head_canon}<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Dustin Montgomery">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Dustin Montgomery, in green block-letter ASCII art">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@DustinMontgomer">
<meta name="twitter:creator" content="@DustinMontgomer">
{extra_head}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="Dustin Montgomery" href="/feed.xml">
{f'<link rel="alternate" type="text/plain" href="{path}index.txt">' + chr(10) if path.endswith('/') else ''}<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0a0e0a">
{prefetch}<style>{strip_css_comments(CSS + extra_css)}</style>
</head>
<body>
<div class="grid" aria-hidden="true"></div>
<div class="wrap">
<header><nav><span class="site">dustinmontgomery.com</span><span class="sp"></span>{links}</nav></header>
<main class="desk{main_class}"{main_attrs}>
{headings(body.strip()).replace('https://legittorrents.info/', 'https://www.legittorrents.info/')}
</main>
<footer class="foot">
<p>No cookies, no trackers, no JavaScript.{size}</p>
</footer>
</div>
</body>
</html>
"""

def win(title, inner, cls='', tag='div', id=''):
    i = f' id="{id}"' if id else ''
    c = f'win {cls}'.strip()
    return (f'<{tag} class="{c}"{i}><div class="bar"><i></i><i></i><i></i><b>{title}</b>'
            f'</div><div class="bd">{inner}</div></{tag}>')

def desk_of(path):
    """Body of the current hand-written page: everything inside <div class="desk">."""
    s = rd(path)
    m = re.search(r'<div class="desk">\n(.*)\n</div>\n<div class="foot">', s, re.S)
    assert m, path
    return m.group(1)

def fix_common(b):
    b = b.replace('<p style="margin-top:9px">', '<p class="more">')
    b = b.replace('href="/consulting/', 'href="/seo-consulting/')
    b = b.replace('>/consulting/</a>', '>/seo-consulting/</a>')
    b = b.replace('href="/writing/', 'href="/blog/').replace('>/writing/</a>', '>/blog/</a>')
    assert 'style=' not in b, b[b.index('style='):][:80]
    return b

def must_sub(old, new, s):
    assert old in s, old[:80]
    return s.replace(old, new)

# ------------------------------------------------- WordPress -> clean HTML
OLD2NEW = {
    'direct-to-consumer-seo': '/seo-consulting/direct-to-consumer-seo/',
    'what-is-dtc-ecommerce': '/seo-consulting/what-is-dtc-ecommerce/',
    'pros-and-cons-of-selling-direct-to-customers': '/seo-consulting/pros-and-cons-of-selling-direct-to-customers/',
    'how-manufacturers-can-successfully-sell-direct-to-consumers': '/seo-consulting/manufacturers-selling-direct/',
    'note-taking-applications': '/blog/note-taking-applications/',
}
KEEP = {'p', 'h2', 'h3', 'ul', 'ol', 'li', 'a', 'strong', 'em', 'br', 'img'}

def clean(frag):
    frag = re.sub(r'<(script|style|iframe|footer)[^>]*>.*?</\1>', '', frag, flags=re.S)
    frag = re.sub(r'<!--.*?-->', '', frag, flags=re.S)
    # Yoast FAQ block: question becomes an h3, answer stays a paragraph
    frag = re.sub(r'<strong class="schema-faq-question">(.*?)</strong>', r'<h3>\1</h3>', frag, flags=re.S)
    def tag(m):
        close, name, attrs = m.group(1), m.group(2).lower(), m.group(3) or ''
        if name not in KEEP:
            return ''
        if close:
            return f'</{name}>'
        if name == 'a':
            href = re.search(r'href="([^"]*)"', attrs).group(1)
            m2 = re.match(r'https?://(?:www\.)?dustinmontgomery\.com/([^/?#]+)/?$', href)
            if m2:
                href = OLD2NEW[m2.group(1)]
            return f'<a href="{href}">'
        if name == 'img':
            return m.group(0)  # handled by caller
        return f'<{name}>'
    frag = re.sub(r'<(/?)([a-zA-Z0-9]+)((?:\s[^>]*)?)/?>', tag, frag)
    frag = frag.replace('<p>&nbsp;</p>', '').replace('<p></p>', '')
    frag = re.sub(r'<br>\s*</a>', '</a><br>', frag)
    frag = re.sub(r'\n\s*\n+', '\n', frag).strip()
    return frag

def entry(p):
    s = rd(f'{WP}/{p}/index.html')
    m = re.search(r'<div class="entry-content[^"]*"[^>]*>(.*?)</article>', s, re.S)
    return s, m.group(1)

def first_sentence(frag):
    t = html.unescape(re.sub(r'<[^>]+>', '', re.search(r'<p>(.*?)</p>', frag, re.S).group(1)))
    return re.match(r'(.+?[.!?])(\s|$)', t.strip()).group(1)

ARTICLE_DATES = {}  # path -> ISO date, for the sitemap

def article(path, title, date, body, desc, extra_meta='', extra_css=''):
    """date is ISO: YYYY-MM-DD, or YYYY-MM when only the month is known."""
    ARTICLE_DATES[path] = date
    shown = nice_date(date) if len(date) == 10 else nice_month(date)
    inner = (f'<article class="prose h-entry"><link class="u-url" href="{BASE}{path}">'
             f'<h1 class="p-name">{html.escape(title)}</h1>'
             f'<p class="meta"><span class="p-author h-card">Dustin Montgomery</span> &middot; '
             f'<time class="dt-published" datetime="{date}">{shown}</time>{extra_meta}</p>\n'
             f'<div class="e-content">{body}</div></article>')
    return page(path, f'{title} · Dustin Montgomery', desc,
                win({'blog': 'writing'}.get(path.strip('/').split('/')[0],
                                            path.strip('/').split('/')[0].replace('-', ' ')), inner, 'wide doc'),
                on='/' + path.strip('/').split('/')[0] + '/', og_type='article', extra_css=extra_css,
                extra_head=f'<meta property="article:published_time" content="{date}">\n')

def nice_month(iso):
    import datetime
    return datetime.date.fromisoformat(iso + '-01').strftime('%B %Y')

def nice_date(iso):
    import datetime
    d = datetime.date.fromisoformat(iso[:10])
    return d.strftime('%B ') + str(d.day) + d.strftime(', %Y')

# ---- four DTC articles
DTC = [('direct-to-consumer-seo', 'direct-to-consumer-seo'),
       ('what-is-dtc-ecommerce', 'what-is-dtc-ecommerce'),
       ('pros-and-cons-of-selling-direct-to-customers', 'pros-and-cons-of-selling-direct-to-customers'),
       ('how-manufacturers-can-successfully-sell-direct-to-consumers', 'manufacturers-selling-direct')]
for old, new in DTC:
    s, frag = entry(old)
    title = html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1)).strip()
    date = re.search(r'datetime="([0-9T:\-+]+)"', s).group(1)
    body = clean(frag)
    assert '<img' not in body
    # "Key Takeaways" was an h3 straight under the h1; it heads its own section
    body = body.replace('<h3>Key Takeaways</h3>', '<h2>Key Takeaways</h2>')
    wr(f'{SITE}/seo-consulting/{new}/index.html',
       article(f'/seo-consulting/{new}/', title, date[:10], body, first_sentence(body)))

# ---- Note Taking Applications
s, frag = entry('note-taking-applications')
wr(f'{SITE}/blog/note-taking-applications/index.html',
   article('/blog/note-taking-applications/', 'Note Taking Applications', '2019-12-24',
           # doom-emacs moved to doomemacs/core; the old issue URL 404s
           clean(frag).replace('https://github.com/hlissner/doom-emacs/issues/2237',
                               'https://github.com/doomemacs/core/issues/2237'), "Tiago Forte's Building a Second Brain, and what I actually used: Joplin, "
           "Nextcloud Notes, MindForger, and Emacs (Doom) with the Remembrance Agent."))

# ---- I made a thing that haunts me (newsletter post, 2026-05-29, beehiiv). The
# body's first line repeated the title, so it is the h1 here instead.
HAUNT = ('I made a thing that haunts me.', 'Death comes for us all eventually.')

# ---- How This Site Works (2026-10-08). Body lives in src/posts/; code blocks get
# their styling on this page only, so no other page's CSS changes.
WORKS = ('How This Site Works', 'The ASCII art shadow hack, pages you can curl, and running it all for free.')
CODE_CSS = (
    '\n.prose pre{overflow-x:auto;background:#0c130c;border:1px solid #1d291b;'
    'padding:10px 12px;margin:0 0 13px;font-size:12px;line-height:1.5}'
    '\n.prose code{color:#cfe8c8}'
    '\n.prose p code{background:#0c130c;border:1px solid #1d291b;padding:0 3px}\n')
wr(f'{SITE}/blog/how-this-site-works/index.html',
   article('/blog/how-this-site-works/', WORKS[0], '2026-10-08',
           rd(f'{REPO}/src/posts/how-this-site-works.html').strip(), WORKS[1], extra_css=CODE_CSS))
wr(f'{SITE}/blog/i-made-a-thing-that-haunts-me/index.html',
   article('/blog/i-made-a-thing-that-haunts-me/', HAUNT[0], '2026-05-29', """<p>Death comes for us all eventually. The longer you live, the closer you get. Cherish it, plan for it. Do not waste it whatever you do!</p>
<p>This is not related to torrenting, but it is something I created and I wanted to share it with you.</p>
<p>Be warned, this site assumes you believe the Bible to be true, factual, and that you should act on that information.</p>
<p>If you do not believe these things I think the site could still be of use to you, but be warned the picture it paints is sobering.</p>
<p>Check it out: <a href="https://numberyour.day">numberyour.day</a></p>""", HAUNT[1]))

# ---- Seedless Torrents (hand-written HTML on the old site, not WordPress)
s = rd(f'{WP}/seedless-torrents.html')
frag = re.search(r'<h1[^>]*>.*?</h1>(.*)</div>\s*</body>', s, re.S).group(1)
frag = clean(frag)
# the beehiiv iframe was dropped (third-party embed); its sentence links out instead
frag = must_sub('You might also consider signing up for my newsletter where',
                f'You might also consider signing up for <a href="{NEWSLETTER}">my newsletter</a> where',
                frag)
os.makedirs(f'{SITE}/blog/seedless-torrents', exist_ok=True)
seen = []
def seedimg(m):
    src = re.search(r'src="images/([^"]+)"', m.group(0)).group(1)
    alt = re.search(r'alt="([^"]*)"', m.group(0)).group(1)
    name = os.path.splitext(src)[0] + '.webp'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{WP}/images/{src}',
                    '-vf', 'scale=720:-2', '-c:v', 'libwebp', '-quality', '60',
                    '-compression_level', '6', f'{SITE}/blog/seedless-torrents/{name}'], check=True)
    load = ('fetchpriority="high"' if not seen else 'loading="lazy"')
    seen.append(name)
    return f'<img src="{name}" alt="{alt}" width="720" height="540" {load} decoding="async">'
frag = re.sub(r'<img[^>]*>', seedimg, frag)
frag = re.sub(r'<p>\s*(<img[^>]*>)\s*</p>', r'\1', frag)
wr(f'{SITE}/blog/seedless-torrents/index.html',
   article('/blog/seedless-torrents/',
           'My Billion Dollar Idea (Seedless Torrents) is Dead - A Retrospective',
           '2025-02', frag,  # the post only says "February 2025"
           'An idea I had for about 20 years, prototyped with AI, and why it failed past 8 bits.'))

# ---------------------------------------------------- case studies (consulting)
CASES = [  # id on /seo-consulting/, old slug, image, alt
    ('dtc-ecommerce', 'dtc-ecommerce-case-study', '2024/02/dtc-organic-traffic-graph.png',
     'Organic traffic graph for the DTC eCommerce case study'),
    ('fortune-500', 'fortune-500-company-case-study', '2022/06/fortune-500-seo-traffic-case-study.png',
     'Traffic graph for the Fortune 500 case study'),
    ('startup', 'startup-case-study', '2022/06/startup-seo-traffic-case-study-940x108.png',
     'Traffic graph for the startup case study'),
    ('manufacturing', 'manufacturing-case-study', '2022/06/manufacturer-traffic-940x101.png',
     'Traffic graph for the manufacturing case study'),
    ('internal-linking', 'internal-linking-case-study', '2022/07/internal-linking-chart-940x117.png',
     'Traffic graph for the internal linking case study'),
]
TITLES = {'dtc-ecommerce': 'DTC eCommerce', 'fortune-500': 'Fortune 500 company',
          'startup': 'Startup', 'manufacturing': 'Manufacturing',
          'internal-linking': 'Internal linking'}
os.makedirs(f'{SITE}/seo-consulting/img', exist_ok=True)
case_panels = []
for cid, old, img, alt in CASES:
    s, frag = entry(old)
    body = clean(frag)
    # drop the old per-page sales footer; the consulting page has one contact panel
    body, n = re.subn(r'<h3>I drive profitable organic traffic.*$', '', body, flags=re.S)
    assert n == 1, cid
    body = body.strip()
    # the old pages had the headline as h3 and Client/Plan/... as h2; flip them so
    # the result headline leads the section
    body = re.sub(r'<(/?)h2>', r'<\1h4>', body)  # Client/Plan/...; the headline stays h3
    name = os.path.splitext(os.path.basename(img))[0] + '.webp'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{WP}/wp-content/uploads/{img}',
                    '-c:v', 'libwebp', '-lossless', '1', '-compression_level', '6',
                    f'{SITE}/seo-consulting/img/{name}'], check=True)
    w, h = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
                           'stream=width,height', '-of', 'csv=p=0', f'{SITE}/seo-consulting/img/{name}'],
                          capture_output=True, text=True, check=True).stdout.strip().split(',')
    tag = f'<img src="/seo-consulting/img/{name}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">'
    body = re.sub(r'<p>\s*<img[^>]*>\s*</p>|<img[^>]*>', '', body)
    # graph goes right before Results, where the old pages showed it
    n = body.count('<h4>Results</h4>')
    assert n == 1, (cid, n)
    body = re.sub(r'(<h4>Results</h4>)', tag + r'\n\1', body)
    case_panels.append(win(TITLES[cid].lower(), f'<div class="prose case">{body}</div>',
                           'wide doc', 'section', cid))

# ------------------------------------------------------------- hand-written pages
# home
b = fix_common(desk_of(f'{SRC}/index.html'))
b = must_sub('<div class="artband">', f'<link itemprop="url" class="u-url u-uid" href="{BASE}/"><h1 class="vh p-name" itemprop="name">Dustin Montgomery</h1><div class="artband">', b)
b = must_sub('</pre></div></div></div>', f'</pre></div><p class="bio p-note" itemprop="description">{BIO}</p></div></div>', b)
b = must_sub('<li><a href="https://x.com/DustinMontgomer">', '<li><a href="https://x.com/DustinMontgomer" rel="me" class="u-url" itemprop="sameAs">', b)
b = must_sub('<li><a href="https://www.linkedin.com/in/dustinmontgomery">', '<li><a href="https://www.linkedin.com/in/dustinmontgomery" rel="me" class="u-url" itemprop="sameAs">', b)
b = must_sub('<li><a href="/blog/">Seedless Torrents</a>', '<li><a href="/blog/seedless-torrents/">Seedless Torrents</a>', b)
b = must_sub('<li><a href="/blog/seedless-torrents/">Seedless Torrents</a>',
             f'<li><a href="/blog/how-this-site-works/">{WORKS[0]}</a><span class="m">{WORKS[1]}</span></li>'
             f'<li><a href="/blog/i-made-a-thing-that-haunts-me/">{HAUNT[0]}</a><span class="m">{HAUNT[1]}</span></li>'
             '<li><a href="/blog/seedless-torrents/">Seedless Torrents</a>', b)
# home lists the newest three; Note Taking stays on /blog/
b = must_sub('''<li><a href="/blog/">Note Taking Applications</a><span class="m">what I tried
and what stuck</span></li>
''', '', b)
# expert witness lives on LegitTorrents.info; the home panel is the only mention
# here, so this site has no page competing with that one
b = must_sub('''<b>witness</b></div><div class="bd"><p>Expert witness work on torrenting and BitTorrent technology,
from 17 years of running LegitTorrents.info.</p>
<p class="more"><a href="/witness/">Witness &rarr;</a></p>''',
'''<b>expert witness</b></div><div class="bd"><p>Expert witness work for attorneys handling cases involving
torrenting technology and copyright claims, from 17 years of operating the
largest fully legal torrent tracker.</p>
<p class="more"><a href="https://legittorrents.info/torrent-expert-witness.html">Full details &rarr;</a></p>''', b)
b = must_sub('''<a href="/seo-consulting/">Consulting &rarr;</a> &middot;
<a href="https://cal.com/dustinmontgomery/15min">Book 15 minutes</a></p>''',
             '<a href="/seo-consulting/">SEO consulting &rarr;</a></p>', b)
b = must_sub('<b>consulting</b>', '<b>seo consulting</b>', b)
b = must_sub('''One newsletter list, shared between
this site and LegitTorrents.info.</p>''', 'Get on the newsletter for infrequent updates.</p>', b)
b = must_sub('newsletter<span class="m">same list</span>', 'newsletter<span class="m">infrequent</span>', b)
b = must_sub('''<p>One 5 minute interview becomes a week of publish ready vertical clips. We feed
you questions through the glass, you answer on camera. No script, no editing, no
second person on screen. Just you, being human.</p>''',
             '<p>One 5 minute interview becomes a week of publish ready vertical clips.</p>', b)
b = must_sub('''<p>SEO work, when it is the right fit. Two results worth
naming: 0 to 55,000 organic visits a month in about a year, and +402,000 visits a
month in 9 months.</p>''', '''<p>I still do some SEO consulting for the right project. One site went from
nearly 0 to 55,000 organic visits a month in about a year, and another picked up
402,000 more visits a month in 9 months.</p>''', b)
# projects lives on the home page too: just ClipHuman, linked out
b = must_sub('<p class="more"><a href="/projects/">Projects &rarr;</a></p>',
             '<p class="more"><a href="https://cliphuman.com/">cliphuman.com &rarr;</a></p>'
             '<p class="tag">numberyour.day</p>'
             '<p>A free visual tool to help you number your days, in light of Psalm 90:12.</p>'
             '<p class="more"><a href="https://numberyour.day">numberyour.day &rarr;</a></p>', b)
b = must_sub('<div class="win"><div class="bar"><i></i><i></i><i></i><b>projects</b>',
             '<div class="win" id="projects"><div class="bar"><i></i><i></i><i></i><b>projects</b>', b)
b = must_sub('<div class="win"><div class="bar"><i></i><i></i><i></i><b>elsewhere</b>',
             '<div class="win" id="elsewhere"><div class="bar"><i></i><i></i><i></i><b>elsewhere</b>', b)
b = must_sub('<div class="win"><div class="bar"><i></i><i></i><i></i><b>expert witness</b>',
             '<div class="win" id="expert-witness"><div class="bar"><i></i><i></i><i></i><b>expert witness</b>', b)
home = page('/', 'Dustin Montgomery', BIO_DESC, b, on='/', extra_css=ART_CSS, home=True,
            main_attrs=' itemscope itemtype="https://schema.org/Person"', main_class=' h-card')

# writing
b = fix_common(desk_of(f'{SRC}/writing/index.html'))
b = re.sub(r'\n<div class="win"><div class="bar"><i></i><i></i><i></i><b>note</b>.*', '', b, flags=re.S)
assert 'todo' not in b
b = must_sub('<div class="bd"><ul><li><a href="/blog/seedless-torrents/">',
             f'<div class="bd"><ul><li><a href="/blog/how-this-site-works/">{WORKS[0]}</a><span class="m">{WORKS[1]}</span></li>'
             f'<li><a href="/blog/i-made-a-thing-that-haunts-me/">{HAUNT[0]}</a><span class="m">{HAUNT[1]}</span></li>'
             '<li><a href="/blog/seedless-torrents/">', b)
b = re.sub(r'<li><a href="/blog/', '<li class="h-entry"><a class="u-url p-name" href="/blog/', b)
b = b.replace('<span class="m">', '<span class="m p-summary">')
b = '<h1 class="vh p-name">Writing</h1>\n' + b.rstrip() + '\n' + win(
    'newsletter', '<p>Get on the newsletter for infrequent updates.</p>'
    f'<p class="more"><a href="{NEWSLETTER}">Subscribe &rarr;</a></p>') + '\n'
# the post list spans the row, so the half-width newsletter panel sits below it
b = must_sub('<div class="win"><div class="bar"><i></i><i></i><i></i><b>writing</b>',
             '<div class="win wide"><div class="bar"><i></i><i></i><i></i><b>writing</b>', b)
writing = page('/blog/', 'Writing · Dustin Montgomery', 'Notes on what I built and what broke.', b, on='/blog/',
               main_class=' h-feed')


# consulting
b = fix_common(desk_of(f'{SRC}/consulting/index.html'))
b = must_sub('<li>Home appliance manufacturer<span class="m">', '<li>DTC home appliance manufacturer<span class="m">', b)
old_list = re.search(r'<div class="win"><div class="bar"><i></i><i></i><i></i><b>case studies</b>.*?</div></div>\n', b, re.S).group(0)
new_list = win('case studies', '<ul>' + ''.join(
    f'<li><a href="#{i}">{t}</a><span class="m">{m}</span></li>' for i, t, m in [
        ('dtc-ecommerce', 'DTC eCommerce', 'DTC home appliance manufacturer, 0 to 55,000 organic visits a month'),
        ('fortune-500', 'Fortune 500 company', 'financial company, +402,000 visits a month in 9 months'),
        ('startup', 'Startup', 'niche food product startup, 26 to 79,658 visits a month in 12 months'),
        ('manufacturing', 'Manufacturing', 'transportation equipment manufacturer, +775% traffic in six months'),
        ('internal-linking', 'Internal linking', 'niche site in the outdoor space, +139,000 visits a month'),
    ]) + '</ul>') + '\n'
# services, from the old WordPress home page, in plainer words
SERVICES = [
    ('Technical audit', 'I go through the site for anything holding it back in Google, and give '
     'your team each problem along with how to fix it.'),
    ('Research', 'Where competitors are beating you, and which keywords to go after first, by '
     'difficulty, relevance and search volume.'),
    ('Content planning', 'A plan for every piece, with the target keyword, what product or service '
     'it supports, and when it goes live.'),
    ('Promotion', 'Backlink outreach once the content is up, aimed at the keywords that are '
     'hardest to win.'),
    ('White label', 'For agencies that want the work done under their name.'),
    ('General consulting', 'Help working out the roadmap and keeping it on track, even if I am not '
     'the one doing the work.'),
]
new_list += win('what I do', '<ul>' + ''.join(
    f'<li>{n}<span class="m">{d}</span></li>' for n, d in SERVICES) + '</ul>') + '\n'
assert b.count(old_list) == 1
b = b.replace(old_list, new_list)
b = re.sub(r'<div class="win"><div class="bar"><i></i><i></i><i></i><b>five case studies</b>.*?</ul></div></div>\n',
           '\n'.join(case_panels) + '\n', b, flags=re.S)
assert 'todo' not in b and b.count('<section') == 5
b = must_sub(' Kept here with the consulting material rather than under writing.', '', b)
b = must_sub('''SEO work, when it is the right fit. It is not the
headline here any more. It is one page, because it does not need more than one.</p>''',
             'I still do some SEO consulting for the right project. I have been building '
             'websites for over 25 years.</p>', b)
b = must_sub('<p>Two results worth naming:</p>', '<p>Two of the better results:</p>', b)
b = must_sub('''<p><a href="https://cal.com/dustinmontgomery/15min">Book 15
minutes</a>, or email <a href="mailto:hi@dustinmontgomery.com">hi@dustinmontgomery.com</a>.</p>''',
             '<p>Email <a href="mailto:hi@dustinmontgomery.com">hi@dustinmontgomery.com</a>.</p>', b)
b = '<h1 class="vh">SEO consulting</h1>\n' + b
consulting = page('/seo-consulting/', 'SEO consulting · Dustin Montgomery',
                  re.search(r'<meta name="description" content="([^"]*)"', rd(f'{SRC}/consulting/index.html')).group(1),
                  b, on='/seo-consulting/')

# 404: served at any path, so no canonical/og:url
b = fix_common(desk_of(f'{SRC}/404.html'))
b = must_sub('<p><span class="k">404</span> &nbsp;that path does not exist.</p>',
             '<h1>404 &nbsp;that path does not exist.</h1>', b)
b = must_sub('''<li><a href="/witness/">/witness/</a><span class="m">torrent expert witness
</span></li>
''', '', b)
notfound = page('/404.html', 'Not found · Dustin Montgomery', 'That page does not exist.', b, canonical=False, noindex=True)

for rel, s in [('index.html', home), ('blog/index.html', writing),
               ('seo-consulting/index.html', consulting),
               ('404.html', notfound)]:
    wr(f'{SITE}/{rel}', s)

# ------------------------------------------------------------- feed, sitemap, robots, icon
wr(f'{SITE}/feed.xml', f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Dustin Montgomery</title>
<link>{BASE}/</link>
<atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>
<description>Notes on what I built and what broke.</description>
<language>en</language>
<lastBuildDate>Thu, 08 Oct 2026 12:00:00 +0000</lastBuildDate>
<item>
  <title>How This Site Works</title>
  <link>{BASE}/blog/how-this-site-works/</link>
  <guid>{BASE}/blog/how-this-site-works/</guid>
  <pubDate>Thu, 08 Oct 2026 12:00:00 +0000</pubDate>
  <description>The ASCII art shadow hack, pages you can curl, and running it all for free.</description>
</item>
<item>
  <title>I made a thing that haunts me.</title>
  <link>{BASE}/blog/i-made-a-thing-that-haunts-me/</link>
  <guid>{BASE}/blog/i-made-a-thing-that-haunts-me/</guid>
  <pubDate>Fri, 29 May 2026 18:17:41 +0000</pubDate>
  <description>Death comes for us all eventually.</description>
</item>
<item>
  <title>Seedless Torrents</title>
  <link>{BASE}/blog/seedless-torrents/</link>
  <guid>{BASE}/blog/seedless-torrents/</guid>
  <pubDate>Sat, 01 Feb 2025 12:00:00 +0000</pubDate>
  <description>An idea I had for about 20 years, prototyped with AI, and why it
  failed past 8 bits.</description>
</item>
<item>
  <title>Note Taking Applications</title>
  <link>{BASE}/blog/note-taking-applications/</link>
  <guid>{BASE}/blog/note-taking-applications/</guid>
  <pubDate>Tue, 24 Dec 2019 12:03:27 +0000</pubDate>
  <description>Tiago Forte's Building a Second Brain, and what I actually used.</description>
</item>
</channel>
</rss>
""")

import datetime
BUILD_DATE = datetime.date.today().isoformat()
urls = ['/', '/blog/', '/blog/how-this-site-works/', '/blog/i-made-a-thing-that-haunts-me/', '/blog/seedless-torrents/', '/blog/note-taking-applications/',
        '/seo-consulting/'] + [f'/seo-consulting/{n}/' for _, n in DTC]
for u in urls:
    assert os.path.exists(f'{SITE}{u}index.html'), u
wr(f'{SITE}/sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
   '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
   ''.join(f'<url><loc>{BASE}{u}</loc><lastmod>{ARTICLE_DATES.get(u, BUILD_DATE)}</lastmod></url>\n'
           for u in urls) + '</urlset>\n')
wr(f'{SITE}/robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')

# 16x16 pixel D, same stripes as the hero art
D = ['11110', '10001', '10001', '10001', '10001', '10001', '11110']
stripes = ['#dcfcd2', '#b4f1a6', '#84d876', '#6ec95f', '#3f7a35', '#33632a', '#27491f']
rects = ''.join(f'<rect x="{3 + 2 * x}" y="{1 + 2 * y}" width="2" height="2" fill="{stripes[y]}"/>'
                for y, row in enumerate(D) for x, c in enumerate(row) if c == '1')
wr(f'{SITE}/favicon.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" shape-rendering="crispEdges">'
   f'<rect width="16" height="16" fill="#0a0e0a"/>{rects}</svg>\n')
# Plain-text twin of every page (index.txt next to index.html), for curl, Lynx and
# friends. Built from the finished HTML so it never drifts from the page.
from urllib.parse import urljoin
import textwrap

def to_text(page_html, url):
    main = re.search(r'<main[^>]*>(.*)</main>', page_html, re.S).group(1)
    # ASCII art: DUSTIN (61 columns) fits a terminal; MONTGOMERY (124) would wrap
    dust = re.search(r'<pre class="art art-dust"[^>]*>(.*?)</pre>', main, re.S)
    art = [l.rstrip() for l in html.unescape(dust.group(1)).split('\n')] if dust else []
    while art and not art[-1]:
        art.pop()
    main = re.sub(r'<pre class="art\b.*?</pre>', '', main, flags=re.S)
    code = []
    def keep_code(m):
        code.append(html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).rstrip('\n'))
        return f'\x00CODE{len(code) - 1}\x00P'
    main = re.sub(r'<pre\b[^>]*>(.*?)</pre>', keep_code, main, flags=re.S)
    main = re.sub(r'<code>(.*?)</code>', r'`\1`', main, flags=re.S)
    main = re.sub(r'<link\b[^>]*>', '', main)
    main = re.sub(r'<div class="bar"><i></i><i></i><i></i><b>.*?</b></div>', '', main)
    main = re.sub(r'<div class="bar"><i></i><i></i><i></i><h2>(.*?)</h2></div>', r'<h2>\1</h2>', main)
    links = []
    def a(m):
        href, inner = html.unescape(m.group(1)), m.group(2)
        absu = urljoin(url, href)
        if html.unescape(re.sub(r'<[^>]+>', '', inner)).strip() in (href, absu):
            return inner
        if absu not in links:
            links.append(absu)
        return f'{inner} [{links.index(absu) + 1}]'
    main = re.sub(r'<a\b[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', a, main, flags=re.S)
    main = re.sub(r'<img\b[^>]*?alt="([^"]*)"[^>]*>', '\x00P[image: \\1]\x00P', main)
    for t in ('h1', 'h2', 'h3', 'h4'):
        main = re.sub(rf'<{t}\b[^>]*>', '\x00' + t.upper(), main)
    main = re.sub(r'<p class="bio\b[^"]*"[^>]*>', '\x00BIO', main)
    main = re.sub(r'<li\b[^>]*>', '\x00LI', main)
    main = re.sub(r'<span class="m\b[^"]*">', '\x00M', main)
    main = re.sub(r'<br\s*/?>', '\x00BR', main)
    main = re.sub(r'</?(?:p|div|section|article|ul|ol|li|h[1-4])\b[^>]*>', '\x00P', main)
    main = html.unescape(re.sub(r'<[^>]+>', '', main))
    out = [url, ''] + (art + [''] if art else [])
    def para(text, first='', rest=''):
        out.extend(textwrap.wrap(text, 72, initial_indent=first, subsequent_indent=rest,
                                 break_long_words=False, break_on_hyphens=False))
    for part in main.split('\x00'):
        kind = next((k for k in ('CODE', 'H1', 'H2', 'H3', 'H4', 'BIO', 'LI', 'BR', 'M', 'P') if part.startswith(k)), 'P')
        if kind == 'CODE':
            out.append('')
            out.extend('    ' + line for line in code[int(part[4:])].split('\n'))
            continue
        text = ' '.join(part[len(kind):].split()) if part.startswith(kind) else ' '.join(part.split())
        if not text:
            continue
        if kind == 'H1':
            out += ['', text, '=' * min(len(text), 72)]
        elif kind in ('H2', 'H3', 'H4'):
            out += ['', '#' * int(kind[1]) + ' ' + text]
        elif kind == 'BIO':
            out.append('')
            for sentence in re.split(r'(?<=[.!?])\s+', text):
                para(sentence)
        elif kind == 'LI':
            out.append(''); para(text, '- ', '  ')
        elif kind == 'M':
            para(text, '  ', '  ')
        elif kind == 'BR':
            para(text)
        else:
            out.append(''); para(text)
    if links:
        out += ['', 'Links', '-----'] + [f'[{i}] {u}' for i, u in enumerate(links, 1)]
    text = '\n'.join(out)
    return re.sub(r'\n{3,}', '\n\n', text).strip() + '\n', len(art)

# Colour version for terminals (served to curl by the Cloudflare Worker): the art in
# the hero's stripes, headings green, link markers dimmed. 24-bit colour escapes.
STOPS = [(0, 0xdcfcd2), (.26, 0xb4f1a6), (.27, 0x84d876), (.50, 0x6ec95f),
         (.51, 0x3f7a35), (.76, 0x33632a), (.77, 0x27491f), (1, 0x1d3718)]

def stripe(pos):
    """Colour of the hero gradient at pos (0..1), as an ANSI 24-bit escape."""
    for (p0, c0), (p1, c1) in zip(STOPS, STOPS[1:]):
        if pos <= p1:
            f = (pos - p0) / (p1 - p0)
            rgb = [round(((c0 >> sh) & 255) + f * (((c1 >> sh) & 255) - ((c0 >> sh) & 255)))
                   for sh in (16, 8, 0)]
            return '\x1b[38;2;%d;%d;%dm' % tuple(rgb)

def to_ansi(text, art_rows):
    BRIGHT, DIM, BOLD, RESET = '\x1b[38;2;165;235;160m', '\x1b[38;2;126;143;120m', '\x1b[1m', '\x1b[0m'
    lines = text.split('\n')
    out = [DIM + lines[0] + RESET]                       # the URL line
    rows = art_rows + 1                                  # the art box had one blank row
    links = False
    for i, line in enumerate(lines[1:], 1):
        if 2 <= i < 2 + art_rows:                        # art starts after URL + blank
            out.append(stripe((i - 2 + .5) / rows) + line + RESET)
        elif i + 1 < len(lines) and lines[i + 1] and set(lines[i + 1]) == {'='}:
            out.append(BOLD + BRIGHT + line + RESET)     # page title
        elif line and set(line) <= {'=', '-'}:
            out.append(DIM + line + RESET)
        elif line.startswith('#'):
            out.append(BRIGHT + line + RESET)
        elif line == 'Links':
            links = True
            out.append(DIM + line + RESET)
        elif links:
            out.append(re.sub(r'^(\[\d+\])', DIM + r'\1' + RESET, line))
        else:
            out.append(re.sub(r'(\[\d+\])', DIM + r'\1' + RESET, line))
    return '\n'.join(out)

for dirpath, _, files in os.walk(SITE):
    if 'index.html' in files:
        rel = os.path.relpath(dirpath, SITE)
        path = '/' if rel == '.' else f'/{rel}/'
        text, art_rows = to_text(rd(f'{dirpath}/index.html'), BASE + path)
        wr(f'{dirpath}/index.txt', text)
        wr(f'{dirpath}/index.ansi', to_ansi(text, art_rows))

# Share image (og.png, 1200x630): the hero art and bio in a site window, rendered
# by headless Chromium from the finished home page, so it follows any bio change.
def render_og():
    home = rd(f'{SITE}/index.html')
    art = re.search(r'(<pre class="art art-dust".*?</pre><pre class="art art-mont".*?</pre>)', home, re.S).group(1)
    bio = '<br>'.join(re.split(r'(?<=[.!?])\s+', BIO))
    card = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#0a0e0a;
  font:22px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#e7f1e2}}
body{{background-image:radial-gradient(#0f170f 1.5px,transparent 1.5px);background-size:20px 20px}}
.card{{position:absolute;inset:44px;background:#101710;border:1px solid #1d291b;
  display:flex;flex-direction:column}}
.bar{{display:flex;align-items:center;gap:10px;background:#0c130c;border-bottom:1px solid #1d291b;
  padding:10px 16px}}
.bar i{{width:11px;height:11px;border-radius:2px;background:#2b3a28;display:block}}
.bar b{{margin-left:auto;color:#7e8f78;font-size:18px;letter-spacing:.06em;font-weight:400}}
.bd{{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center}}
{ART_CSS}
pre.art-dust{{font-size:27px}}
pre.art-mont{{font-size:13.278px}}
.bio{{margin:30px 60px 0;text-align:center;font-size:22px;line-height:1.5}}
</style></head><body><div class="card"><div class="bar"><i></i><i></i><i></i><b>dustinmontgomery.com</b></div>
<div class="bd">{art}<p class="bio">{bio}</p></div></div></body></html>"""
    with tempfile.TemporaryDirectory() as td:
        open(f'{td}/og.html', 'w').write(card)
        subprocess.run([CHROME, '--no-sandbox', '--hide-scrollbars', '--window-size=1200,630',
                        '--force-device-scale-factor=1', f'--screenshot={SITE}/og.png', f'file://{td}/og.html'],
                       check=True, capture_output=True)

wr(f'{SITE}/CNAME', 'dustinmontgomery.com\n')

# GitHub Pages: serve files as they are, never run Jekyll
wr(f'{SITE}/.nojekyll', '')

# /favicon.ico for crawlers and feed readers that never read <link rel=icon>:
# the SVG rendered at 32px, wrapped as a PNG-in-ICO
import struct, tempfile
CHROME = os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell')
with tempfile.TemporaryDirectory() as td:
    open(f'{td}/i.html', 'w').write('<body style="margin:0"><img src="file://' + SITE + '/favicon.svg" '
                                    'width="32" height="32" style="display:block">')
    subprocess.run([CHROME, '--no-sandbox', '--hide-scrollbars', '--window-size=32,32',
                    '--default-background-color=00000000', f'--screenshot={td}/i.png', f'file://{td}/i.html'],
                   check=True, capture_output=True)
    png = open(f'{td}/i.png', 'rb').read()
assert png[16:24] == struct.pack('>II', 32, 32), 'favicon render is not 32x32'
open(f'{SITE}/favicon.ico', 'wb').write(
    struct.pack('<HHH', 0, 1, 1) + struct.pack('<BBBBHHII', 32, 32, 0, 0, 1, 32, len(png), 22) + png)
render_og()
print('ok')
