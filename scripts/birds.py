"""Sparse ink birds at two depths, drawn and animated entirely inside SVG.

The caller places the supplied groups before and after its main mountains.
Local scenery coordinates are preserved; every animation repeats at 180s.
"""
import xml.etree.ElementTree as ET

import palette

NS = "http://www.w3.org/2000/svg"


def _add(parent, tag, attrs=None):
    return ET.SubElement(parent, f"{{{NS}}}{tag}",
                         {name: str(value) for name, value in (attrs or {}).items()})


def _bird(parent, name, depth, y, scale, opacity, duration, delay, flap, wing_phase):
    # Place flight in a separate group from height, lift, bank, and wings.
    # Neither a wing beat nor a bank can overwrite the bird's world motion.
    initial_x = -100 + 1400 * (delay / duration)
    anchor = _add(parent, "g", {
        "id": name, "data-bird-depth": depth,
        "data-flight-duration": duration, "data-flap-duration": flap,
        "data-flight-delay": -delay, "data-flight-y": y,
        "transform": f"translate(0 {y})", "opacity": opacity,
        "aria-hidden": "true",
    })
    flight = _add(anchor, "g", {
        "class": "sky-bird-motion sky-bird-flight",
        "transform": f"translate({initial_x:.3f} 0)",
        "style": f"animation-duration:{duration}s;animation-delay:-{delay}s",
    })
    lift = _add(flight, "g", {
        "class": f"sky-bird-motion sky-bird-lift-{depth}",
        "style": f"animation-delay:-{wing_phase}s",
    })
    bank = _add(lift, "g", {
        "class": "sky-bird-motion sky-bird-bank",
        "style": f"animation-duration:{10 if depth == 'far' else 6}s;animation-delay:-{wing_phase}s",
    })
    body = _add(bank, "g", {"transform": f"scale({scale})", "fill": palette.INK})
    # Unequal curved wings make a small ink silhouette, not a regular M mark.
    # Each wing articulates at its root; the far wing is slightly foreshortened.
    for side, shape, phase in [
        ("left", "M.2 .15 C-2.2 -2.1 -5.1 -5.7 -10.5 -6.4 "
                 "C-7.1 -4.6 -4.9 -1.2 -1.4 .8 Z", wing_phase),
        ("right", "M-.2 .15 C1.5 -2.4 4.7 -5.2 8.4 -5.5 "
                  "C5.4 -3.9 3.8 -1.2 .7 .8 Z", wing_phase + flap * .07),
    ]:
        wing = _add(body, "g", {
            "class": f"sky-bird-motion sky-bird-wing sky-bird-wing-{side}",
            "data-bird-wing": side,
            "style": f"animation-duration:{flap}s;animation-delay:-{phase:g}s",
        })
        _add(wing, "path", {"d": shape})
    _add(body, "path", {
        "d": "M-2.9 1.1 L-4.2 2.6 L-.8 1.6 C.8 1.45 1.9 .2 2.4 -.35 "
             "L4 -.65 L2.8 -1.15 C2.1 -2 1.25 -1.7 .65 -.7 "
             "C-.45 -.1 -1.45 .35 -2.9 1.1 Z",
    })


def build_birds(defs, behind_group, front_group):
    """Draw two distant birds behind peaks and one nearer crossing in front.

    ``defs`` is accepted alongside the ambient drawing API; each bird retains
    its own wing groups so animation works inside a native SVG image as well
    as a standalone document. No external resources or scripts are emitted.
    """
    _bird(behind_group, "sky-bird-far-0", "far", 365, .58, .42, 180, 42, 1.8, .35)
    _bird(behind_group, "sky-bird-far-1", "far", 338, .51, .36, 180, 108, 1.8, 1.17)
    _bird(front_group, "sky-bird-near-0", "near", 396, .94, .72, 90, 51, 1.5, .62)
    return CSS


CSS = """
.sky-bird-flight { animation:sky-bird-crossing 180s linear infinite; }
@keyframes sky-bird-crossing {
  from { transform:translateX(-100px); }
  to { transform:translateX(1300px); }
}
.sky-bird-lift-far { animation:sky-bird-far-lift 9s ease-in-out infinite; }
.sky-bird-lift-near { animation:sky-bird-near-lift 6s ease-in-out infinite; }
@keyframes sky-bird-far-lift {
  0%,100% { transform:translateY(0px); }
  50% { transform:translateY(-4px); }
}
@keyframes sky-bird-near-lift {
  0%,100% { transform:translateY(0px); }
  50% { transform:translateY(-8px); }
}
.sky-bird-bank { transform-origin:0 0; animation:sky-bird-bank 6s ease-in-out infinite; }
@keyframes sky-bird-bank {
  0%,100% { transform:rotate(-3deg); }
  50% { transform:rotate(4deg); }
}
.sky-bird-wing { transform-origin:0 0; transform:scaleY(.35); }
.sky-bird-wing-left { animation:sky-bird-left-wing 1.8s ease-in-out infinite; }
.sky-bird-wing-right { animation:sky-bird-right-wing 1.8s ease-in-out infinite; }
@keyframes sky-bird-left-wing {
  0%,100% { transform:rotate(-4deg) scaleY(.95); }
  29% { transform:rotate(6deg) scaleY(-.52); }
  58%,83% { transform:rotate(0deg) scaleY(.28); }
}
@keyframes sky-bird-right-wing {
  0%,100% { transform:rotate(3deg) scaleY(.88); }
  29% { transform:rotate(-5deg) scaleY(-.42); }
  58%,83% { transform:rotate(0deg) scaleY(.32); }
}
@media(prefers-reduced-motion:reduce) {
  .sky-bird-motion { animation:none !important; }
}
"""
