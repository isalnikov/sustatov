#!/usr/bin/env python3
"""
Сборка базы персон Кошелихи из GEDCOM, VGD №86148 и связанных источников.
Выход: cursor/koshelikha_persons.json
"""

from __future__ import annotations

import json
import re
import urllib.request
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GEDCOM = ROOT / "sustatov.ged"
TEMPLATE = ROOT / "schemas" / "person.template.json"
VGD_SNIPPETS = Path("/tmp/vgd_snippets.json")
VGD_EXTRACT = ROOT / "data" / "vgd_koshelikha_extract.json"
OUTPUT = ROOT / "koshelikha_persons.json"

SLUG_ALIASES: dict[str, str] = {
    "@I500001@": "sust-gv-1954",
    "@I500007@": "sust-vg-1930",
    "@I500071@": "sust-gv-1912",
    "@I500072@": "abram-eva-1911",
    "@I500073@": "sust-vi-1891",
    "@I500074@": "korol-praskovya",
    "@I500094@": "sust-ng-1936",
    "@I500081@": "abram-nikita",
    "@I500082@": "markin-anna",
}

KOSHELIKHA_PLACE = {
    "governorate": "Нижегородская губерния",
    "district": "Ардатовский уезд",
    "volost": "Кременковская",
    "settlement": "с. Кошелиха (Камкина Мордовская)",
    "modernName": "Кошелиха, Первомайский р-н, Нижегородская обл.",
    "note": None,
}

RELATED_SURNAMES = {
    "Абрамов", "Абрамова", "Порунов", "Порунова",
    "Королёв", "Королева", "Королёва", "Маюков", "Маюкова",
    "Клейменов", "Клейменова", "Маркин", "Маркина",
    "Ермолин", "Ермолина", "Ермолинa",
}

SETTLEMENT_HISTORY = """
Село Кошелиха (до XIX в. — Камкина / Камкина Мордовская) — мордовское (эрзянское) село
Кременковской волости Ардатовского уезда Нижегородской губернии.
Современно: Первомайский муниципальный округ, Нижегородская область.

Ключевые вехи (по теме ВГД №86148):
• ~1724 — переселение части семей из д. Сыресева (Утишный стан) в Камкину из-за утайки при переписи 1721.
• 1748 — в ревизии Камкины зафиксирован «прибылой из д. Сыресева» Никита Иванов (29) с сыном Петром (8) — предок рода Сустатовых.
• До 1855 — приход ц. Михаила Архангела с. Павловское; затем Пokrovская ц. Кошелихи.
• XIX–XX вв. — крестьянский род Сустатовых; метрики ЦАНО ф.570; ревизии ф.60 оп.239А.
• 1910-е — спиртзавод, колхоз «Красный Октябрь»; родственные связи с Абрамовыми, Поруновыми, Королёвыми, Маюковыми.
""".strip()


@dataclass
class Indi:
    xref: str
    name: str = ""
    givn: str = ""
    surn: str = ""
    sex: str = "U"
    birt: str = ""
    birt_plac: str = ""
    deat: str = ""
    deat_plac: str = ""
    note: str = ""
    refn: str = ""
    sources: list[str] = field(default_factory=list)
    famc: list[str] = field(default_factory=list)
    fams: list[str] = field(default_factory=list)


@dataclass
class Fam:
    xref: str
    husb: str = ""
    wife: str = ""
    children: list[str] = field(default_factory=list)
    marr: str = ""


def read_gedcom(path: Path) -> tuple[dict[str, Indi], dict[str, Fam]]:
    raw = path.read_bytes()
    text = None
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            text = raw.decode(enc)
            if "INDI" in text:
                break
        except UnicodeDecodeError:
            continue
    text = text or raw.decode("utf-8", errors="replace")

    indis: dict[str, Indi] = {}
    fams: dict[str, Fam] = {}
    cur_indi: Indi | None = None
    cur_fam: Fam | None = None
    ctx = ""

    for line in text.splitlines():
        m = re.match(r"^(\d+)\s+(@\S+@\s+)?(\S+)(?:\s+(.*))?$", line)
        if not m:
            continue
        lvl, xref_part, tag, val = int(m.group(1)), (m.group(2) or "").strip(), m.group(3), (m.group(4) or "").strip()

        if lvl == 0:
            ctx = ""
            if tag == "INDI":
                xref = val.split()[0] if val.startswith("@") else xref_part
                if not xref.startswith("@"):
                    parts = line.split()
                    xref = parts[1] if len(parts) > 1 and parts[1].startswith("@") else xref_part
                cur_indi = Indi(xref=xref)
                indis[xref] = cur_indi
                cur_fam = None
            elif tag == "FAM":
                parts = line.split()
                xref = parts[1] if len(parts) > 1 else xref_part
                cur_fam = Fam(xref=xref)
                fams[xref] = cur_fam
                cur_indi = None
            else:
                cur_indi = cur_fam = None
            continue

        if cur_indi:
            if lvl == 1:
                ctx = tag
            if tag == "NAME" and lvl == 1:
                cur_indi.name = val.split("/")[0].strip() if "/" in val else val
            elif tag == "GIVN":
                cur_indi.givn = val
            elif tag == "SURN":
                cur_indi.surn = val
            elif tag == "SEX" and lvl == 1:
                cur_indi.sex = val
            elif tag == "DATE" and ctx in ("BIRT", "DEAT"):
                if ctx == "BIRT":
                    cur_indi.birt = val
                else:
                    cur_indi.deat = val
            elif tag == "PLAC" and ctx in ("BIRT", "DEAT"):
                if ctx == "BIRT":
                    cur_indi.birt_plac = val
                else:
                    cur_indi.deat_plac = val
            elif tag == "NOTE" and lvl == 1:
                cur_indi.note = val
            elif tag == "REFN" and lvl == 1:
                cur_indi.refn = val
            elif tag == "RIN" and lvl == 1 and not cur_indi.refn:
                m = re.search(r"I(\d+)", val)
                if m:
                    cur_indi.refn = f"I{m.group(1)}"
            elif tag == "SOUR" and lvl == 1:
                pass
            elif tag == "PAGE" and ctx == "SOUR":
                cur_indi.sources.append(val)
            elif tag == "FAMC" and lvl == 1:
                cur_indi.famc.append(val.split()[0] if val else xref_part)
            elif tag == "FAMS" and lvl == 1:
                cur_indi.fams.append(val.split()[0] if val else xref_part)

        if cur_fam:
            if lvl == 1:
                ctx = tag
            if tag == "HUSB" and lvl == 1:
                cur_fam.husb = val.split()[0] if val else xref_part
            elif tag == "WIFE" and lvl == 1:
                cur_fam.wife = val.split()[0] if val else xref_part
            elif tag == "CHIL" and lvl == 1:
                cur_fam.children.append(val.split()[0] if val else xref_part)
            elif tag == "DATE" and ctx == "MARR":
                cur_fam.marr = val

    return indis, fams


def parse_name_parts(full: str, givn: str, surn: str) -> tuple[str | None, str | None, str | None]:
    if givn and surn:
        parts = givn.split()
        if len(parts) >= 3:
            return surn, f"{parts[0]} {parts[1]}", parts[2]
        if len(parts) == 2:
            return surn, parts[0], parts[1]
        return surn, parts[0] if parts else givn, None
    # fallback from NAME
    m = re.match(r"^(.+?)\s+([А-ЯЁA-Z][а-яёa-z]+(?:ович|евич|овна|евна|ич|ична|ьевич|ьевна))$", full)
    if m:
        return surn or "Сустатов", m.group(1).split()[-1], m.group(2)
    parts = full.replace("(", " ").replace(")", " ").split()
    if not parts:
        return surn or None, None, None
    surname = surn or (parts[-1] if parts[-1][0].isupper() else None)
    return surname, parts[0] if parts else None, None


def ged_date_to_json(d: str) -> dict:
    if not d:
        return {"value": None, "calendar": None, "precision": None, "note": None}
    d = d.strip()
    cal = "gregorian"
    prec = "exact"
    if d.startswith("ABT"):
        prec = "circa"
        d = d[3:].strip()
    elif d.startswith("BEF"):
        prec = "before"
        d = d[3:].strip()
    elif d.startswith("AFT"):
        prec = "after"
        d = d[3:].strip()
    # GEDCOM: 24 JAN 1930
    m = re.match(r"(\d{1,2})\s+(\w{3})\s+(\d{4})", d)
    months = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06",
              "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    if m:
        dd, mon, yy = m.group(1).zfill(2), months.get(m.group(2), "01"), m.group(3)
        return {"value": f"{dd}.{mon}.{yy}", "calendar": cal, "precision": prec, "note": None}
    m = re.match(r"^(\d{4})$", d)
    if m:
        return {"value": m.group(1), "calendar": cal, "precision": "year", "note": None}
    return {"value": d, "calendar": cal, "precision": prec, "note": None}


def place_json(plac: str) -> dict:
    if not plac:
        return deepcopy(KOSHELIKHA_PLACE)
    p = deepcopy(KOSHELIKHA_PLACE)
    p["settlement"] = plac
    return p


def slug_id(indi: Indi) -> str:
    if indi.xref in SLUG_ALIASES:
        return SLUG_ALIASES[indi.xref]
    if indi.refn and not indi.refn.startswith("side-") and not indi.refn.startswith("sust-"):
        # MyHeritage REFN like I500081 — normalize to lowercase
        if re.match(r"I\d+", indi.refn):
            return indi.refn.lower()
    if indi.refn:
        return indi.refn
    m = re.match(r"@I(\d+)@", indi.xref)
    if m:
        return f"i{m.group(1)}"
    return re.sub(r"[^a-z0-9._-]+", "-", indi.xref.strip("@").lower()).strip("-")


def confidence_from_note(note: str) -> str:
    n = note.upper()
    if "CONFIRMED" in n:
        return "reliable"
    if "PROBABLE" in n or "HYPOTHESIS" in n:
        return "needs_verification"
    return "needs_verification"


def research_status(note: str) -> str | None:
    n = note.upper()
    for s in ("CONFIRMED", "PROBABLE", "HYPOTHESIS", "NOT FOUND"):
        if s in n:
            return s.lower().replace(" ", "_")
    return None


def role_from_note(note: str) -> str | None:
    n = note.lower()
    if "direct" in n or "прям" in n:
        return "direct"
    if "inlaw" in n:
        return "inlaw"
    if "side" in n or "боков" in n:
        return "collateral"
    return None


def is_sustatov(indi: Indi) -> bool:
    s = (indi.surn or indi.name).lower()
    return "сустат" in s


def is_related_surname(indi: Indi) -> bool:
    surn = indi.surn or ""
    for rs in RELATED_SURNAMES:
        if surn.startswith(rs.rstrip("а")):
            return True
    return False


def collect_relevant_xrefs(indis: dict[str, Indi], fams: dict[str, Fam]) -> set[str]:
    """All Sustatovs + anyone linked by FAM within 2 hops of a Sustatov."""
    sustatov_xrefs = {x for x, i in indis.items() if is_sustatov(i)}
    relevant = set(sustatov_xrefs)

    def add_family_members(xref: str) -> None:
        indi = indis.get(xref)
        if not indi:
            return
        for fam_x in indi.famc + indi.fams:
            fam = fams.get(fam_x)
            if not fam:
                continue
            for m in [fam.husb, fam.wife] + fam.children:
                if m:
                    relevant.add(m)

    changed = True
    while changed:
        changed = False
        snap = set(relevant)
        for x in snap:
            before = len(relevant)
            add_family_members(x)
            if len(relevant) > before:
                changed = True

    # Also include explicitly related surnames from Koshelikha thread
    for x, i in indis.items():
        if is_related_surname(i) and any(
            fams.get(fx) and (
                fams[fx].husb in relevant or fams[fx].wife in relevant or
                any(c in relevant for c in fams[fx].children)
            )
            for fx in i.famc + i.fams
        ):
            relevant.add(x)

    return relevant


def build_relationships(xref: str, slug: str, indis: dict[str, Indi], fams: dict[str, Fam], xref_to_slug: dict[str, str]) -> dict:
    indi = indis[xref]
    father_id = mother_id = None
    spouses: list[str] = []
    children: list[dict] = []
    siblings_full: list[str] = []

    for fam_x in indi.famc:
        fam = fams.get(fam_x)
        if not fam:
            continue
        if fam.husb and fam.husb != xref:
            father_id = xref_to_slug.get(fam.husb)
        if fam.wife and fam.wife != xref:
            mother_id = xref_to_slug.get(fam.wife)
        for ch in fam.children:
            if ch != xref:
                cid = xref_to_slug.get(ch)
                if cid:
                    siblings_full.append(cid)

    order = 1
    for fam_x in indi.fams:
        fam = fams.get(fam_x)
        if not fam:
            continue
        if fam.husb and fam.husb != xref:
            sid = xref_to_slug.get(fam.husb)
            if sid and sid not in spouses:
                spouses.append(sid)
        if fam.wife and fam.wife != xref:
            sid = xref_to_slug.get(fam.wife)
            if sid and sid not in spouses:
                spouses.append(sid)
        for ch in fam.children:
            cid = xref_to_slug.get(ch)
            if cid:
                children.append({"id": cid, "order": order, "note": None})
                order += 1

    return {
        "parents": {"fatherId": father_id, "motherId": mother_id},
        "spouses": spouses,
        "children": children,
        "siblings": {
            "full": sorted(set(siblings_full)),
            "halfByFather": [],
            "halfByMother": [],
            "step": [],
        },
    }


def indi_to_person(indi: Indi, indis: dict[str, Indi], fams: dict[str, Fam], xref_to_slug: dict[str, str], template: dict) -> dict:
    p = deepcopy(template)
    pid = slug_id(indi)
    surn, given, patr = parse_name_parts(indi.name, indi.givn, indi.surn)

    p["id"] = pid
    p["gedcomId"] = indi.xref
    p["sex"] = indi.sex if indi.sex in ("M", "F") else "U"
    p["role"] = role_from_note(indi.note)

    p["identification"]["surname"]["primary"] = surn
    p["identification"]["givenName"] = given
    p["identification"]["patronymic"] = patr
    p["identification"]["displayName"] = indi.name or f"{given or ''} {patr or ''} {surn or ''}".strip()

    # Secret names from notes
    if "Кошка" in indi.note or "Кошка" in indi.name:
        p["identification"]["secretNames"] = ["Кoshka"]
    for src in indi.sources:
        if "кошка" in src.lower():
            p["identification"]["secretNames"] = ["Кошка"]

    p["lifeCycle"]["birth"]["date"] = ged_date_to_json(indi.birt)
    p["lifeCycle"]["birth"]["place"] = place_json(indi.birt_plac)
    p["lifeCycle"]["death"]["date"] = ged_date_to_json(indi.deat)
    p["lifeCycle"]["death"]["place"] = place_json(indi.deat_plac)

    p["relationships"] = build_relationships(indi.xref, pid, indis, fams, xref_to_slug)

    conf = confidence_from_note(indi.note)
    refs = [{"title": "GEDCOM sustatov.ged", "reference": indi.xref, "confidence": conf, "note": None}]
    for s in indi.sources:
        if s.startswith("http"):
            refs.append({"title": "VGD / источник", "reference": s, "confidence": conf, "note": None})
        elif s:
            refs.append({"title": s, "reference": f"https://forum.vgd.ru/2339/86148/", "confidence": conf, "note": None})
    p["sources"]["references"] = refs
    p["sources"]["overallConfidence"] = conf

    if indi.note:
        p["media"]["notes"] = indi.note

    p["meta"]["researchStatus"] = research_status(indi.note)
    p["meta"]["createdAt"] = datetime.now(timezone.utc).isoformat()
    p["meta"]["updatedAt"] = None

    return p


def add_manual_relatives(persons: dict[str, dict]) -> None:
    """Porunov branch and other VGD-only persons not fully in GEDCOM."""
    manual = [
        {
            "id": "por-na-cousin",
            "identification": {
                "surname": {"primary": "Порунов", "married": None, "variants": []},
                "givenName": "Николай", "patronymic": "Александрович",
                "displayName": "Порунов Николай Александрович",
                "secretNames": [],
            },
            "sex": "M", "role": "collateral",
            "relationships": {
                "parents": {"fatherId": "por-ap-1912", "motherId": None},
                "spouses": [], "children": [],
                "siblings": {"full": ["por-ip-1922"], "halfByFather": [], "halfByMother": [], "step": []},
            },
            "sources": {
                "references": [
                    {"title": "Мемуары Н.Г. Сустатова, ч. III",
                     "reference": "https://sarpust.ru/2015/02/vospominaniya-n-g-sustatova-chast-iii-dezertiry-i-gul-komovtsy/",
                     "confidence": "reliable", "note": "Двоюродный брат Василия Григорьевича"},
                ],
                "overallConfidence": "reliable",
            },
            "media": {"biography": "Двоюродный брат Сустатовых; пас лошадей вместе с В.Г. Сустатовым («Кошка»)."},
            "meta": {"researchStatus": "confirmed"},
        },
        {
            "id": "por-ap-1912",
            "identification": {
                "surname": {"primary": "Порунов", "married": None, "variants": []},
                "givenName": "Александр", "patronymic": "Павлович",
                "displayName": "Порунов Александр Павлович",
                "secretNames": [],
            },
            "sex": "M", "role": "collateral",
            "lifeCycle": {
                "birth": {"date": {"value": "1912", "calendar": "gregorian", "precision": "year", "note": None},
                          "place": deepcopy(KOSHELIKHA_PLACE)},
                "death": {"date": {"value": "1942", "calendar": "gregorian", "precision": "year", "note": "Погиб в ВОВ"},
                          "place": deepcopy(KOSHELIKHA_PLACE), "cause": "ВОВ"},
            },
            "relationships": {
                "parents": {"fatherId": "por-pe-1916", "motherId": None},
                "spouses": [], "children": [{"id": "por-na-cousin", "order": 1, "note": "HYPOTHESIS — Николай А."}],
                "siblings": {"full": ["por-ip-1922"], "halfByFather": [], "halfByMother": [], "step": []},
            },
            "sources": {
                "references": [{"title": "VGD №86148 /20.htm", "reference": "https://forum.vgd.ru/2339/86148/20.htm",
                                  "confidence": "reliable", "note": "Списки ВОВ"}],
                "overallConfidence": "reliable",
            },
            "meta": {"researchStatus": "confirmed"},
        },
        {
            "id": "por-ip-1922",
            "identification": {
                "surname": {"primary": "Порунов", "married": None, "variants": []},
                "givenName": "Иван", "patronymic": "Павлович",
                "displayName": "Порунов Иван Павлович",
                "secretNames": [],
            },
            "sex": "M", "role": "collateral",
            "lifeCycle": {
                "birth": {"date": {"value": "1922", "calendar": "gregorian", "precision": "year", "note": None},
                          "place": deepcopy(KOSHELIKHA_PLACE)},
                "death": {"date": {"value": "1942", "calendar": "gregorian", "precision": "year", "note": None},
                          "place": deepcopy(KOSHELIKHA_PLACE), "cause": "ВОВ"},
            },
            "relationships": {
                "parents": {"fatherId": "por-pe-1916", "motherId": None},
                "spouses": [], "children": [],
                "siblings": {"full": ["por-ap-1912"], "halfByFather": [], "halfByMother": [], "step": []},
            },
            "sources": {
                "references": [{"title": "VGD №86148 /20.htm", "reference": "https://forum.vgd.ru/2339/86148/20.htm",
                                  "confidence": "reliable", "note": None}],
                "overallConfidence": "reliable",
            },
            "meta": {"researchStatus": "confirmed"},
        },
        {
            "id": "por-pe-1916",
            "identification": {
                "surname": {"primary": "Порунов", "married": None, "variants": []},
                "givenName": "Павел", "patronymic": "Егорович",
                "displayName": "Порунов Павел Егорович",
                "secretNames": [],
            },
            "sex": "M", "role": "collateral",
            "lifeCycle": {
                "birth": {"date": {"value": "~1897", "calendar": "gregorian", "precision": "circa", "note": "19 л. в 1916"},
                          "place": deepcopy(KOSHELIKHA_PLACE)},
            },
            "relationships": {
                "parents": {"fatherId": None, "motherId": None},
                "spouses": [], "children": [
                    {"id": "por-ap-1912", "order": 1, "note": None},
                    {"id": "por-ip-1922", "order": 2, "note": None},
                ],
                "siblings": {"full": ["por-km-1906", "por-dm-unknown"], "halfByFather": [], "halfByMother": [], "step": []},
            },
            "socialPortrait": {
                "occupations": [{"title": "плотник", "employer": "Кошелихинский лесозавод №27",
                                 "from": {"value": "1919", "precision": "year"}, "note": "VGD /270.htm"}],
            },
            "sources": {
                "references": [
                    {"title": "VGD №86148 /160.htm", "reference": "https://forum.vgd.ru/2339/86148/160.htm",
                     "confidence": "reliable", "note": "Брак с Клейменовой Анной Васильевной, ~1916"},
                ],
                "overallConfidence": "reliable",
            },
            "meta": {"researchStatus": "confirmed"},
        },
    ]

    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    for m in manual:
        base = deepcopy(template)
        merge_deep(base, m)
        persons[m["id"]] = base

    # Link Sustatov cousins to Porunov
    if "sust-vg-1930" in persons:
        rel = persons["sust-vg-1930"].setdefault("relationships", {})
        sibs = rel.setdefault("siblings", {})
        cousins = sibs.setdefault("full", [])
        if "por-na-cousin" not in cousins:
            # cousin not sibling - add note in media
            persons["sust-vg-1930"]["media"]["notes"] = (
                (persons["sust-vg-1930"]["media"].get("notes") or "") +
                " Двоюродный брат: por-na-cousin (Порунов Н.А.)"
            ).strip()


def merge_deep(base: dict, override: dict) -> None:
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            merge_deep(base[k], v)
        else:
            base[k] = v


def person_key(surn: str | None, given: str | None, patr: str | None) -> tuple[str, str, str]:
    def n(s: str | None) -> str:
        if not s:
            return ""
        s = s.lower().replace("ё", "е")
        s = re.sub(r"[^a-zа-я0-9]", "", s)
        return s
    return n(surn), n(given), n(patr)


def vgd_confidence(level: str) -> str:
    if level in ("confirmed_metric", "confirmed_document", "confirmed"):
        return "reliable"
    if level == "hypothesis":
        return "hypothesis"
    return "needs_verification"


def parse_vgd_date(raw: str | None) -> dict:
    if not raw:
        return {"value": None, "calendar": "gregorian", "precision": None, "note": None}
    raw = raw.strip()
    prec = "exact"
    if raw.startswith("~"):
        prec = "circa"
        raw = raw[1:]
    if "?" in raw:
        prec = "circa"
        raw = raw.replace("?", "")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", raw)
    if m:
        return {"value": f"{m.group(3)}.{m.group(2)}.{m.group(1)}", "calendar": "gregorian", "precision": prec, "note": None}
    m = re.match(r"(\d{4})", raw)
    if m:
        return {"value": m.group(1), "calendar": "gregorian", "precision": "year" if prec == "exact" else prec, "note": None}
    return {"value": raw, "calendar": "gregorian", "precision": prec, "note": None}


def vgd_slug(entry: dict, existing: set[str]) -> str:
    surn = (entry.get("surname") or "x").lower()
    given = (entry.get("given_name") or "x").lower()
    patr = (entry.get("patronymic") or "x").lower()
    base = re.sub(r"[^a-z0-9]+", "-", f"vgd-{surn}-{given}-{patr}").strip("-")[:48]
    slug = base
    i = 2
    while slug in existing:
        slug = f"{base}-{i}"
        i += 1
    return slug


def merge_vgd_extract(persons: dict[str, dict], template: dict) -> dict[str, Any]:
    """Merge curated subagent extraction (/data/vgd_koshelikha_extract.json)."""
    meta: dict[str, Any] = {}
    if not VGD_EXTRACT.exists():
        return meta
    data = json.loads(VGD_EXTRACT.read_text(encoding="utf-8"))
    meta = {
        "vgdMeta": data.get("meta", {}),
        "keyPosts": data.get("key_posts", {}),
        "villageFacts": data.get("village_facts", []),
    }

    index: dict[tuple[str, str, str], str] = {}
    for pid, p in persons.items():
        ident = p.get("identification", {})
        index[person_key(
            ident.get("surname", {}).get("primary"),
            ident.get("givenName"),
            ident.get("patronymic"),
        )] = pid

    added = 0
    enriched = 0
    for entry in data.get("persons", []):
        key = person_key(entry.get("surname"), entry.get("given_name"), entry.get("patronymic"))
        pid = index.get(key)
        conf = vgd_confidence(entry.get("confidence", ""))
        ref = {
            "title": "VGD №86148",
            "reference": entry.get("source_url", "https://forum.vgd.ru/2339/86148/"),
            "confidence": conf,
            "note": entry.get("notes"),
        }
        vgd_post = {"page": None, "url": entry.get("source_url"), "excerpt": entry.get("notes") or entry.get("full_name")}

        if pid:
            p = persons[pid]
            refs = p.setdefault("sources", {}).setdefault("references", [])
            if ref["reference"] not in {r.get("reference") for r in refs}:
                refs.append(ref)
            posts = p.setdefault("sources", {}).setdefault("vgdPosts", [])
            if vgd_post["url"] and vgd_post["url"] not in {x.get("url") for x in posts}:
                posts.append(vgd_post)
            if conf == "reliable":
                p["sources"]["overallConfidence"] = "reliable"
            if entry.get("notes"):
                note = (p.get("media", {}).get("notes") or "")
                if entry["notes"] not in note:
                    p.setdefault("media", {})["notes"] = (note + " | " + entry["notes"]).strip(" |")
            enriched += 1
            continue

        # new person from VGD only
        slug = vgd_slug(entry, set(persons.keys()))
        p = deepcopy(template)
        p["id"] = slug
        p["gedcomId"] = None
        p["sex"] = "U"
        p["role"] = "collateral" if (entry.get("surname") or "").startswith("Сустат") else "inlaw"
        p["identification"]["surname"]["primary"] = entry.get("surname")
        p["identification"]["givenName"] = entry.get("given_name")
        p["identification"]["patronymic"] = entry.get("patronymic")
        p["identification"]["displayName"] = entry.get("full_name")
        if entry.get("birth"):
            p["lifeCycle"]["birth"]["date"] = parse_vgd_date(entry["birth"])
            p["lifeCycle"]["birth"]["place"] = deepcopy(KOSHELIKHA_PLACE)
        if entry.get("death"):
            p["lifeCycle"]["death"]["date"] = parse_vgd_date(str(entry["death"]))
            p["lifeCycle"]["death"]["place"] = deepcopy(KOSHELIKHA_PLACE)
        if entry.get("marriage"):
            p["lifeCycle"]["marriages"] = [{
                "date": parse_vgd_date(str(entry["marriage"])),
                "place": deepcopy(KOSHELIKHA_PLACE),
                "witnesses": [], "marriageRecordNumber": None, "spouseId": None,
                "divorce": {"date": parse_vgd_date(None), "place": deepcopy(KOSHELIKHA_PLACE), "note": None},
                "sources": [ref],
            }]
        p["sources"]["references"] = [ref]
        p["sources"]["vgdPosts"] = [vgd_post]
        p["sources"]["overallConfidence"] = conf
        if entry.get("notes"):
            p["media"]["notes"] = entry["notes"]
            if any(w in (entry.get("notes") or "").lower() for w in ("вов", "рядовой", "погиб", "плен", "ранен")):
                p["socialPortrait"]["militaryService"] = [{"note": entry["notes"]}]
        p["meta"]["researchStatus"] = entry.get("confidence", "needs_verification").replace("confirmed_metric", "confirmed").replace("confirmed_document", "confirmed")
        persons[slug] = p
        index[key] = slug
        added += 1

    meta["vgdMerge"] = {"enriched": enriched, "added": added}
    return meta


def attach_vgd_snippets(persons: dict[str, dict]) -> None:
    if not VGD_SNIPPETS.exists():
        return
    snippets = json.loads(VGD_SNIPPETS.read_text(encoding="utf-8"))
    for person in persons.values():
        name = person.get("identification", {}).get("displayName") or ""
        given = person.get("identification", {}).get("givenName") or ""
        surn = person.get("identification", {}).get("surname", {}).get("primary") or ""
        if not given and not surn:
            continue
        hits = []
        for sn in snippets:
            t = sn["text"]
            if surn and surn in t and given and given in t:
                hits.append({"page": sn["page"], "url": sn["url"], "excerpt": t[:300]})
        if hits:
            person.setdefault("sources", {})["vgdPosts"] = hits[:5]


def main() -> None:
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    indis, fams = read_gedcom(GEDCOM)
    relevant = collect_relevant_xrefs(indis, fams)

    xref_to_slug: dict[str, str] = {x: slug_id(indis[x]) for x in relevant if x in indis}

    persons: dict[str, dict] = {}
    for xref in sorted(relevant):
        indi = indis[xref]
        person = indi_to_person(indi, indis, fams, xref_to_slug, template)
        persons[person["id"]] = person

    add_manual_relatives(persons)
    attach_vgd_snippets(persons)
    vgd_meta = merge_vgd_extract(persons, template)

    # Fix Кoshka typo
    for p in persons.values():
        sn = p.get("identification", {}).get("secretNames", [])
        p["identification"]["secretNames"] = ["Кошка" if x in ("Кoshka", "Koshka") else x for x in sn]

    collection = {
        "$schema": "./schemas/person.schema.json",
        "collection": {
            "title": "Кошелиха — Сустатовы и родственники",
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "primarySource": "https://forum.vgd.ru/2339/86148/",
            "relatedThreads": [
                {"title": "Кошелиха (Камкина Мордовская)", "url": "https://forum.vgd.ru/2339/86148/", "pages": 30},
                {"title": "Сыресева — ревизии", "url": "https://forum.vgd.ru/2339/75748/"},
                {"title": "Метрики с. Павловского", "url": "https://forum.vgd.ru/2304/157478/"},
            ],
            "archives": [
                {"name": "ЦАНО", "note": "ф.570 метрики; ф.60 оп.239А ревизии"},
                {"name": "РГАДА", "note": "ф.350 оп.2 — ревизии Сыресева/Камкины"},
            ],
            "settlementHistory": SETTLEMENT_HISTORY,
            "personCount": len(persons),
            **{k: v for k, v in vgd_meta.items() if k not in ("vgdMerge",)},
        },
        "persons": list(persons.values()),
    }

    OUTPUT.write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8")
    sustatov_count = sum(1 for p in persons.values() if (p.get("identification", {}).get("surname", {}).get("primary") or "").startswith("Сустат"))
    merge_info = vgd_meta.get("vgdMerge", {})
    print(f"Wrote {OUTPUT}: {len(persons)} persons ({sustatov_count} Sustatovs); VGD +{merge_info.get('added',0)} enriched {merge_info.get('enriched',0)}")


if __name__ == "__main__":
    main()
