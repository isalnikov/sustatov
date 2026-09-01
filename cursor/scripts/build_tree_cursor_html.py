#!/usr/bin/env python3
"""Generate cursor/tree_cursor.html from koshelikha_persons.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERSONS_JSON = ROOT / "koshelikha_persons.json"
OUTPUT = ROOT / "tree_cursor.html"


def person_name(p: dict) -> str:
    ident = p.get("identification", {})
    if ident.get("displayName"):
        return ident["displayName"]
    parts = [
        ident.get("givenName"),
        ident.get("patronymic"),
        (ident.get("surname") or {}).get("primary"),
    ]
    return " ".join(x for x in parts if x) or p.get("id", "?")


def date_val(block: dict | None) -> str | None:
    if not block:
        return None
    d = block.get("date") or {}
    return d.get("value")


def to_graph_node(p: dict) -> dict:
    ident = p.get("identification", {})
    rel = p.get("relationships", {})
    lc = p.get("lifeCycle", {})
    place = lc.get("birth", {}).get("place", {}) or {}
    settlement = place.get("settlement") or place.get("modernName") or ""

    parent_ids = [x for x in [
        rel.get("parents", {}).get("fatherId"),
        rel.get("parents", {}).get("motherId"),
    ] if x]

    child_ids = [c["id"] for c in rel.get("children", []) if c.get("id")]
    spouse_ids = list(rel.get("spouses") or [])
    sibs = rel.get("siblings") or {}
    sibling_ids = []
    for key in ("full", "halfByFather", "halfByMother", "step"):
        sibling_ids.extend(sibs.get(key) or [])

    refs = []
    for r in p.get("sources", {}).get("references") or []:
        if r.get("reference"):
            refs.append(r["reference"])
    for vp in p.get("sources", {}).get("vgdPosts") or []:
        if vp.get("url"):
            refs.append(vp["url"])

    status = (p.get("meta") or {}).get("researchStatus") or "needs_verification"
    if status in ("confirmed", "reliable"):
        status = "confirmed"
    elif status in ("probable", "needs_verification"):
        status = "probable"
    elif status in ("hypothesis", "not_found"):
        status = "hypothesis" if status == "hypothesis" else "notfound"

    conf = p.get("sources", {}).get("overallConfidence", "")
    if conf == "reliable":
        status = "confirmed"
    elif conf == "hypothesis":
        status = "hypothesis"

    role = p.get("role") or "unknown"
    if role == "collateral":
        role = "side"

    surn = (ident.get("surname") or {}).get("primary") or ""
    is_sustatov = surn.startswith("Сустат")

    return {
        "id": p["id"],
        "name": person_name(p),
        "born": date_val(lc.get("birth")),
        "died": date_val(lc.get("death")),
        "place": settlement,
        "sex": p.get("sex") or "U",
        "surn": surn,
        "isSustatov": is_sustatov,
        "parentIds": parent_ids,
        "spouseIds": spouse_ids,
        "childIds": child_ids,
        "siblingIds": sibling_ids,
        "role": role,
        "status": status,
        "gedcomId": p.get("gedcomId"),
        "notes": (p.get("media") or {}).get("notes") or (p.get("media") or {}).get("biography") or "",
        "sources": refs[:8],
    }


HTML_HEAD = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Кошелиха — интерактивный граф персон</title>
<style>
:root {
  --bg: #0b0f14; --surface: #151c27; --surface2: #1c2636; --border: #2a3749;
  --text: #e8eef6; --muted: #8fa3bc;
  --direct: #3b82f6; --side: #10b981; --inlaw: #a78bfa; --unknown: #64748b;
  --confirmed: #22c55e; --probable: #eab308; --hypothesis: #f97316;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); }
header { padding: 1rem 1.5rem; background: linear-gradient(120deg,#1a3a5c 0%,#0b0f14 70%); border-bottom: 1px solid var(--border); }
header h1 { margin: 0 0 .2rem; font-size: 1.35rem; }
header p { margin: 0; color: var(--muted); font-size: .88rem; }
.layout { display: grid; grid-template-columns: 1fr 340px; grid-template-rows: auto 1fr; min-height: calc(100vh - 72px); }
.toolbar { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: .6rem; padding: .75rem 1.5rem; background: var(--surface); border-bottom: 1px solid var(--border); align-items: center; }
.toolbar input, .toolbar select, .toolbar button {
  background: var(--surface2); border: 1px solid var(--border); color: var(--text);
  padding: .4rem .65rem; border-radius: 8px; font-size: .85rem;
}
.toolbar button { cursor: pointer; }
.toolbar button:hover { border-color: var(--direct); }
#graph-wrap { position: relative; overflow: hidden; background: radial-gradient(ellipse at center,#151c27 0%,#0b0f14 100%); }
#graph-canvas { width: 100%; height: 100%; display: block; cursor: grab; }
#graph-canvas:active { cursor: grabbing; }
aside { border-left: 1px solid var(--border); background: var(--surface); overflow: auto; padding: 1rem; }
aside h2 { margin: 0 0 .75rem; font-size: 1rem; }
#detail-empty { color: var(--muted); font-size: .9rem; }
#detail { display: none; }
#detail.visible { display: block; }
#detail h3 { margin: 0 0 .5rem; font-size: 1.05rem; line-height: 1.3; }
#detail .badges { display: flex; flex-wrap: wrap; gap: .35rem; margin-bottom: .75rem; }
.badge { font-size: .68rem; padding: .15rem .45rem; border-radius: 4px; text-transform: uppercase; letter-spacing: .03em; }
.badge.direct { background: rgba(59,130,246,.22); color: #93c5fd; }
.badge.side { background: rgba(16,185,129,.22); color: #6ee7b7; }
.badge.inlaw { background: rgba(167,139,250,.22); color: #c4b5fd; }
.badge.sustatov { background: rgba(245,158,11,.2); color: #fcd34d; }
.badge.relative { background: rgba(100,116,139,.25); color: #cbd5e1; }
#detail dl { display: grid; grid-template-columns: 88px 1fr; gap: .3rem .6rem; margin: 0; font-size: .84rem; }
#detail dt { color: var(--muted); }
#detail dd { margin: 0; }
#detail a { color: #60a5fa; word-break: break-all; }
.stats { display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: .75rem; }
.stat { background: var(--surface2); border: 1px solid var(--border); border-radius: 8px; padding: .35rem .65rem; font-size: .78rem; }
.stat b { font-size: 1.1rem; display: block; }
.legend { font-size: .78rem; color: var(--muted); margin-bottom: .5rem; }
.legend span { display: inline-flex; align-items: center; gap: .3rem; margin-right: .75rem; }
.edge-line { display: inline-block; width: 24px; height: 3px; border-radius: 2px; vertical-align: middle; }
.edge-parent { background: #60a5fa; }
.edge-spouse { border-top: 2px dashed #c084fc; height: 0; width: 24px; }
.edge-sibling { border-top: 2px dashed #34d399; height: 0; width: 24px; }
#tooltip { position: absolute; pointer-events: none; background: #0f172a; border: 1px solid var(--border); padding: .35rem .55rem; border-radius: 6px; font-size: .76rem; display: none; z-index: 10; max-width: 260px; }
#edge-info { font-size: .78rem; color: var(--muted); margin-top: .5rem; padding-top: .5rem; border-top: 1px solid var(--border); }
.hidden-node { opacity: 0.12; pointer-events: none; }
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; grid-template-rows: auto 55vh auto; }
  aside { border-left: none; border-top: 1px solid var(--border); max-height: 40vh; }
}
</style>
</head>
<body>
<header>
  <h1>Кошелиха — граф персон</h1>
  <p>Сустатовы и родственники · VGD №86148 · __PERSON_COUNT__ персон · перетаскивание, зум колёсиком, клик — карточка</p>
</header>
<div class="layout">
  <div class="toolbar">
    <input type="search" id="search" placeholder="Поиск ФИО…" aria-label="Поиск">
    <select id="filter-surn"><option value="">Все фамилии</option><option value="sustatov">Только Сустатовы</option><option value="relative">Родственники</option></select>
    <select id="filter-role"><option value="">Все роли</option><option value="direct">Прямая</option><option value="side">Боковая</option><option value="inlaw">По браку</option></select>
    <select id="filter-edge"><option value="all">Все рёбра</option><option value="parent">Только родители</option><option value="spouse">Только браки</option><option value="sibling">Только братья/сёстры</option></select>
    <select id="filter-focus"><option value="">Весь граф</option><option value="direct">Подграф: прямая линия</option><option value="sust-gv-1954">От Григория (1954)</option><option value="sust-vg-1930">От Василия (1930)</option><option value="sust-ni-1719">От Никиты (~1719)</option></select>
    <button type="button" id="btn-reset">Сброс вида</button>
    <button type="button" id="btn-fit">Вписать в экран</button>
  </div>
  <div id="graph-wrap">
    <canvas id="graph-canvas"></canvas>
    <div id="tooltip"></div>
  </div>
  <aside>
    <div class="stats" id="stats"></div>
    <div class="legend">
      <span><i class="edge-line edge-parent"></i> родитель→ребёнок</span>
      <span><i class="edge-line edge-spouse"></i> брак</span>
      <span><i class="edge-line edge-sibling"></i> sibling</span>
    </div>
    <h2>Карточка</h2>
    <div id="detail-empty">Кликните на узел графа</div>
    <div id="detail"></div>
    <div id="edge-info"></div>
  </aside>
</div>
<script>
const NODES = __NODES_JSON__;
const COLLECTION = __COLLECTION_JSON__;
const byId = Object.fromEntries(NODES.map(n => [n.id, n]));

function dates(n) {
  const b = n.born || '?';
  const d = n.died || '—';
  return `${b} — ${d}`;
}

function names(ids) {
  return (ids || []).map(i => byId[i]?.name || i).filter(Boolean).join(', ') || '—';
}

function buildEdges(nodeList, edgeFilter) {
  const ids = new Set(nodeList.map(n => n.id));
  const edges = [];
  const seen = new Set();
  const add = (a, b, type) => {
    if (!ids.has(a) || !ids.has(b)) return;
    const k = [a,b].sort().join('|') + type;
    if (seen.has(k)) return;
    seen.add(k);
    edges.push({ from: a, to: b, type });
  };
  nodeList.forEach(n => {
    (n.parentIds||[]).forEach(p => add(p, n.id, 'parent'));
    (n.spouseIds||[]).forEach(s => add(n.id, s, 'spouse'));
    (n.childIds||[]).forEach(c => add(n.id, c, 'parent'));
    (n.siblingIds||[]).forEach(s => add(n.id, s, 'sibling'));
    // implicit siblings via shared parent
    (n.parentIds||[]).forEach(pid => {
      nodeList.filter(x => x.id !== n.id && (x.parentIds||[]).includes(pid))
        .forEach(sib => add(n.id, sib.id, 'sibling'));
    });
  });
  if (edgeFilter && edgeFilter !== 'all')
    return edges.filter(e => e.type === edgeFilter);
  return edges;
}

function getFilteredNodes() {
  const q = (document.getElementById('search').value || '').toLowerCase().trim();
  const surn = document.getElementById('filter-surn').value;
  const role = document.getElementById('filter-role').value;
  const focus = document.getElementById('filter-focus').value;
  let list = NODES.slice();
  if (q) list = list.filter(n => n.name.toLowerCase().includes(q) || n.id.toLowerCase().includes(q));
  if (surn === 'sustatov') list = list.filter(n => n.isSustatov);
  if (surn === 'relative') list = list.filter(n => !n.isSustatov);
  if (role) list = list.filter(n => n.role === role);
  if (focus === 'direct') list = list.filter(n => n.role === 'direct');
  if (focus && byId[focus]) {
    const keep = new Set();
    const walk = (id, depth) => {
      if (!id || !byId[id] || keep.has(id) || depth > 20) return;
      keep.add(id);
      const n = byId[id];
      [...(n.parentIds||[]), ...(n.childIds||[]), ...(n.spouseIds||[]), ...(n.siblingIds||[])].forEach(x => walk(x, depth+1));
    };
    walk(focus, 0);
    list = list.filter(n => keep.has(n.id));
  }
  return list;
}

function renderStats(list, edges) {
  document.getElementById('stats').innerHTML = `
    <div class="stat"><b>${list.length}</b>узлов</div>
    <div class="stat"><b>${edges.length}</b>рёбер</div>
    <div class="stat"><b>${list.filter(n=>n.isSustatov).length}</b>Сустатовы</div>
    <div class="stat"><b>${list.filter(n=>n.role==='direct').length}</b>прямая</div>`;
}

function showDetail(id) {
  const n = byId[id];
  const empty = document.getElementById('detail-empty');
  const el = document.getElementById('detail');
  if (!n) { el.classList.remove('visible'); empty.style.display = 'block'; return; }
  empty.style.display = 'none';
  el.classList.add('visible');
  const roleLabel = {direct:'прямая',side:'боковая',inlaw:'по браку',unknown:'—'}[n.role] || n.role;
  const src = (n.sources||[]).map(s => `<a href="${s}" target="_blank" rel="noopener">${s.replace(/https:\\/\\//,'')}</a>`).join('<br>') || '—';
  el.innerHTML = `
    <h3>${n.name}</h3>
    <div class="badges">
      <span class="badge ${n.isSustatov?'sustatov':'relative'}">${n.isSustatov?'Сустатов':'родня'}</span>
      <span class="badge ${n.role}">${roleLabel}</span>
      <span class="badge">${n.status}</span>
    </div>
    <dl>
      <dt>ID</dt><dd><code>${n.id}</code>${n.gedcomId ? ' · '+n.gedcomId : ''}</dd>
      <dt>Даты</dt><dd>${dates(n)}</dd>
      <dt>Место</dt><dd>${n.place || '—'}</dd>
      <dt>Родители</dt><dd>${names(n.parentIds)}</dd>
      <dt>Супруг(и)</dt><dd>${names(n.spouseIds)}</dd>
      <dt>Дети</dt><dd>${names(n.childIds)}</dd>
      <dt>Братья/сёстры</dt><dd>${names(n.siblingIds)}</dd>
      <dt>Заметки</dt><dd>${n.notes || '—'}</dd>
      <dt>Источники</dt><dd>${src}</dd>
    </dl>`;
}

let graph = null;

function initGraph() {
  const canvas = document.getElementById('graph-canvas');
  const wrap = document.getElementById('graph-wrap');
  const tooltip = document.getElementById('tooltip');
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  let W, H;
  const resize = () => {
    W = wrap.clientWidth; H = wrap.clientHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  resize();

  const nodeList = getFilteredNodes();
  const edgeFilter = document.getElementById('filter-edge').value;
  const edges = buildEdges(nodeList, edgeFilter);
  renderStats(nodeList, edges);

  const simNodes = nodeList.map((n, i) => ({
    id: n.id, data: n,
    x: W/2 + Math.cos(i / Math.max(nodeList.length,1) * Math.PI * 2) * Math.min(W,H) * 0.32,
    y: H/2 + Math.sin(i / Math.max(nodeList.length,1) * Math.PI * 2) * Math.min(W,H) * 0.32,
    vx: 0, vy: 0,
  }));
  const simMap = Object.fromEntries(simNodes.map(n => [n.id, n]));
  const simEdges = edges.filter(e => simMap[e.from] && simMap[e.to]);

  graph = {
    canvas, ctx, W, H, simNodes, simEdges, simMap,
    panX: graph?.panX ?? 0, panY: graph?.panY ?? 0, zoom: graph?.zoom ?? 1,
    selected: graph?.selected ?? null, dragging: null, dragOff: {x:0,y:0}, panStart: {x:0,y:0},
    hoverEdge: null,
  };

  const roleColor = (n) => {
    if (n.isSustatov) {
      return ({direct:'#3b82f6',side:'#10b981',inlaw:'#f59e0b',unknown:'#64748b'}[n.role] || '#3b82f6');
    }
    return ({direct:'#6366f1',side:'#14b8a6',inlaw:'#c084fc',unknown:'#475569'}[n.role] || '#475569');
  };

  function step() {
    const rep = 1200, spring = 0.028, damp = 0.86, center = 0.0015;
    simNodes.forEach(a => {
      simNodes.forEach(b => {
        if (a.id >= b.id) return;
        let dx = a.x - b.x, dy = a.y - b.y;
        let d2 = dx*dx + dy*dy + 0.01;
        let f = rep / d2;
        a.vx += dx * f; a.vy += dy * f;
        b.vx -= dx * f; b.vy -= dy * f;
      });
    });
    simEdges.forEach(e => {
      const a = simMap[e.from], b = simMap[e.to];
      let dx = b.x - a.x, dy = b.y - a.y;
      let d = Math.hypot(dx, dy) || 1;
      let rest = e.type === 'spouse' ? 85 : e.type === 'sibling' ? 105 : 125;
      let f = (d - rest) * spring;
      a.vx += dx/d*f; a.vy += dy/d*f;
      b.vx -= dx/d*f; b.vy -= dy/d*f;
    });
    simNodes.forEach(n => {
      n.vx += (W/2 - n.x) * center;
      n.vy += (H/2 - n.y) * center;
      n.vx *= damp; n.vy *= damp;
      n.x += n.vx; n.y += n.vy;
    });
  }

  function draw() {
    const { panX, panY, zoom, selected, hoverEdge } = graph;
    ctx.clearRect(0, 0, W, H);
    ctx.save();
    ctx.translate(panX, panY);
    ctx.scale(zoom, zoom);
    simEdges.forEach(e => {
      const a = simMap[e.from], b = simMap[e.to];
      const hl = hoverEdge && hoverEdge.from === e.from && hoverEdge.to === e.to;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      if (e.type === 'parent') {
        ctx.strokeStyle = hl ? '#93c5fd' : 'rgba(96,165,250,.45)';
        ctx.lineWidth = hl ? 2.5 : 1.8;
        ctx.setLineDash([]);
        // arrow toward child (to)
        const ang = Math.atan2(b.y - a.y, b.x - a.x);
        const ax = b.x - Math.cos(ang)*14, ay = b.y - Math.sin(ang)*14;
        ctx.lineTo(ax, ay);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(b.x, b.y);
        ctx.lineTo(ax - Math.cos(ang-0.4)*8, ay - Math.sin(ang-0.4)*8);
        ctx.lineTo(ax - Math.cos(ang+0.4)*8, ay - Math.sin(ang+0.4)*8);
        ctx.closePath();
        ctx.fillStyle = ctx.strokeStyle;
        ctx.fill();
      } else if (e.type === 'spouse') {
        ctx.strokeStyle = hl ? '#d8b4fe' : 'rgba(192,132,252,.55)';
        ctx.lineWidth = hl ? 2 : 1.4;
        ctx.setLineDash([7,5]);
        ctx.stroke();
      } else {
        ctx.strokeStyle = hl ? '#6ee7b7' : 'rgba(52,211,153,.4)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4,6]);
        ctx.stroke();
      }
    });
    ctx.setLineDash([]);
    simNodes.forEach(n => {
      const sel = n.id === selected;
      const r = sel ? 13 : (n.data.isSustatov ? 11 : 9);
      ctx.beginPath();
      ctx.fillStyle = roleColor(n.data);
      ctx.arc(n.x, n.y, r, 0, Math.PI*2);
      ctx.fill();
      if (sel) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.5; ctx.stroke(); }
      ctx.fillStyle = '#e8eef6';
      ctx.font = (n.data.isSustatov ? 'bold ' : '') + '10px Segoe UI,sans-serif';
      ctx.textAlign = 'center';
      const label = n.data.name.length > 26 ? n.data.name.slice(0,24)+'…' : n.data.name;
      ctx.fillText(label, n.x, n.y + r + 13);
    });
    ctx.restore();
  }

  if (graph._raf) cancelAnimationFrame(graph._raf);
  (function loop() { step(); draw(); graph._raf = requestAnimationFrame(loop); })();

  function screenToWorld(sx, sy) {
    return { x: (sx - graph.panX) / graph.zoom, y: (sy - graph.panY) / graph.zoom };
  }

  function hitEdge(w) {
    let best = null, bestD = 12;
    simEdges.forEach(e => {
      const a = simMap[e.from], b = simMap[e.to];
      const dx = b.x - a.x, dy = b.y - a.y;
      const len2 = dx*dx + dy*dy || 1;
      let t = ((w.x-a.x)*dx + (w.y-a.y)*dy) / len2;
      t = Math.max(0, Math.min(1, t));
      const px = a.x + t*dx, py = a.y + t*dy;
      const d = Math.hypot(w.x - px, w.y - py);
      if (d < bestD) { bestD = d; best = e; }
    });
    return best;
  }

  canvas.onmousedown = ev => {
    const rect = canvas.getBoundingClientRect();
    const w = screenToWorld(ev.clientX - rect.left, ev.clientY - rect.top);
    const hit = simNodes.find(n => Math.hypot(n.x - w.x, n.y - w.y) < 14);
    if (hit) {
      graph.selected = hit.id;
      graph.dragging = hit;
      graph.dragOff = { x: w.x - hit.x, y: w.y - hit.y };
      showDetail(hit.id);
      document.getElementById('edge-info').textContent = '';
    } else {
      const e = hitEdge(w);
      if (e) {
        const labels = {parent:'родитель → ребёнок', spouse:'брак', sibling:'брат/сестра'};
        document.getElementById('edge-info').textContent =
          labels[e.type] + ': ' + (byId[e.from]?.name||e.from) + ' ↔ ' + (byId[e.to]?.name||e.to);
      } else {
        graph.dragging = 'pan';
        graph.panStart = { x: ev.clientX - graph.panX, y: ev.clientY - graph.panY };
      }
    }
  };
  window.onmousemove = ev => {
    const rect = canvas.getBoundingClientRect();
    const w = screenToWorld(ev.clientX - rect.left, ev.clientY - rect.top);
    if (graph.dragging === 'pan') {
      graph.panX = ev.clientX - graph.panStart.x;
      graph.panY = ev.clientY - graph.panStart.y;
      return;
    }
    if (graph.dragging && graph.dragging !== 'pan') {
      graph.dragging.x = w.x - graph.dragOff.x;
      graph.dragging.y = w.y - graph.dragOff.y;
      graph.dragging.vx = graph.dragging.vy = 0;
      return;
    }
    const hit = simNodes.find(n => Math.hypot(n.x - w.x, n.y - w.y) < 14);
    if (hit) {
      tooltip.style.display = 'block';
      tooltip.style.left = (ev.clientX - rect.left + 12) + 'px';
      tooltip.style.top = (ev.clientY - rect.top + 12) + 'px';
      tooltip.textContent = hit.data.name + ' · ' + dates(hit.data);
      graph.hoverEdge = null;
    } else {
      graph.hoverEdge = hitEdge(w);
      tooltip.style.display = graph.hoverEdge ? 'block' : 'none';
      if (graph.hoverEdge) {
        tooltip.textContent = graph.hoverEdge.type + ': ' + (byId[graph.hoverEdge.from]?.name||'');
        tooltip.style.left = (ev.clientX - rect.left + 12) + 'px';
        tooltip.style.top = (ev.clientY - rect.top + 12) + 'px';
      }
    }
  };
  window.onmouseup = () => { graph.dragging = null; };
  canvas.onwheel = ev => {
    ev.preventDefault();
    graph.zoom = Math.min(3, Math.max(0.25, graph.zoom * (ev.deltaY > 0 ? 0.92 : 1.08)));
  };
}

document.getElementById('btn-reset').onclick = () => {
  if (graph) { graph.panX = graph.panY = 0; graph.zoom = 1; }
  initGraph();
};
document.getElementById('btn-fit').onclick = () => {
  if (!graph || !graph.simNodes.length) return;
  const xs = graph.simNodes.map(n => n.x), ys = graph.simNodes.map(n => n.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const pw = maxX - minX + 80, ph = maxY - minY + 80;
  graph.zoom = Math.min(graph.W / pw, graph.H / ph, 1.2);
  graph.panX = graph.W/2 - (minX + maxX)/2 * graph.zoom;
  graph.panY = graph.H/2 - (minY + maxY)/2 * graph.zoom;
};
['search','filter-surn','filter-role','filter-edge','filter-focus'].forEach(id => {
  document.getElementById(id).addEventListener('input', initGraph);
  document.getElementById(id).addEventListener('change', initGraph);
});
window.addEventListener('resize', initGraph);
initGraph();
</script>
</body>
</html>
"""


def main() -> None:
    data = json.loads(PERSONS_JSON.read_text(encoding="utf-8"))
    persons = data.get("persons", [])
    nodes = [to_graph_node(p) for p in persons]
    collection = {
        "title": data.get("collection", {}).get("title"),
        "personCount": len(nodes),
        "primarySource": data.get("collection", {}).get("primarySource"),
    }

    html = HTML_HEAD.replace("__PERSON_COUNT__", str(len(nodes)))
    html = html.replace("__NODES_JSON__", json.dumps(nodes, ensure_ascii=False))
    html = html.replace("__COLLECTION_JSON__", json.dumps(collection, ensure_ascii=False))

    OUTPUT.write_text(html, encoding="utf-8")
    edge_count = 0
    ids = {n["id"] for n in nodes}
    for n in nodes:
        for p in n["parentIds"]:
            if p in ids:
                edge_count += 1
        for s in n["spouseIds"]:
            if s in ids:
                edge_count += 1
        for c in n["childIds"]:
            if c in ids:
                edge_count += 1
    print(f"Wrote {OUTPUT}: {len(nodes)} nodes, ~{edge_count} directed edges")


if __name__ == "__main__":
    main()
