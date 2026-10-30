#!/usr/bin/env python3
"""Render deterministic sample commit history as a Shan Shui landscape.
Mountain cosine/noise contours and tapered ink strokes adapted from
Lingdong Huang's shan-shui-inf (2018), MIT. See THIRD_PARTY_NOTICES.md.
No network access, dependencies, secrets, or account data needed.
"""
from pathlib import Path
import datetime as dt
import json, math, random
from html import escape

ROOT = Path(__file__).resolve().parents[1]
W, H = 1200, 740
START = dt.date(2025, 10, 26)

def fixture():
    rng = random.Random(2318)
    daily = []
    # Deliberate ebbs and sprints; all values are fictional.
    for i in range(364):
        week = i // 7
        envelope = 3.3 + 2.7 * math.sin(week * .22 - .9) ** 2 + 3.0 * math.sin(week * .63 + .3) ** 4
        weekend = .45 if i % 7 in (0, 6) else 1
        count = 0 if rng.random() < .21 else round(max(0, rng.gauss(envelope, 2.5)) * weekend)
        if 17 <= week <= 19: count = round(count * .35)
        if 37 <= week <= 40: count = round(count * 1.9)
        daily.append({'date':str(START + dt.timedelta(days=i)), 'commits':count})
    return {'sample':True, 'description':'Fictional commit activity for a design mockup; not Jeremy Su\'s real activity.', 'start':str(START), 'end':daily[-1]['date'], 'days':daily}

def summarize(data):
    days = data['days']
    weeks=[]
    for i in range(0, len(days), 7):
        group=days[i:i+7]
        weeks.append({'start':group[0]['date'], 'end':group[-1]['date'], 'commits':sum(d['commits'] for d in group), 'active_days':sum(d['commits']>0 for d in group)})
    peak=max(weeks,key=lambda x:x['commits'])
    longest=streak=0
    for d in days:
        streak = streak+1 if d['commits'] else 0
        longest=max(longest,streak)
    data['weeks']=weeks
    data['summary']={'commits':sum(d['commits'] for d in days),'active_days':sum(d['commits']>0 for d in days),'weeks':len(weeks),'peak_week_commits':peak['commits'],'peak_week_start':peak['start'],'peak_week_end':peak['end'],'longest_streak_days':longest}
    return data

def noise(x, seed):
    # Smooth deterministic multiscale noise substitutes the original Perlin field.
    return .50 + .24*math.sin(x*1.71+seed*2.37)+.14*math.sin(x*4.27-seed*.83)+.08*math.sin(x*9.31+seed*1.17)

def pointsstr(points):
    return ' '.join(f'{x:.1f},{y:.1f}' for x,y in points)

def brush(points, color, width=1, opacity=1):
    # The original stroke algorithm offsets a polyline on both sides, tapers its
    # width sinusoidally, then closes the outline to create an organic ink mark.
    if len(points)<3: return ''
    left=[];right=[]
    for i,(x,y) in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
        angle=math.atan2(b[1]-a[1],b[0]-a[0])+math.pi/2
        w=width*math.sin(math.pi*i/(len(points)-1))*(.65+.35*noise(i*.5, width))
        left.append((x+math.cos(angle)*w,y+math.sin(angle)*w))
        right.append((x-math.cos(angle)*w,y-math.sin(angle)*w))
    return f'<polygon points="{pointsstr(left+right[::-1])}" fill="{color}" opacity="{opacity:.3f}"/>'

PALETTES={
'dark':dict(bg='#101919',ink='#dbe4ce',muted='#a5b6a9',fine='#536f63',mountain='#25473d',mountain2='#315649',tree='#a6b8a0',water='#89a795',red='#e78772',zero='#25332e',grid=['#405f4b','#668563','#94ad7d','#d2dfaf']),
'light':dict(bg='#f2f0e6',ink='#263d35',muted='#587265',fine='#bec7b8',mountain='#c2cdb9',mountain2='#a2b49f',tree='#375d48',water='#648b73',red='#ad513e',zero='#e0e4d7',grid=['#bacba6','#8fae80','#5f895d','#365d43'])}

def render(data, mode):
    c=PALETTES[mode];rng=random.Random(391)
    out=[]
    def add(s):out.append(s)
    def text(x,y,s,size=18,color=None,font='mono',anchor='start',weight='400',spacing=None):
        ff='Georgia, Times New Roman, serif' if font=='serif' else 'ui-monospace, SFMono-Regular, Consolas, monospace' if font=='mono' else 'Arial, sans-serif'
        add(f'<text x="{x}" y="{y}" fill="{color or c["ink"]}" font-family="{ff}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"'+(f' letter-spacing="{spacing}"' if spacing else '')+f'>{escape(str(s))}</text>')
    s=data['summary'];weeks=data['weeks'];peak=s['peak_week_commits']
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">')
    add('<title id="title">A year, written in mountains — sample commit landscape</title>')
    add(f'<desc id="desc">Illustrative 52-week history from {data["start"]} to {data["end"]}. {s["commits"]} sample commits across {s["active_days"]} active days. Weekly summit height is proportional to commits, each pine represents one active day, and the seven-row grid shows daily commits. All activity is fictional.</desc>')
    add(f'<defs><linearGradient id="mist" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{c["bg"]}" stop-opacity=".95"/></linearGradient><linearGradient id="wash" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["mountain2"]}" stop-opacity=".8"/><stop offset="1" stop-color="{c["bg"]}" stop-opacity=".25"/></linearGradient><clipPath id="art"><rect x="35" y="240" width="1130" height="282"/></clipPath></defs>')
    add(f'<rect width="1200" height="740" rx="8" fill="{c["bg"]}"/>')
    # Grain is vector-native, keeping the image portable and crisp.
    for i in range(350):
        x=rng.uniform(0,1200);y=rng.uniform(0,740)
        add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.15,.55):.2f}" fill="{c["ink"]}" opacity=".045"/>')
    text(48,45,'COMMIT LANDSCAPE  /  FIELD NOTES',17,c['muted'],spacing='2')
    text(48,103,'A year, written in mountains.',49,font='serif')
    text(50,138,'Every commit leaves a trace.',19,c['muted'],font='sans')
    add(f'<rect x="1078" y="45" width="72" height="72" rx="3" fill="none" stroke="{c["red"]}" stroke-width="2.3"/>')
    text(1114,76,'山',27,c['red'],font='serif',anchor='middle')
    text(1114,104,'水',27,c['red'],font='serif',anchor='middle')
    text(1150,140,'SAMPLE DATA',16,c['red'],anchor='end',spacing='1.2')
    for x,number,label in [(50,f'{s["commits"]:,}','COMMITS'),(300,str(s['active_days']),'ACTIVE DAYS'),(550,str(s['peak_week_commits']),'PEAK WEEK')]:
        text(x,203,number,35,font='serif')
        text(x,228,label,16,c['muted'],spacing='1.8')
    text(1150,201,'OCT 26, 2025 — OCT 24, 2026',16,c['muted'],anchor='end')
    text(1150,226,'52 WEEKS · 364 DAYS',16,c['muted'],anchor='end',spacing='1.5')
    add('<g clip-path="url(#art)">')
    # A faint circular wash gives the ink composition a luminous focal point.
    add(f'<circle cx="908" cy="324" r="56" fill="{c["ink"]}" opacity=".025"/>')
    add(f'<circle cx="908" cy="324" r="55" fill="none" stroke="{c["ink"]}" stroke-width=".7" opacity=".18"/>')
    # Distant decorative wash: subdued, broad forms behind the measured peaks.
    distant=[]
    for k in range(161):
        x=35+k*7.1
        rise=(35+68*math.sin(k*.029+.3)**4+32*math.sin(k*.087)**2)
        distant.append((x,478-rise*(.8+.2*noise(k*.23,8))))
    add(f'<polygon points="{pointsstr(distant+[(1170,505),(35,505)])}" fill="{c["mountain2"]}" opacity=".22"><title>Decorative distant ridge</title></polygon>')
    add(brush(distant,c['fine'],1,.18))
    centers=[110+i*19 for i in range(52)]
    baseline=492
    # Generate each peak in its own chronological column. Broad lower shoulders
    # overlap, but visible summit height remains tied to that week's commit total.
    # The cosine/noise mountain cross-sections follow the original mountain().
    silhouettes=[]
    for i,wk in enumerate(weeks):
        cx=centers[i];height=20+205*wk['commits']/peak
        half=38+height*.22
        pts=[]
        for k in range(31):
            u=-1+2*k/30
            shape=max(0,math.cos(u*math.pi/2))**.95
            # All positive samples remain below the central peak, preserving its
            # exact data height while adding subordinate rocky contours.
            rough=1-(.22+.35*abs(u))*(1-noise(k*.65,i+.1))*abs(u)**.45
            pts.append((cx+u*half,baseline-height*shape*rough))
        silhouettes.append((pts,cx,height,half,wk,i))
    # Render tall peaks behind shorter ones to retain their summits.
    for pts,cx,height,half,wk,i in sorted(silhouettes,key=lambda z:-z[2]):
        add(f'<g data-week="{i}" data-commits="{wk["commits"]}"><title>Week of {wk["start"]}: {wk["commits"]} commits; {wk["active_days"]} active days</title>')
        add(f'<polygon points="{pointsstr(pts+[(cx+half,baseline),(cx-half,baseline)])}" fill="{c["mountain"]}"/>')
        add(f'<polygon points="{pointsstr(pts+[(cx+half,baseline),(cx-half,baseline)])}" fill="url(#wash)"/>')
        add(brush(pts,c['ink'],.9,.39))
        # Vertical brush texture follows shrinking/noisy mountain cross-sections.
        for j in range(12):
            frac=(j+.5)/12
            xx=cx-half*.75+frac*half*1.5
            u=(xx-cx)/half
            top=pts[min(30,max(0,round((u+1)*15)))][1]
            trace=[]
            for k in range(8):
                t=k/7
                trace.append((xx+(noise(t*9+i*.7,j)-.5)*3.8+(xx-cx)*t*.12,top+4+(baseline-top-6)*t))
            add(brush(trace,c['ink'],rng.uniform(.4,.85),rng.uniform(.16,.38)))
        # Broken ink hatching builds irregular rocky faces without a uniform mesh.
        for j in range(18):
            u=rng.uniform(-.72,.72);xx=cx+u*half
            rim=pts[min(30,max(0,round((u+1)*15)))][1]
            yy=rim+rng.uniform(.12,.72)*(baseline-rim)
            length=rng.uniform(.06,.18)*height
            trace=[(xx+math.sin(k*.9+j)*1.6+u*k*.3,yy+k*length/5) for k in range(6)]
            add(brush(trace,c['ink'],rng.uniform(.45,1.0),rng.uniform(.10,.33)))
        # One broad side wash makes the peak read as folded rock.
        summit=pts[15]
        fold=[summit,(cx+half*.13,baseline-height*.65),(cx-half*.12,baseline-height*.37),(cx+half*.45,baseline),(cx+half*.85,baseline),(cx+half*.46,baseline-height*.42)]
        add(f'<polygon points="{pointsstr(fold)}" fill="{c["bg"]}" opacity=".18"/>')
        # Side contours suggest the folding rock faces of a hand-painted scroll.
        for k in range(3):
            q=.3+k*.18
            curve=[]
            for j in range(9):
                t=j/8
                curve.append((cx+half*t*.8,baseline-height*(1-q)*(1-t*.8)+math.sin(t*7+i)*2))
            add(brush(curve,c['fine'],.6,.45))
        add('</g>')
    add(f'<rect x="35" y="438" width="1130" height="69" fill="url(#mist)"/>')
    # One small pine for each active day; total count is data-driven.
    for i,wk in enumerate(weeks):
        for j in range(wk['active_days']):
            x=centers[i]-7+(j/(max(1,wk['active_days']-1)))*14
            y=491+rng.uniform(-3,4);h=rng.uniform(13,24)
            commands=[f'M{x:.1f},{y-h:.1f}q{rng.uniform(-1,1):.1f},{h*.45:.1f} -.4,{h:.1f}']
            add('<g data-active-day-tree="true">')
            for z in range(3):
                yy=y-h*(.7-z*.2);ww=h*(.16+z*.055)
                left=ww*rng.uniform(.7,1.25);right=ww*rng.uniform(.7,1.25)
                commands.append(f'M{x-left:.1f},{yy+2:.1f}l{left:.1f},-3 {right:.1f},2')
                canopy=[(x-left,yy+2),(x-left*.6,yy-.5),(x-.5,yy-2),(x+right*.5,yy),(x+right,yy+1),(x+right*.65,yy+2.7)]
                add(f'<polygon points="{pointsstr(canopy)}" fill="{c["tree"]}" opacity=".4"/>')
            add(f'<path d="{" ".join(commands)}" fill="none" stroke="{c["tree"]}" stroke-width=".75" opacity=".65"/>')
            add('</g>')
    # Fine shoreline and overlapping water strokes close the ink scroll.
    shore=[(45+k*7.0,501+math.sin(k*.12)*2.2+noise(k*.4,8)*2.5) for k in range(159)]
    add(brush(shore,c['water'],.7,.35))
    for i in range(33):
        x=rng.uniform(48,1110);y=rng.uniform(500,520);width=rng.uniform(6,55)
        add(brush([(x,y),(x+width*.4,y-.5),(x+width,y)],c['water'],.45,rng.uniform(.1,.4)))
    add('</g>')
    # Clearly expose the data relationship without making the picture look like a dashboard.
    text(50,551,'THE YEAR IN COMMITS',15,c['muted'],spacing='1.4')
    text(1150,551,'PEAK HEIGHT = WEEKLY COMMITS · PINES = ACTIVE DAYS',16,c['muted'],anchor='end')
    # Month labels and seven-row contribution calendar use exactly the same x mapping.
    prior=None
    for i,wk in enumerate(weeks):
        date=dt.date.fromisoformat(wk['start'])
        if date.month!=prior:
            if i>0:text(centers[i]-6,579,date.strftime('%b'),16,c['muted'])
            prior=date.month
    for row,label in [(1,'Mon'),(3,'Wed'),(5,'Fri')]:text(51,598+row*12+8,label,13,c['muted'])
    for i,wk in enumerate(weeks):
        for j in range(7):
            day=data['days'][i*7+j];n=day['commits']
            fill=c['zero'] if n==0 else c['grid'][0 if n<4 else 1 if n<8 else 2 if n<13 else 3]
            add(f'<rect data-commit-day="{day["date"]}" x="{centers[i]-5}" y="{592+j*12}" width="10" height="10" rx="1.5" fill="{fill}"><title>{day["date"]}: {n} commits (sample)</title></rect>')
    text(50,709,'52 weekly peaks. 364 daily marks.',16,c['muted'],font='sans')
    text(897,709,'0',14,c['muted'])
    for i,col in enumerate([c['zero']]+c['grid']):add(f'<rect x="{916+i*16}" y="699" width="11" height="11" rx="1.5" fill="{col}"/>')
    text(1005,709,'13+ commits/day',14,c['muted'])
    add('</svg>')
    return '\n'.join(out)

def render_mobile(data, mode):
    """Recompose the same generated art and day cells for a narrow README."""
    import xml.etree.ElementTree as ET
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    full=ET.fromstring(render(data,mode))
    c=PALETTES[mode];s=data['summary']
    out=[]
    def add(value):out.append(value)
    def text(x,y,value,size=22,color=None,serif=False,anchor='start'):
        ff='Georgia, Times New Roman, serif' if serif else 'ui-monospace, SFMono-Regular, Consolas, monospace'
        add(f'<text x="{x}" y="{y}" fill="{color or c["ink"]}" font-family="{ff}" font-size="{size}" text-anchor="{anchor}">{escape(str(value))}</text>')
    add('<svg xmlns="http://www.w3.org/2000/svg" width="560" height="650" viewBox="0 0 560 650" role="img" aria-labelledby="mobile-title mobile-desc">')
    add('<title id="mobile-title">A year, written in mountains — sample commit landscape</title>')
    add(f'<desc id="mobile-desc">Fictional 52-week commit landscape. {s["commits"]} sample commits, {s["active_days"]} active days, {s["peak_week_commits"]} commits in the peak week. Each mountain represents a week and each pine one active day.</desc>')
    for node in full:
        if node.tag.endswith('}defs'):add(ET.tostring(node,encoding='unicode'))
    add(f'<rect width="560" height="650" rx="8" fill="{c["bg"]}"/>')
    text(24,39,'COMMIT LANDSCAPE',22,c['muted'])
    text(24,91,'A year, written',42,serif=True)
    text(24,139,'in mountains.',42,serif=True)
    for x,number,label in [(24,f'{s["commits"]:,}','COMMITS'),(205,str(s['active_days']),'ACTIVE DAYS'),(397,str(s['peak_week_commits']),'PEAK WEEK')]:
        text(x,199,number,38,serif=True)
        text(x,229,label,22,c['muted'])
    text(24,269,'26 OCT 2025 — 24 OCT 2026',22,c['muted'])
    # The mountain geometry and all pines are reused without regeneration.
    add('<g transform="translate(0 180) scale(0.4666667)">')
    for node in full:
        if node.tag.endswith('}g') and node.attrib.get('clip-path')=='url(#art)':
            add(ET.tostring(node,encoding='unicode'))
    add('</g>')
    # Retain every day cell, with fewer readable labels around the small grid.
    prior=None
    for i,wk in enumerate(data['weeks']):
        date=dt.date.fromisoformat(wk['start'])
        if date.month!=prior and date.month in (1,4,7,10):
            x=(110+i*19)*.4666667
            text(x,453,date.strftime('%b').upper(),22,c['muted'],anchor='middle')
        prior=date.month
    add('<g transform="translate(0 194) scale(0.4666667)">')
    for node in full:
        if node.attrib.get('data-commit-day'):add(ET.tostring(node,encoding='unicode'))
    add('</g>')
    text(24,548,'Peak height = weekly commits',22,c['muted'])
    text(24,581,'One pine = one active day',22,c['muted'])
    text(24,625,'SAMPLE DATA',22,c['red'])
    text(536,625,'52 WEEKS',22,c['muted'],anchor='end')
    add('</svg>')
    return '\n'.join(out)

def main():
    path=ROOT/'data/activity.json'
    data=json.loads(path.read_text()) if path.exists() else fixture()
    if len(data['days'])!=364: raise ValueError('This mockup expects 52 complete weeks / 364 days.')
    data=summarize(data)
    path.write_text(json.dumps(data,indent=2)+'\n')
    for theme,name in [('dark','commit-landscape.svg'),('light','commit-landscape-light.svg')]:
        (ROOT/'assets'/name).write_text(render(data,theme))
    for theme,name in [('dark','commit-landscape-mobile.svg'),('light','commit-landscape-mobile-light.svg')]:
        (ROOT/'assets'/name).write_text(render_mobile(data,theme))
    print(json.dumps(data['summary'],indent=2))

if __name__=='__main__':main()
