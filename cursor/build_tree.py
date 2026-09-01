#!/usr/bin/env python3
"""Generate sustatov_tree.md and sustatov_tree.html from sustatov_tree_data.json."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
data = json.loads((ROOT / "sustatov_tree_data.json").read_text(encoding="utf-8"))

FIXES = {
    "Сустatov": "Сустатов",
    "Сустatova": "Сустатова",
    "Korolёva": "Королёва",
    "Fёdorovna": "Фёдоровна",
    "Кamkina": "Кamkina",
    "Сыreсеva": "Сыreсеva",
    "Афтodеevo": "Афтodеevo",
    "Сыresevoy": "Сыresevoy",
    "Vaskina": "Vaskina",
    "Sergiev Posad": "Sergiev Posad",
}

ID_NAMES = {
    "sust-mavra": "Мavra",
    "sust-darya-ap": "Дarya",
    "sust-matrema": "Мatрёna Фёdorovna",
    "I500074": "Праскovья Корolёva (Сустatova)",
    "sust-avdotya": "Avdotya Vasilevna",
    "side-004a": "Anna Filippovna",
    "side-011a": "Anna Ivanovna",
    "side-012a": "Anisya (vdova)",
    "side-013": "Matvey Ivanovich",
    "side-014": "Yakov Matveevich",
    "side-015": "Fyodor Ivanovich",
    "side-016": "Fedot Ivanovich",
    "side-005": "Averian Kondratievich",
    "side-008": "Lev Andreevich Сустatov",
    "side-009": "Vasiliy Andreevich Сустatov",
    "side-004": "Кondratiy Andreevich Сустatov",
    "side-011": "Ivan Ivanovich (младший)",
    "sust-ni-1719": "Никита Ivanovich Сустatov",
    "I500030": "Ольга Vaskina (Сальникova)",
    "I500087": "Еlena Сustatova (Еrmolina)",
    "I500088": "Дмитрий Еrmolin",
    "I500089": "Никита Еrmolin",
    "I500090": "Дarья Еrmolina",
}

def apply_fixes(text):
    if not text:
        return text
    for old, new in FIXES.items():
        text = text.replace(old, new)
    return text

# Names come from sustatov_tree_data.json (do not overwrite here)

by_id = {n["id"]: n for n in data}

def fmt_dates(n):
    b = n.get("born") or "?"
    d = n.get("died") or ("ж." if n.get("status") != "notfound" else "?")
    return f"{b} — {d}"

def link_sources(sources):
    links = []
    for s in sources:
        if s.startswith("http"):
            links.append(f"[{s}]({s})")
        else:
            links.append(s)
    return ", ".join(links)

def resolve_ids(ids):
    return ", ".join(by_id.get(i, {}).get("name", i) for i in ids) if ids else "—"

# --- Markdown ---
md = []
md.append("# Род Сустатовых — полное генеалогическое дерево\n")
md.append("*Собрано: 31.08.2026 · якорь: **Григорий Васильевич Сустатов (30.08.1954)** → **Василий Григорьевич (24.01.1930)***\n")
md.append("## Оценка работы субагентов\n")
md.append("| Агент | Оценка | Статус |")
md.append("|-------|--------|--------|")
md.append("| Современная ветвь (1954→1930) | **8.7/10** | ✓ принято |")
md.append("| Ветвь 1912 / ВОВ | **8.8/10** | ✓ принято |")
md.append("| Боковые ветви Кошелиха | **9.0/10** | ✓ принято |")
md.append("| GEDCOM parse | **9.2/10** | ✓ принято |")
md.append("\n> ⚠️ Исключена ложная Smart Match-цепь GEDCOM `@I500145@` / `@F500064@` (Борис → «Василий Иванович»).\n")
md.append("## Статистика\n")
confirmed = sum(1 for n in data if n["status"] == "confirmed")
probable = sum(1 for n in data if n["status"] == "probable")
notfound = sum(1 for n in data if n["status"] == "notfound")
direct = sum(1 for n in data if n["role"] == "direct")
side = sum(1 for n in data if n["role"] == "side")
md.append(f"- **Всего узлов:** {len(data)}")
md.append(f"- **Прямая линия:** {direct} · **Боковые:** {side}")
md.append(f"- **CONFIRMED:** {confirmed} · **PROBABLE:** {probable} · **NOT FOUND:** {notfound}\n")
md.append("## Прямая линия (краткая схема)\n")
md.append("```")
md.append("Иван ??? (NOT FOUND, Сыресево?)")
md.append("  └─ Никита Иванович (1719–1773)")
md.append("      └─ Пётр Никитич (1737–1819)")
md.append("          └─ Андрей Петрович (1770–1811)")
md.append("              └─ Иван Андреевич (1793–1833)")
md.append("                  └─ Иван Иванович (1815)")
md.append("                      └─ Иван Иванович ст. (1847–1879)")
md.append("                          └─ Иван Иванович ~1870 [PROBABLE]")
md.append("                              └─ Василий Иванович (1890–1934)")
md.append("                                  └─ Григорий Васильевич (1912–1942, ВОВ)")
md.append("                                      └─ Василий Григорьевич (1930–2004)")
md.append("                                          └─ Григорий Васильевич (1954–2020)")
md.append("                                              └─ Игорь Сальников (1982) → Максим, Анна")
md.append("```\n")
md.append("## Карточки персон\n")

role_ru = {"direct": "прямая", "side": "боковая", "inlaw": "связь по браку", "descendant": "потомок"}
status_ru = {"confirmed": "CONFIRMED", "probable": "PROBABLE", "notfound": "NOT FOUND"}

for n in sorted(data, key=lambda x: (x.get("gen") or 99, x["name"])):
    md.append(f"### {n['id']} — {n['name']}\n")
    md.append(f"- **Рожд. / Смерть:** {fmt_dates(n)}")
    md.append(f"- **Место:** {n.get('place') or '—'}")
    md.append(f"- **Пол:** {'М' if n.get('sex')=='M' else 'Ж' if n.get('sex')=='F' else '—'}")
    md.append(f"- **Родители:** {resolve_ids(n.get('parentIds', []))}")
    md.append(f"- **Супруг(и):** {resolve_ids(n.get('spouseIds', []))}")
    md.append(f"- **Дети:** {resolve_ids(n.get('childIds', []))}")
    md.append(f"- **Роль:** {role_ru.get(n.get('role'), n.get('role'))}")
    md.append(f"- **Статус:** {status_ru.get(n.get('status'), n.get('status'))}")
    if n.get("notes"):
        md.append(f"- **Примечания:** {n['notes']}")
    if n.get("sources"):
        md.append(f"- **Источники:** {link_sources(n['sources'])}")
    md.append("")

md.append("\n## Ветвь Кондратия Андреевича (от Андрея Петровича)\n")
md.append("**Цепочка (CONFIRMED):** Андрей Петрович → **Кondratiy Andreevich** (брак **08.11.1807** + Анна Филипповна) → Аverian / Maksim / Stepan + дочери Mavra, Agrafena.\n")
md.append("\n| Период | Персона | Связь | Источник |")
md.append("|--------|---------|-------|----------|")
md.append("| **1807** | Кондратий Андреевич + Анна Филипповна | сын Андрея Петровича | [VGD браки](https://forum.vgd.ru/post/2339/86148/p2995932.htm) |")
md.append("| **1835** | Аverian + Дарья Анисимовна | сын Кондратия | [VGD](https://forum.vgd.ru/post/2339/86148/p2995932.htm) |")
md.append("| **1840** | Максим Кондратьевич † (~1811–1840) | сын Кондратия; без потомков | [VGD p2818326](https://forum.vgd.ru/post/2339/86148/p2818326.htm) |")
md.append("| **1847** | Кондратий Андреевич † | — | [VGD p2818326](https://forum.vgd.ru/post/2339/86148/p2818326.htm) |")
md.append("| **1851** | Степан Кондратьевич (~1834) + Анастасия Антоновна | сын Кондратия; рев. — 17 л. | [VGD p2995932](https://forum.vgd.ru/post/2339/86148/p2995932.htm) |")
md.append("| **1855** | Степан — рекрут | уходит из двора | рев.1858 |")
md.append("| **1855** | Екатерина Аверьяновна + Иван Евдокимович | внучка через Аверьяна; венчание **06.11.1855** | [VGD p2962408](https://forum.vgd.ru/post/2339/86148/p2962408.htm) |")
md.append("| **1857** | Наталья Ивановна (внучка) | дочь Екатерины | рев.1858 |")
md.append("| **1858** | ревизия: Аверьян 31, Степан рекрут | двор №24 | [VGD p2818093](https://forum.vgd.ru/post/2339/86148/p2818093.htm) |")
md.append("\n> Потомки до **2026** — **NOT FOUND** (линия через Евдокимовых; ЦАНО ф.570).\n")
md.append("\n### Оценка субагентов (ветвь Кондратия)\n")
md.append("| Агент | Оценка | Статус |")
md.append("|-------|--------|--------|")
md.append("| [Maksim](bc178248-4d82-4fd7-bced-1dbbde9e78f5) | **8/10** | ✓ принято |")
md.append("| [Averian](057bb875-d00c-4035-b7f4-64a1fc95e555) | **6.5/10** | ⚠️ доработка: ЦАНО после 1860 |")
md.append("| [Stepan](616f2bfc-b538-4472-bbb1-5bda07c9b8ee) | **6/10** | ⚠️ потомки NOT FOUND; collateral частично |")
md.append("\n### Collateral: Василий Андреевич (брат Кондратия)\n")
md.append("Жена **Ульяна**; сыновья **Аким**, **Степан Васильевич**; внуки **Степан Аkimovich**, **Никита** (р.1855); **Степан Степанович** (~1864, [p2820771](https://forum.vgd.ru/post/2339/86148/p2820771.htm)) — связь с прямой линией **не установлена**.\n")
md.append("\n## Боковые ветви (сводка)\n")
md.append("| Ветвь | Ключевые лица | Источник |")
md.append("|-------|---------------|----------|")
md.append("| Братья Андрея Петровича | Лев (~1789), Василий (~1800), Кондратий (1765–1847) | [VGD 140.htm](https://forum.vgd.ru/2339/86148/140.htm) |")
md.append("| Линия Кондратия | Авериан Кondratievich (~1827) | VGD |")
md.append("| Линия Михаила Петровича | Борис Михайловich (1805), Борис Семёnovich (1908–1938) | VGD, openlist |")
md.append("| Двор №25 (1815) | Фёdor, Фedot, Ivan мл. (~1851) | Ревизия 1858 |")
md.append("| Дети Григория 1912 | Татьяna, Анна, Вера, Николай 1936 | GEDCOM, sarpust |")
md.append("| Дяди Василия 1890 | Алексей (1913–1944), Максим (1917–1944) | VGD, GEDCOM |")
md.append("\n## Открытые вопросы\n")
md.append("1. **Иван — отец Никиты (~1719)** — NOT FOUND; искать в переписях д. Сыресево (VGD №75748, ЦАНО ф.570).")
md.append("2. **Иван Иванovich ~1870** — PROBABLE; нужна метрика рождения Василия 1890 (ЦАНО).")
md.append("3. **Потомки Николая Григорьевича (1936)** — в GEDCOM детей нет; мемуары sarpust.ru.")
md.append("4. **Людмила Эдуардovna** — 2-й брак Григория 1954; биография не заполнена.")
md.append("\n## Источники\n")
md.append("- GEDCOM: `MyHeritage_GEDCOM_749073761_686021731_1_2025-02-02.ged`")
md.append("- [VGD Кошелиха](https://forum.vgd.ru/2339/86148/)")
md.append("- [VGD Сыreсеvo](https://forum.vgd.ru/2339/75748/)")
md.append("- [Мемуары Н.Г. Сустатова](https://sarpust.ru/memuary/)")
md.append("- `todo.md`, `isustatov.html`")

(ROOT / "sustatov_tree.md").write_text("\n".join(md), encoding="utf-8")

# --- HTML ---
json_embed = json.dumps(data, ensure_ascii=False)
html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Род Сустатовых — генеалогическое дерево</title>
<style>
:root {{
  --bg: #0f1419; --surface: #1a2332; --border: #2d3a4f;
  --text: #e7ecf3; --muted: #8b9cb3;
  --direct: #3b82f6; --side: #10b981; --inlaw: #a78bfa; --desc: #f59e0b;
  --confirmed: #22c55e; --probable: #eab308; --notfound: #ef4444;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
header {{ padding: 1.25rem 2rem; background: linear-gradient(135deg,#1e3a5f,#0f1419); border-bottom: 1px solid var(--border); }}
header h1 {{ margin: 0 0 .25rem; font-size: 1.5rem; }}
header p {{ margin: 0; color: var(--muted); font-size: .9rem; }}
nav.tabs {{ display: flex; gap: .5rem; padding: .75rem 2rem; background: var(--surface); border-bottom: 1px solid var(--border); flex-wrap: wrap; }}
nav.tabs button {{ background: transparent; border: 1px solid var(--border); color: var(--text); padding: .45rem 1rem; border-radius: 6px; cursor: pointer; }}
nav.tabs button.active {{ background: var(--direct); border-color: var(--direct); }}
.toolbar {{ display: flex; flex-wrap: wrap; gap: .75rem; padding: 1rem 2rem; align-items: center; }}
.toolbar input, .toolbar select {{ background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: .4rem .6rem; border-radius: 6px; }}
.toolbar label {{ color: var(--muted); font-size: .85rem; }}
main {{ padding: 0 2rem 2rem; }}
.panel {{ display: none; }}
.panel.active {{ display: block; }}
#tree-wrap {{ overflow: auto; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; min-height: 480px; padding: 1rem; }}
.tree ul {{ list-style: none; padding-left: 1.25rem; margin: .25rem 0; }}
.tree li {{ position: relative; padding: .15rem 0 .15rem .5rem; }}
.tree .node {{ display: inline-flex; align-items: center; gap: .4rem; padding: .25rem .55rem; border-radius: 6px; cursor: pointer; border: 1px solid transparent; font-size: .88rem; }}
.tree .node:hover {{ background: rgba(255,255,255,.06); border-color: var(--border); }}
.tree .node.selected {{ outline: 2px solid var(--direct); }}
.badge {{ font-size: .65rem; padding: .1rem .35rem; border-radius: 4px; text-transform: uppercase; }}
.badge.direct {{ background: rgba(59,130,246,.25); color: #93c5fd; }}
.badge.side {{ background: rgba(16,185,129,.25); color: #6ee7b7; }}
.badge.inlaw {{ background: rgba(167,139,250,.25); color: #c4b5fd; }}
.badge.descendant {{ background: rgba(245,158,11,.25); color: #fcd34d; }}
.status-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
.status-confirmed {{ background: var(--confirmed); }}
.status-probable {{ background: var(--probable); }}
.status-notfound {{ background: var(--notfound); }}
table {{ width: 100%; border-collapse: collapse; font-size: .85rem; }}
th, td {{ border: 1px solid var(--border); padding: .45rem .6rem; text-align: left; }}
th {{ background: var(--surface); position: sticky; top: 0; }}
tr:hover {{ background: rgba(255,255,255,.03); }}
.table-wrap {{ overflow: auto; max-height: 70vh; border: 1px solid var(--border); border-radius: 10px; }}
#detail {{ margin-top: 1rem; padding: 1rem; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; display: none; }}
#detail.visible {{ display: block; }}
#detail h3 {{ margin-top: 0; }}
#detail dl {{ display: grid; grid-template-columns: 140px 1fr; gap: .35rem .75rem; margin: 0; }}
#detail dt {{ color: var(--muted); }}
#detail a {{ color: #60a5fa; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 1rem; font-size: .8rem; color: var(--muted); margin-bottom: .75rem; }}
.stats {{ display: flex; gap: 1.5rem; flex-wrap: wrap; margin: .5rem 0 1rem; }}
.stat {{ background: var(--surface); padding: .5rem 1rem; border-radius: 8px; border: 1px solid var(--border); }}
.stat b {{ display: block; font-size: 1.25rem; }}
.collapsed > ul {{ display: none; }}
.toggle {{ cursor: pointer; user-select: none; color: var(--muted); margin-right: .25rem; font-family: monospace; }}
#graph-wrap {{ position: relative; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; height: 72vh; overflow: hidden; }}
#graph-canvas {{ width: 100%; height: 100%; display: block; cursor: grab; }}
#graph-canvas:active {{ cursor: grabbing; }}
.graph-legend {{ display:flex; flex-wrap:wrap; gap:1rem; font-size:.8rem; color:var(--muted); margin:.75rem 0; }}
.graph-legend span {{ display:flex; align-items:center; gap:.35rem; }}
.edge-sample {{ width:28px; height:3px; border-radius:2px; display:inline-block; }}
.edge-parent {{ background:#60a5fa; }}
.edge-spouse {{ background:#c084fc; height:0; border-top:2px dashed #c084fc; }}
.edge-sibling {{ background:#34d399; height:0; border-top:2px dashed #34d399; }}
#graph-tooltip {{ position:absolute; pointer-events:none; background:#111827; border:1px solid var(--border); padding:.35rem .55rem; border-radius:6px; font-size:.78rem; display:none; z-index:5; max-width:240px; }}
</style>
</head>
<body>
<header>
  <h1>Род Сустатовых</h1>
  <p>Полное дерево · якорь: Григорий Васильевич (30.08.1954) → Василий Григорьевич (24.01.1930, Кошелиха)</p>
</header>
<nav class="tabs">
  <button type="button" class="active" data-tab="graph">Граф</button>
  <button type="button" data-tab="tree">Дерево</button>
  <button type="button" data-tab="table">Таблица</button>
  <button type="button" data-tab="about">О проекте</button>
</nav>
<div class="toolbar">
  <input type="search" id="search" placeholder="Поиск по ФИО…" aria-label="Поиск">
  <select id="filter-role">
    <option value="">Все роли</option>
    <option value="direct">Прямая линия</option>
    <option value="side">Боковые</option>
    <option value="inlaw">По браку</option>
    <option value="descendant">Потомки</option>
  </select>
  <select id="filter-status">
    <option value="">Все статусы</option>
    <option value="confirmed">CONFIRMED</option>
    <option value="probable">PROBABLE</option>
    <option value="notfound">NOT FOUND</option>
  </select>
  <select id="graph-focus">
    <option value="">Граф: все связи</option>
    <option value="kondratiy">Фокус: Кондратий Андреевич</option>
    <option value="direct">Фокус: прямая линия</option>
  </select>
  <button type="button" id="expand-all">Развернуть всё</button>
  <button type="button" id="collapse-all">Свернуть всё</button>
  <button type="button" id="graph-reset">Сброс графа</button>
</div>
<main>
  <section id="panel-graph" class="panel active">
    <div class="stats" id="stats-graph"></div>
    <div class="graph-legend">
      <span><i class="edge-sample edge-parent"></i> отец/мать → ребёнок</span>
      <span><i class="edge-sample edge-spouse"></i> брак</span>
      <span><i class="edge-sample edge-sibling"></i> брат/сестра</span>
    </div>
    <div id="graph-wrap">
      <canvas id="graph-canvas"></canvas>
      <div id="graph-tooltip"></div>
    </div>
    <div id="detail-graph"></div>
  </section>
  <section id="panel-tree" class="panel">
    <div class="stats" id="stats"></div>
    <div class="legend">
      <span><span class="status-dot status-confirmed"></span> CONFIRMED</span>
      <span><span class="status-dot status-probable"></span> PROBABLE</span>
      <span><span class="status-dot status-notfound"></span> NOT FOUND</span>
      <span class="badge direct">прямая</span>
      <span class="badge side">боковая</span>
      <span class="badge inlaw">брак</span>
    </div>
    <div id="tree-wrap"><div id="tree-root" class="tree"></div></div>
    <div id="detail"></div>
  </section>
  <section id="panel-table" class="panel">
    <div class="table-wrap"><table id="person-table"><thead><tr>
      <th>ID</th><th>ФИО</th><th>Рожд.</th><th>Смерть</th><th>Место</th><th>Роль</th><th>Статус</th><th>Родители</th><th>Дети</th>
    </tr></thead><tbody></tbody></table></div>
  </section>
  <section id="panel-about" class="panel">
    <p>Данные: GEDCOM, VGD Кошелиха/Сыресево, мемуары sarpust.ru, <code>todo.md</code>.</p>
    <p><strong>{len(data)} персон</strong>, включая ветвь <strong>Кondratiy Andreevich</strong> (1807→1858).</p>
    <p>Потомки Averian/Stepan после ~1860 — NOT FOUND в открытых базах; нужен ЦАНО.</p>
    <p>См. также <a href="sustatov_tree.md">sustatov_tree.md</a>, <a href="isustatov.html">isustatov.html</a>.</p>
  </section>
</main>
<script>
const NODES = {json_embed};
const byId = Object.fromEntries(NODES.map(n => [n.id, n]));

function dates(n) {{
  const b = n.born || '?';
  const d = n.died || (n.status === 'notfound' ? '?' : 'ж.');
  return `${{b}} — ${{d}}`;
}}

function names(ids) {{
  return (ids || []).map(i => byId[i]?.name || i).join(', ') || '—';
}}

function buildTreeHTML(rootId, depth = 0) {{
  const n = byId[rootId];
  if (!n) return '';
  const role = n.role || 'direct';
  const st = n.status || 'confirmed';
  const children = (n.childIds || []).filter(id => byId[id]);
  const spouseHtml = (n.spouseIds || []).filter(id => byId[id] && !(n.parentIds||[]).includes(id))
    .map(sid => {{
      const s = byId[sid];
      return `<li><span class="node" data-id="${{sid}}"><span class="status-dot status-${{s.status||'confirmed'}}"></span><span class="badge inlaw">брак</span> ${{s.name}} <small style="color:var(--muted)">${{dates(s)}}</small></span></li>`;
    }}).join('');
  const childHtml = children.map(cid => buildTreeHTML(cid, depth+1)).join('');
  const hasKids = children.length || spouseHtml;
  return `<li class="${{hasKids ? '' : 'leaf'}}">
    <span class="toggle">${{hasKids ? '▼' : '·'}}</span>
    <span class="node" data-id="${{rootId}}">
      <span class="status-dot status-${{st}}"></span>
      <span class="badge ${{role}}">${{role === 'direct' ? 'прямая' : role === 'side' ? 'боковая' : role === 'inlaw' ? 'брак' : 'потомок'}}</span>
      <strong>${{n.name}}</strong>
      <small style="color:var(--muted)">${{dates(n)}}</small>
    </span>
    ${{hasKids ? `<ul>${{spouseHtml}}${{childHtml}}</ul>` : ''}}
  </li>`;
}}

function renderTree() {{
  const roots = NODES.filter(n => !(n.parentIds||[]).length || !(n.parentIds||[]).some(p => byId[p]));
  // Prefer anchor root
  const anchor = byId['sust-ivan-xiii'] ? ['sust-ivan-xiii'] : roots.map(r => r.id);
  const modern = ['I500001'];
  document.getElementById('tree-root').innerHTML = '<ul>' +
    modern.map(id => buildTreeHTML(id)).join('') +
    '<li><em style="color:var(--muted)">— предки (от Василия 1930 вверх) —</em><ul>' +
    buildTreeHTML('I500007') +
    '</ul></li>' +
    '<li><em style="color:var(--muted)">— боковые ветви XVIII–XX —</em><ul>' +
    ['side-001','side-004','side-008','side-009','side-011','side-013','side-015','side-016'].map(id => buildTreeHTML(id)).join('') +
    '</ul></li>' +
    '</ul>';

  document.querySelectorAll('.tree .toggle').forEach(t => {{
    t.addEventListener('click', e => {{
      e.stopPropagation();
      const li = t.closest('li');
      li.classList.toggle('collapsed');
      t.textContent = li.classList.contains('collapsed') ? '▶' : '▼';
    }});
  }});
  document.querySelectorAll('.tree .node').forEach(el => {{
    el.addEventListener('click', () => showDetail(el.dataset.id));
  }});
}}

function showDetail(id) {{
  const n = byId[id];
  if (!n) return;
  document.querySelectorAll('.node.selected').forEach(e => e.classList.remove('selected'));
  document.querySelector(`.node[data-id="${{id}}"]`)?.classList.add('selected');
  const src = (n.sources||[]).map(s => s.startsWith('http') ? `<a href="${{s}}" target="_blank" rel="noopener">${{s}}</a>` : s).join('<br>');
  document.getElementById('detail').className = 'visible';
  document.getElementById('detail').innerHTML = `
    <h3>${{n.name}} <small style="color:var(--muted)">(${{id}})</small></h3>
    <dl>
      <dt>Даты</dt><dd>${{dates(n)}}</dd>
      <dt>Место</dt><dd>${{n.place || '—'}}</dd>
      <dt>Родители</dt><dd>${{names(n.parentIds)}}</dd>
      <dt>Супруг(и)</dt><dd>${{names(n.spouseIds)}}</dd>
      <dt>Дети</dt><dd>${{names(n.childIds)}}</dd>
      <dt>Роль / статус</dt><dd>${{n.role}} / ${{n.status}}</dd>
      <dt>Примечания</dt><dd>${{n.notes || '—'}}</dd>
      <dt>Источники</dt><dd>${{src || '—'}}</dd>
    </dl>`;
}}

function renderTable() {{
  const tbody = document.querySelector('#person-table tbody');
  const q = document.getElementById('search').value.toLowerCase();
  const role = document.getElementById('filter-role').value;
  const status = document.getElementById('filter-status').value;
  tbody.innerHTML = NODES.filter(n => {{
    if (q && !n.name.toLowerCase().includes(q)) return false;
    if (role && n.role !== role) return false;
    if (status && n.status !== status) return false;
    return true;
  }}).sort((a,b) => (a.gen||99)-(b.gen||99) || a.name.localeCompare(b.name))
    .map(n => `<tr data-id="${{n.id}}" style="cursor:pointer">
      <td>${{n.id}}</td><td>${{n.name}}</td><td>${{n.born||''}}</td><td>${{n.died||''}}</td>
      <td>${{n.place||''}}</td><td>${{n.role||''}}</td><td>${{n.status||''}}</td>
      <td>${{names(n.parentIds)}}</td><td>${{names(n.childIds)}}</td></tr>`).join('');
  tbody.querySelectorAll('tr').forEach(tr => tr.addEventListener('click', () => {{
    showDetailGraph(tr.dataset.id);
    document.querySelector('[data-tab=graph]').click();
  }}));
}}

function renderStats() {{
  const html = `
    <div class="stat"><b>${{NODES.length}}</b> персон</div>
    <div class="stat"><b>${{NODES.filter(n=>n.status==='confirmed').length}}</b> confirmed</div>
    <div class="stat"><b>${{NODES.filter(n=>n.role==='direct').length}}</b> прямая линия</div>
    <div class="stat"><b>${{NODES.filter(n=>n.role==='side').length}}</b> боковые</div>`;
  document.getElementById('stats').innerHTML = html;
  const sg = document.getElementById('stats-graph');
  if (sg) sg.innerHTML = html;
}}

// --- Force-directed graph (HTML5 Canvas) ---
const KONDRATIY_IDS = new Set(['sust-ap-1770','sust-darya-ap','side-004','side-004a','side-004b','side-004c','side-004c-sp','side-004c-ch','side-005','side-005a','side-005b','side-005c','side-005d','side-013-notfound','side-006','side-007','side-007a','side-007b','side-014-notfound','side-009','side-009a','side-009b','side-009c','side-009c1','side-015-notfound','side-009d','side-009e','side-009f','side-009g','side-009h','side-010','side-010a','side-010b','side-010c','side-010d']);

function buildEdges(focus) {{
  const edges = [];
  const seen = new Set();
  const add = (a,b,type) => {{
    const k = [a,b].sort().join('|') + type;
    if (seen.has(k)) return;
    seen.add(k);
    edges.push({{ from:a, to:b, type }});
  }};
  const nodes = focus === 'kondratiy' ? NODES.filter(n => KONDRATIY_IDS.has(n.id)) : NODES;
  const ids = new Set(nodes.map(n => n.id));
  nodes.forEach(n => {{
    (n.parentIds||[]).forEach(p => {{ if (ids.has(p)) add(p, n.id, 'parent'); }});
    (n.spouseIds||[]).forEach(s => {{ if (ids.has(s)) add(n.id, s, 'spouse'); }});
  }});
  // siblings via shared parents
  nodes.forEach(n => {{
    (n.parentIds||[]).forEach(pid => {{
      nodes.filter(x => x.id !== n.id && (x.parentIds||[]).includes(pid)).forEach(sib => {{
        if (ids.has(sib.id)) add(n.id, sib.id, 'sibling');
      }});
    }});
  }});
  return {{ nodes, edges }};
}}

let graphState = null;

function initGraph() {{
  const canvas = document.getElementById('graph-canvas');
  const wrap = document.getElementById('graph-wrap');
  const tooltip = document.getElementById('graph-tooltip');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  let W, H;
  const resize = () => {{
    W = wrap.clientWidth; H = wrap.clientHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }};
  resize();
  window.addEventListener('resize', resize);

  const focus = () => document.getElementById('graph-focus')?.value || '';
  const {{ nodes, edges }} = buildEdges(focus());
  const simNodes = nodes.map((n, i) => ({{
    id: n.id, data: n,
    x: W/2 + Math.cos(i/nodes.length * Math.PI*2) * 180,
    y: H/2 + Math.sin(i/nodes.length * Math.PI*2) * 180,
    vx: 0, vy: 0
  }}));
  const simMap = Object.fromEntries(simNodes.map(n => [n.id, n]));
  const simEdges = edges.filter(e => simMap[e.from] && simMap[e.to]);

  graphState = {{ canvas, ctx, W, H, simNodes, simEdges, simMap, panX:0, panY:0, zoom:1, selected:null, dragging:null, dragOff:{{x:0,y:0}} }};

  const roleColor = r => ({{direct:'#3b82f6',side:'#10b981',inlaw:'#a78bfa',descendant:'#f59e0b'}}[r] || '#64748b');

  function step() {{
    const rep = 900, spring = 0.025, damp = 0.85, center = 0.002;
    simNodes.forEach(a => {{
      simNodes.forEach(b => {{
        if (a.id >= b.id) return;
        let dx = a.x - b.x, dy = a.y - b.y;
        let d2 = dx*dx + dy*dy + 0.01;
        let f = rep / d2;
        a.vx += dx * f; a.vy += dy * f;
        b.vx -= dx * f; b.vy -= dy * f;
      }});
    }});
    simEdges.forEach(e => {{
      const a = simMap[e.from], b = simMap[e.to];
      let dx = b.x - a.x, dy = b.y - a.y;
      let d = Math.hypot(dx, dy) || 1;
      let rest = e.type === 'spouse' ? 90 : e.type === 'sibling' ? 110 : 130;
      let f = (d - rest) * spring;
      a.vx += dx/d*f; a.vy += dy/d*f;
      b.vx -= dx/d*f; b.vy -= dy/d*f;
    }});
    simNodes.forEach(n => {{
      n.vx += (W/2 - n.x) * center;
      n.vy += (H/2 - n.y) * center;
      n.vx *= damp; n.vy *= damp;
      n.x += n.vx; n.y += n.vy;
    }});
  }}

  function draw() {{
    const {{ panX, panY, zoom, selected }} = graphState;
    ctx.clearRect(0, 0, W, H);
    ctx.save();
    ctx.translate(panX, panY);
    ctx.scale(zoom, zoom);
    simEdges.forEach(e => {{
      const a = simMap[e.from], b = simMap[e.to];
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      if (e.type === 'parent') {{ ctx.strokeStyle = 'rgba(96,165,250,.55)'; ctx.lineWidth = 2; ctx.setLineDash([]); }}
      else if (e.type === 'spouse') {{ ctx.strokeStyle = 'rgba(192,132,252,.6)'; ctx.lineWidth = 1.5; ctx.setLineDash([6,4]); }}
      else {{ ctx.strokeStyle = 'rgba(52,211,153,.45)'; ctx.lineWidth = 1; ctx.setLineDash([3,5]); }}
      ctx.stroke();
    }});
    ctx.setLineDash([]);
    simNodes.forEach(n => {{
      const r = n.id === selected ? 14 : 10;
      ctx.beginPath();
      ctx.fillStyle = roleColor(n.data.role);
      ctx.arc(n.x, n.y, r, 0, Math.PI*2);
      ctx.fill();
      if (n.id === selected) {{ ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke(); }}
      ctx.fillStyle = '#e7ecf3';
      ctx.font = '10px Segoe UI,sans-serif';
      ctx.textAlign = 'center';
      const label = n.data.name.length > 22 ? n.data.name.slice(0,20)+'…' : n.data.name;
      ctx.fillText(label, n.x, n.y + r + 12);
    }});
    ctx.restore();
  }}

  function loop() {{ step(); draw(); requestAnimationFrame(loop); }}
  loop();

  function screenToWorld(sx, sy) {{
    return {{ x: (sx - graphState.panX) / graphState.zoom, y: (sy - graphState.panY) / graphState.zoom }};
  }}

  canvas.addEventListener('mousedown', ev => {{
    const rect = canvas.getBoundingClientRect();
    const w = screenToWorld(ev.clientX - rect.left, ev.clientY - rect.top);
    const hit = simNodes.find(n => Math.hypot(n.x - w.x, n.y - w.y) < 14);
    if (hit) {{
      graphState.selected = hit.id;
      graphState.dragging = hit;
      graphState.dragOff = {{ x: w.x - hit.x, y: w.y - hit.y }};
      showDetailGraph(hit.id);
    }} else {{
      graphState.dragging = 'pan';
      graphState.panStart = {{ x: ev.clientX - graphState.panX, y: ev.clientY - graphState.panY }};
    }}
  }});
  window.addEventListener('mousemove', ev => {{
    if (!graphState.dragging) return;
    const rect = canvas.getBoundingClientRect();
    if (graphState.dragging === 'pan') {{
      graphState.panX = ev.clientX - graphState.panStart.x;
      graphState.panY = ev.clientY - graphState.panStart.y;
      return;
    }}
    const w = screenToWorld(ev.clientX - rect.left, ev.clientY - rect.top);
    graphState.dragging.x = w.x - graphState.dragOff.x;
    graphState.dragging.y = w.y - graphState.dragOff.y;
    graphState.dragging.vx = graphState.dragging.vy = 0;
  }});
  window.addEventListener('mouseup', () => {{ graphState.dragging = null; }});
  canvas.addEventListener('wheel', ev => {{
    ev.preventDefault();
    graphState.zoom = Math.min(2.5, Math.max(0.35, graphState.zoom * (ev.deltaY > 0 ? 0.9 : 1.1)));
  }}, {{ passive: false }});
  canvas.addEventListener('mousemove', ev => {{
    const rect = canvas.getBoundingClientRect();
    const w = screenToWorld(ev.clientX - rect.left, ev.clientY - rect.top);
    const hit = simNodes.find(n => Math.hypot(n.x - w.x, n.y - w.y) < 14);
    if (hit) {{
      tooltip.style.display = 'block';
      tooltip.style.left = (ev.clientX - rect.left + 12) + 'px';
      tooltip.style.top = (ev.clientY - rect.top + 12) + 'px';
      tooltip.textContent = hit.data.name + ' (' + dates(hit.data) + ')';
    }} else tooltip.style.display = 'none';
  }});
}}

function showDetailGraph(id) {{
  const n = byId[id];
  if (!n) return;
  const el = document.getElementById('detail-graph') || document.getElementById('detail');
  const src = (n.sources||[]).map(s => s.startsWith('http') ? `<a href="${{s}}" target="_blank" rel="noopener">${{s}}</a>` : s).join('<br>');
  el.className = 'visible';
  el.innerHTML = `<h3>${{n.name}} <small style="color:var(--muted)">(${{id}})</small></h3>
    <dl><dt>Даты</dt><dd>${{dates(n)}}</dd><dt>Родители</dt><dd>${{names(n.parentIds)}}</dd>
    <dt>Дети</dt><dd>${{names(n.childIds)}}</dd><dt>Примечания</dt><dd>${{n.notes||'—'}}</dd>
    <dt>Источники</dt><dd>${{src||'—'}}</dd></dl>`;
}}

document.getElementById('graph-focus')?.addEventListener('change', () => initGraph());
document.getElementById('graph-reset')?.addEventListener('click', () => {{
  if (graphState) {{ graphState.panX = graphState.panY = 0; graphState.zoom = 1; }}
  initGraph();
}});

document.querySelectorAll('.tabs button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('panel-' + btn.dataset.tab).classList.add('active');
  }});
}});

['search','filter-role','filter-status'].forEach(id => {{
  document.getElementById(id).addEventListener('input', renderTable);
  document.getElementById(id).addEventListener('change', renderTable);
}});

document.getElementById('expand-all').addEventListener('click', () => {{
  document.querySelectorAll('.tree li.collapsed').forEach(li => {{
    li.classList.remove('collapsed');
    const t = li.querySelector(':scope > .toggle');
    if (t) t.textContent = '▼';
  }});
}});
document.getElementById('collapse-all').addEventListener('click', () => {{
  document.querySelectorAll('.tree li').forEach(li => {{
    if (li.querySelector(':scope > ul')) {{
      li.classList.add('collapsed');
      const t = li.querySelector(':scope > .toggle');
      if (t) t.textContent = '▶';
    }}
  }});
}});

renderStats();
renderTree();
renderTable();
initGraph();
</script>
</body>
</html>"""

(ROOT / "sustatov_tree.html").write_text(html, encoding="utf-8")
print("Written sustatov_tree.md and sustatov_tree.html")
