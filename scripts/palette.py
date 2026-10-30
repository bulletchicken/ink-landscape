"""Three ink palettes shared by the mountain, plant, and river renderers.

Renderers access this module's colors at drawing time so several themes can
be generated in one process without carrying colors over from a previous run.
"""

THEMES = {
    "white": {
        "PAGE_BG": "#ffffff", "BG": "#ffffff", "INK": "#111111",
        "MUTED": "#666666", "FINE": "#777777", "WASH": "#e4e4e4",
        "MOUNTAIN": "#f2f2f2", "LAND_BOTTOM": "#f7f7f7", "STONE": "#e7e7e7",
        "TREE": "#303030", "ACCENT": "#4a4a4a", "FISH": "#222222",
        "WATER": "#707070", "CLOUD": "#bababa",
        "GRID": ("#ededed", "#cfcfcf", "#969696", "#5b5b5b", "#1f1f1f"),
        "OUTLINE_OPACITY": .82,
    },
    "green": {
        "PAGE_BG": "#101919", "BG": "#101919", "INK": "#dbe4ce",
        "MUTED": "#a5b6a9", "FINE": "#536f63", "WASH": "#315649",
        "MOUNTAIN": "#203a32", "LAND_BOTTOM": "#1a2d27", "STONE": "#1d302a",
        "TREE": "#a6b8a0", "ACCENT": "#e78772", "FISH": "#b8cbb7",
        "WATER": "#89a795", "CLOUD": "#6f8e7d",
        "GRID": ("#25332e", "#405f4b", "#668563", "#94ad7d", "#d2dfaf"),
        "OUTLINE_OPACITY": .43,
    },
    "black": {
        "PAGE_BG": "#0e1116", "BG": "#171717", "INK": "#e3e3e3",
        "MUTED": "#acacac", "FINE": "#626262", "WASH": "#494949",
        "MOUNTAIN": "#303030", "LAND_BOTTOM": "#262626", "STONE": "#292929",
        "TREE": "#b2b2b2", "ACCENT": "#c9c9c9", "FISH": "#c4c4c4",
        "WATER": "#9c9c9c", "CLOUD": "#808080",
        "GRID": ("#2e2e2e", "#505050", "#777777", "#a2a2a2", "#d6d6d6"),
        "OUTLINE_OPACITY": .43,
    },
}


def configure(theme):
    """Select a named palette for the next sequential render."""
    if theme not in THEMES:
        raise ValueError(f"Unknown theme {theme!r}; choose {', '.join(THEMES)}.")
    globals().update(THEMES[theme])


configure("white")
