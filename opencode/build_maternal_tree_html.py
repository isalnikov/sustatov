#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build interactive maternal-branches tree from maternal_tree_data.json."""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(DIR, "maternal_tree_data.json")
OUT_PATH = os.path.join(DIR, "maternal_tree.html")

BRANCH_COLOR = {
    "direct": "#3fb950",
    "korolev": "#ff7b72",
    "abramov": "#d29922",
    "markin": "#e3b341",
    "kovrigin": "#58a6ff",
    "dvornikov": "#79c0ff",
    "salnikov": "#a5d6ff",
    "kulikov": "#bc8cff",
    "belov": "#d2a8ff",
    "botvinin": "#f778ba",
    "collateral": "#8b949e",
    "koshelikha": "#6e7681",
    "aftodeevo": "#6e7681",
    "unknown": "#484f58",
}

ROLE_LABEL = {
    "wife": "жена",
    "mother": "мать",
    "father": "отец",
    "husband": "муж (линия)",
    "daughter": "дочь",
    "collateral": "родня",
    "descendant": "потомок",
}

with open(DATA_PATH, encoding="utf-8") as f:
    meta = json.load(f)

nodes = meta["nodes"]
data_js = json.dumps(nodes, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Материнские ветви — род Сустатовых</title>
<style>
:root{{--bg:#0d1117;--panel:#161b22;--line:#30363d;--text:#e6edf3;--muted:#8b949e;--wife:#ff7b72;--mother:#f778ba;--father:#79c0ff}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column;overflow:hidden}}
header{{padding:10px 18px;border-bottom:1px solid var(--line);background:var(--panel);display:flex;flex-wrap:wrap;gap:10px;align-items:center}}
header h1{{font-size:1.05rem}}
.sub{{color:var(--muted);font-size:.78rem}}
.toolbar{{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap}}
.toolbar input,.toolbar select,.toolbar button{{background:var(--bg);border:1px solid var(--line);color:var(--text);border-radius:8px;padding:5px 10px;font-size:.82rem}}
.toolbar button{{cursor:pointer}} .toolbar button.active{{background:#3fb950;color:#0d1117;border-color:#3fb950}}
#stage{{flex:1;position:relative;overflow:hidden;cursor:grab}}
#stage.dragging{{cursor:grabbing}}
.legend{{position:absolute;left:10px;bottom:10px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 12px;font-size:.7rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:8px;max-width:85%}}
.legend span{{display:flex;align-items:center;gap:4px}}
.legend i{{width:10px;height:10px;border-radius:2px;display:inline-block}}
.node rect{{stroke-width:1.5;cursor:pointer}}
.node.dim{{opacity:.15}}
.node .nm{{font-size:11px;font-weight:600;fill:var(--text)}}
.node .dt{{font-size:9px;fill:var(--muted)}}
.node .rl{{font-size:8px;fill:var(--muted)}}
.edge{{fill:none;stroke:#444;stroke-width:1.3}}
.edge.parent{{stroke:#79c0ff;stroke-width:1.8}}
.edge.marriage{{stroke:var(--wife);stroke-dasharray:5 4}}
.modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:50;align-items:center;justify-content:center;padding:16px}}
.modal.open{{display:flex}}
.modal .box{{background:var(--panel);border:1px solid var(--line);border-radius:12px;max-width:520px;width:100%;max-height:80vh;overflow:auto}}
.modal .head{{padding:14px 18px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between}}
.modal .close{{background:none;border:none;color:var(--muted);font-size:1.3rem;cursor:pointer}}
.modal .body{{padding:14px 18px;font-size:.85rem;line-height:1.5}}
.modal dl{{display:grid;grid-template-columns:110px 1fr;gap:4px 10px}}
.modal dt{{color:var(--muted)}}
.modal a{{color:#58a6ff}}
</style>
</head>
<body>
<header>
  <h1>Материнские ветви <span class="sub">жёны · матери · родители жён</span></h1>
  <span class="sub" id="stats"></span>
  <div class="toolbar">
    <input id="q" placeholder="Поиск…">
    <select id="branch"><option value="">Все ветви</option></select>
    <button id="bWives">Только жёны</button>
    <button id="bDirect" class="active">Прямая линия</button>
    <button id="bAll">Все</button>
    <button id="bIn">+</button><button id="bOut">−</button><button id="bReset">Сброс</button>
  </div>
</header>
<div id="stage"><svg id="svg"></svg>
<div class="legend" id="legend"></div>
</div>
<div class="modal" id="modal"><div class="box"><div class="head"><h2 id="mTitle"></h2><button class="close" onclick="closeM()">×</button></div><div class="body" id="mBody"></div></div></div>
<script>
const NODES = {data_js};
const byId = {{}}; NODES.forEach(n => byId[n.id] = n);

const BRANCH_COLOR = {json.dumps(BRANCH_COLOR, ensure_ascii=False)};
const ROLE_LABEL = {json.dumps(ROLE_LABEL, ensure_ascii=False)};

// layout: ancestors above, wives beside husbands
const childrenOf = {{}};
NODES.forEach(n => {{
  (n.parentIds||[]).forEach(pid => {{
    if (!byId[pid]) return;
    (childrenOf[pid] = childrenOf[pid]||[]).push(n.id);
  }});
}});
Object.keys(childrenOf).forEach(k => childrenOf[k] = [...new Set(childrenOf[k])]);

const hasParent = {{}};
NODES.forEach(n => (n.parentIds||[]).forEach(p => {{ if(byId[p]) hasParent[n.id]=true; }}));

// roots: no parent in graph
const roots = NODES.filter(n => !hasParent[n.id]).map(n => n.id);

let slot = 0;
function walk(id, depth) {{
  const n = byId[id]; n._depth = depth;
  const kids = childrenOf[id] || [];
  if (!kids.length) {{ n._slot = slot; n._min = n._max = slot; slot += 1.2; }}
  else {{
    let mn = 1e9, mx = -1;
    kids.forEach(c => {{ walk(c, depth+1); mn=Math.min(mn,byId[c]._min); mx=Math.max(mx,byId[c]._max); }});
    n._min = mn; n._max = mx; n._slot = (mn+mx)/2;
  }}
}}
roots.forEach(r => walk(r, 0));

// place spouses adjacent
NODES.forEach(n => {{
  (n.spouseIds||[]).forEach(sid => {{
    const s = byId[sid]; if(!s) return;
    if (s._slot === undefined) {{ s._depth = n._depth; s._slot = n._slot + 0.85; s._min = s._max = s._slot; }}
  }});
}});

NODES.filter(n => n._slot === undefined).forEach((n,i) => {{ n._depth=0; n._slot=slot+i; }});

const CW=230, RH=58, YG=22;
const X=id=>byId[id]._slot*CW;
const Y=id=>byId[id]._depth*(RH+YG)+24;
const maxD=Math.max(...NODES.map(n=>n._depth||0));
const W=Math.ceil((slot+3)*CW), H=Math.ceil((maxD+2)*(RH+YG)+80);

const svg=document.getElementById('svg');
svg.setAttribute('width',W); svg.setAttribute('height',H);
const g=document.createElementNS('http://www.w3.org/2000/svg','g'); g.id='vp'; svg.appendChild(g);
const eg=document.createElementNS('http://www.w3.org/2000/svg','g'); g.appendChild(eg);
const ng=document.createElementNS('http://www.w3.org/2000/svg','g'); g.appendChild(ng);

function edge(x1,y1,x2,y2,cls) {{
  const p=document.createElementNS('http://www.w3.org/2000/svg','path');
  p.setAttribute('d',`M${{x1}},${{y1}} C${{x1}},${{(y1+y2)/2}} ${{x2}},${{(y1+y2)/2}} ${{x2}},${{y2}}`);
  p.setAttribute('class','edge '+cls); eg.appendChild(p);
}}

NODES.forEach(n => {{
  (n.parentIds||[]).forEach(pid => {{
    if(!byId[pid]) return;
    edge(X(pid), Y(pid)+RH-6, X(n.id), Y(n.id), 'parent');
  }});
  (n.spouseIds||[]).forEach(sid => {{
    if(!byId[sid] || n.id > sid) return;
    edge(X(n.id)+90, Y(n.id)+RH/2, X(sid)-90, Y(sid)+RH/2, 'marriage');
  }});
}});

const boxW=CW-36;
NODES.forEach(n => {{
  const el=document.createElementNS('http://www.w3.org/2000/svg','g');
  el.setAttribute('class','node'); el.setAttribute('data-id',n.id);
  el.setAttribute('transform',`translate(${{X(n.id)-boxW/2+18}},${{Y(n.id)}})`);
  const col=BRANCH_COLOR[n.branch]||'#666';
  const r=document.createElementNS('http://www.w3.org/2000/svg','rect');
  r.setAttribute('width',boxW); r.setAttribute('height',RH-4); r.setAttribute('rx',8);
  r.setAttribute('fill',col+'28'); r.setAttribute('stroke',col);
  el.appendChild(r);
  [['nm',n.name,18],['dt',(n.born||'')+(n.died?' — '+n.died:''),34],['rl',(ROLE_LABEL[n.role]||n.role)+' · '+n.branch,48]].forEach(([c,t,y])=>{{
    const tx=document.createElementNS('http://www.w3.org/2000/svg','text');
    tx.setAttribute('x',8); tx.setAttribute('y',y); tx.setAttribute('class',c);
    tx.textContent = t.length>32?t.slice(0,32)+'…':t; el.appendChild(tx);
  }});
  el.addEventListener('click',()=>openM(n.id));
  ng.appendChild(el);
}});

// direct-line wives chain
const DIRECT_H = ['h-nikita','h-petr','h-andrey','h-ivan-andreevich','h-ivan-1815','h-ivan-1847','h-ivan-1870','h-vasiliy-1890','h-grigoriy-1912','h-vasiliy-1930','h-grigoriy-1954'];
const directSet = new Set(DIRECT_H);
DIRECT_H.forEach(hid => {{
  const h=byId[hid]; if(!h) return;
  (h.spouseIds||[]).forEach(wid => directSet.add(wid));
  (h.parentIds||[]).forEach(pid => directSet.add(pid));
}});
function markDirect(id) {{
  let q=[id]; const seen=new Set();
  while(q.length) {{
    const cur=q.pop(); if(seen.has(cur)) continue; seen.add(cur); directSet.add(cur);
    const n=byId[cur]; if(!n) continue;
    (n.parentIds||[]).forEach(p=>q.push(p));
    (n.spouseIds||[]).forEach(s=>q.push(s));
    (n.childIds||[]).forEach(c=>q.push(c));
  }}
}}
['w-praskovya','w-evdokia','w-alexandra','w-olga'].forEach(markDirect);

let directMode=true, wivesMode=false, branchFilter='';
function applyFilter() {{
  document.querySelectorAll('.node').forEach(el => {{
    const n=byId[el.getAttribute('data-id')];
    let show=true;
    if(directMode && !directSet.has(n.id)) show=false;
    if(wivesMode && n.role!=='wife' && n.role!=='mother' && n.role!=='father') show=false;
    if(branchFilter && n.branch!==branchFilter) show=false;
    el.classList.toggle('dim', !show);
  }});
}}
document.getElementById('bDirect').onclick=()=>{{directMode=true;wivesMode=false;document.getElementById('bDirect').classList.add('active');document.getElementById('bAll').classList.remove('active');document.getElementById('bWives').classList.remove('active');applyFilter();}};
document.getElementById('bAll').onclick=()=>{{directMode=false;wivesMode=false;document.getElementById('bAll').classList.add('active');document.getElementById('bDirect').classList.remove('active');document.getElementById('bWives').classList.remove('active');applyFilter();}};
document.getElementById('bWives').onclick=()=>{{wivesMode=true;directMode=false;document.getElementById('bWives').classList.add('active');document.getElementById('bDirect').classList.remove('active');document.getElementById('bAll').classList.remove('active');applyFilter();}};

const branches=[...new Set(NODES.map(n=>n.branch))].sort();
const sel=document.getElementById('branch');
branches.forEach(b=>{{const o=document.createElement('option');o.value=b;o.textContent=b;sel.appendChild(o);}});
sel.onchange=()=>{{branchFilter=sel.value;applyFilter();}};

document.getElementById('q').oninput=e=>{{
  const q=e.target.value.toLowerCase();
  document.querySelectorAll('.node').forEach(el=>{{
    const n=byId[el.getAttribute('data-id')];
    el.classList.toggle('dim', q && !n.name.toLowerCase().includes(q));
  }});
}};

function openM(id) {{
  const n=byId[id]; if(!n) return;
  document.getElementById('mTitle').textContent=n.name;
  const spouses=(n.spouseIds||[]).map(s=>byId[s]?.name).filter(Boolean).join(', ');
  const parents=(n.parentIds||[]).map(p=>byId[p]?.name).filter(Boolean).join(', ');
  const children=(n.childIds||[]).map(c=>byId[c]?.name).filter(Boolean).join(', ');
  const src=(n.sources||[]).map(s=>s.startsWith('http')?`<a href="${{s}}" target="_blank">${{s.slice(0,40)}}…</a>`:s).join('<br>');
  document.getElementById('mBody').innerHTML=`<dl>
    <dt>Роль</dt><dd>${{ROLE_LABEL[n.role]||n.role}} · ${{n.branch}}</dd>
    <dt>Рожд.</dt><dd>${{n.born||'—'}}</dd><dt>Смерть</dt><dd>${{n.died||'—'}}</dd>
    <dt>Родители</dt><dd>${{parents||'—'}}</dd>
    <dt>Супруг(и)</dt><dd>${{spouses||'—'}}</dd>
    <dt>Дети</dt><dd>${{children||'—'}}</dd>
    <dt>Статус</dt><dd>${{n.status}}</dd>
    <dt>Источники</dt><dd>${{src||'—'}}</dd>
    <dt>Примечания</dt><dd>${{n.notes||'—'}}</dd>
  </dl>`;
  document.getElementById('modal').classList.add('open');
}}
function closeM(){{document.getElementById('modal').classList.remove('open');}}
document.getElementById('modal').onclick=e=>{{if(e.target.id==='modal')closeM();}};

let v={{x:30,y:30,k:1}}; function applyV(){{g.setAttribute('transform',`translate(${{v.x}},${{v.y}}) scale(${{v.k}})`);}}
applyV();
const stage=document.getElementById('stage'); let pan=false,sx,sy;
stage.onmousedown=e=>{{pan=true;sx=e.clientX-v.x;sy=e.clientY-v.y;stage.classList.add('dragging');}};
window.onmousemove=e=>{{if(!pan)return;v.x=e.clientX-sx;v.y=e.clientY-sy;applyV();}};
window.onmouseup=()=>{{pan=false;stage.classList.remove('dragging');}};
stage.onwheel=e=>{{e.preventDefault();v.k=Math.min(3,Math.max(.2,v.k*(e.deltaY<0?1.1:.9)));applyV();}};
document.getElementById('bIn').onclick=()=>{{v.k=Math.min(3,v.k*1.2);applyV();}};
document.getElementById('bOut').onclick=()=>{{v.k=Math.max(.2,v.k/1.2);applyV();}};
document.getElementById('bReset').onclick=()=>{{v={{x:30,y:30,k:1}};applyV();}};

const leg=document.getElementById('legend');
Object.entries(BRANCH_COLOR).forEach(([b,c])=>{{
  leg.innerHTML+=`<span><i style="background:${{c}}"></i>${{b}}</span>`;
}});
document.getElementById('stats').textContent=`${{NODES.length}} персон · ${{NODES.filter(n=>n.role==='wife').length}} жён · ${{NODES.filter(n=>n.status==='notfound').length}} пробелов`;
applyFilter();
</script>
</body>
</html>"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Wrote {OUT_PATH} ({len(nodes)} nodes)")
