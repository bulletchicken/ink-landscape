#!/usr/bin/env python3
"""Create seamless native SVG ink scrolls from the static commit landscapes.

Python standard library only. Run generate_landscape.py first if necessary.
Animation is CSS inside the SVG; no scripts, embedded raster images, or network.
Original mountain geometry and attribution remain in THIRD_PARTY_NOTICES.md.
"""
from pathlib import Path
from copy import deepcopy
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
PERIOD = 988
DURATION = 45


def element(tag, attributes=None, text=None):
    node = ET.Element(f'{{{NS}}}{tag}', attributes or {})
    if text is not None:
        node.text = text
    return node


def append(parent, tag, attributes=None, text=None):
    child = element(tag, attributes, text)
    parent.append(child)
    return child


def make_style():
    return element('style', text=f'''
    .ink-scroll {{ animation: ink-panorama {DURATION}s linear infinite; }}
    @keyframes ink-panorama {{
      from {{ transform: translateX(0px); }}
      to {{ transform: translateX(-{PERIOD}px); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .ink-scroll {{ animation: none; }}
    }}
    ''')


def make_scroll(tile):
    outer = element('g', {'transform': 'translate(100 0)'})
    strip = append(outer, 'g', {'class': 'ink-scroll'})
    for offset in [-PERIOD, 0, PERIOD, PERIOD * 2]:
        append(strip, 'use', {'href': f'#{tile}', 'x': str(offset)})
    return outer


def desktop(theme):
    source = ASSETS / ('commit-landscape.svg' if theme == 'dark' else 'commit-landscape-light.svg')
    root = ET.fromstring(source.read_text())
    defs = next(node for node in root if node.tag.endswith('}defs'))
    art = next(node for node in root if node.attrib.get('clip-path') == 'url(#art)')
    mountains = [node for node in art if 'data-week' in node.attrib]
    pines = [node for node in art if 'data-active-day-tree' in node.attrib]
    assert len(mountains) == 52 and len(pines) == 269

    # Seamless periodic tiles include shoulders extending across either edge.
    # Each mountain's three copies share a depth position in the paint order,
    # ensuring the overlap order is identical on both sides of the join.
    clip = append(defs, 'clipPath', {'id': 'cyclic-tile-clip'})
    append(clip, 'rect', {'x': '0', 'y': '240', 'width': str(PERIOD), 'height': '282'})
    mountain_tile = append(defs, 'g', {'id': 'cyclic-mountains', 'clip-path': 'url(#cyclic-tile-clip)'})
    for mountain in mountains:
        mountain_id = f'weekly-mountain-{mountain.attrib["data-week"]}'
        original = deepcopy(mountain)
        original.set('id', mountain_id)
        defs.append(original)
        for offset in [-PERIOD, 0, PERIOD]:
            append(mountain_tile, 'use', {'href': f'#{mountain_id}', 'x': str(offset - 100)})
    pine_original = append(defs, 'g', {'id': 'weekly-pines'})
    for pine in pines:
        pine_original.append(deepcopy(pine))
    pine_tile = append(defs, 'g', {'id': 'cyclic-pines', 'clip-path': 'url(#cyclic-tile-clip)'})
    for offset in [-PERIOD, 0, PERIOD]:
        append(pine_tile, 'use', {'href': '#weekly-pines', 'x': str(offset - 100)})

    # Both scene edges fade smoothly into the paper. The fading mask stays
    # fixed while the terrain moves behind it, avoiding fade-in/out flashes.
    fade = append(defs, 'linearGradient', {'id': 'scroll-edge-fade', 'gradientUnits': 'userSpaceOnUse',
                                          'x1': '35', 'y1': '0', 'x2': '1165', 'y2': '0'})
    for offset, value in [('0', '0'), ('.035', '.12'), ('.085', '.6'), ('.15', '1'),
                          ('.85', '1'), ('.915', '.6'), ('.965', '.12'), ('1', '0')]:
        append(fade, 'stop', {'offset': offset, 'stop-color': 'white', 'stop-opacity': value})
    mask = append(defs, 'mask', {'id': 'scroll-mist-mask', 'maskUnits': 'userSpaceOnUse',
                                'x': '35', 'y': '240', 'width': '1130', 'height': '282',
                                'style': 'mask-type:alpha'})
    append(mask, 'rect', {'x': '35', 'y': '240', 'width': '1130', 'height': '282',
                          'fill': 'url(#scroll-edge-fade)'})
    art.set('mask', 'url(#scroll-mist-mask)')

    mountain_index = list(art).index(mountains[0])
    for mountain in mountains:
        art.remove(mountain)
    art.insert(mountain_index, make_scroll('cyclic-mountains'))
    pine_index = list(art).index(pines[0])
    for pine in pines:
        art.remove(pine)
    art.insert(pine_index, make_scroll('cyclic-pines'))

    # Make the far ridge dissolve vertically as well, rather than ending in a
    # straight horizontal cut below the trees. This is purely decorative.
    for node in art:
        if node.tag.endswith('}polygon') and any('Decorative distant ridge' in (child.text or '') for child in node):
            points = node.attrib['points'].split()
            points[-2:] = ['1170,522', '35,522']
            node.set('points', ' '.join(points))
            node.set('fill', 'url(#wash)')
    for node in root:
        if node.tag.endswith('}text') and node.text == '52 weekly peaks. 364 daily marks.':
            node.text = '52 weeks · returning through the mist'
        if node.tag.endswith('}desc'):
            node.text = ((node.text or '') + ' The foreground scrolls through the same year in a seamless 45-second loop. '
                         'The calendar stays fixed as a year overview. Motion is disabled when reduced motion is preferred.')
    root.insert(2, make_style())
    return root


def mobile(theme, full):
    source = ASSETS / ('commit-landscape-mobile.svg' if theme == 'dark' else 'commit-landscape-mobile-light.svg')
    root = ET.fromstring(source.read_text())
    full_defs = next(node for node in full if node.tag.endswith('}defs'))
    full_art = next(node for node in full if node.attrib.get('clip-path') == 'url(#art)')
    for node in list(root):
        if node.tag.endswith('}defs'):
            idx = list(root).index(node)
            root.remove(node)
            root.insert(idx, deepcopy(full_defs))
    for parent in root.iter():
        for node in list(parent):
            if node.attrib.get('clip-path') == 'url(#art)':
                idx = list(parent).index(node)
                parent.remove(node)
                parent.insert(idx, deepcopy(full_art))
    root.insert(2, make_style())
    for node in root:
        if node.tag.endswith('}desc'):
            node.text = ((node.text or '') + ' The same year repeats seamlessly while the calendar remains fixed. '
                         'Reduced-motion preference disables the scroll.')
    return root


if __name__ == '__main__':
    for theme in ['dark', 'light']:
        full = desktop(theme)
        for is_mobile, root in [(False, full), (True, mobile(theme, full))]:
            suffix = ('-mobile' if is_mobile else '') + ('-light' if theme == 'light' else '')
            target = ASSETS / f'commit-landscape-loop{suffix}.svg'
            target.write_bytes(ET.tostring(root, encoding='utf-8'))
            assert len([n for n in root.iter() if 'data-week' in n.attrib]) == 52
            assert len([n for n in root.iter() if 'data-active-day-tree' in n.attrib]) == 269
            assert len([n for n in root.iter() if 'data-commit-day' in n.attrib]) == 364
            assert not any(n.tag.endswith('}script') or n.tag.endswith('}image') or n.tag.endswith('}foreignObject') for n in root.iter())
            print(f'{target.name}: {target.stat().st_size:,} bytes;52 weeks,269 pines,364 days;45s native CSS loop')
