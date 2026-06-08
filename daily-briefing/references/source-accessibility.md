# Source Accessibility Reference

All 15 curl-accessible sources verified 2026-06-08. Each source's extraction method and performance noted.

## AI / Tech (6 sources)

### leiphone.com/category/ai
- **Method:** Regex `<a href="..." title="...">` from single HTML request
- **Speed:** < 2s for 5 items
- **Extraction:** `re.findall(r'<a[^>]*href="(https?://[^"]+\.html)"[^>]*title="([^"]+)"', html)`
- **Language:** Chinese
- **Notes:** Most reliable Chinese AI source. Title attribute on `<a>` tag.

### arstechnica.com/ai
- **Method:** `extract_h2h3()` — h2/h3 > a pattern from single HTML request
- **Speed:** < 2s for 5 items
- **Extraction:** `re.findall(r'<h[23][^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)` then strip tags
- **Language:** English
- **Notes:** Rich AI coverage. Filter out section pages by checking for `/2026/` or `/ai/` in URL.

### techcrunch.com/category/artificial-intelligence/
- **Method:** `extract_h2h3()` from single HTML request
- **Speed:** < 2s for 5 items
- **Language:** English
- **Notes:** First result is always "TechCrunch Desktop Logo" (logo link) — must skip by checking link != homepage.

### wired.com/category/artificial-intelligence/
- **Method:** `extract_h2h3()`, filter for `/story/` or `/2026/` in URL
- **Speed:** < 2s
- **Language:** English
- **Notes:** Many section links mixed in. Must filter out `/topic/`, `/magazines/` paths.

### bbc.com/news/technology
- **Method:** Two-phase: (1) extract article URLs from href, (2) fetch each URL's og:title
- **Speed:** ~2-3s per article (slow!)
- **Extraction:** Phase 1: `re.findall(r'href="(/news/articles/[^"]+)"', html)`. Phase 2: `re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', article_html)`
- **Language:** English
- **Notes:** Next.js rendered. Article page has og:title in `<head>`. Deduplicate URLs with `dict.fromkeys()`.

### arxiv.org/rss/cs.AI
- **Method:** XML ET.parse from RSS feed
- **Speed:** < 2s for 5 items
- **Language:** English (papers)
- **Notes:** Uses subprocess curl (not urllib) due to macOS SSL cert issues. Handle XML namespaces.

## International (5 sources)

### bbc.com/news
- **Method:** Same as bbc.com/news/technology (two-phase)
- **Speed:** ~2-3s per article
- **Language:** English
- **Notes:** Most comprehensive international coverage.

### apnews.com
- **Method:** `extract_h2h3()`, filter for `/article/` or `/live/` in URL
- **Speed:** < 2s for 5 items
- **Language:** English
- **Notes:** 140+ article links on homepage. Excellent source.

### theguardian.com/international
- **Method:** `extract_h2h3()`, filter for `/2026/` or `/live/` in URL
- **Speed:** < 2s
- **Language:** English
- **Notes:** URLs are relative. Must prepend `https://www.theguardian.com`.

### npr.org/sections/news/
- **Method:** `extract_h2h3()`, filter for `/2026/` in URL
- **Speed:** < 2s
- **Language:** English
- **Notes:** US public radio. Good for US-centric international news.

### scmp.com/news
- **Method:** `extract_h2h3()`, filter for `/news/` in URL and exclude `module=` params
- **Speed:** < 2s
- **Language:** English (Hong Kong/Asia focus)
- **Notes:** Section pages mixed in. Must exclude `module=` query params.

## Finance (3 sources)

### cnbc.com/markets/
- **Method:** `extract_h2h3()`, filter for `/2026/` in URL
- **Speed:** < 2s for 5 items
- **Language:** English
- **Notes:** Good mix of market news, stock analysis, macro economics.

### businessinsider.com/markets
- **Method:** `extract_h2h3()`, filter for `/markets/` or `/stock-market-` or `/spacex-` in URL
- **Speed:** < 2s
- **Language:** English
- **Notes:** First result is "Stock Market News" section page — must skip.

### finance.yahoo.com
- **Method:** `extract_h2h3()`, filter for `/markets/` or `/sectors/` or `/articles/` in URL
- **Speed:** < 2s
- **Language:** English
- **Notes:** Fewer articles per page (2-3), but reliable.

## JS-rendered / blocked sources (use web_search only)

| Source | URL | Issue |
|--------|-----|-------|
| Reuters | reuters.com | JS-rendered, curl gets "Please enable JS" message |
| Bloomberg | bloomberg.com | HTTP 403 — CDN/Varnish blocks curl |
| WSJ | wsj.com | HTTP 401 — paywall |
| The Verge | theverge.com | JS-rendered Next.js, no content in HTML |
| Al Jazeera | aljazeera.com | JS-rendered |
| Nikkei 中文 | cn.nikkei.com | JS-rendered |
| Caixin | caixin.com | Login required |
| Jiqizhixin | jiqizhixin.com | HTML heavy, title extraction unreliable |

## Common extraction function (`extract_h2h3`)

```python
def extract_h2h3(html: str, base_url: str) -> list[dict]:
    items = []
    for m in re.finditer(r'<h[23][^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL):
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        title = title.replace('&#x27;', "'").replace('&amp;', '&').replace('&quot;', '"')
        link = m.group(1)
        if not title or len(title) < 15 or len(title) > 150:
            continue
        if any(x in link.lower() for x in ['logo', 'javascript', '#']):
            continue
        if link.startswith('/'):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            link = f"{parsed.scheme}://{parsed.netloc}{link}"
        items.append({"title": title, "url": link})
    return items
```

This pattern works for: arstechnica, techcrunch, wired, apnews, guardian, npr, scmp, cnbc, businessinsider, yahoo-finance.
