#!/usr/bin/env python3
"""Profile banners for LinkedIn and X, made from the site's ASCII header.

Reads the built home page (../dustinmontgomery-site/index.html by default, or
$SITE/index.html) for the art and its CSS, and renders PNGs into this folder with
headless Chromium ($CHROME, or the same lookup build.py uses). Not part of the site.
"""
import os, re, subprocess, tempfile, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('SITE', os.path.join(os.path.dirname(os.path.dirname(HERE)), 'dustinmontgomery-site'))

def chrome():
    if os.environ.get('CHROME'):
        return os.environ['CHROME']
    shells = sorted(glob.glob(os.path.expanduser(
        '~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell')))
    if shells:
        return shells[-1]
    for n in ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable', 'chrome'):
        if shutil.which(n):
            return shutil.which(n)
    raise SystemExit('No Chromium found: set CHROME')

home = open(f'{SITE}/index.html', encoding='utf-8').read()
art = re.search(r'(<pre class="art art-dust".*?</pre><pre class="art art-mont".*?</pre>)', home, re.S).group(1)
style = re.search(r'<style>(.*?)</style>', home, re.S).group(1)
art_css = style[style.index('.artband'):]          # the hero art rules (shadow hack)

# name: (width, height, dust font px, CSS placing the art clear of the avatar)
# The art is sized to fill the banner's height, kept clear of where each site lays
# the profile photo over the banner (LinkedIn: bottom-left quarter; X: bottom-left).
BANNERS = {
    'linkedin-banner': (1584, 396, 25, 'right:56px;top:50%;transform:translateY(-50%)'),
    'x-header':        (1500, 500, 30, 'left:50%;top:50%;transform:translate(-50%,-50%)'),
}

for name, (w, h, px, place) in BANNERS.items():
    # The overlay reaches .6em past the text; it must stay inside the panel, because
    # outside it there is nothing to blend with and it shows as a light line.
    pad = max(16, round(px * .6) + 3)
    page = f"""<!doctype html><meta charset="utf-8"><style>
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:#0a0e0a}}
body{{background-image:radial-gradient(#132013 1.5px,transparent 1.5px);background-size:20px 20px}}
.art-box{{position:absolute;{place};background:#101710;border:1px solid #1d291b;padding:{pad}px {pad + 6}px}}
{art_css}
/* The R's tail crosses the bottom of the text box. Where the gradient ends and the
   dark fill below it starts, rounding can leave a 1px row covered by neither, and the
   overlay's light base colour showed through as a line under the R. Overlap the dark
   fill 2px into the gradient's (equally dark) end so no gap can open. */
pre.art::after{{inset:-.6em;background:linear-gradient(#1d3718,#1d3718) 0 100%/100% calc(.6em + 2px) no-repeat,
  linear-gradient(#dcfcd2 0%,#b4f1a6 26%,#84d876 27%,#6ec95f 50%,#3f7a35 51%,#33632a 76%,#27491f 77%,#1d3718 100%)
  0 .6em/100% calc(100% - 1.2em) no-repeat,#dcfcd2}}
pre.art-dust{{font-size:{px}px}}
pre.art-mont{{font-size:{px * 14.172 / 28.818:.3f}px;margin-top:{px * .45:.1f}px}}
</style><div class="art-box">{art}</div>"""
    with tempfile.TemporaryDirectory() as td:
        open(f'{td}/b.html', 'w').write(page)
        subprocess.run([chrome(), '--no-sandbox', '--hide-scrollbars', f'--window-size={w},{h}',
                        '--force-device-scale-factor=1', f'--screenshot={HERE}/{name}.png',
                        f'file://{td}/b.html'], check=True, capture_output=True)
    print(f'{name}.png  {w}x{h}')
