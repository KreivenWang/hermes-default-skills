#!/usr/bin/env python3
"""
每日简报 — 新闻源抓取脚本 v2
抓取 curl 可访问的新闻源，提取标题 + URL。
输出 JSON Lines 格式。

用法:
  python3 fetch_sources.py              # 抓取全部
  python3 fetch_sources.py ai           # 仅 AI
  python3 fetch_sources.py intl         # 仅国际
  python3 fetch_sources.py finance      # 仅金融
  python3 fetch_sources.py list         # 列出可用的源

curl 可访问的源:
  AI  : leiphone, arstechnica, techcrunch, wired, bbc-tech, arxiv
  Intl: bbc, apnews, theguardian, npr, scmp
  Fin : cnbc, businessinsider, yahoo-finance
"""

import sys
import json
import re
import subprocess
from urllib.parse import urlparse

CURL_OPTS = ["curl", "-sL", "--max-time", "12", "-A",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"]
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def curl_get(url: str) -> str:
    result = subprocess.run(CURL_OPTS + [url], capture_output=True, text=True, timeout=20)
    return result.stdout


def extract_h2h3(html: str, base_url: str) -> list[dict]:
    """从 h2/h3 内的 <a> 提取标题+URL"""
    items = []
    for m in re.finditer(r'<h[23][^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL):
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        title = title.replace('&#x27;', "'").replace('&amp;', '&')
        title = title.replace('&#x20;', ' ').replace('&quot;', '"')
        title = title.replace('\u201c', '"').replace('\u201d', '"')
        link = m.group(1)
        if not title or len(title) < 15 or len(title) > 150:
            continue
        if any(x in link.lower() for x in ['logo', 'javascript', '#']):
            continue
        # Make absolute
        if link.startswith('/'):
            parsed = urlparse(base_url)
            link = f"{parsed.scheme}://{parsed.netloc}{link}"
        items.append({"title": title, "url": link})
    return items


def fetch_leiphone_ai(max_items: int = 5) -> list[dict]:
    html = curl_get("https://www.leiphone.com/category/ai")
    items = []
    for m in re.finditer(r'<a[^>]*href="(https?://[^"]+\.html)"[^>]*title="([^"]+)"', html):
        items.append({"title": m.group(2).strip(), "url": m.group(1)})
        if len(items) >= max_items:
            break
    return items


def fetch_bbc(path: str, max_items: int = 5) -> list[dict]:
    html = curl_get(f"https://www.bbc.com{path}")
    urls = list(dict.fromkeys(
        f"https://www.bbc.com{u}" for u in re.findall(r'href="(/news/articles/[^"]+)"', html)
    ))
    items = []
    for url in urls[:max_items]:
        ah = curl_get(url)
        m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', ah)
        if m:
            title = m.group(1).replace('&#x27;', "'").replace('&amp;', '&')
            items.append({"title": title, "url": url})
    return items


def fetch_arxiv(category: str = "cs.AI", max_items: int = 3) -> list[dict]:
    import xml.etree.ElementTree as ET
    import html as htmlmod
    xml_data = curl_get(f"https://arxiv.org/rss/{category}")
    if not xml_data:
        return []
    root = ET.fromstring(xml_data)
    items = []
    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        if title_el and link_el and title_el.text:
            title = htmlmod.unescape(title_el.text.strip())
            items.append({"title": title, "url": link_el.text.strip()})
            if len(items) >= max_items:
                break
    return items


def fetch_arstechnica_ai(max_items: int = 5) -> list[dict]:
    html = curl_get("https://arstechnica.com/ai/")
    return extract_h2h3(html, "https://arstechnica.com")[:max_items]


def fetch_techcrunch_ai(max_items: int = 5) -> list[dict]:
    html = curl_get("https://techcrunch.com/category/artificial-intelligence/")
    return extract_h2h3(html, "https://techcrunch.com")[:max_items]


def fetch_wired_ai(max_items: int = 5) -> list[dict]:
    html = curl_get("https://www.wired.com/category/artificial-intelligence/")
    items = extract_h2h3(html, "https://www.wired.com")[:max_items]
    # Filter: only keep items with full article paths
    return [i for i in items if '/story/' in i['url'] or '/2026/' in i['url']][:max_items]


def fetch_apnews(max_items: int = 5) -> list[dict]:
    html = curl_get("https://apnews.com/")
    items = extract_h2h3(html, "https://apnews.com")
    # Filter out section pages, keep real articles
    return [i for i in items if '/article/' in i['url'] or '/live/' in i['url']][:max_items]


def fetch_guardian(max_items: int = 5) -> list[dict]:
    html = curl_get("https://www.theguardian.com/international")
    items = extract_h2h3(html, "https://www.theguardian.com")
    return [i for i in items if '/2026/' in i['url'] or '/live/' in i['url']][:max_items]


def fetch_npr(max_items: int = 5) -> list[dict]:
    html = curl_get("https://www.npr.org/sections/news/")
    items = extract_h2h3(html, "https://www.npr.org")
    return [i for i in items if '/2026/' in i['url']][:max_items]


def fetch_scmp(max_items: int = 3) -> list[dict]:
    html = curl_get("https://www.scmp.com/news")
    items = extract_h2h3(html, "https://www.scmp.com")
    return [i for i in items if '/news/' in i['url'] and 'module=' not in i['url']][:max_items]


def fetch_cnbc_markets(max_items: int = 5) -> list[dict]:
    html = curl_get("https://www.cnbc.com/markets/")
    items = extract_h2h3(html, "https://www.cnbc.com")
    return [i for i in items if '/2026/' in i['url']][:max_items]


def fetch_businessinsider_markets(max_items: int = 5) -> list[dict]:
    html = curl_get("https://www.businessinsider.com/markets")
    items = extract_h2h3(html, "https://www.businessinsider.com")
    return [i for i in items if '/markets/' in i['url'] or '/stock-market-' in i['url'] or '/spacex-' in i['url']][:max_items]


def fetch_yahoo_finance(max_items: int = 3) -> list[dict]:
    html = curl_get("https://finance.yahoo.com/")
    items = extract_h2h3(html, "https://finance.yahoo.com")
    return [i for i in items if '/markets/' in i['url'] or '/sectors/' in i['url'] or '/articles/' in i['url']][:max_items]


def print_json(items: list[dict], source: str):
    for item in items:
        item["source"] = source
        print(json.dumps(item, ensure_ascii=False))


SOURCES = {
    "ai": [
        ("leiphone", fetch_leiphone_ai),
        ("arstechnica", fetch_arstechnica_ai),
        ("techcrunch", fetch_techcrunch_ai),
        ("wired", fetch_wired_ai),
        ("bbc-tech", lambda: fetch_bbc("/news/technology", 3)),
        ("arxiv", lambda: fetch_arxiv("cs.AI", 3)),
    ],
    "intl": [
        ("bbc", lambda: fetch_bbc("/news", 5)),
        ("apnews", fetch_apnews),
        ("guardian", fetch_guardian),
        ("npr", fetch_npr),
        ("scmp", fetch_scmp),
    ],
    "finance": [
        ("cnbc", fetch_cnbc_markets),
        ("businessinsider", fetch_businessinsider_markets),
        ("yahoo-finance", fetch_yahoo_finance),
    ],
}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode == "list":
        print("=== curl 可访问的来源 ===")
        for cat, srcs in SOURCES.items():
            print(f"\n{cat}:")
            for name, _ in srcs:
                print(f"  {name}")
        sys.exit(0)

    categories = [mode] if mode in SOURCES else list(SOURCES.keys())

    for cat in categories:
        for name, fetcher in SOURCES[cat]:
            try:
                items = fetcher()
                print_json(items, name)
            except Exception as e:
                print(json.dumps({"source": name, "error": str(e)[:100]}), file=sys.stderr)
