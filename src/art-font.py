#!/usr/bin/env python3
"""Writes src/art-font.woff2: a 5-glyph font (space and the block characters
█ ▀ ▄ ▌) for the hero ASCII art. Phones without these glyphs in their monospace
font (Android's Droid Sans Mono) borrowed them from a font with a different
width, which sheared the art; this one is embedded in the page, so every
browser draws the art from the same cells. build.py only reads the output;
re-run this (needs `pip install fonttools brotli`) only to change the glyphs."""
import os
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

UPM, W, ASC, DESC = 1000, 600, 800, -200  # 0.6em cells; with line-height:1 a cell is exactly one line
MID = (ASC + DESC) // 2
# Blocks reach into the neighbouring cell so adjacent cells never leave a seam: .03em
# sideways, .06em up and down (Chromium snaps glyph edges to whole pixels vertically,
# which swallowed .03em on phones). Inner edges (the half blocks' middle, ▌'s right
# side) stay exact.
O, OY = 30, 60

def box(x0, y0, x1, y1):
    p = TTGlyphPen(None)
    if x1 > x0:
        p.moveTo((x0, y0)); p.lineTo((x0, y1)); p.lineTo((x1, y1)); p.lineTo((x1, y0)); p.closePath()
    return p.glyph()

glyphs = {'.notdef': box(0, 0, 0, 0), 'space': box(0, 0, 0, 0),
          'full': box(-O, DESC - OY, W + O, ASC + OY), 'upper': box(-O, MID, W + O, ASC + OY),
          'lower': box(-O, DESC - OY, W + O, MID), 'left': box(-O, DESC - OY, W // 2, ASC + OY)}
fb = FontBuilder(UPM, isTTF=True)
fb.setupGlyphOrder(list(glyphs))
fb.setupCharacterMap({0x20: 'space', 0x2588: 'full', 0x2580: 'upper', 0x2584: 'lower', 0x258C: 'left'})
fb.setupGlyf(glyphs)
fb.setupHorizontalMetrics({g: (W, 0) for g in glyphs})
fb.setupHorizontalHeader(ascent=ASC, descent=DESC)
fb.setupNameTable({'familyName': 'artblocks', 'styleName': 'Regular'}, mac=False)
fb.setupOS2(version=4, sTypoAscender=ASC, sTypoDescender=DESC, sTypoLineGap=0,
            usWinAscent=ASC, usWinDescent=-DESC, fsSelection=0x80)  # USE_TYPO_METRICS
fb.setupPost(isFixedPitch=1, keepGlyphNames=False)
fb.updateHead(created=3_900_000_000, modified=3_900_000_000)  # fixed, so re-running gives the same bytes
fb.font.flavor = 'woff2'
fb.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'art-font.woff2'))
