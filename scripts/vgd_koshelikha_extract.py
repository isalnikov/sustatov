#!/usr/bin/env python3
"""Extract genealogy data from VGD Koshelikha thread (86148)."""

import json
import re
import time
import urllib.request
from html import unescape
from urllib.parse import urljoin

BASE = "https://forum.vgd.ru/2339/86148/"
PAGES = list(range(0, 300, 10))  # 0, 10, ..., 290 = 30 pages

SURNAMES = [
    r"Сустат[оа]в",
    r"Абрамов",
    r"Порунов",
    r"Корол[её]в",
    r"Ма[юy]ков",
    r"Клейменов",
    r"Маркин",
]

SURNAME_RE = re.compile("|".join(SURNAMES), re.I)

# Person name patterns (Russian genealogy context)
PERSON_PATTERNS = [
    # Full FIO with patronymic
    re.compile(
        r"([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\s+(?:Сустат[оа]в|Абрамов|Порунов|Корол[её]в|Ма[юy]ков|Клейменов|Маркин)",
        re.I,
    ),
    re.compile(
        r"(?:Сустат[оа]в|Абрамов|Порунов|Корол[её]в|Ма[юy]ков|Клейменов|Маркин)\s+([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)",
        re.I,
    ),
    re.compile(
        r"([А-ЯЁ][а-яё]+)\s+(?:Сустат[оа]в|Абрамов|Порунов|Корол[её]в|Ма[юy]ков|Клейменов|Маркин)\s+([А-ЯЁ][а-яё]+)",
        re.I,
    ),
]

DATE_PATTERNS = [
    re.compile(r"(\d{1,2}\.\d{1,2}\.\d{4})"),  # DD.MM.YYYY
    re.compile(r"(\d{4})\s*г\.?\s*р\.?", re.I),  # YYYY г.р.
    re.compile(r"р\.?\s*(\d{4})", re.I),
    re.compile(r"(\d{4})\s*г\.?\s*рожд", re.I),
    re.compile(r"ум\.?\s*(\d{1,2}\.\d{1,2}\.\d{4})", re.I),
    re.compile(r"(\d{1,2}\.\d{1,2}\.\d{4})\s*г\.?\s*р\.?", re.I),
]


def fetch(url: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) GenealogyBot/1.0"}
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("windows-1251", errors="replace")
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    return ""


def page_url(page: int) -> str:
    if page == 0:
        return BASE
    return f"{BASE}{page}.htm"


def html_to_text(html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()


def parse_posts(html: str, page: int) -> list[dict]:
    posts = []
    # Match post blocks: div id="pNNNNN" ... until next post or end
    for m in re.finditer(
        r'<div id="p(\d+)"[^>]*>(.*?)(?=<div id="p\d+"|<div class="postnav"|$)',
        html,
        re.S,
    ):
        post_id = m.group(1)
        raw = m.group(2)
        text = html_to_text(raw)

        # Extract author from preceding context if possible
        author = ""
        pre = html[max(0, m.start() - 800) : m.start()]
        author_m = re.search(r'class="postauthor"[^>]*>([^<]+)', pre)
        if author_m:
            author = html_to_text(author_m.group(1))

        # Extract date
        date = ""
        date_m = re.search(r'title="Написано ([^"]+)"', pre)
        if date_m:
            date = date_m.group(1)

        post_url = f"https://forum.vgd.ru/post/2339/86148/p{post_id}.htm#pp{post_id}"

        posts.append(
            {
                "post_id": post_id,
                "url": post_url,
                "page": page,
                "author": author,
                "date": date,
                "text": text,
                "raw_html": raw,
            }
        )
    return posts


def extract_links(html: str) -> list[str]:
    links = set()
    for m in re.finditer(r'href="([^"]+)"', html):
        href = m.group(1)
        if "forum.vgd.ru" in href or href.startswith("/"):
            full = urljoin(BASE, href)
            if "86148" not in full or "/post/" in full:
                links.add(full.split("#")[0])
        elif "vgd.ru" in href:
            links.add(href.split("#")[0])
    return sorted(links)


def is_relevant(text: str) -> bool:
    return bool(SURNAME_RE.search(text))


def extract_dates(text: str) -> dict:
    dates = {"birth": [], "death": [], "marriage": [], "other": []}
    for m in re.finditer(r"(\d{1,2}\.\d{1,2}\.\d{4})", text):
        dates["other"].append(m.group(1))
    for m in re.finditer(r"(\d{4})\s*г\.?\s*р\.?", text, re.I):
        dates["birth"].append(m.group(1))
    for m in re.finditer(r"р\.?\s*(\d{4})", text, re.I):
        dates["birth"].append(m.group(1))
    for m in re.finditer(r"ум\.?\s*(\d{1,2}\.\d{1,2}\.\d{4})", text, re.I):
        dates["death"].append(m.group(1))
    for m in re.finditer(r"погиб[^;,\n]{0,30}(\d{1,2}\.\d{1,2}\.\d{4}|\d{4})", text, re.I):
        dates["death"].append(m.group(1))
    for m in re.finditer(r"брак[^;,\n]{0,30}(\d{1,2}\.\d{1,2}\.\d{4}|\d{4})", text, re.I):
        dates["marriage"].append(m.group(1))
    for m in re.finditer(r"венчан[^;,\n]{0,30}(\d{1,2}\.\d{1,2}\.\d{4}|\d{4})", text, re.I):
        dates["marriage"].append(m.group(1))
    # dedupe
    for k in dates:
        dates[k] = list(dict.fromkeys(dates[k]))
    return dates


def extract_relations(text: str) -> dict:
    rel = {"parents": [], "spouse": [], "children": [], "siblings": [], "other": []}
    patterns = [
        (r"(?:сын|дочь|дочери|сына)\s+([А-ЯЁ][а-яё\s]+)", "parents"),
        (r"(?:отец|мать|родител[ьи])\s*[:\-]?\s*([А-ЯЁ][а-яё\s,\.]+)", "parents"),
        (r"(?:жена|муж|супруг[аи]?|в\s+браке\s+с)\s*[:\-]?\s*([А-ЯЁ][а-яё\s,\.]+)", "spouse"),
        (r"(?:брат|сестра|братья|сёстры)\s*[:\-]?\s*([А-ЯЁ][а-яё\s,\.]+)", "siblings"),
        (r"(?:дети|ребёнок|ребенок|сын|дочь)\s*[:\-]?\s*([А-ЯЁ][а-яё\s,\.]+)", "children"),
    ]
    for pat, key in patterns:
        for m in re.finditer(pat, text, re.I):
            val = m.group(1).strip()
            if len(val) > 3 and len(val) < 120:
                rel[key].append(val)
    return rel


def extract_persons_from_post(post: dict) -> list[dict]:
    persons = []
    text = post["text"]
    if not is_relevant(text):
        return persons

    # Split into sentences/fragments around surname mentions
    fragments = []
    for m in SURNAME_RE.finditer(text):
        start = max(0, m.start() - 300)
        end = min(len(text), m.end() + 300)
        fragments.append(text[start:end])

    if not fragments:
        fragments = [text]

    seen_names = set()
    for frag in fragments:
        for pat in PERSON_PATTERNS:
            for m in pat.finditer(frag):
                groups = m.groups()
                if len(groups) == 3:
                    surname, given, patronymic = groups[0], groups[1], groups[2]
                    # check which is surname
                    if re.match(r"Сустат|Абрамов|Порунов|Корол|Ма[юy]ков|Клейменов|Маркин", groups[2], re.I):
                        surname, given, patronymic = groups[2], groups[0], groups[1]
                    elif re.match(r"Сустат|Абрамов|Порунов|Корол|Ма[юy]ков|Клейменов|Маркин", groups[0], re.I):
                        surname, given, patronymic = groups[0], groups[1], groups[2]
                elif len(groups) == 2:
                    g0, g1 = groups
                    if re.match(r"Сустат|Абрамов|Порунов|Корол|Ма[юy]ков|Клейменов|Маркин", g0, re.I):
                        surname, given, patronymic = g0, g1, ""
                    else:
                        surname, given, patronymic = g1, g0, ""
                else:
                    continue

                name_key = f"{surname} {given} {patronymic}".lower()
                if name_key in seen_names:
                    continue
                seen_names.add(name_key)

                dates = extract_dates(frag)
                rel = extract_relations(frag)

                # Determine confidence
                confidence = "hypothesis"
                frag_lower = frag.lower()
                if any(w in frag_lower for w in ["метрическ", "исправно", "исправно", "исправн", "выписк", "архив", "гаф", "цано", "фонд", "оп\."]):
                    confidence = "confirmed_metric"
                elif any(w in frag_lower for w in ["погиб", "умер", "арестован", "приговор", "гaрф", "гарф", "мемориал", "обнинск", "мемориал"]):
                    confidence = "confirmed_document"
                elif any(w in frag_lower for w in ["возможно", "предполож", "вероятно", "думаю", "скорее всего"]):
                    confidence = "hypothesis"
                elif re.search(r"\d{4}", frag):
                    confidence = "probable"

                persons.append(
                    {
                        "surname": surname.strip(),
                        "given_name": given.strip(),
                        "patronymic": patronymic.strip(),
                        "full_name": f"{surname} {given} {patronymic}".strip(),
                        "birth": dates["birth"],
                        "death": dates["death"],
                        "marriage": dates["marriage"],
                        "other_dates": dates["other"],
                        "parents": rel["parents"],
                        "spouse": rel["spouse"],
                        "children": rel["children"],
                        "siblings": rel["siblings"],
                        "context": frag.strip(),
                        "source_url": post["url"],
                        "post_author": post["author"],
                        "post_date": post["date"],
                        "confidence": confidence,
                    }
                )

    # Also capture unstructured mentions (e.g. "Сустатов В.Я.")
    for m in re.finditer(
        r"(Сустат[оа]в|Абрамов\w*|Порунов\w*|Корол[её]в\w*|Ма[юy]ков\w*|Клейменов\w*|Маркин\w*)\s+([А-ЯЁ]\.?\s*[А-ЯЁ]\.?|[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)",
        text,
        re.I,
    ):
        surname = m.group(1)
        rest = m.group(2).strip()
        name_key = f"{surname} {rest}".lower()
        if name_key in seen_names:
            continue
        # Skip if already captured as full name
        if any(name_key in p["full_name"].lower() for p in persons):
            continue
        seen_names.add(name_key)
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 200)
        frag = text[start:end]
        dates = extract_dates(frag)
        persons.append(
            {
                "surname": surname,
                "given_name": rest,
                "patronymic": "",
                "full_name": f"{surname} {rest}",
                "birth": dates["birth"],
                "death": dates["death"],
                "marriage": dates["marriage"],
                "other_dates": dates["other"],
                "parents": [],
                "spouse": [],
                "children": [],
                "siblings": [],
                "context": frag.strip(),
                "source_url": post["url"],
                "post_author": post["author"],
                "post_date": post["date"],
                "confidence": "probable" if dates["birth"] or dates["death"] else "hypothesis",
            }
        )

    return persons


def extract_village_facts(posts: list[dict]) -> list[dict]:
    facts = []
    keywords = [
        r"кошелих",
        r"кamkina|камкина",
        r"церков",
        r"приход",
        r"завод",
        r"метрическ",
        r"перепис",
        r"сохранил",
        r"истори",
        r"село",
        r"деревн",
        r"мура",
        r"сыресь",
    ]
    kw_re = re.compile("|".join(keywords), re.I)
    for post in posts:
        if not is_relevant(post["text"]) and not kw_re.search(post["text"]):
            continue
        text = post["text"]
        for m in SURNAME_RE.finditer(text):
            start = max(0, m.start() - 400)
            end = min(len(text), m.end() + 400)
            frag = text[start:end]
            if kw_re.search(frag):
                facts.append(
                    {
                        "text": frag.strip(),
                        "source_url": post["url"],
                        "post_date": post["date"],
                    }
                )
    return facts


def main():
    all_posts = []
    all_persons = []
    all_links = set()
    page_summaries = []

    print("Fetching 30 pages...")
    for page in PAGES:
        url = page_url(page)
        print(f"  Page {page // 10 + 1}/30: {url}")
        try:
            html = fetch(url)
            posts = parse_posts(html, page)
            all_posts.extend(posts)
            relevant = [p for p in posts if is_relevant(p["text"])]
            page_summaries.append(
                {"page": page, "url": url, "total_posts": len(posts), "relevant_posts": len(relevant)}
            )
            for p in relevant:
                persons = extract_persons_from_post(p)
                all_persons.extend(persons)
                for link in extract_links(p["raw_html"]):
                    if is_relevant(link) or "/post/" in link:
                        all_links.add(link)
            time.sleep(0.3)
        except Exception as e:
            print(f"  ERROR on page {page}: {e}")
            page_summaries.append({"page": page, "url": url, "error": str(e)})

    # Fetch linked posts
    linked_posts = []
    linked_persons = []
    vgd_post_links = [
        l
        for l in all_links
        if "/post/" in l and "86148" not in l and l.startswith("http")
    ]
    # Also fetch linked posts from same thread that weren't on fetched pages
    same_thread_links = [
        l for l in all_links if "/post/2339/86148/" in l
    ]

    extra_links = list(set(vgd_post_links))[:50]  # limit external
    print(f"\nFetching {len(extra_links)} external linked posts...")
    for link in extra_links:
        try:
            html = fetch(link)
            posts = parse_posts(html, -1)
            if not posts:
                # single post page
                text = html_to_text(html)
                if is_relevant(text):
                    posts = [{"post_id": "linked", "url": link, "page": -1, "author": "", "date": "", "text": text, "raw_html": html}]
            for p in posts:
                if is_relevant(p["text"]):
                    linked_posts.append(p)
                    linked_persons.extend(extract_persons_from_post(p))
            time.sleep(0.3)
        except Exception as e:
            print(f"  ERROR fetching {link}: {e}")

    village_facts = extract_village_facts(all_posts + linked_posts)

    # Deduplicate persons by full_name + source
    seen = set()
    unique_persons = []
    for p in all_persons + linked_persons:
        key = (p["full_name"].lower(), p["source_url"])
        if key not in seen:
            seen.add(key)
            unique_persons.append(p)

    result = {
        "thread_url": BASE,
        "pages_fetched": len(PAGES),
        "page_summaries": page_summaries,
        "total_posts": len(all_posts),
        "relevant_posts_count": sum(1 for p in all_posts if is_relevant(p["text"])),
        "persons": unique_persons,
        "village_facts": village_facts,
        "linked_posts_fetched": len(linked_posts),
        "external_links_found": sorted(all_links),
    }

    out_path = "/tmp/vgd_koshelikha_extract.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {out_path}")
    print(f"Total posts: {len(all_posts)}")
    print(f"Relevant posts: {result['relevant_posts_count']}")
    print(f"Persons extracted: {len(unique_persons)}")
    print(f"Village facts: {len(village_facts)}")


if __name__ == "__main__":
    main()
