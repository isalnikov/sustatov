#!/usr/bin/env python3
"""
Сборка полного GEDCOM рода Сустатовых из:
  - MyHeritage GEDCOM (современная ветвь, супруги)
  - sustatov_tree_data.json (прямая линия + боковые ветви VGD)
  - синхронизация с базой LifeLines (llines/llexec) → sustatov.ged

Использование:
  python3 build_sustatov_ged.py              # полный цикл
  python3 build_sustatov_ged.py --no-llines  # только генерация GEDCOM
  python3 build_sustatov_ged.py --import-only
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent
MYHERITAGE = ROOT / "MyHeritage_GEDCOM_749073761_686021731_1_2025-02-02.ged"
TREE_JSON = ROOT / "sustatov_tree_data.json"
LLINESRC = ROOT / "lifelines" / "linesrc"
LL_DB = ROOT / "sustatov"
OUTPUT_GED = ROOT / "sustatov.ged"
STAGING_GED = ROOT / "lifelines" / "output" / "_staging_merged.ged"

# Ложная Smart Match-цепь MyHeritage (todo.md, sustatov_tree.md)
EXCLUDE_INDI: Set[str] = {"I500145", "I500085"}
EXCLUDE_FAM: Set[str] = {"F500064", "F500065"}

STATUS_NOTE = {
    "confirmed": "CONFIRMED",
    "probable": "PROBABLE",
    "notfound": "NOT FOUND",
    "hypothesis": "HYPOTHESIS",
}


@dataclass
class GedLine:
    level: int
    tag: str
    value: str = ""
    xref: str = ""


@dataclass
class GedRecord:
    xref: str
    tag: str
    lines: List[GedLine] = field(default_factory=list)

    def add(self, level: int, tag: str, value: str = "", xref: str = "") -> None:
        self.lines.append(GedLine(level, tag, value, xref))

    def prepend(self, level: int, tag: str, value: str = "", xref: str = "") -> None:
        self.lines.insert(0, GedLine(level, tag, value, xref))

    def remove_tag(self, tag: str) -> None:
        self.lines = [ln for ln in self.lines if ln.tag != tag]

    def set_tag(self, level: int, tag: str, value: str) -> None:
        for ln in self.lines:
            if ln.level == level and ln.tag == tag:
                ln.value = value
                return
        self.add(level, tag, value)

    def get_refs(self, tag: str) -> List[str]:
        return [ln.xref or ln.value for ln in self.lines if ln.tag == tag and (ln.xref or ln.value)]

    def append_refs(self, tag: str, xrefs: Iterable[str]) -> None:
        existing = set(self.get_refs(tag))
        for x in xrefs:
            if x not in existing:
                self.add(1, tag, xref=x)


@dataclass
class GedDatabase:
    header: List[GedLine] = field(default_factory=list)
    indis: Dict[str, GedRecord] = field(default_factory=dict)
    fams: Dict[str, GedRecord] = field(default_factory=dict)
    others: Dict[str, GedRecord] = field(default_factory=dict)

    def all_records(self) -> Iterable[GedRecord]:
        yield from self.indis.values()
        yield from self.fams.values()
        yield from self.others.values()


def read_gedcom(path: Path) -> GedDatabase:
    raw = path.read_bytes()
    text = None
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            text = raw.decode(enc)
            if "Сустатов" in text or "HEAD" in text:
                break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = raw.decode("utf-8", errors="replace")

    db = GedDatabase()
    current: Optional[GedRecord] = None

    for line in text.splitlines():
        if not line.strip():
            continue
        m = re.match(r"^(\d+)\s+(@\S+@\s+)?(\S+)(?:\s+(.*))?$", line)
        if not m:
            continue
        level = int(m.group(1))
        xref = (m.group(2) or "").strip()
        tag = m.group(3)
        value = (m.group(4) or "").strip()
        if xref:
            value = value  # value may be empty when xref is record id

        if level == 0 and tag == "HEAD":
            db.header.append(GedLine(0, "HEAD"))
            current = None
            continue
        if level == 0 and tag == "TRLR":
            break
        if current is None and level == 0 and tag == "HEAD":
            continue

        if level == 0:
            rec_xref = xref.rstrip()
            if not rec_xref:
                m2 = re.match(r"^(@\S+@)", line.split(None, 2)[1] if len(line.split()) > 1 else "")
                rec_xref = m2.group(1) if m2 else ""
            # parse "0 @I1@ INDI"
            parts = line.split()
            if len(parts) >= 3 and parts[1].startswith("@"):
                rec_xref = parts[1]
                rtag = parts[2]
            else:
                rtag = tag
            current = GedRecord(rec_xref, rtag)
            if rtag == "INDI":
                db.indis[rec_xref] = current
            elif rtag == "FAM":
                db.fams[rec_xref] = current
            else:
                db.others[rec_xref] = current
            continue

        if current is not None:
            ln_xref = ""
            if value.startswith("@") and value.endswith("@"):
                ln_xref = value
                value = ""
            elif tag in ("FAMC", "FAMS", "HUSB", "WIFE", "CHIL", "SOUR", "REPO", "SUBM"):
                if value.startswith("@"):
                    ln_xref = value
                    value = ""
            current.lines.append(GedLine(level, tag, value, ln_xref))

    return db


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _wrap_line(level: int, tag: str, value: str) -> List[Tuple[int, str, str]]:
    """Разбить длинные значения по правилам GEDCOM 5.5 (≤255 символов на строку)."""
    prefix = f"{level} {tag} "
    max_val = max(1, 255 - len(prefix))
    if not value:
        return [(level, tag, "")]
    if len(prefix) + len(value) <= 255:
        return [(level, tag, value)]

    out: List[Tuple[int, str, str]] = [(level, tag, value[:max_val])]
    rest = value[max_val:]
    cont_tag = "CONC" if tag in ("NOTE", "TEXT", "CONT") else "CONT"
    while rest:
        cont_prefix = f"{level + 1} {cont_tag} "
        max_cont = max(1, 255 - len(cont_prefix))
        out.append((level + 1, cont_tag, rest[:max_cont]))
        rest = rest[max_cont:]
    return out


def sanitize_record(rec: GedRecord) -> None:
    """Исправить иерархию уровней и очистить значения для LifeLines."""
    if not rec.lines:
        return
    cleaned: List[GedLine] = []
    prev = 0
    for ln in rec.lines:
        if ln.tag.startswith("_") and ln.tag not in ("_UID",):
            continue
        lvl = ln.level
        if lvl > prev + 1:
            lvl = prev + 1
        if lvl < 1:
            lvl = 1
        if ln.xref:
            cleaned.append(GedLine(lvl, ln.tag, "", ln.xref))
            prev = lvl
            continue
        val = _strip_html(ln.value) if ln.value else ""
        if ln.tag in ("TEXT", "NOTE") and len(val) > 500:
            val = val[:497] + "..."
        for pl, pt, pv in _wrap_line(lvl, ln.tag, val):
            cleaned.append(GedLine(pl, pt, pv, ""))
            prev = pl
    rec.lines = cleaned


def ensure_name_block(rec: GedRecord) -> None:
    """NAME/GIVN/SURN — первыми строками INDI (требование GEDCOM)."""
    if rec.tag != "INDI":
        return
    name_lines = [ln for ln in rec.lines if ln.tag in ("NAME", "GIVN", "SURN", "_MARNM")]
    other = [ln for ln in rec.lines if ln.tag not in ("NAME", "GIVN", "SURN", "_MARNM")]
    if not name_lines:
        return
    rec.lines = name_lines + other


def sanitize_database(db: GedDatabase) -> None:
    for rec in db.all_records():
        ensure_name_block(rec)
        sanitize_record(rec)
    # Убрать пустые семьи
    for fid in list(db.fams):
        fam = db.fams[fid]
        if not fam.get_refs("HUSB") and not fam.get_refs("WIFE") and not fam.get_refs("CHIL"):
            del db.fams[fid]


def write_gedcom(db: GedDatabase, path: Path) -> None:
    sanitize_database(db)
    out: List[str] = []
    out.append("0 HEAD")
    out.append("1 SOUR SUSTATOV-BUILDER")
    out.append("2 NAME build_sustatov_ged.py")
    out.append("2 VERS 1.0")
    out.append("1 GEDC")
    out.append("2 VERS 5.5.1")
    out.append("2 FORM LINEAGE-LINKED")
    out.append("1 CHAR UTF-8")
    out.append("1 LANG Russian")
    out.append(f"1 DATE {date.today().strftime('%d %b %Y').upper()}")
    out.append("1 FILE sustatov.ged")
    out.append("1 SUBM @SUBM1@")
    out.append("0 @SUBM1@ SUBM")
    out.append("1 NAME Sustatov Research Project")

    for rec in sorted(db.indis.values(), key=lambda r: r.xref):
        out.extend(_format_record(rec))
    for rec in sorted(db.fams.values(), key=lambda r: r.xref):
        out.extend(_format_record(rec))
    for rec in sorted(db.others.values(), key=lambda r: r.xref):
        out.extend(_format_record(rec))
    out.append("0 TRLR")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def _format_record(rec: GedRecord) -> List[str]:
    lines = [f"0 {rec.xref} {rec.tag}"]
    for ln in rec.lines:
        if ln.xref:
            line = f"{ln.level} {ln.tag} {ln.xref}"
        elif ln.value:
            line = f"{ln.level} {ln.tag} {ln.value}"
        else:
            line = f"{ln.level} {ln.tag}"
        if len(line) > 255:
            # fallback truncate
            line = line[:255]
        lines.append(line)
    return lines


def clean_excluded(db: GedDatabase) -> None:
    bad = {f"@{x}@" for x in EXCLUDE_INDI | EXCLUDE_FAM}
    for iid in list(db.indis):
        if iid.strip("@") in EXCLUDE_INDI:
            del db.indis[iid]
    for fid in list(db.fams):
        if fid.strip("@") in EXCLUDE_FAM:
            del db.fams[fid]

    for rec in db.all_records():
        rec.lines = [
            ln
            for ln in rec.lines
            if not (ln.xref in bad or ln.value in bad)
        ]


def split_name(full: str) -> Tuple[str, str]:
    full = full.strip()
    if "/" in full:
        parts = full.split("/")
        given = parts[0].strip()
        surn = parts[1].strip() if len(parts) > 1 else "Сустатов"
        return given, surn or "Сустатов"
    tokens = full.split()
    if len(tokens) >= 2 and tokens[-1].lower().endswith("ов"):
        return " ".join(tokens[:-1]), tokens[-1]
    return full, "Сустатов"


class TreeMerger:
    def __init__(self, db: GedDatabase, nodes: List[dict]):
        self.db = db
        self.nodes = {n["id"]: n for n in nodes if "notfound" not in n["id"]}
        self.id_map: Dict[str, str] = {}
        self.new_indi_counter = 900001
        self.new_fam_counter = 900001
        self._init_id_map()

    def _init_id_map(self) -> None:
        for nid in self.nodes:
            if re.match(r"^I\d+$", nid):
                xref = f"@{nid}@"
                self.id_map[nid] = xref
            elif nid.startswith("I") and nid[1:].isdigit():
                self.id_map[nid] = f"@{nid}@"

    def xref(self, node_id: str) -> str:
        if node_id in self.id_map:
            return self.id_map[node_id]
        while True:
            cand = f"@I{self.new_indi_counter}@"
            self.new_indi_counter += 1
            if cand not in self.db.indis:
                break
        self.id_map[node_id] = cand
        return cand

    def fam_xref(self) -> str:
        while True:
            cand = f"@F{self.new_fam_counter}@"
            self.new_fam_counter += 1
            if cand not in self.db.fams:
                return cand

    def merge_all(self) -> None:
        for node in self.nodes.values():
            self._ensure_indi(node)
        self._build_families_from_tree()
        self._add_project_source()

    def _ensure_indi(self, node: dict) -> GedRecord:
        xref = self.xref(node["id"])
        if xref not in self.db.indis:
            rec = GedRecord(xref, "INDI")
            self.db.indis[xref] = rec
        else:
            rec = self.db.indis[xref]

        name = node.get("name") or "?"
        given, surn = split_name(name)
        rec.lines = [ln for ln in rec.lines if ln.tag not in ("NAME", "GIVN", "SURN", "_MARNM")]
        rec.lines.insert(0, GedLine(2, "SURN", surn))
        rec.lines.insert(0, GedLine(2, "GIVN", given))
        rec.lines.insert(0, GedLine(1, "NAME", f"{given} /{surn}/"))

        sex = node.get("sex") or ""
        if sex in ("M", "F"):
            rec.set_tag(1, "SEX", sex)
        elif sex == "" and "овна" in name:
            rec.set_tag(1, "SEX", "F")
        elif sex == "" and ("ович" in name or "евич" in name or "ич " in name):
            rec.set_tag(1, "SEX", "M")

        self._set_event(rec, "BIRT", node.get("born"), node.get("place"))
        self._set_event(rec, "DEAT", node.get("died"), node.get("place"))

        status = STATUS_NOTE.get(node.get("status", ""), node.get("status", ""))
        role = node.get("role", "")
        notes = []
        if status:
            notes.append(f"Статус: {status}")
        if role:
            notes.append(f"Роль: {role}")
        if node.get("notes"):
            notes.append(node["notes"])
        if notes:
            rec.remove_tag("NOTE")
            rec.add(1, "NOTE", " | ".join(notes))

        rec.remove_tag("REFN")
        rec.add(1, "REFN", node["id"])

        sources = node.get("sources") or []
        for i, src in enumerate(sources[:5]):
            if src.startswith("http"):
                rec.add(1, "SOUR", value=src)
                rec.add(2, "PAGE", src)
            else:
                rec.add(1, "SOUR", value=src)

        return rec

    def _set_event(self, rec: GedRecord, tag: str, when: Optional[str], place: Optional[str]) -> None:
        if not when:
            return
        # remove existing same-level event block — simplify: append if no DATE
        date_val = self._format_date(when)
        rec.add(1, tag)
        rec.add(2, "DATE", date_val)
        if place:
            rec.add(2, "PLAC", place)

    @staticmethod
    def _format_date(val: str) -> str:
        val = str(val).strip()
        if re.match(r"^\d{4}$", val):
            return val
        if val.startswith("~"):
            return f"ABT {val[1:]}"
        if re.match(r"^\d{4}-\d{2}-\d{2}$", val):
            y, m, d = val.split("-")
            months = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
            return f"{int(d)} {months[int(m)-1]} {y}"
        return val

    def _find_existing_fam(self, husb: str, wife: str) -> Optional[str]:
        for fid, fam in self.db.fams.items():
            hs = fam.get_refs("HUSB")
            ws = fam.get_refs("WIFE")
            if husb in hs and (not wife or wife in ws):
                return fid
            if wife in ws and (not husb or husb in hs):
                return fid
        return None

    def _find_parent_fam(self, child_xref: str) -> Optional[str]:
        for fid, fam in self.db.fams.items():
            if child_xref in fam.get_refs("CHIL"):
                return fid
        rec = self.db.indis.get(child_xref)
        if rec:
            famcs = rec.get_refs("FAMC")
            if famcs:
                return famcs[0]
        return None

    def _build_families_from_tree(self) -> None:
        seen_pairs: Set[Tuple[str, str]] = set()

        for node in self.nodes.values():
            cx = self.xref(node["id"])
            parents = [self.id_map[p] for p in node.get("parentIds", []) if p in self.id_map]
            if parents:
                self._link_child_to_parents(cx, parents)

            for sid in node.get("spouseIds", []):
                if sid not in self.nodes:
                    continue
                sx = self.xref(sid)
                pair = tuple(sorted([cx, sx]))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                self._ensure_couple_fam(cx, sx, node, self.nodes[sid])

            for cid in node.get("childIds", []):
                if cid not in self.nodes or "notfound" in cid:
                    continue
                chx = self.xref(cid)
                self._link_child_to_parents(chx, [cx] + [
                    self.xref(s) for s in node.get("spouseIds", []) if s in self.id_map
                ][:1])

    def _ensure_couple_fam(
        self, x1: str, x2: str, n1: dict, n2: dict
    ) -> str:
        sex1 = n1.get("sex") or self.db.indis.get(x1, GedRecord("", "")).get_refs("SEX")
        husb, wife = x1, x2
        if n1.get("sex") == "F" or n2.get("sex") == "M":
            husb, wife = x2, x1
        fid = self._find_existing_fam(husb, wife)
        if not fid:
            fid = self.fam_xref()
            fam = GedRecord(fid, "FAM")
            self.db.fams[fid] = fam
            if husb:
                fam.add(1, "HUSB", xref=husb)
            if wife:
                fam.add(1, "WIFE", xref=wife)
        else:
            fam = self.db.fams[fid]
            if husb and husb not in fam.get_refs("HUSB"):
                fam.add(1, "HUSB", xref=husb)
            if wife and wife not in fam.get_refs("WIFE"):
                fam.add(1, "WIFE", xref=wife)

        for x in (x1, x2):
            indi = self.db.indis.get(x)
            if indi:
                indi.append_refs("FAMS", [fid])
        return fid

    def _link_child_to_parents(self, child_xref: str, parent_xrefs: List[str]) -> None:
        if not parent_xrefs:
            return
        husb = wife = ""
        for px in parent_xrefs:
            pnode = next((n for n in self.nodes.values() if self.id_map.get(n["id"]) == px), None)
            if not pnode:
                continue
            if pnode.get("sex") == "F":
                wife = px
            else:
                husb = px if not husb else husb

        fid = self._find_parent_fam(child_xref)
        if fid:
            fam = self.db.fams[fid]
        else:
            fid = self.fam_xref()
            fam = GedRecord(fid, "FAM")
            self.db.fams[fid] = fam
            if husb:
                fam.add(1, "HUSB", xref=husb)
            if wife:
                fam.add(1, "WIFE", xref=wife)

        if child_xref not in fam.get_refs("CHIL"):
            fam.add(1, "CHIL", xref=child_xref)
        indi = self.db.indis.get(child_xref)
        if indi:
            indi.append_refs("FAMC", [fid])

    def _add_project_source(self) -> None:
        sid = "@S900001@"
        if sid not in self.db.others:
            src = GedRecord(sid, "SOUR")
            src.add(1, "TITL", "Sustatov tree research project")
            src.add(1, "PUBL", "sustatov_tree_data.json + VGD forum 86148")
            src.add(1, "REPO", value="https://forum.vgd.ru/2339/86148/")
            self.db.others[sid] = src


def build_merged_gedcom() -> GedDatabase:
    if not MYHERITAGE.exists():
        sys.exit(f"GEDCOM не найден: {MYHERITAGE}")
    if not TREE_JSON.exists():
        sys.exit(f"JSON не найден: {TREE_JSON}")

    db = read_gedcom(MYHERITAGE)
    clean_excluded(db)
    nodes = json.loads(TREE_JSON.read_text(encoding="utf-8"))
    TreeMerger(db, nodes).merge_all()
    return db


def llines_import(db_path: Path, ged_path: Path) -> bool:
    """Импорт GEDCOM в базу LifeLines через pexpect (требует TTY)."""
    try:
        import pexpect
    except ImportError:
        print("⚠ pexpect не установлен — пропуск импорта в LifeLines")
        return False

    errs_log = ROOT / "errs.log"
    if errs_log.exists():
        errs_log.unlink()

    if db_path.exists():
        shutil.rmtree(db_path)
    db_path.mkdir(parents=True)

    staging = ged_path.resolve()
    short_ged = Path("/tmp/sustatov_import.ged")
    shutil.copy(staging, short_ged)

    child = pexpect.spawn(
        "llines",
        [str(db_path)],
        encoding="utf-8",
        timeout=180,
        dimensions=(40, 120),
        env={**{"TERM": "xterm", "LANG": "C", "LC_ALL": "C"}, **__import__("os").environ},
    )
    child.setwinsize(40, 120)

    try:
        idx = child.expect(
            ["no LifeLines database", "What do you want", "database in that", pexpect.TIMEOUT],
            timeout=30,
        )
        if idx in (0, 2):
            child.send("y")
            child.expect(["What do you want", pexpect.TIMEOUT], timeout=30)

        child.send("u")
        child.expect(["utility", "What utility", pexpect.TIMEOUT], timeout=20)
        child.send("r")
        child.expect(["GEDCOM", "file", pexpect.TIMEOUT], timeout=20)
        child.sendline(str(short_ged))
        idx = child.expect(
            ["original keys", "Use original", "added", "not loaded", pexpect.TIMEOUT],
            timeout=180,
        )
        if idx in (0, 1):
            child.sendline("y")
            child.expect(["added", "records", "not loaded", "utility", "What utility", pexpect.TIMEOUT], timeout=180)
        child.send("q")
        child.expect(["What do you want", pexpect.TIMEOUT], timeout=15)
        child.send("q")
        try:
            child.expect(pexpect.EOF, timeout=10)
        except pexpect.TIMEOUT:
            pass
        child.close()
    except Exception as exc:
        print(f"⚠ LifeLines import: {exc}")
        child.close(force=True)
        # частичный успех — проверим ниже

    r = subprocess.run(["dbverify", "-in", str(db_path)], capture_output=True, text=True)
    count = r.stdout.count("[Node: I")
    if count >= 10:
        print(f"  LifeLines: загружено ~{count} персон")
        return True
    if errs_log.exists():
        print("  errs.log:", errs_log.read_text(encoding="utf-8", errors="replace")[:400])
    return False


def llines_export(db_path: Path, out_path: Path) -> bool:
    """Экспорт базы LifeLines → GEDCOM через llexec + gedall.ll."""
    report = ROOT / "lifelines" / "reports" / "gedall.ll"
    if not report.exists():
        print(f"⚠ Отчёт {report} не найден")
        return False

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "llexec",
        f"-C{LLINESRC}",
        str(db_path),
        f"-x{report}",
    ]
    answers = f"y\n\n{out_path.resolve()}\n"
    proc = subprocess.run(cmd, input=answers, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0 and "successfully" not in (proc.stdout + proc.stderr):
        print("llexec:", (proc.stdout + proc.stderr)[:500])
        return False
    if out_path.exists() and out_path.stat().st_size > 500:
        return True
    print("llexec: файл не создан")
    return False


def stats(db: GedDatabase) -> str:
    return f"INDI={len(db.indis)} FAM={len(db.fams)} OTHER={len(db.others)}"


def main() -> None:
    ap = argparse.ArgumentParser(description="Сборка sustatov.ged (LifeLines + все ветви)")
    ap.add_argument("--no-llines", action="store_true", help="Только Python-GEDCOM, без LifeLines")
    ap.add_argument("--import-only", action="store_true", help="Импорт staging в базу sustatov")
    ap.add_argument("--export-only", action="store_true", help="Экспорт базы sustatov → sustatov.ged")
    ap.add_argument("-o", "--output", type=Path, default=OUTPUT_GED)
    args = ap.parse_args()

    if args.export_only:
        if llines_export(LL_DB, args.output):
            print(f"✓ Экспорт LifeLines → {args.output}")
        else:
            sys.exit(1)
        return

    print("=== Сборка merged GEDCOM ===")
    db = build_merged_gedcom()
    STAGING_GED.parent.mkdir(parents=True, exist_ok=True)
    write_gedcom(db, STAGING_GED)
    write_gedcom(db, args.output)
    print(f"✓ {stats(db)}")
    print(f"✓ Записано: {args.output}")
    print(f"  Staging: {STAGING_GED}")

    if args.no_llines:
        print("\nРежим --no-llines: база LifeLines не обновлялась.")
        print(f"  Импорт вручную: llines {LL_DB} → u → r → {args.output}")
        return

    if args.import_only or not args.no_llines:
        print("\n=== Импорт в LifeLines (sustatov/) ===")
        if llines_import(LL_DB, STAGING_GED):
            print("✓ База LifeLines обновлена")
            ll_export = ROOT / "lifelines" / "output" / "sustatov_llines.ged"
            print("\n=== Экспорт через llexec/gedall.ll ===")
            if llines_export(LL_DB, ll_export):
                print(f"✓ LifeLines-экспорт: {ll_export}")
            print(f"✓ Основной GEDCOM (REFN, источники): {args.output}")
        else:
            print("⚠ Авто-импорт в LifeLines недоступен (нет TTY / curses).")
            print(f"  GEDCOM готов: {args.output}")
            print(f"  Загрузите вручную: llines {LL_DB}")
            print("    u → r → указать путь к sustatov.ged → y (original keys)")


if __name__ == "__main__":
    main()
