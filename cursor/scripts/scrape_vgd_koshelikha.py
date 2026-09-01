#!/usr/bin/env python3
"""Scrape VGD thread 86148 (Koshelikha) for genealogy mentions."""

from __future__ import annotations

import json
import re
import time
import urllib.request
from html import unescape
from pathlib import Path

THREAD = "86148"
BASE = f"https://forum.vgd.ru/2339/{THREAD}/"
PAGES = list(range(0, 300, 10))  # 0..290 = 30 pages

SURNAMES = [
    "Сустатов", "Сустатова", "Сустатовы", "Сустатовых",
    "Абрамов", "Абрамова", "Абрамовы",
    "Порунов", "Порунова",
    "Королёв", "Королева", "Королёва",
    "Маюков", "Маюкова",
    "Клейменов", "Клейменова",
    "Маркин", "Маркина",
    "Ермолин", "Ермолина",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (genealogy research)"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    raw = urllib.request.urlopen(req, timeout=30).read()
    for enc in ("windows-1251", "utf-8", "cp1251"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def strip_html(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return unescape(re.sub(r"\s+", " ", html)).strip()


def extract_posts(html: str, page_url: str) -> list[dict]:
    posts = []
    # VGD post blocks often contain post id in links like post/2339/86148/pNNNN.htm
    chunks = re.split(r'class="postbody"|class="posttext"', html, flags=re.I)
    if len(chunks) < 2:
        chunks = re.split(r'id="post\d+"', html, flags=re.I)
    for chunk in chunks[1:]:
        post_id = None
        m = re.search(rf"/post/2339/{THREAD}/(p\d+\.htm)", chunk)
        if m:
            post_id = m.group(1)
        text = strip_html(chunk[:8000])
        if not text or len(text) < 20:
            continue
        matched = [s for s in SURNAMES if s.lower() in text.lower()]
        if not matched:
            continue
        url = f"https://forum.vgd.ru/post/2339/{THREAD}/{post_id}" if post_id else page_url
        posts.append({
            "url": url,
            "page": page_url,
            "surnames": sorted(set(matched)),
            "text": text[:4000],
        })
    return posts


def extract_sustatov_lines(text: str) -> list[str]:
    lines = []
    for m in re.finditer(
        r"[^.;\n]{0,80}Сустат[а-яёА-ЯЁ]{0,20}[^.;\n]{0,120}",
        text,
        flags=re.I,
    ):
        s = m.group(0).strip()
        if len(s) > 15:
            lines.append(s)
    return lines


def main() -> None:
    out_dir = Path("/tmp/vgd_koshelikha")
    out_dir.mkdir(exist_ok=True)
    all_posts: list[dict] = []
    all_snippets: list[dict] = []
    linked_threads: set[str] = set()

    for offset in PAGES:
        url = BASE if offset == 0 else f"{BASE}{offset}.htm"
        print(f"Fetching {url}")
        try:
            html = fetch(url)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
        posts = extract_posts(html, url)
        all_posts.extend(posts)
        for link in re.findall(r'href="(/2339/\d+/)"', html):
            linked_threads.add(f"https://forum.vgd.ru{link}")
        for link in re.findall(rf'href="(/post/2339/{THREAD}/p\d+\.htm)"', html):
            linked_threads.add(f"https://forum.vgd.ru{link}")
        time.sleep(0.3)

    # Dedupe posts by url+text prefix
    seen: set[str] = set()
    unique_posts = []
    for p in all_posts:
        key = p["url"] + p["text"][:200]
        if key not in seen:
            seen.add(key)
            unique_posts.append(p)
            for line in extract_sustatov_lines(p["text"]):
                all_snippets.append({"url": p["url"], "snippet": line})

    result = {
        "thread": BASE,
        "pages_fetched": len(PAGES),
        "posts_with_surnames": len(unique_posts),
        "linked_urls": sorted(linked_threads),
        "posts": unique_posts,
        "sustatov_snippets": all_snippets,
    }
    out_path = out_dir / "raw_extract.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}: {len(unique_posts)} posts, {len(all_snippets)} snippets")


if __name__ == "__main__":
    main()
