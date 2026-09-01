#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, glob

DIR = "/home/igor/cursorwork/sustatov/opencode"
OUT = os.path.join(DIR, "tree.html")

persons = []
for fp in sorted(glob.glob(os.path.join(DIR, "people", "*.json"))):
    with open(fp, encoding="utf-8") as f:
        persons.append(json.load(f))

data_js = json.dumps(persons, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Род Сустатовых — интерактивный граф</title>
<style>
:root{
  --bg:#0d1117; --panel:#161b22; --line:#30363d; --text:#e6edf3; --muted:#8b949e;
  --direct:#3fb950; --sibling:#56d364; --cousin:#58a6ff; --collateral:#a5d6ff;
  --spouse:#ff7b72; --spouse_family:#ffa198; --xvii:#d2a8ff; --porunov:#d29922;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--text);overflow:hidden;height:100vh;display:flex;flex-direction:column}
header{padding:12px 20px;border-bottom:1px solid var(--line);background:var(--panel);display:flex;flex-wrap:wrap;gap:12px;align-items:center}
header h1{font-size:1.15rem;font-weight:600}
header .sub{color:var(--muted);font-size:.8rem}
.toolbar{display:flex;flex-wrap:wrap;gap:8px;margin-left:auto;align-items:center}
.toolbar input{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:6px 12px;color:var(--text);width:200px;font-size:.85rem}
.toolbar button{background:var(--panel);border:1px solid var(--line);color:var(--text);padding:6px 12px;border-radius:8px;cursor:pointer;font-size:.82rem}
.toolbar button:hover{background:var(--line)}
.toolbar button.active{background:var(--direct);color:#0d1117;border-color:var(--direct)}
#stage{flex:1;position:relative;overflow:hidden;cursor:grab}
#stage.dragging{cursor:grabbing}
#stage svg{display:block}
.legend{position:absolute;left:12px;bottom:12px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:.72rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:10px;max-width:70%}
.legend span{display:flex;align-items:center;gap:5px}
.legend i{width:11px;height:11px;border-radius:3px;display:inline-block}
.node{cursor:pointer}
.node rect{stroke-width:1.5;transition:filter .15s}
.node:hover rect{filter:brightness(1.15)}
.node.dim{opacity:.12}
.node .nm{font-weight:600;font-size:12px;fill:var(--text)}
.node .dt{font-size:10px;fill:var(--muted)}
.node .rel{font-size:9px;fill:var(--muted)}
.edge{fill:none;stroke:#30363d;stroke-width:1.4}
.edge.marriage{stroke:var(--spouse);stroke-dasharray:4 3;stroke-width:1.2}
.edge.direct{stroke:var(--direct);stroke-width:2.2}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;align-items:center;justify-content:center;padding:20px}
.modal.open{display:flex}
.modal .box{background:var(--panel);border:1px solid var(--line);border-radius:14px;max-width:560px;width:100%;max-height:80vh;overflow-y:auto}
.modal .head{padding:16px 20px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:flex-start}
.modal .head h2{font-size:1.1rem}
.modal .close{background:transparent;border:none;color:var(--muted);font-size:1.4rem;cursor:pointer;line-height:1}
.modal .body{padding:16px 20px}
.modal dl{display:grid;grid-template-columns:130px 1fr;gap:5px 12px;font-size:.85rem}
.modal dt{color:var(--muted)}
.modal dd{margin:0;word-break:break-word}
.modal a{color:var(--cousin);text-decoration:none}
.modal a:hover{text-decoration:underline}
.badge{display:inline-block;font-size:.65rem;padding:1px 7px;border-radius:8px;font-weight:600;letter-spacing:.03em}
.b-CONFIRMED{background:#1a3326;color:#3fb950}.b-PROBABLE{background:#33230d;color:#d29922}.b-HYPOTHESIS{background:#2d1620;color:#ff7b72}
</style>
</head>
<body>
<header>
  <h1>Род Сустатовых <span style="color:var(--muted);font-weight:400">— граф связей</span></h1>
  <span class="sub" id="stats"></span>
  <div class="toolbar">
    <input id="q" placeholder="Поиск…">
    <button id="bIn">+</button>
    <button id="bOut">−</button>
    <button id="bReset">Сброс</button>
    <button id="bDirect" class="active">Только прямая линия</button>
    <button id="bAll">Все</button>
  </div>
</header>
<div id="stage"><svg id="svg"></svg><div class="legend">
  <span><i style="background:#3fb950"></i> прямая</span>
  <span><i style="background:#56d364"></i> брат/сестра</span>
  <span><i style="background:#58a6ff"></i> двоюродные</span>
  <span><i style="background:#a5d6ff"></i> боковые</span>
  <span><i style="background:#ff7b72"></i> супруги</span>
  <span><i style="background:#d2a8ff"></i> XVII век</span>
  <span><i style="background:#d29922"></i> Поруновы</span>
  <span>━ супруг · ── ребёнок</span>
</div></div>
<div class="modal" id="modal"><div class="box"><div class="head"><h2 id="mTitle"></h2><button class="close" onclick="closeModal()">×</button></div><div class="body" id="mBody"></div></div></div>
<script>
const DATA = __DATA__;

const byId = {};
DATA.forEach(p => byId[p.id] = p);

const CAT_COLOR = {
  direct:'#3fb950', sibling:'#56d364', cousin:'#58a6ff', collateral:'#a5d6ff',
  spouse:'#ff7b72', spouse_family:'#ffa198', xvii:'#d2a8ff', porunov:'#d29922'
};
const CAT_LABEL = {
  direct:'прямая линия', sibling:'брат/сестра', cousin:'двоюродные', collateral:'боковая ветвь',
  spouse:'супруг(а)', spouse_family:'родня супруга', xvii:'XVII век', porunov:'Поруновы'
};

// --- граф ---
// father-based children
const childrenOf = {};
DATA.forEach(p => {
  const f = p.relationships.father;
  if (f && byId[f]) (childrenOf[f] = childrenOf[f] || []).push(p.id);
  // spouse-family children (F -> child spouse)
  (p.relationships.children || []).forEach(c => {
    if (byId[c] && !byId[c].relationships.father) {
      (childrenOf[p.id] = childrenOf[p.id] || []).push(c);
    }
  });
});
// de-dup
Object.keys(childrenOf).forEach(k => childrenOf[k] = [...new Set(childrenOf[k])]);

// roots: persons not a child of anyone (via father or mother)
const hasParent = {};
DATA.forEach(p => {
  if (p.relationships.father && byId[p.relationships.father]) hasParent[p.id] = true;
  if (p.relationships.mother && byId[p.relationships.mother]) hasParent[p.id] = true;
});
DATA.forEach(p => {
  (p.relationships.children || []).forEach(c => { if (byId[c]) hasParent[c] = true; });
});
// "pure spouses": супруги без собственных родителей/детей — размещаются рядом с партнёром
const pureSpouse = {};
DATA.forEach(p => {
  if (p.category === 'spouse' && !p.relationships.father && !p.relationships.mother) {
    const isParent = Object.keys(childrenOf).some(k => (childrenOf[k]||[]).includes(p.id));
    if (!isParent) pureSpouse[p.id] = true;
  }
});
const roots = DATA.filter(p => !hasParent[p.id] && !pureSpouse[p.id]).map(p => p.id);

// lay out (leaf-slot)
let slot = 0;
const pos = {};
function walk(id, depth){
  const kids = childrenOf[id] || [];
  const p = byId[id];
  p._depth = depth;
  if (kids.length === 0) { p._slot = slot; p._min = p._max = slot; slot++; }
  else {
    let mn = 1e9, mx = -1;
    kids.forEach(c => { walk(c, depth + 1); mn = Math.min(mn, byId[c]._min); mx = Math.max(mx, byId[c]._max); });
    p._min = mn; p._max = mx; p._slot = (mn + mx) / 2;
  }
}
roots.forEach(r => { slot += 1.5; walk(r, 0); });

// isolated nodes (no edge at all) -> grid
const isolated = DATA.filter(p => p._slot === undefined);
isolated.forEach((p, i) => {
  p._depth = 0;
  p._slot = slot + i;
  p._min = p._max = p._slot;
});
if (isolated.length) slot += isolated.length;

const CW = 250, RH = 66, YGAP = 24;
const X = id => byId[id]._slot * CW;
const Y = id => byId[id]._depth * (RH + YGAP) + 20;
const maxD = Math.max(...DATA.map(p => p._depth || 0));
const W = Math.ceil((slot + 2) * CW);
const H = Math.ceil((maxD + 1) * (RH + YGAP) + 100);

const svg = document.getElementById('svg');
svg.setAttribute('width', W); svg.setAttribute('height', H);
const g = document.createElementNS('http://www.w3.org/2000/svg','g'); g.id='vp'; svg.appendChild(g);
const edgesG = document.createElementNS('http://www.w3.org/2000/svg','g'); g.appendChild(edgesG);
const nodesG = document.createElementNS('http://www.w3.org/2000/svg','g'); g.appendChild(nodesG);

// helper: is in direct chain (walks father)
function isDirect(id){
  let t = byId[id];
  while (t) {
    if (t.category === 'direct') return true;
    t = t.relationships.father ? byId[t.relationships.father] : null;
  }
  return false;
}

// edges: father->child and mother->child
DATA.forEach(p => {
  const f = p.relationships.father;
  if (f && byId[f]) {
    const l = document.createElementNS('http://www.w3.org/2000/svg','path');
    const x1 = X(f), y1 = Y(f) + RH - 8, x2 = X(p.id), y2 = Y(p.id);
    l.setAttribute('d', `M${x1},${y1} C${x1},${(y1+y2)/2} ${x2},${(y1+y2)/2} ${x2},${y2}`);
    l.setAttribute('class', 'edge' + (isDirect(p.id) ? ' direct' : ''));
    edgesG.appendChild(l);
  }
});

// marriage edges (spouse <-> spouse) — dashed; place spouse to the right
DATA.forEach(p => {
  (p.relationships.spouses || []).forEach(s => {
    if (!byId[s]) return;
    // position spouse to the right if not already placed by tree
    if (byId[s]._slot === undefined) {
      byId[s]._depth = p._depth;
      byId[s]._slot = p._slot + 1.05;
    }
    const l = document.createElementNS('http://www.w3.org/2000/svg','path');
    const x1 = X(p.id) + (CW - 40) / 2, x2 = X(s) - (CW - 40) / 2, y1 = Y(p.id) + RH/2, y2 = Y(s) + RH/2;
    l.setAttribute('d', `M${x1},${y1} C${(x1+x2)/2},${y1} ${(x1+x2)/2},${y2} ${x2},${y2}`);
    l.setAttribute('class', 'edge marriage');
    edgesG.appendChild(l);
  });
});

// re-lay spouse families (F) whose slot undefined — grid after isolated
const stillUnplaced = DATA.filter(p => p._slot === undefined);
stillUnplaced.forEach((p, i) => { p._depth = 0; p._slot = slot + i; });
if (stillUnplaced.length) slot += stillUnplaced.length;

// nodes
const boxW = CW - 40;
DATA.forEach(p => {
  const ng = document.createElementNS('http://www.w3.org/2000/svg','g');
  ng.setAttribute('class','node');
  ng.setAttribute('data-id', p.id);
  const x = X(p.id) - boxW/2 + 20, y = Y(p.id);
  ng.setAttribute('transform', `translate(${x},${y})`);
  const hasRel = (p.relationships.father || p.relationships.mother || (p.relationships.spouses||[]).length || (p.relationships.children||[]).length);
  const h = 62;
  const rect = document.createElementNS('http://www.w3.org/2000/svg','rect');
  rect.setAttribute('width', boxW); rect.setAttribute('height', h); rect.setAttribute('rx',9); rect.setAttribute('ry',9);
  rect.setAttribute('fill', (CAT_COLOR[p.category]||'#666') + '22');
  rect.setAttribute('stroke', CAT_COLOR[p.category]||'#666');
  ng.appendChild(rect);
  const nm = document.createElementNS('http://www.w3.org/2000/svg','text');
  nm.setAttribute('x',10); nm.setAttribute('y',18); nm.setAttribute('class','nm');
  nm.textContent = p.full_name.length > 34 ? p.full_name.slice(0,34)+'…' : p.full_name;
  ng.appendChild(nm);
  const dt = document.createElementNS('http://www.w3.org/2000/svg','text');
  dt.setAttribute('x',10); dt.setAttribute('y',34); dt.setAttribute('class','dt');
  const dts = (p.birth.date||'') + (p.death.date ? ' — ' + p.death.date : '');
  dt.textContent = dts;
  ng.appendChild(dt);
  const rel = document.createElementNS('http://www.w3.org/2000/svg','text');
  rel.setAttribute('x',10); rel.setAttribute('y',50); rel.setAttribute('class','rel');
  rel.textContent = CAT_LABEL[p.category] + ' · ' + p.status;
  ng.appendChild(rel);
  ng.addEventListener('click', () => openModal(p.id));
  nodesG.appendChild(ng);
});

// pan/zoom
let v = {x: 40, y: 20, k: 1};
function apply(){ g.setAttribute('transform', `translate(${v.x},${v.y}) scale(${v.k})`); }
apply();
const stage = document.getElementById('stage');
let pan = false, sx, sy;
stage.addEventListener('mousedown', e => { pan = true; sx = e.clientX - v.x; sy = e.clientY - v.y; stage.classList.add('dragging'); });
window.addEventListener('mousemove', e => { if(!pan) return; v.x = e.clientX - sx; v.y = e.clientY - sy; apply(); });
window.addEventListener('mouseup', () => { pan = false; stage.classList.remove('dragging'); });
stage.addEventListener('wheel', e => { e.preventDefault(); v.k = Math.min(3, Math.max(0.25, v.k * (e.deltaY < 0 ? 1.1 : 0.9))); apply(); }, {passive:false});
document.getElementById('bIn').onclick = () => { v.k = Math.min(3, v.k * 1.2); apply(); };
document.getElementById('bOut').onclick = () => { v.k = Math.max(0.25, v.k / 1.2); apply(); };
document.getElementById('bReset').onclick = () => { v = {x:40,y:20,k:1}; apply(); };

let directMode = true;
function setDirect(on){
  directMode = on;
  document.getElementById('bDirect').classList.toggle('active', on);
  document.getElementById('bAll').classList.toggle('active', !on);
  document.querySelectorAll('.node').forEach(el => {
    const p = byId[el.getAttribute('data-id')];
    el.classList.toggle('dim', on && !isDirect(p.id) && !(p.category === 'spouse' && (p.relationships.spouses||[]).some(s => isDirect(s))));
  });
}
document.getElementById('bDirect').onclick = () => setDirect(true);
document.getElementById('bAll').onclick = () => setDirect(false);

document.getElementById('q').oninput = e => {
  const q = e.target.value.trim().toLowerCase();
  document.querySelectorAll('.node').forEach(el => {
    const p = byId[el.getAttribute('data-id')];
    el.classList.toggle('dim', q && !(p.full_name + ' ' + (p.birth.date||'') + ' ' + (p.notes||'')).toLowerCase().includes(q));
  });
};

function openModal(id){
  const p = byId[id];
  document.getElementById('mTitle').innerHTML = p.full_name + ' <span class="badge b-' + p.status + '">' + p.status + '</span>';
  const rel = [];
  if (p.relationships.father && byId[p.relationships.father]) rel.push(['Отец', byId[p.relationships.father].full_name]);
  if (p.relationships.mother && byId[p.relationships.mother]) rel.push(['Мать', byId[p.relationships.mother].full_name]);
  (p.relationships.spouses||[]).forEach(s => { if (byId[s]) rel.push(['Супруг(а)', byId[s].full_name]); });
  (p.relationships.children||[]).forEach(c => { if (byId[c]) rel.push(['Ребёнок', byId[c].full_name]); });
  const src = (p.sources||[]).map(s => {
    const r = s.ref;
    return /^https?:/.test(r) ? `<a href="${r}" target="_blank">${s.type}: ${r}</a>` : `${s.type}: ${r}`;
  }).join('<br>');
  document.getElementById('mBody').innerHTML = `
    <dl>
      <dt>Даты</dt><dd>${p.birth.date||'?'} — ${p.death.date||''}</dd>
      <dt>Место рожд.</dt><dd>${p.birth.place||'—'}</dd>
      <dt>Категория</dt><dd>${CAT_LABEL[p.category]||p.category}</dd>
      <dt>Родство</dt><dd>${p.relation_to_direct_line||'—'}</dd>
      <dt>Сословие</dt><dd>${p.social_estate||'—'}</dd>
      <dt>Занятие</dt><dd>${p.occupation||'—'}</dd>
      ${rel.map(r=>`<dt>${r[0]}</dt><dd>${r[1]}</dd>`).join('')}
      <dt>Примечание</dt><dd>${p.notes||'—'}</dd>
      <dt>Источники</dt><dd>${src||'—'}</dd>
    </dl>`;
  document.getElementById('modal').classList.add('open');
}
function closeModal(){ document.getElementById('modal').classList.remove('open'); }
document.getElementById('modal').addEventListener('click', e => { if (e.target.id === 'modal') closeModal(); });

document.getElementById('stats').textContent = DATA.length + ' персон · ' + DATA.filter(p=>p.category==='direct').length + ' в прямой линии';
setDirect(true);
</script>
</body>
</html>
"""

html = html.replace("__DATA__", data_js)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("Сгенерирован:", OUT, len(persons), "персон")
