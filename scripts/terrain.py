"""Shared ink mountain geometry for measured peaks and decorative depth.

Developed from the contour/brush techniques of Lingdong Huang's shan-shui-inf
(MIT). Foreground and background use the same faceted, asymmetric renderer.
"""
import math
import random
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
import palette

SNOW_THRESHOLD = 160


def add(parent, tag, attrs):
    return ET.SubElement(parent, f"{{{NS}}}{tag}", {k: str(v) for k, v in attrs.items()})


def pts(points):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def noise(x, seed):
    return (.50 + .24 * math.sin(x * 1.71 + seed * 2.37)
            + .14 * math.sin(x * 4.27 - seed * .83)
            + .08 * math.sin(x * 9.31 + seed * 1.17))


def brush(parent, points, color=None, width=.7, opacity=.3):
    color = palette.INK if color is None else color
    left, right = [], []
    for i, (x, y) in enumerate(points):
        a, b = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
        angle = math.atan2(b[1] - a[1], b[0] - a[0]) + math.pi / 2
        w = width * math.sin(math.pi * i / (len(points) - 1)) * (.65 + .35 * noise(i * .5, width))
        dx, dy = math.cos(angle) * w, math.sin(angle) * w
        left.append((x + dx, y + dy))
        right.append((x - dx, y - dy))
    add(parent, "polygon", {"points": pts(left + right[::-1]), "fill": color, "opacity": opacity})


def ridge(height, half, seed, base):
    rng = random.Random(seed)
    profiles = []
    for _ in range(2):
        slope = rng.uniform(1.1, 1.65)
        crags = []
        for lower, upper in [(.16, .34), (.37, .59), (.64, .83)]:
            if rng.random() < .85:
                crags.append((rng.uniform(lower, upper), rng.uniform(.055, .13), rng.uniform(.08, .23)))
        crags.append((rng.uniform(.22, .65), rng.uniform(.07, .15), -rng.uniform(.04, .13)))
        profiles.append((slope, crags))
    points = []
    for k in range(81):
        u = -1 + k / 40
        slope, crags = profiles[0 if u < 0 else 1]
        distance = abs(u)
        shape = (1 - distance) ** slope
        for position, width, amplitude in crags:
            shape += amplitude * max(0, 1 - abs(distance - position) / width)
        shape = max(0, min(1 - distance * .2, shape))
        rough = 1 - .12 * (1 - noise(k * .78, seed / 91 + .1)) * distance ** .4
        points.append((u * half, base - height * shape * rough))
    return points


def _snowcap(defs, parent, identifier, height, half, seed, base):
    """Snow settles into uneven summit gullies without changing the terrain.

    The cap is clipped twice: once to the actual mountain silhouette, then
    to its own ragged snowline for the shaded folds and exposed rock seams.
    Larger peaks carry deeper snow; all variation comes from the peak seed.
    """
    if height < SNOW_THRESHOLD:
        return
    rng = random.Random(seed + 2183)
    maturity = min(1, (height - SNOW_THRESHOLD) / 100)
    depth = height * (.13 + .12 * maturity)
    summit = base - height
    extent = half * .5
    # Unequal broad tongues, rather than a row of regular zigzags. These
    # channels continue the same slightly right-leaning rock planes below.
    channels = [(-.12, .075, .20), (.025, .04, .27), (.11, .06, .39)]
    phase = rng.uniform(-1, 1)

    def snowline(x):
        u = x / half
        line = .83 + .09 * math.sin(u * 21 + phase) + .035 * math.sin(u * 91 + phase * 2)
        for center, width, amount in channels:
            line += amount * max(0, 1 - abs(u - center - phase * .013) / width)
        return summit + depth * line

    edge = [(extent * (-1 + k / 30), snowline(extent * (-1 + k / 30)))
            for k in range(61)]
    cap = [(-extent, summit - 3), (extent, summit - 3)] + edge[::-1]
    snow = add(parent, "g", {
        "data-snowcap": identifier, "data-snow-height": f"{height:.5f}",
        "data-snow-depth": f"{depth:.5f}",
        "clip-path": f"url(#{identifier}-clip)",
    })
    add(snow, "polygon", {"points": pts(cap), "fill": palette.SNOW,
                           "opacity": palette.SNOW_OPACITY})
    clip = add(defs, "clipPath", {"id": identifier + "-snow-clip"})
    add(clip, "polygon", {"points": pts(cap)})
    folds = add(snow, "g", {"clip-path": f"url(#{identifier}-snow-clip)"})
    # A quiet shadow face and a narrow bright seam make the snow read as
    # snow-covered rock rather than an opaque triangle pasted onto the peak.
    fold = [(0, summit), (half * .018, summit + depth * .29),
            (half * .008, summit + depth * .48), (half * .085, summit + depth * 1.2),
            (half * .14, summit + depth * 1.3), (half * .045, summit + depth * .35)]
    add(folds, "polygon", {"points": pts(fold), "fill": palette.SNOW_SHADE, "opacity": ".28"})
    brush(folds, fold[:4], palette.SNOW_EDGE, .5, .30)
    for u, length in [(-.085, .3), (.045, .28), (.13, .43)]:
        x = half * (u + rng.uniform(-.012, .012))
        bottom = snowline(x)
        reach = depth * length
        # A thin sliver of exposed rock reaches upward from each gully.
        seam = [(x - half * .009, bottom + 3), (x - half * .012, bottom - reach * .36),
                (x - half * .004, bottom - reach), (x + half * .008, bottom - reach * .22),
                (x + half * .019, bottom + 3)]
        add(folds, "polygon", {"points": pts(seam), "fill": palette.MOUNTAIN, "opacity": ".42"})
        brush(folds, seam[1:4], palette.SNOW_EDGE, .4, .3)
    # Broken lower edges and a few short contour traces leave plenty of
    # untouched paper; the original silhouette remains the only outer rim.
    for start, stop in [(17, 25), (27, 34), (37, 43)]:
        brush(snow, edge[start:stop], palette.SNOW_EDGE, .52, .35)
    for i in range(7):
        x = rng.uniform(-half * .14, half * .13)
        y = summit + depth * rng.uniform(.25, .81)
        brush(folds, [(x, y), (x + 1.5, y + .8), (x + rng.uniform(3, 6), y + 1.2)],
              palette.SNOW_SHADE, .36, .30)


def paint_mountain(defs, parent, identifier, height, half, seed, base=535, detail=1):
    """Paint a peak with an exact height; atmosphere belongs to the caller."""
    rim = ridge(height, half, seed, base)
    silhouette = rim + [(half, base + 3), (-half, base + 3)]
    clip = add(defs, "clipPath", {"id": identifier + "-clip"})
    add(clip, "polygon", {"points": pts(silhouette)})
    add(parent, "polygon", {"points": pts(silhouette), "fill": palette.MOUNTAIN})
    add(parent, "polygon", {"points": pts(silhouette), "fill": "url(#mountain-wash)"})
    interior = add(parent, "g", {"clip-path": f"url(#{identifier}-clip)"})
    rng = random.Random(seed + 57)

    # Long rock planes read first; fine broken grain sits within them.
    fold = [(0, base - height), (.09 * half, base - height * .72),
            (-.02 * half, base - height * .47), (.24 * half, base - height * .2),
            (.4 * half, base + 4), (half, base + 4)]
    add(interior, "polygon", {"points": pts(fold), "fill": palette.BG, "opacity": ".32"})
    brush(interior, fold[:5], palette.INK, .9, .22)
    for sample in [19, 30, 53, 64]:
        x, top = min(rim[sample - 3:sample + 4], key=lambda point: point[1])
        direction = -1 if x < 0 else 1
        reach = base - top
        face = [(x, top), (x + direction * half * .025, top + reach * .28),
                (x + direction * half * .08, top + reach * .52),
                (x + direction * half * .16, base),
                (x + direction * half * .33, base)]
        add(interior, "polygon", {"points": pts(face), "fill": palette.BG, "opacity": ".12"})
        brush(interior, face[:4], palette.INK, .55, .20)

    for j in range(max(8, round(half * height / 850 * detail))):
        u = rng.uniform(-.94, .94)
        x = u * half
        top = rim[max(0, min(80, round((u + 1) * 40)))][1]
        start = top + rng.uniform(.03, .45) * (base - top)
        finish = min(base + 1, start + rng.uniform(.12, .55) * height)
        trace = []
        for k in range(9):
            t = k / 8
            trace.append((x + (noise(t * 5, j + seed) - .5) * (2 + height * .016)
                          + u * t * half * .12, start + t * (finish - start)))
        brush(interior, trace, palette.INK if j % 4 else palette.BG, rng.uniform(.35, .8), rng.uniform(.10, .22))

    # Broken strata follow the crags, with unequal offsets to avoid a mesh.
    for j, fraction in enumerate([.18, .29, .43, .61, .78]):
        contour = []
        for k, (x, y) in enumerate(rim):
            yy = base - (base - y) * fraction
            contour.append((x * (1.03 - fraction * .03), yy + math.sin(k * .3 + j) * min(2, height * .015)))
        for start, end in [(6 + j, 27 + j), (43 - j, 70 - j)]:
            brush(interior, contour[start:end], palette.INK, .34, .10 + .035 * fraction)

    for _ in range(round((6 + height / 9) * detail)):
        x = rng.uniform(-half * .84, half * .84)
        y = base - rng.uniform(.04, .54) * height
        brush(interior, [(x, y), (x + 3, y - 1), (x + rng.uniform(5, 11), y + 1)],
              palette.INK, rng.uniform(.3, .6), rng.uniform(.12, .25))
    _snowcap(defs, interior, identifier, height, half, seed, base)
    brush(parent, rim, palette.INK, .82, palette.OUTLINE_OPACITY)
    return rim
