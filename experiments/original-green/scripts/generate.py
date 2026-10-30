#!/usr/bin/env python3
"""A living, vector-native commit landscape. Python standard library only.

Procedural mountain contours and tapered brush strokes are adapted from
Lingdong Huang's shan-shui-inf (MIT); see THIRD_PARTY_NOTICES.md.
This continues the first design's simplified renderer, not the full engine.
"""
from pathlib import Path
from collections import OrderedDict
import copy
import datetime as dt
import json
import math
import random
import xml.etree.ElementTree as ET

from ambient import build_ambient
from terrain import paint_mountain
from vegetation import tree

ROOT = Path(__file__).resolve().parents[1]
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
BG, INK, MUTED = "#101919", "#dbe4ce", "#a5b6a9"
FINE, JADE, TREE, RED = "#536f63", "#315649", "#a6b8a0", "#e78772"
SERIF = "Georgia, Times New Roman, serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, monospace"
SPACING, BASE, MAX_HEIGHT = 210, 535, 260
PERIOD = 13 * SPACING
CENTER = SPACING / 2
START = 9 * SPACING + CENTER - 600  # July's summit opens at the center.
FAR_PERIOD, MID_PERIOD, SHORE_PERIOD = PERIOD / 4, PERIOD / 2, PERIOD * 1.25


def add(parent, tag, attrs=None, text=None):
    node = ET.SubElement(parent, f"{{{NS}}}{tag}",
                         {k: str(v) for k, v in (attrs or {}).items()})
    node.text = text
    return node


def label(parent, x, y, text, size=16, color=INK, font=MONO, anchor="start", **attrs):
    return add(parent, "text", {"x": x, "y": y, "font-family": font,
               "font-size": size, "fill": color, "text-anchor": anchor, **attrs}, str(text))


def pts(points):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def noise(x, seed):
    return (.50 + .24 * math.sin(x * 1.71 + seed * 2.37)
            + .14 * math.sin(x * 4.27 - seed * .83)
            + .08 * math.sin(x * 9.31 + seed * 1.17))


def brush(parent, points, color=INK, width=.7, opacity=.3):
    """Tapered polygons preserve the ink edge without SVG stroke filters."""
    left, right = [], []
    for i, (x, y) in enumerate(points):
        a, b = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
        angle = math.atan2(b[1] - a[1], b[0] - a[0]) + math.pi / 2
        w = width * math.sin(math.pi * i / (len(points) - 1)) * (.65 + .35 * noise(i * .5, width))
        dx, dy = math.cos(angle) * w, math.sin(angle) * w
        left.append((x + dx, y + dy))
        right.append((x - dx, y - dy))
    add(parent, "polygon", {"points": pts(left + right[::-1]), "fill": color, "opacity": opacity})


def mountain(defs, month, index, peak):
    count = month["commits"]
    height = max(7, MAX_HEIGHT * (count / peak) ** 2) if count else 0
    half = (45 + 130 * (count / peak) ** 1.15) * (.92 + .14 * noise(index, 17))
    node = add(defs, "g", {"id": f"mountain-{index}", "data-month": month["month"],
               "data-commits": count, "data-height": f"{height:.5f}", "data-center": CENTER + index * SPACING})
    add(node, "title", text=f'{month["month"]}: {count} commits')
    if count:
        paint_mountain(defs, node, f"mountain-{index}", height, half, 743 + index * 91)
    return height


def connected_land(parent):
    """A shallow, continuous shelf grounds the peaks without filling the river."""
    upper, lower = [], []
    for i in range(274):
        x = PERIOD * i / 273
        phase = 2 * math.pi * x / PERIOD
        upper.append((x, BASE - 3 + 1.6 * math.sin(phase * 11 + .7)
                      + .8 * math.sin(phase * 29)))
        lower.append((x, BASE + 14 + 2.1 * math.sin(phase * 7 + 1.3)
                      + 1.1 * math.sin(phase * 31 + .9)))
    land = add(parent, "g", {"data-scenery": "connected-shoreline"})
    add(land, "polygon", {"points": pts(upper + lower[::-1]), "fill": "url(#land-wash)"})
    # Broken edges and little mineral strokes avoid an outlined ribbon.
    for start in range(3, len(lower) - 9, 13):
        brush(land, lower[start:start + 9], FINE, .55, .30)
    rng = random.Random(810)
    for i in range(72):
        x = rng.uniform(12, PERIOD - 44)
        y = rng.uniform(BASE + 4, BASE + 10)
        length = rng.uniform(8, 27)
        brush(land, [(x, y), (x + length * .45, y - rng.uniform(.3, 1.2)),
                     (x + length, y + .2)], FINE, .32, rng.uniform(.15, .28))


def decoration(defs):
    # Real cragged mountains in every depth plane, sharing the main renderer.
    # Paint separate low-contrast tiles; their repeats are explicitly wrapped.
    for name, period, count, opacity, seed, baseline in [
        ("far", FAR_PERIOD, 5, .18, 4201, 513),
        ("mid", MID_PERIOD, 10, .30, 7271, 528),
    ]:
        clipping = add(defs, "clipPath", {"id": f"{name}-period"})
        add(clipping, "rect", {"x": 0, "y": 240, "width": period, "height": 305})
        tile = add(defs, "g", {"id": f"{name}-tile", "clip-path": f"url(#{name}-period)", "opacity": opacity})
        rng = random.Random(seed)
        mountains = []
        for i in range(count):
            center = (i + .5) * period / count + rng.uniform(-22, 22)
            # Unequal massing avoids a fence of similarly sized background peaks.
            heights = [74, 117, 46, 91, 61] if name == "far" else [58, 86, 45, 71, 38, 92, 52, 76, 44, 65]
            height = heights[i] + rng.uniform(-6, 6)
            half = height * .62 + rng.uniform(35, 57)
            identifier = f"{name}-peak-{i}"
            peak = add(defs, "g", {"id": identifier, "data-decorative-peak": name})
            paint_mountain(defs, peak, identifier, height, half, seed + i * 123, baseline, detail=.5)
            mountains.append((height, center, identifier))
        for height, center, identifier in sorted(mountains, reverse=True):
            for offset in [-period, 0, period]:
                add(tile, "use", {"href": f"#{identifier}", "x": center + offset})
    shore = add(defs, "g", {"id": "shore-tile"})
    rng = random.Random(183)
    for i in range(11):
        x = 110 + i * (SHORE_PERIOD / 11) + rng.uniform(-68, 68)
        y = rng.uniform(546, 564)
        half = rng.uniform(26, 66)
        rock = [(x - half, y + 3), (x - half * .65, y - 1), (x - 8, y - 4),
                (x + half * .38, y - 1.8), (x + half, y + 3)]
        add(shore, "polygon", {"points": pts(rock), "fill": BG, "opacity": ".82"})
        brush(shore, rock, FINE, .8, .6)
        # Low angular stones and broken bank strokes ground each planting.
        for j in range(3):
            rx = x + rng.uniform(-half * .55, half * .55)
            width = rng.uniform(5, 14)
            rise = rng.uniform(2, 5)
            stone = [(rx - width, y + 1), (rx - width * .42, y - rise * .8),
                     (rx + width * .15, y - rise), (rx + width, y + 1)]
            add(shore, "polygon", {"points": pts(stone), "fill": "#1d302a", "opacity": ".7"})
            brush(shore, stone, TREE, .35, .27)
        for j in range(2):
            offset = rng.uniform(-half * .65, half * .2)
            brush(shore, [(x + offset, y + 4 + j * 2), (x + offset + 12, y + 3.6 + j * 2),
                          (x + offset + 31, y + 4 + j * 2)], FINE, .45, .32)
        for j in range(1 + (i % 3 == 0)):
            tree(shore, x + rng.uniform(-14, 14), y - 2, rng.uniform(28, 45), (i + j) % 3, i * 11 + j)
        # A few low reeds, so islands do not look uniformly planted.
        if i % 4 == 1:
            for j in range(5):
                xx = x + half * .5 + j * 2
                brush(shore, [(xx, y), (xx + 1, y - 3), (xx + rng.uniform(-2, 3), y - rng.uniform(4, 9))], TREE, .32, .35)


def month_labels(parent, month, index, peak_day):
    cx = CENTER + index * SPACING
    node = add(parent, "g", {"data-label-month": month["month"], "data-commits": month["commits"], "data-center": cx,
                                      "transform": f"translate({cx} 0)"})
    first, last = [dt.date.fromisoformat(month["days"][i]["date"]) for i in [0, -1]]
    add(node, "path", {"d": "M0 622 L0 632 M-2 625 L0 623 L2 625", "stroke": RED, "stroke-width": ".8", "fill": "none", "opacity": ".65"})
    label(node, 0, 654, first.strftime("%B %Y"), 19, INK, SERIF, "middle")
    label(node, 0, 675, f'{first.strftime("%b").upper()} {first.day:02d} — {last.day:02d}', 11, MUTED, anchor="middle", **{"letter-spacing": "1.4"})
    label(node, -36, 714, f'{month["commits"]}', 30, INK, SERIF, "middle")
    label(node, -36, 733, "COMMITS", 10, MUTED, anchor="middle", **{"letter-spacing": "1.5"})
    # A compact calendar travels beside each total, preserving daily detail.
    calendar = add(node, "g", {"data-calendar-month": month["month"]})
    first_of_month = first.replace(day=1)
    offset = (first_of_month.weekday() + 1) % 7
    for day in month["days"]:
        date = dt.date.fromisoformat(day["date"])
        slot = offset + date.day - 1
        amount = day["commits"]
        colors = ["#25332e", "#405f4b", "#668563", "#94ad7d", "#d2dfaf"]
        level = 0 if not amount else min(4, 1 + int(amount / max(1, peak_day) * 3.99))
        cell = add(calendar, "rect", {"x": 24 + (slot % 7) * 8, "y": 692 + (slot // 7) * 8,
            "width": 6, "height": 6, "rx": 1, "fill": colors[level], "data-date": day["date"], "data-commits": amount})
        add(cell, "title", text=f'{day["date"]}: {amount} commits')


def render(data):
    months = OrderedDict()
    for day in data["days"]:
        key = day["date"][:7]
        month = months.setdefault(key, {"month": key, "days": [], "commits": 0})
        month["days"].append(day)
        month["commits"] += day["commits"]
    months = list(months.values())
    if len(months) != 13:
        raise ValueError("This composition expects 13 month bins; adjust period and spacing for another date span.")
    total = sum(m["commits"] for m in months)
    active = sum(d["commits"] > 0 for d in data["days"])
    peak = max(1, max(m["commits"] for m in months))
    peak_day = max(d["commits"] for d in data["days"])
    root = ET.Element(f"{{{NS}}}svg", {"width": "1200", "height": "620", "viewBox": "0 0 1200 620", "role": "img", "aria-labelledby": "title desc"})
    add(root, "title", {"id": "title"}, "Monthly commits — an ink mountain landscape")
    add(root, "desc", {"id": "desc"}, f"{total:,} fictional commits across {active} active days, from {data['start']} to {data['end']}. Main mountain height grows with squared monthly commits. Each date, count, and daily calendar travels with its mountain. Fainter cragged peaks use the same drawing at different depths. Brushwork trees, mist, reflections and river life are decorative. A fish jumps at a different spot every 7.5 seconds. The seamless scene repeats every 180 seconds. Reduced motion is supported.")
    defs = add(root, "defs")
    style = add(root, "style")
    for name, stops in [("mountain-wash", [(0, JADE, .78), (1, BG, .10)]),
                        ("base-mist", [(0, BG, 0), (1, BG, .45)]),
                        ("land-wash", [(0, "#203a32", 1), (1, "#1a2d27", 1)])]:
        gradient = add(defs, "linearGradient", {"id": name, "x1": 0, "x2": 0, "y1": 0, "y2": 1})
        for offset, color, opacity in stops:
            add(gradient, "stop", {"offset": offset, "stop-color": color, "stop-opacity": opacity})
    edge = add(defs, "linearGradient", {"id": "edge-fade"})
    for offset, color in [(0, "black"), (.055, "white"), (.945, "white"), (1, "black")]:
        add(edge, "stop", {"offset": offset, "stop-color": color})
    mask = add(defs, "mask", {"id": "scene-fade", "maskUnits": "userSpaceOnUse", "x": 35, "y": 240, "width": 1130, "height": 510})
    add(mask, "rect", {"x": 35, "y": 240, "width": 1130, "height": 510, "fill": "url(#edge-fade)"})
    clip = add(defs, "clipPath", {"id": "art-clip"})
    add(clip, "rect", {"x": 35, "y": 240, "width": 1130, "height": 380})
    period_clip = add(defs, "clipPath", {"id": "history-period"})
    add(period_clip, "rect", {"x": 0, "y": 240, "width": PERIOD, "height": 510})
    reflection_clip = add(defs, "clipPath", {"id": "reflection-bands"})
    for y, height in [(552, 1.4), (557, 2), (563, 2.6), (570, 2), (578, 1.2), (587, 1)]:
        add(reflection_clip, "rect", {"x": 0, "y": y, "width": PERIOD, "height": height})
    reflection_gradient = add(defs, "linearGradient", {"id": "reflection-fade", "x1": 0, "x2": 0, "y1": 0, "y2": 1})
    add(reflection_gradient, "stop", {"offset": 0, "stop-color": "white", "stop-opacity": ".9"})
    add(reflection_gradient, "stop", {"offset": 1, "stop-color": "white", "stop-opacity": 0})
    reflection_mask = add(defs, "mask", {"id": "reflection-mask", "maskUnits": "userSpaceOnUse", "x": 0, "y": 551, "width": PERIOD, "height": 45})
    add(reflection_mask, "rect", {"x": 0, "y": 551, "width": PERIOD, "height": 45, "fill": "url(#reflection-fade)"})
    decoration(defs)
    tile = add(defs, "g", {"id": "history-tile", "clip-path": "url(#history-period)"})
    reflections = add(tile, "g", {"clip-path": "url(#reflection-bands)", "mask": "url(#reflection-mask)", "opacity": ".28", "aria-hidden": "true"})
    connected_land(tile)
    heights = []
    for index, month in enumerate(months):
        height = mountain(defs, month, index, peak)
        heights.append({"month": month["month"], "commits": month["commits"], "height": height})
        cx = CENTER + index * SPACING
        for delta in [-PERIOD, 0, PERIOD]:
            # Wrapped copies preserve shoulders that cross the timeline seam.
            add(tile, "use", {"href": f"#mountain-{index}", "x": cx + delta})
            add(reflections, "use", {"href": f"#mountain-{index}", "transform": f"translate({cx + delta} 632.25) scale(1 -.15)"})
        month_labels(tile, month, index, peak_day)
    add(root, "rect", {"width": 1200, "height": 620, "rx": 8, "fill": BG})
    rng = random.Random(391)
    for _ in range(310):
        add(root, "circle", {"cx": f"{rng.uniform(0,1200):.1f}", "cy": f"{rng.uniform(0,620):.1f}", "r": f"{rng.uniform(.15,.55):.2f}", "fill": INK, "opacity": ".035"})
    for x, number, caption, offset in [(50, f"{total:,}", "COMMITS", 70), (260, active, "ACTIVE DAYS", 53), (480, peak, "PEAK MONTH", 53)]:
        label(root, x, 45, number, 25, font=SERIF)
        label(root, x + offset, 43, caption, 10, MUTED, **{"letter-spacing": 1.2})
    add(root, "rect", {"x": 1005, "y": 36, "width": 3, "height": 3, "fill": RED, "opacity": ".8"})
    label(root, 1150, 43, "SAMPLE ACTIVITY", 10, MUTED, anchor="end", **{"letter-spacing": 1.3})
    composition = add(root, "g", {"transform": "translate(0 -165)"})
    scene = add(composition, "g", {"mask": "url(#scene-fade)"})
    background = add(scene, "g", {"clip-path": "url(#art-clip)"})
    weather = add(background, "g")
    for name, period in [("far", FAR_PERIOD), ("mid", MID_PERIOD)]:
        lane = add(background, "g", {"class": f"{name}-track"})
        for offset in [-period, 0, period, 2 * period]:
            add(lane, "use", {"href": f"#{name}-tile", "x": offset})
    history = add(scene, "g", {"class": "history-track"})
    for offset in [0, PERIOD, 2 * PERIOD]:
        add(history, "use", {"href": "#history-tile", "x": offset})
    foreground = add(scene, "g", {"clip-path": "url(#art-clip)"})
    add(foreground, "rect", {"x": 35, "y": 512, "width": 1130, "height": 24, "fill": "url(#base-mist)"})
    shore = add(foreground, "g", {"class": "shore-track"})
    for offset in [-SHORE_PERIOD, 0, SHORE_PERIOD, 2 * SHORE_PERIOD]:
        add(shore, "use", {"href": "#shore-tile", "x": offset})
    water = add(foreground, "g")
    ambient_css = build_ambient(defs, weather, water)
    add(root, "line", {"x1": 50, "x2": 1150, "y1": 590, "y2": 590, "stroke": FINE, "opacity": ".24"})
    label(root, 50, 609, "Monthly commits · taller peaks, busier months", 10, MUTED)
    label(root, 1150, 609, "26 OCT 2025 — 24 OCT 2026", 10, MUTED, anchor="end", **{"letter-spacing": ".8"})
    style.text = (CSS.replace("$START", str(-START)).replace("$END", str(-START - PERIOD))
                 .replace("$FAR", str(-FAR_PERIOD)).replace("$MID", str(-MID_PERIOD))
                 .replace("$SHORE", str(-SHORE_PERIOD))) + ambient_css
    return root, heights


CSS = """
.history-track { transform:translateX($STARTpx); animation:history-drift 180s linear infinite; }
.far-track { animation:far-drift 180s linear infinite; }
.mid-track { animation:mid-drift 180s linear infinite; }
.shore-track { animation:shore-drift 180s linear infinite; }
.tree-sway { animation:tree-breathe 12s ease-in-out infinite; transform-origin:0 0; }
@keyframes history-drift { from {transform:translateX($STARTpx)} to {transform:translateX($ENDpx)} }
@keyframes far-drift { from {transform:translateX(0px)} to {transform:translateX($FARpx)} }
@keyframes mid-drift { from {transform:translateX(0px)} to {transform:translateX($MIDpx)} }
@keyframes shore-drift { from {transform:translateX(0px)} to {transform:translateX($SHOREpx)} }
@keyframes tree-breathe { 0%,100% {transform:rotate(-.7deg)} 50% {transform:rotate(.8deg)} }
@media(prefers-reduced-motion:reduce) {
  .history-track,.far-track,.mid-track,.shore-track,.tree-sway {animation:none !important}
}
"""


def main():
    data = json.loads((ROOT / "data/activity.json").read_text())
    root, heights = render(data)
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    ET.ElementTree(root).write(assets / "nocturne.svg", encoding="utf-8", xml_declaration=True)
    still = copy.deepcopy(root)
    still.find(f"{{{NS}}}style").text += "\n* {animation:none !important}\n.ambient-fish,.ambient-splash,.ambient-droplets {opacity:0 !important}\n"
    ET.ElementTree(still).write(assets / "nocturne-still.svg", encoding="utf-8", xml_declaration=True)
    print(json.dumps({"assets": ["nocturne.svg", "nocturne-still.svg"], "months": heights}, indent=2))


if __name__ == "__main__":
    main()
