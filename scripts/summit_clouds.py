"""Sparse foreground mist that passes over the upper mountain faces.

The caller places the supplied group after the mountain track and before
nearby birds. Native SVG gradients soften the wash without raster filters.
"""
import xml.etree.ElementTree as ET

import palette

NS = "http://www.w3.org/2000/svg"


def _add(parent, tag, attrs=None):
    return ET.SubElement(parent, f"{{{NS}}}{tag}",
                         {name: str(value) for name, value in (attrs or {}).items()})


def _wash(defs):
    # On white paper the body veils dark rock marks; on the two dark papers
    # the same pale wash uses less pigment so it remains a transparent wisp.
    light_paper = int(palette.BG[1:3], 16) > 200
    mist = palette.BG if light_paper else palette.INK
    density = 1 if light_paper else .28
    fill = _add(defs, "linearGradient", {
        "id": "summit-mist-wash", "x1": 0, "y1": 0, "x2": 0, "y2": 1,
    })
    for offset, opacity in [(0, 0), (.14, .07), (.35, .56), (.54, .92),
                            (.73, .38), (.9, .06), (1, 0)]:
        _add(fill, "stop", {"offset": offset, "stop-color": mist,
                             "stop-opacity": opacity * density})
    shadow = _add(defs, "linearGradient", {
        "id": "summit-mist-shadow", "x1": 0, "y1": 0, "x2": 0, "y2": 1,
    })
    for offset, opacity in [(0, 0), (.4, .08 if light_paper else .035),
                            (.65, .055 if light_paper else .025), (1, 0)]:
        _add(shadow, "stop", {"offset": offset, "stop-color": palette.CLOUD,
                               "stop-opacity": opacity})
    edge = _add(defs, "linearGradient", {
        "id": "summit-mist-edge", "x1": 0, "y1": 0, "x2": 1, "y2": 0,
    })
    for offset, opacity in [(0, 0), (.12, .45), (.3, 1), (.7, 1), (.9, .4), (1, 0)]:
        _add(edge, "stop", {"offset": offset, "stop-color": "white", "stop-opacity": opacity})
    mask = _add(defs, "mask", {"id": "summit-mist-mask", "maskUnits": "userSpaceOnUse",
                               "x": 0, "y": -5, "width": 440, "height": 65})
    _add(mask, "rect", {"x": 0, "y": -5, "width": 440, "height": 65,
                         "fill": "url(#summit-mist-edge)"})
    mark = _add(defs, "g", {"id": "summit-mist-mark", "mask": "url(#summit-mist-mask)"})
    # Broken, uneven deposits form long tendrils rather than a cloud outline.
    for d, opacity in [
        ("M0 26 C39 19 70 24 104 17 C136 10 151 18 181 11 "
         "C208 4 225 14 250 10 C278 6 298 16 320 14 "
         "C349 12 372 23 420 23 C380 26 352 30 324 27 "
         "C294 24 280 34 251 30 C223 26 206 35 180 31 "
         "C146 25 126 35 100 30 C67 24 36 30 0 26Z", 1),
        ("M47 32 C79 26 102 33 131 27 C157 22 175 29 195 24 "
         "C226 17 244 29 269 25 C297 21 309 31 337 29 "
         "C318 39 297 33 273 38 C248 43 230 33 207 38 "
         "C182 42 165 35 143 39 C115 42 93 34 47 32Z", .77),
        ("M208 16 C240 8 267 15 284 9 C304 2 321 12 343 8 "
         "C372 4 394 15 437 17 C408 20 388 17 364 20 "
         "C336 23 316 15 296 19 C267 23 246 17 208 16Z", .56),
    ]:
        _add(mark, "path", {"d": d, "fill": "url(#summit-mist-wash)", "opacity": opacity})
    _add(mark, "path", {
        "d": "M29 32 C69 24 101 35 129 29 C154 23 183 33 211 28 "
             "C243 23 264 35 296 30 C322 26 346 32 393 30 "
             "C352 41 323 35 299 40 C267 46 247 36 220 41 "
             "C188 46 167 37 138 42 C105 46 78 36 29 32Z",
        "fill": "url(#summit-mist-shadow)",
    })


def build_summit_clouds(defs, front_group):
    """Add two independently drifting, sparsely populated foreground lanes.

    Coordinates match the existing scene before its vertical translation.
    Both lanes have long gaps and wrap outside the masked artwork. Their
    speeds differ from the mountains, revealing and veiling the same summit.
    """
    _wash(defs)
    for name, duration, marks in [
        ("high", 180, [(395, 272, 1, .9, 1), (1040, 292, .47, .6, .62)]),
        ("low", 90, [(-95, 346, .78, .7, .72), (765, 350, .6, .82, .72)]),
    ]:
        tile = _add(defs, "g", {"id": f"summit-cloud-{name}-tile"})
        for x, y, sx, sy, opacity in marks:
            _add(tile, "use", {"href": "#summit-mist-mark",
                                "transform": f"translate({x} {y}) scale({sx} {sy})",
                                "opacity": opacity})
        lane = _add(front_group, "g", {
            "class": f"summit-cloud-motion summit-cloud-{name}",
            "data-summit-cloud-lane": name, "data-cloud-period": 1200,
            "data-cloud-duration": duration, "data-cloud-speed": -1200 / duration,
            "aria-hidden": "true",
        })
        for offset in [-1200, 0, 1200, 2400]:
            _add(lane, "use", {"href": f"#summit-cloud-{name}-tile", "x": offset})
    return CSS


CSS = """
.summit-cloud-motion { animation:summit-cloud-drift 180s linear infinite; }
.summit-cloud-low { animation-duration:90s; }
@keyframes summit-cloud-drift {
  from { transform:translateX(0px); }
  to { transform:translateX(-1200px); }
}
@media(prefers-reduced-motion:reduce) {
  .summit-cloud-motion { animation:none !important; }
}
"""
