#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Парсит GEDCOM и генерирует all_ds.html — интерактивный граф родословной."""
import json, os

GED = "/home/igor/cursorwork/sustatov/cursor/MyHeritage_GEDCOM_749073761_686021731_1_2025-02-02.ged"
OUT = "/home/igor/cursorwork/sustatov/opencode/all_ds.html"

def parse_gedcom(path):
    lines = open(path, encoding="utf-8-sig", errors="replace").read().splitlines()
    indi, fam = {}, {}
    cur = None
    ctx = None  # 'birt' / 'deat'
    for ln in lines:
        if not ln.strip():
            continue
        toks = ln.split(None, 2)
        lvl = int(toks[0])
        tag = toks[1] if len(toks) > 1 else ""
        val = toks[2] if len(toks) > 2 else ""
        if lvl == 0:
            if tag.startswith("@") and val == "INDI":
                pid = tag.strip("@")
                indi[pid] = {"id": pid, "name": "", "sex": "", "birt": "", "bplac": "",
                             "deat": "", "dplac": "", "occu": "", "fams": [], "famc": []}
                cur = ("I", pid); ctx = None
            elif tag.startswith("@") and val == "FAM":
                fid = tag.strip("@")
                fam[fid] = {"id": fid, "husb": None, "wife": None, "chil": []}
                cur = ("F", fid); ctx = None
            else:
                cur = None; ctx = None
            continue
        if cur is None:
            continue
        typ, rid = cur
        if typ == "I":
            if tag == "NAME": indi[rid]["name"] = val
            elif tag == "SEX": indi[rid]["sex"] = val
            elif tag == "BIRT": ctx = "birt"
            elif tag == "DEAT": ctx = "deat"
            elif tag == "DATE":
                if ctx == "birt": indi[rid]["birt"] = val
                elif ctx == "deat": indi[rid]["deat"] = val
            elif tag == "PLAC":
                if ctx == "birt": indi[rid]["bplac"] = val
                elif ctx == "deat": indi[rid]["dplac"] = val
            elif tag == "OCCU": indi[rid]["occu"] = val
            elif tag == "FAMS": indi[rid]["fams"].append(val.strip("@"))
            elif tag == "FAMC": indi[rid]["famc"].append(val.strip("@"))
        elif typ == "F":
            if tag == "HUSB": fam[rid]["husb"] = val.strip("@")
            elif tag == "WIFE": fam[rid]["wife"] = val.strip("@")
            elif tag == "CHIL": fam[rid]["chil"].append(val.strip("@"))
    return indi, fam

indi, fam = parse_gedcom(GED)

def split_name(nm):
    parts = nm.split("/")
    given = parts[0].strip() if parts else ""
    surname = parts[1].strip() if len(parts) > 1 else ""
    return given, surname

nodes = []
for pid, d in indi.items():
    given, surname = split_name(d["name"])
    full = (given + (" " + surname if surname else "")).strip() or "(без имени)"
    nodes.append({"id": pid, "given": given, "surname": surname, "full": full,
                  "sex": d["sex"], "birt": d["birt"], "bplac": d["bplac"],
                  "deat": d["deat"], "dplac": d["dplac"], "occu": d["occu"],
                  "fams": d["fams"], "famc": d["famc"]})

# parent (father) via FAMC
parentOf = {}
for pid, d in indi.items():
    for fc in d["famc"]:
        if fc in fam:
            f = fam[fc]
            if f["husb"] and f["husb"] != pid:
                parentOf[pid] = f["husb"]; break
            elif f["wife"] and f["wife"] != pid:
                parentOf[pid] = f["wife"]; break

childrenOf = {}
for pid, p in parentOf.items():
    childrenOf.setdefault(p, []).append(pid)

spouseOf = {}
for fid, f in fam.items():
    if f["husb"] and f["wife"]:
        spouseOf.setdefault(f["husb"], []).append(f["wife"])
        spouseOf.setdefault(f["wife"], []).append(f["husb"])

byid = {n["id"]: n for n in nodes}
roots = [n["id"] for n in nodes if n["id"] not in parentOf]

slot = 0
def walk(pid, depth):
    global slot
    n = byid[pid]
    n["_depth"] = depth
    kids = childrenOf.get(pid, [])
    if not kids:
        n["_slot"] = n["_min"] = n["_max"] = slot
        slot += 1
    else:
        mn, mx = 1e9, -1
        for c in kids:
            walk(c, depth + 1)
            mn = min(mn, byid[c]["_min"]); mx = max(mx, byid[c]["_max"])
        n["_min"] = mn; n["_max"] = mx; n["_slot"] = (mn + mx) / 2

for r in roots:
    slot += 1.2
    walk(r, 0)

iso = [n["id"] for n in nodes if "_slot" not in byid[n["id"]]]
for i, pid in enumerate(iso):
    byid[pid]["_depth"] = 0
    byid[pid]["_slot"] = slot + i
if iso: slot += len(iso)

for pid in list(nodes):
    for s in spouseOf.get(pid["id"], []):
        if s in byid and "_slot" not in byid[s]:
            byid[s]["_depth"] = byid[pid["id"]].get("_depth", 0)
            byid[s]["_slot"] = byid[pid["id"]]["_slot"] + 1.05

left = [n["id"] for n in nodes if "_slot" not in byid[n["id"]]]
for i, pid in enumerate(left):
    byid[pid]["_depth"] = 0; byid[pid]["_slot"] = slot + i
if left: slot += len(left)

for n in nodes:
    n["x"] = byid[n["id"]]["_slot"] * 250
    n["y"] = byid[n["id"]]["_depth"] * 88 + 20
    n["depth"] = byid[n["id"]]["_depth"]

maxd = max((n["depth"] for n in nodes), default=0)
W = int((slot + 2) * 250)
H = int((maxd + 1) * 88 + 120)

data = {"nodes": nodes, "parentOf": parentOf, "spouseOf": spouseOf,
        "childrenOf": childrenOf, "W": W, "H": H}
data_js = json.dumps(data, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Родословная (GEDCOM) — граф</title>
<style>
:root{--bg:#0d1117;--panel:#161b22;--line:#30363d;--text:#e6edf3;--muted:#8b949e;--male:#58a6ff;--female:#ff7b72;--sustatov:#3fb950}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column;overflow:hidden}
header{padding:12px 20px;border-bottom:1px solid var(--line);background:var(--panel);display:flex;flex-wrap:wrap;gap:12px;align-items:center}
header h1{font-size:1.15rem;font-weight:600}
header .sub{color:var(--muted);font-size:.8rem}
.toolbar{display:flex;flex-wrap:wrap;gap:8px;margin-left:auto;align-items:center}
.toolbar input{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:6px 12px;color:var(--text);width:200px;font-size:.85rem}
.toolbar button{background:var(--panel);border:1px solid var(--line);color:var(--text);padding:6px 12px;border-radius:8px;cursor:pointer;font-size:.82rem}
.toolbar button:hover{background:var(--line)}
.toolbar button.active{background:var(--sustatov);color:#0d1117;border-color:var(--sustatov)}
#stage{flex:1;position:relative;overflow:hidden;cursor:grab}
#stage.dragging{cursor:grabbing}
.legend{position:absolute;left:12px;bottom:12px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:.72rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:10px;max-width:70%}
.legend span{display:flex;align-items:center;gap:5px}
.legend i{width:11px;height:11px;border-radius:3px;display:inline-block}
.node{cursor:pointer}
.node rect{stroke-width:1.5;transition:filter .15s}
.node:hover rect{filter:brightness(1.15)}
.node.dim{opacity:.12}
.node .nm{font-weight:600;font-size:12px;fill:var(--text)}
.node .dt{font-size:10px;fill:var(--muted)}
.edge{fill:none;stroke:#30363d;stroke-width:1.3}
.edge.marriage{stroke:#7d8590;stroke-dasharray:4 3;stroke-width:1.1}
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
</style>
</head>
<body>
<header>
  <h1>Родословная <span style="color:var(--muted);font-weight:400">— граф (GEDCOM)</span></h1>
  <span class="sub" id="stats"></span>
  <div class="toolbar">
    <input id="q" placeholder="Поиск…">
    <button id="bIn">+</button><button id="bOut">−</button><button id="bReset">Сброс</button>
    <button id="bSust" class="active">Только Сустатовы</button><button id="bAll">Все</button>
  </div>
</header>
<div id="stage"><svg id="svg"></svg>
<div class="legend">
  <span><i style="background:#58a6ff"></i> муж.</span>
  <span><i style="background:#ff7b72"></i> жен.</span>
  <span><i style="background:#3fb950"></i> Сустатовы</span>
  <span>━ брак · ── ребёнок</span>
</div></div>
<div class="modal" id="modal"><div class="box"><div class="head"><h2 id="mTitle"></h2><button class="close" onclick="closeModal()">×</button></div><div class="body" id="mBody"></div></div></div>
<script>
const D = __DATA__;
const byid = {};
D.nodes.forEach(n => byid[n.id] = n);
const NODES = D.nodes, parentOf = D.parentOf, spouseOf = D.spouseOf;
const CW = 250, RH = 64;

const svg = document.getElementById('svg');
svg.setAttribute('width', D.W); svg.setAttribute('height', D.H);
const g = document.createElementNS('http://www.w3.org/2000/svg','g'); g.id='vp'; svg.appendChild(g);
const eG = document.createElementNS('http://www.w3.org/2000/svg','g'); g.appendChild(eG);
const nG = document.createElementNS('http://www.w3.org/2000/svg','g'); g.appendChild(nG);

const isSust = id => byid[id].surname === 'Сустатов';

Object.keys(parentOf).forEach(cid => {
  const p = parentOf[cid];
  if (!byid[p] || !byid[cid]) return;
  const l = document.createElementNS('http://www.w3.org/2000/svg','path');
  const x1 = byid[p].x + (CW-40)/2, y1 = byid[p].y + RH, x2 = byid[cid].x, y2 = byid[cid].y;
  l.setAttribute('d', `M${x1},${y1} C${x1},${(y1+y2)/2} ${x2},${(y1+y2)/2} ${x2},${y2}`);
  l.setAttribute('class','edge');
  eG.appendChild(l);
});
Object.keys(spouseOf).forEach(a => {
  spouseOf[a].forEach(b => {
    if (!byid[b] || a > b) return;
    const l = document.createElementNS('http://www.w3.org/2000/svg','path');
    const x1 = byid[a].x + (CW-40)/2, x2 = byid[b].x + (CW-40)/2, y1 = byid[a].y + RH/2, y2 = byid[b].y + RH/2;
    l.setAttribute('d', `M${x1},${y1} C${(x1+x2)/2},${y1} ${(x1+x2)/2},${y2} ${x2},${y2}`);
    l.setAttribute('class','edge marriage');
    eG.appendChild(l);
  });
});

const boxW = CW - 40;
NODES.forEach(n => {
  const ng = document.createElementNS('http://www.w3.org/2000/svg','g');
  ng.setAttribute('class','node'); ng.setAttribute('data-id', n.id);
  ng.setAttribute('transform', `translate(${n.x - boxW/2 + 20},${n.y})`);
  const color = n.surname === 'Сустатов' ? '#3fb950' : (n.sex === 'F' ? '#ff7b72' : '#58a6ff');
  const rect = document.createElementNS('http://www.w3.org/2000/svg','rect');
  rect.setAttribute('width', boxW); rect.setAttribute('height', RH); rect.setAttribute('rx',9); rect.setAttribute('ry',9);
  rect.setAttribute('fill', color + '22'); rect.setAttribute('stroke', color);
  if (n.surname === 'Сустатов') rect.setAttribute('stroke-width', 2.5);
  ng.appendChild(rect);
  const nm = document.createElementNS('http://www.w3.org/2000/svg','text');
  nm.setAttribute('x',10); nm.setAttribute('y',18); nm.setAttribute('class','nm');
  nm.textContent = n.full.length > 36 ? n.full.slice(0,36)+'…' : n.full;
  ng.appendChild(nm);
  const dt = document.createElementNS('http://www.w3.org/2000/svg','text');
  dt.setAttribute('x',10); dt.setAttribute('y',34); dt.setAttribute('class','dt');
  dt.textContent = (n.birt||'?') + (n.deat ? ' — ' + n.deat : '');
  ng.appendChild(dt);
  const pl = document.createElementNS('http://www.w3.org/2000/svg','text');
  pl.setAttribute('x',10); pl.setAttribute('y',50); pl.setAttribute('class','dt');
  pl.textContent = ((n.bplac || n.dplac || '') || '').length > 40 ? (n.bplac||n.dplac||'').slice(0,40)+'…' : (n.bplac || n.dplac || '');
  ng.appendChild(pl);
  ng.addEventListener('click', () => openModal(n.id));
  nG.appendChild(ng);
});

let v = {x:40, y:20, k:1};
function apply(){ g.setAttribute('transform', `translate(${v.x},${v.y}) scale(${v.k})`); }
apply();
const stage = document.getElementById('stage');
let pan=false,sx,sy;
stage.addEventListener('mousedown',e=>{pan=true;sx=e.clientX-v.x;sy=e.clientY-v.y;stage.classList.add('dragging');});
window.addEventListener('mousemove',e=>{if(!pan)return;v.x=e.clientX-sx;v.y=e.clientY-sy;apply();});
window.addEventListener('mouseup',()=>{pan=false;stage.classList.remove('dragging');});
stage.addEventListener('wheel',e=>{e.preventDefault();v.k=Math.min(3,Math.max(0.2,v.k*(e.deltaY<0?1.1:0.9)));apply();},{passive:false});
document.getElementById('bIn').onclick=()=>{v.k=Math.min(3,v.k*1.2);apply();};
document.getElementById('bOut').onclick=()=>{v.k=Math.max(0.2,v.k/1.2);apply();};
document.getElementById('bReset').onclick=()=>{v={x:40,y:20,k:1};apply();};

let sustOnly = true;
function setSust(on){
  sustOnly = on;
  document.getElementById('bSust').classList.toggle('active', on);
  document.getElementById('bAll').classList.toggle('active', !on);
  document.querySelectorAll('.node').forEach(el => {
    el.classList.toggle('dim', on && !isSust(el.getAttribute('data-id')));
  });
}
document.getElementById('bSust').onclick=()=>setSust(true);
document.getElementById('bAll').onclick=()=>setSust(false);

document.getElementById('q').oninput=e=>{
  const q=e.target.value.trim().toLowerCase();
  document.querySelectorAll('.node').forEach(el=>{
    const p=byid[el.getAttribute('data-id')];
    el.classList.toggle('dim', q && !(p.full+' '+(p.birt||'')+' '+(p.deat||'')+' '+(p.bplac||'')).toLowerCase().includes(q));
  });
};

function openModal(id){
  const p = byid[id];
  document.getElementById('mTitle').textContent = p.full;
  const rel = [];
  if (parentOf[id] && byid[parentOf[id]]) rel.push(['Родитель', byid[parentOf[id]].full]);
  (spouseOf[id]||[]).forEach(s=>{ if(byid[s]) rel.push(['Супруг(а)', byid[s].full]); });
  (D.childrenOf[id]||[]).forEach(c=>{ if(byid[c]) rel.push(['Ребёнок', byid[c].full]); });
  document.getElementById('mBody').innerHTML = `<dl>
    <dt>Фамилия</dt><dd>${p.surname||'—'}</dd>
    <dt>Пол</dt><dd>${p.sex==='M'?'муж.':p.sex==='F'?'жен.':'—'}</dd>
    <dt>Рождение</dt><dd>${p.birt||'—'}${p.bplac?' · '+p.bplac:''}</dd>
    <dt>Смерть</dt><dd>${p.deat||'—'}${p.dplac?' · '+p.dplac:''}</dd>
    <dt>Занятие</dt><dd>${p.occu||'—'}</dd>
    ${rel.map(r=>`<dt>${r[0]}</dt><dd>${r[1]}</dd>`).join('')}
  </dl>`;
  document.getElementById('modal').classList.add('open');
}
function closeModal(){ document.getElementById('modal').classList.remove('open'); }
document.getElementById('modal').addEventListener('click',e=>{if(e.target.id==='modal')closeModal();});

document.getElementById('stats').textContent = NODES.length + ' персон · ' + NODES.filter(n=>isSust(n.id)).length + ' Сустатовых';
setSust(true);
</script>
</body>
</html>
"""

html = html.replace("__DATA__", data_js)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print("Индивидов (INDI):", len(indi))
print("Семей (FAM):", len(fam))
print("Сустатовых:", sum(1 for n in nodes if n["surname"] == "Сустатов"))
print("Сгенерирован:", OUT, f"({os.path.getsize(OUT)} байт)")
