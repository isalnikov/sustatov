#!/usr/bin/env python3
"""Apply subagent corrections (Maksim, Averian, Stepan) to tree JSON."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
data = json.loads((ROOT / "sustatov_tree_data.json").read_text(encoding="utf-8"))
by_id = {n["id"]: n for n in data}

VGD2806392 = "https://forum.vgd.ru/post/2339/86148/p2806392.htm"
VGD2818326 = "https://forum.vgd.ru/post/2339/86148/p2818326.htm"
VGD2818093 = "https://forum.vgd.ru/post/2339/86148/p2818093.htm"
VGD2962408 = "https://forum.vgd.ru/post/2339/86148/p2962408.htm"
VGD2995932 = "https://forum.vgd.ru/post/2339/86148/p2995932.htm"
VGD140 = "https://forum.vgd.ru/2339/86148/140.htm"
VGD2879430 = "https://forum.vgd.ru/post/2339/86148/p2879430.htm"
VGD2820771 = "https://forum.vgd.ru/post/2339/86148/p2820771.htm"

PATCHES = {
    "side-004": {
        "sources": [VGD140, VGD2818326, VGD2879430],
        "notes": "Брак 08.11.1807 + Анна Филипповна (дочь Филиппа Михайловича); †1847",
    },
    "side-004a": {
        "born": "~1798",
        "notes": "Дочь Филиппа Михайловича; рев.1834/1858 — 60/67 лет",
        "sources": [VGD2879430, VGD2818326, VGD140],
    },
    "side-004b": {
        "name": "Мавра Кондратьевна",
        "born": "~1798",
        "notes": "Рев.1816 — 18 лет; дальнейшая судьба NOT FOUND",
        "sources": [VGD2806392, VGD140],
    },
    "side-004c": {
        "born": "~1803",
        "notes": "Рев.1816 — 13 лет; рев.1850 — жена Ефима Ивановича",
        "sources": [VGD2806392, VGD2818093, VGD140],
    },
    "side-005": {
        "sources": [VGD140, VGD2818093, VGD2995932, VGD2818326],
        "notes": "Брак 08.11.1835 + Дарья Анисимовна; рев.1858 двор №24 — 31/38 лет; смерть и потомки после 1858 NOT FOUND",
    },
    "side-005a": {
        "born": "~1816",
        "notes": "Брак 08.11.1835; рев.1858 — 42 года",
        "sources": [VGD2995932, VGD140, VGD2818093],
    },
    "side-005b": {
        "name": "Екатерина Аверьяновна",
        "sources": [VGD140, VGD2962408, VGD2818326],
        "notes": "Рев.1851 — 14 л.; венчание 06.11.1855 + Иван Евдокимович («Аверкий Кондратьевич» в метрике); фамилия Сустатов далее не продолжается",
    },
    "side-005c": {
        "born": "~1837",
        "sources": [VGD140, VGD2962408, VGD2879430],
        "notes": "Сын умерш. Евдокима Михеевича; рев.1858 — 20 лет",
    },
    "side-005d": {
        "name": "Наталья Ивановна",
        "born": "~1857",
        "status": "confirmed",
        "notes": "Внучка Аверьяна; рев.1858 — 6 мес.; потомки до 2026 NOT FOUND (ЦАНО ф.570)",
        "sources": [VGD140, VGD2818093],
    },
    "side-006": {
        "born": "~1811",
        "notes": "Рев.1816 — 5 лет; рев.1834 — «умер в 1840 г.» (~29 лет); брак и дети NOT FOUND — ветвь обрывается",
        "sources": [VGD2806392, VGD2818326, VGD2995932],
    },
    "side-007": {
        "born": "~1834",
        "sources": [VGD140, VGD2818326, VGD2995932, VGD2818093],
        "notes": "Рев.1834 — 2 мес.; рев.1851 — 17 л.; рекрут с 1855 (числится в дворе Аверьяна, №24); потомки NOT FOUND",
        "childIds": ["side-014-notfound"],
    },
    "side-007a": {
        "born": "~1835",
        "notes": "Дочь Антона Григорьевича; рев.1858 — 23 года",
    },
    "side-007b": {
        "status": "probable",
        "notes": "«Племянница Аверьяна» (32 г. в 1858) — связь со Степаном Кондратьевичем не доказана (конфликт возраста); NOT FOUND",
        "parentIds": [],
    },
    "side-009c": {
        "childIds": ["side-009c1"],
        "sources": [VGD140, VGD2820771, "брак 09.11.1845"],
        "notes": "Рекрут с 1853; жена Анна Тимофеевна; сын Степан Степанович (~1864, PROBABLE)",
    },
    "side-009f": {
        "notes": "Рев.1858 — 11/18 л.; потомки NOT FOUND",
    },
    "side-009g": {
        "notes": "Р.1855; потомки NOT FOUND",
    },
}

for nid, patch in PATCHES.items():
    if nid in by_id:
        by_id[nid].update(patch)

# Ensure Stepan line ends at NOT FOUND placeholder (not side-007b)
if "side-007" in by_id:
    by_id["side-007"]["childIds"] = ["side-014-notfound"]

# Add NOT FOUND placeholder node for post-1860 gap (Averian line)
if "side-013-notfound" not in by_id:
    by_id["side-013-notfound"] = {
        "id": "side-013-notfound",
        "name": "Потомки ветви Аверьяна после 1860",
        "born": None,
        "died": None,
        "place": "",
        "sex": "",
        "parentIds": ["side-005d"],
        "spouseIds": [],
        "childIds": [],
        "status": "notfound",
        "role": "side",
        "gen": 6,
        "sources": [],
        "notes": "GEDCOM, openlist, sarpust, опубликованные метрики VGD 1860–2026 — записей нет",
    }
    by_id["side-005d"]["childIds"] = ["side-013-notfound"]

# Stepan Kondratievich — no confirmed children; NOT FOUND after 1858
if "side-014-notfound" not in by_id:
    by_id["side-014-notfound"] = {
        "id": "side-014-notfound",
        "name": "Потомки Степана Кондратьевича после 1858",
        "born": None,
        "died": None,
        "place": "",
        "sex": "",
        "parentIds": ["side-007"],
        "spouseIds": [],
        "childIds": [],
        "status": "notfound",
        "role": "side",
        "gen": 4,
        "sources": [],
        "notes": "Рекрут с 1855; GEDCOM, openlist, метрики VGD 1860–2026 — записей нет",
    }

# Collateral: Stepan Stepanovich (son of Stepan Vasilyevich)
if "side-009c1" not in by_id:
    by_id["side-009c1"] = {
        "id": "side-009c1",
        "name": "Степан Степанович Сустатов",
        "born": "~1864",
        "died": None,
        "place": "Кошелиха",
        "sex": "M",
        "parentIds": ["side-009c", "side-009h"],
        "spouseIds": [],
        "childIds": ["side-015-notfound"],
        "status": "probable",
        "role": "side",
        "gen": 4,
        "sources": [VGD2820771],
        "notes": "~4 л. в списке солдатских семей; ≠ Степан Кондратьевич; потомки NOT FOUND",
    }
    if "side-009c" in by_id:
        kids = set(by_id["side-009c"].get("childIds") or [])
        kids.add("side-009c1")
        by_id["side-009c"]["childIds"] = sorted(kids)

if "side-015-notfound" not in by_id:
    by_id["side-015-notfound"] = {
        "id": "side-015-notfound",
        "name": "Потомки Степана Степановича (collateral)",
        "born": None,
        "died": None,
        "place": "",
        "sex": "",
        "parentIds": ["side-009c1"],
        "spouseIds": [],
        "childIds": [],
        "status": "notfound",
        "role": "side",
        "gen": 5,
        "sources": [],
        "notes": "Ветвь Василия Андреевича; связь с прямой линией не установлена",
    }

out = sorted(by_id.values(), key=lambda n: (n.get("gen") or 99, n.get("name") or ""))
(ROOT / "sustatov_tree_data.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"Patched {len(PATCHES)} nodes; total {len(out)}")
