/* Composition and commit mapping around the original, unmodified renderer.
 * No mountains, people, architecture, boats, trees, or water are redrawn here.
 */
const fs = require('fs');
const path = require('path');
const {createEngine,hashSeed} = require('./engine.cjs');
const ROOT = path.join(__dirname,'..');
const sourceData = JSON.parse(fs.readFileSync(path.join(ROOT,'data/activity.json'),'utf8'));
const months = [];
for (const day of sourceData.days) {
  const key=day.date.slice(0,7);
  let month=months.find(m=>m.key===key);
  if(!month){month={key,commits:0,activeDays:0,days:0};months.push(month);}
  month.commits+=day.commits;month.activeDays+=Number(day.commits>0);month.days++;
}
const engine=createEngine();
const WIDTH=months.length*400,HEIGHT=620;
const maxCommits=Math.max(1,...months.map(m=>m.commits));
const MAX_RISE=350,MIN_RISE=6,REFERENCE_HEIGHT=500,MOUNTAIN_BASELINE=385;
const features=[];
const manifest={sample:true,source:JSON.parse(fs.readFileSync(path.join(ROOT,'vendor/source.json'),'utf8')),width:WIDTH,height:HEIGHT,period:WIDTH,months,features:[],mapping:{mountains:'Visible terrain rise = max(6,350 × (monthly commits / peak month)^2), zero for zero commits. Original ret:1 contour measures noise; a complete original mountain rendered at hei500 is uniformly scaled to the target rise. Above the floor,150:100:50 commits gives9:4:1 mountain heights.',mountainWidth:'Final width =130+330 × (monthly commits / peak month)^1.1, compensated inside the original renderer before uniform scaling.',texture:'Original texture count =85+4 × monthly active days.',groves:'ceil(active days /7) explicitly planted original foreground trees per month; additional vegetation is generated internally by the original renderer.',boats:'One original boat01, including its original ferryman, for each active month.',figures:'People and pavilions are original decorative artwork, not a count of contributors.',seed:'Stable hash of month and feature kind; commit totals do not reseed the scenery.'}};
function add(kind,month,x,y,fn,args,extra={}) {
  const key=month?.key||'background';
  const seed=engine.reset(`${key}:${kind}`);
  const svg=fn(seed/100000,args);
  if(/NaN|Infinity|undefined/.test(svg))throw new Error(`Invalid geometry ${key}/${kind}`);
  const record={kind,month:key,x,y,args,...extra};
  features.push({y,svg:`<g data-feature="${kind}" data-month="${key}">${svg}</g>`});
  manifest.features.push(record);
}

// Pale triangulated ridges and fine water come directly from the original.
for(let i=0;i<months.length;i++){
  const m=months[i],cx=i*400+200;
  add('distant-ridge',m,cx-270,370,(seed,a)=>`<g opacity="0.18">${engine.Mount.distMount(cx-270,370,seed,a)}</g>`,{hei:25+25*Math.pow(m.commits/maxCommits,2),len:550,seg:5},{drawOrder:0});
  features[features.length-1].y=-1000;
  const riverY=590+8*Math.sin(i*1.9);
  add('river',m,cx,riverY,(seed,a)=>engine.water(cx,riverY,seed,a),{len:300,clu:3,hei:.8},{drawOrder:1});
  features[features.length-1].y=-500;
}

for(let i=0;i<months.length;i++){
  const m=months[i],cx=i*400+200;
  const baseline=MOUNTAIN_BASELINE,ratio=m.commits/maxCommits;
  const targetRise=m.commits?Math.max(MIN_RISE,MAX_RISE*ratio**2):0;
  const renderWidth=m.commits?130+330*ratio**1.1:0;
  const tex=85+4*m.activeDays;
  // Measure the original contour at a healthy reference height. Reusing the
  // exact seed for final drawing leaves all original brush/figure routines
  // untouched while making the visible terrain rise independent of noise.
  // Scaling the whole drawing preserves the proportions of its decorations;
  // driving the original hei toward zero would inflate some internal trees.
  const probeSeed=engine.reset(`${m.key}:monthly-mountain`)/100000;
  const contours=engine.Mount.mountain(0,0,probeSeed,{hei:REFERENCE_HEIGHT,wid:500,tex,veg:true,ret:1})[0];
  const referenceRise=-Math.min(...contours[0].map(point=>point[1]));
  if(!(referenceRise>0))throw new Error(`Invalid reference contour for ${m.key}`);
  const scale=targetRise/referenceRise;
  const wid=scale?renderWidth/scale:500;
  m.mountain={x:cx,y:baseline,hei:REFERENCE_HEIGHT,wid,tex,targetRise,referenceRise,scale,renderWidth};
  add('monthly-mountain',m,cx,baseline,(seed,a)=>scale?`<g transform="translate(${cx} ${baseline}) scale(${scale})">${engine.Mount.mountain(0,0,seed,a)}</g>`:'',{hei:REFERENCE_HEIGHT,wid,tex,veg:true},{outerScale:scale,targetRise,referenceRise,renderWidth});

  // Explicit trees grow with active days. Original mountain vegetation remains.
  const trees=Math.ceil(m.activeDays/7);m.explicitTrees=trees;
  for(let j=0;j<trees;j++){
    const x=cx-112+j*51,y=397+Math.sin(j+i)*7;
    const variant=['tree01','tree03','tree07'][j%3];
    add(`grove-${j}`,m,x,y,(seed,a)=>engine.Tree[variant](x,y,a),{hei:45+9*j,wid:2.2,col:'rgba(100,100,100,0.55)'},{originalFunction:`Tree.${variant}`});
  }

  // Quiet rocky shores make foreground scale legible without filling the river.
  const rockx=cx-130;
  add('shore-rock',m,rockx,420,(seed,a)=>engine.Mount.rock(rockx,420,seed,a),{wid:85,hei:30,tex:20,sha:3});

  if(i%3===0){
    const islandx=cx-75,islandy=497;
    add('foreground-island',m,islandx,islandy,(seed,a)=>engine.Mount.flatMount(islandx,islandy,seed,a),{hei:70,wid:285,tex:55,cho:.40});
    features[features.length-1].y=430;
    add('pavilion',m,islandx,472,(seed,a)=>engine.Arch.arch01(islandx,472,seed,a),{wid:150,hei:78,per:6});
    add('traveller-footing',m,islandx+111,494,(seed,a)=>engine.Mount.rock(islandx+111,494,seed,a),{wid:92,hei:34,tex:18,sha:2});
    features[features.length-1].y=460;
    add('traveller',m,islandx+111,475,(seed,a)=>engine.Man.man(islandx+111,475,{...a,hat:engine.Man.hat02,ite:engine.Man.stick01}),{sca:.72,fli:false},{originalFunction:'Man.man + Man.hat02 + Man.stick01'});
  } else if(i%3===1){
    const px=cx+100;
    add('shore-pagoda',m,px,415,(seed,a)=>engine.Arch.arch03(px,415,seed,a),{wid:48,hei:13,sto:3+Math.floor(m.commits/100),per:5});
  }

  if(m.activeDays){
    const bx=cx+24,by=545+18*Math.sin(i*2.4),scale=1.2;
    // Original boat01 sca is held at1: its hull uses sqrt(sin(i/len));
    // external vector scaling enlarges both original boat and original figure.
    add('ferry',m,bx,by,(seed,a)=>`<g transform="translate(${bx} ${by}) scale(${scale})">${engine.Arch.boat01(0,0,seed,a)}</g>`,{len:112,sca:1,fli:i%2===1},{outerScale:scale,originalFunction:'Arch.boat01 → Man.man + Man.hat02 + Man.stick01'});
    add('ferry-water',m,bx+50,by+25,(seed,a)=>engine.water(bx+50,by+25,seed,a),{len:180,clu:4,hei:.65});
  }
}

features.sort((a,b)=>a.y-b.y);
const scene=`<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${HEIGHT}" viewBox="0 0 ${WIDTH} ${HEIGHT}" role="img" aria-labelledby="scene-title scene-desc"><title id="scene-title">A commit journey, drawn with Lingdong Huang’s original Shan Shui renderer</title><desc id="scene-desc">Thirteen calendar chapters from sample commit history. Monthly commits set mountain scale; active days set texture and groves. Original boats, ferrymen, travellers and pavilions populate the riverbanks. All counts are illustrative.</desc><g id="lingdong-scene">${features.map(f=>f.svg).join('\n')}</g></svg>`;
fs.mkdirSync(path.join(ROOT,'assets'),{recursive:true});fs.mkdirSync(path.join(ROOT,'data'),{recursive:true});
fs.writeFileSync(path.join(ROOT,'assets/scene.svg'),scene);
fs.writeFileSync(path.join(ROOT,'data/scene-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({width:WIDTH,height:HEIGHT,months:months.length,commits:months.reduce((s,m)=>s+m.commits,0),features:features.length,bytes:Buffer.byteLength(scene)}));
