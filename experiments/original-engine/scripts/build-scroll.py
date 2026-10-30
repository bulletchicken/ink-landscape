#!/usr/bin/env python3
"""Frame the original Lingdong-generated scene as a native, looping SVG."""
from pathlib import Path
import copy
import json
import datetime as dt
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
PAPER = '#f1eadb'
INK = '#33372f'
MUTED = '#6b7063'
DURATION = 180

def el(tag, attrs=None, text=None):
    node = ET.Element(f'{{{NS}}}{tag}', {k:str(v) for k,v in (attrs or {}).items()})
    node.text = text
    return node

def add(parent, tag, attrs=None, text=None):
    node=el(tag,attrs,text);parent.append(node);return node

def label(parent,x,y,text,size=18,color=INK,serif=False,anchor='start',spacing=0):
    return add(parent,'text',{'x':x,'y':y,'fill':color,'font-family':'Georgia, Times New Roman, serif' if serif else 'Arial, Helvetica, sans-serif','font-size':size,'text-anchor':anchor,'letter-spacing':spacing},str(text))

def build(still=False):
    scene=ET.parse(ROOT/'assets/scene.svg').getroot()
    period=float(scene.get('width','5200').replace('px',''))
    source_height=float(scene.get('height','620').replace('px',''))
    activity=json.loads((ROOT/'data/activity.json').read_text())
    manifest=json.loads((ROOT/'data/scene-manifest.json').read_text())
    mountain_x={month['key']:month['mountain']['x'] for month in manifest['months']}
    months={}
    for day in activity['days']:
        key=day['date'][:7]
        entry=months.setdefault(key,{'commits':0,'active':0,'start':day['date']})
        entry['end']=day['date']
        entry['commits']+=day['commits'];entry['active']+=day['commits']>0
    total=sum(v['commits'] for v in months.values())
    active=sum(v['active'] for v in months.values())
    width=1200;height=940;scene_y=176;scroll_height=736
    root=el('svg',{'width':width,'height':height,'viewBox':f'0 0 {width} {height}','role':'img','aria-labelledby':'v2-title v2-desc'})
    add(root,'title',{'id':'v2-title'},'A year along the river — original Shan Shui renderer, sample commits')
    add(root,'desc',{'id':'v2-desc'},f'{total:,} fictional commits across {active} active days, grouped into {len(months)} calendar months. Lingdong Huang’s original drawing functions generate these ink mountains, trees, pavilions, boats and people. Monthly commits set mountain scale; active days set texture and grove density. A ferry marks each active month. Each mountain’s month, represented date range, and commit total travel directly beneath it in the same scroll. The complete panorama repeats every {DURATION} seconds. Reduced-motion preference stops the scroll.')
    defs=add(root,'defs')
    for n in scene:
        if n.tag.endswith('}defs'):
            for child in n: defs.append(copy.deepcopy(child))
    # Render one full original scene with all opaque white occlusion intact.
    # Multiplication is applied after the scene is composed, as in the original.
    tile=add(defs,'g',{'id':'original-scene'})
    feature_root=next(n for n in scene if n.get('id')=='lingdong-scene')
    # Wrap each feature before clipping the tile, preserving paint order at
    # the join. Original shapes crossing a boundary continue on the other side.
    for i,n in enumerate(feature_root):
        original=copy.deepcopy(n)
        original.set('id',f'original-feature-{i}')
        defs.append(original)
        for offset in [-period,0,period]:
            add(tile,'use',{'href':f'#original-feature-{i}','x':offset})
    clip=add(defs,'clipPath',{'id':'scroll-window'})
    add(clip,'rect',{'x':0,'y':0,'width':width,'height':scroll_height})
    tileclip=add(defs,'clipPath',{'id':'tile-boundary'})
    add(tileclip,'rect',{'x':0,'y':0,'width':period,'height':source_height})
    tile.set('clip-path','url(#tile-boundary)')
    fade=add(defs,'linearGradient',{'id':'river-mist','x1':0,'x2':width,'y1':0,'y2':0,'gradientUnits':'userSpaceOnUse'})
    for offset,opacity in [(0,0),(.025,.15),(.06,.65),(.10,1),(.90,1),(.94,.65),(.975,.15),(1,0)]:
        add(fade,'stop',{'offset':offset,'stop-color':'white','stop-opacity':opacity})
    mask=add(defs,'mask',{'id':'soft-edges','x':0,'y':0,'width':width,'height':scroll_height,'maskUnits':'userSpaceOnUse','style':'mask-type:alpha'})
    add(mask,'rect',{'width':width,'height':scroll_height,'fill':'url(#river-mist)'})
    # Dates use the mountain's recorded world-space center, not a separate
    # evenly spaced summary. Both live inside one animated transform, so they
    # stay attached through every frame and across the repeated panorama seam.
    dates=add(defs,'g',{'id':'mountain-dates'})
    for key,value in months.items():
        x=mountain_x[key]
        start=dt.date.fromisoformat(value['start']);end=dt.date.fromisoformat(value['end'])
        group=add(dates,'g',{'data-month-label':key,'data-mountain-x':x,'transform':f'translate({x} 0)'})
        add(group,'title',text=f"{start.strftime('%B %Y')}: {value['start']} to {value['end']}, {value['commits']} sample commits")
        add(group,'line',{'x1':0,'x2':0,'y1':634,'y2':650,'stroke':'#9c9582','stroke-width':1})
        label(group,0,678,start.strftime('%B %Y'),25,INK,True,'middle')
        label(group,0,701,f'{start.day}–{end.day} {start.strftime("%b")}',15,MUTED,anchor='middle')
        label(group,0,727,f"{value['commits']:,} commits",19,INK,anchor='middle')
    grain=add(defs,'filter',{'id':'paper-grain','x':0,'y':0,'width':'100%','height':'100%'})
    add(grain,'feTurbulence',{'type':'fractalNoise','baseFrequency':'.65','numOctaves':3,'seed':9,'stitchTiles':'stitch'})
    add(grain,'feColorMatrix',{'type':'saturate','values':0})
    if not still:
        add(root,'style',text=f'.river-scroll{{animation:river-passage {DURATION}s linear infinite}}@keyframes river-passage{{from{{transform:translateX(0px)}}to{{transform:translateX(-{period:g}px)}}}}@media(prefers-reduced-motion:reduce){{.river-scroll{{animation:none}}}}')
    add(root,'rect',{'width':width,'height':height,'rx':6,'fill':PAPER})
    add(root,'rect',{'width':width,'height':height,'rx':6,'filter':'url(#paper-grain)','opacity':'.045','style':'mix-blend-mode:multiply'})
    label(root,44,40,'JEREMY SU   /   INK SCROLL II',15,MUTED,spacing=2)
    label(root,44,102,'A year along the river.',49,serif=True)
    label(root,46,139,f'{total:,} commits   ·   {active} active days   ·   {len(months)} monthly chapters',18,MUTED)
    add(root,'rect',{'x':1087,'y':33,'width':67,'height':73,'rx':2,'fill':'none','stroke':'#a7553e','stroke-width':1.8})
    label(root,1120,65,'山',25,'#a7553e',True,'middle')
    label(root,1120,94,'水',25,'#a7553e',True,'middle')
    label(root,1154,137,'SAMPLE HISTORY',13,'#a7553e',anchor='end',spacing=1)
    positioned=add(root,'g',{'transform':f'translate(0 {scene_y})'})
    window=add(positioned,'g',{'clip-path':'url(#scroll-window)','mask':'url(#soft-edges)','style':'mix-blend-mode:multiply'})
    strip=add(window,'g',{'class':'river-scroll'})
    for x in [-period,0,period]:
        add(strip,'use',{'href':'#original-scene','x':x})
        add(strip,'use',{'href':'#mountain-dates','x':x})
    # A quiet fixed separator frames the moving dates without a second clock.
    line_y=810
    add(root,'line',{'x1':44,'x2':1156,'y1':line_y,'y2':line_y,'stroke':'#b5ad9a','stroke-opacity':'.5'})
    label(root,44,924,'Mountain height scales with commits² · 150 commits = 2.25× the height of 100 · Sample history',14,MUTED)
    return root

if __name__=='__main__':
    for still,name in [(False,'lingdong-commit-scroll.svg'),(True,'lingdong-commit-scroll-still.svg')]:
        target=ROOT/'assets'/name
        target.write_bytes(ET.tostring(build(still),encoding='utf-8'))
        print(f'{name}: {target.stat().st_size:,} bytes')
