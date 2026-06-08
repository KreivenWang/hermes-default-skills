# 新闻来源 curl 可访问性测试方法论

当需要为简报添加新来源时，按此流程系统测试 curl 能否提取文章。

## 快速测试脚本

```python
import subprocess, re

def test_source(name: str, url: str):
    result = subprocess.run(
        ["curl", "-sL", "--max-time", "10", "-A",
         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", url],
        capture_output=True, text=True, timeout=15
    )
    html = result.stdout
    size = len(html)

    # 1. 基本检查
    blocked = "enable js" in html[:500].lower() or "captcha" in html[:500].lower()
    has_title = bool(re.search(r'<title>([^<]+)</title>', html))

    # 2. 统计文章链接数
    article_urls = len(set(re.findall(r'href="[^"]*/(2026|2025|article|story|news|p/|live/)[^"]+"', html)))

    # 3. 尝试 h2/h3 提取
    h2h3 = re.findall(r'<h[23][^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    valid = [(l, t) for l, t in h2h3
             if re.sub(r'<[^>]+>', '', t).strip()
             and len(re.sub(r'<[^>]+>', '', t).strip()) > 15]

    # 4. 尝试 og:title
    og_titles = re.findall(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html)

    # 5. 判断 Next.js 嵌入数据
    has_next_data = bool(re.search(r'__NEXT_DATA__', html))

    print(f"\n{'='*50}")
    print(f"📌 {name}  ({url})")
    print(f"   大小: {size:>7}B | 标题: {has_title} | 文章链接: {article_urls:>3}")
    print(f"   阻塞: {blocked} | Next.js: {has_next_data} | og:title: {len(og_titles)}")
    print(f"   h2/h3有效: {len(valid)}")

    # 结论
    if blocked or size < 2000:
        status = "🚫 JS渲染或反爬 — 需 web_search"
    elif len(valid) >= 3:
        status = "✅ 可用 — h2/h3 提取"
    elif article_urls >= 3:
        status = "⚠️ 有文章链接，需逐个请求 og:title"
    else:
        status = "❌ 不可用"

    print(f"   结论: {status}")

    # 展示第一条有效标题
    if valid:
        t = re.sub(r'<[^>]+>', '', valid[0][1]).strip()
        print(f"   首条: {t[:80]}")
```

## 判断树

```
开始 → curl -sL URL
  │
  ├─ 返回 < 2KB 或含 "enable javascript"?
  │     → 🚫 JS渲染/反爬，标记为 web_search 源
  │
  ├─ h2h3 提取 ≥3 条有效标题?
  │     → ✅ 单次请求即可，用 extract_h2h3() 
  │
  ├─ 有大量 /article/ 或 /news/ 路径?
  │     → ⚠️ 提取 URL 列表，逐个请求 og:title（两阶段法）
  │       ├─ og:title 存在 → ✅ 可用（如 BBC）
  │       └─ og:title 不存在 → ❌ JS渲染
  │
  ├─ 有 __NEXT_DATA__ 嵌入?
  │     → ⚠️ Next.js，尝试 JSON 解析提取文章数据
  │
  └─ 以上都不行?
        → ❌ 标记为不可用
```

## 三阶段提取模式

### Phase 1: 单请求提取（最快，< 2s）
适用站点：leiphone, arstechnica, techcrunch, wired, apnews, guardian, npr, scmp, cnbc, businessinsider, yahoo-finance

```python
def extract_h2h3(html, base_url):
    """从 h2/h3 内的 <a> 提取标题+URL"""
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

**过滤规则**（因站而异）：
| 站点 | 过滤条件 | 原因 |
|------|----------|------|
| techcrunch | 排除 link == homepage | 首条是 logo 链接 |
| wired | 保留 `/story/` 路径 | 混了 `/topic/` 栏目页 |
| apnews | 保留 `/article/` 或 `/live/` | 混了栏目导航 |
| guardian | 保留 `/2026/` 或 `/live/` | 混了栏目名 |
| cnbc | 保留 `/2026/` | 混了 `/markets/` 栏目页 |
| businessinsider | 保留 `/markets/` 或 `/stock-market-` | 首条是栏目页 |

### Phase 2: 两阶段法（慢，2-3s/条）
适用站点：BBC (bbc.com/news, bbc.com/news/technology)

```python
# Phase 1: 从列表页提取所有文章URL
urls = list(dict.fromkeys(
    f"https://www.bbc.com{u}" for u in re.findall(r'href="(/news/articles/[^"]+)"', html)
))

# Phase 2: 逐个请求获取 og:title
for url in urls[:max_items]:
    ah = curl_get(url)
    m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', ah)
    if m:
        items.append({"title": m.group(1), "url": url})
```

**为何慢？** 每个 URL 需单独 HTTP 请求。BBC 首页可提取 15+ 个文章 URL，逐个请求就是 30-45s。

### Phase 3: XML RSS
适用站点：arXiv (arxiv.org/rss/cs.AI)

```python
root = ET.fromstring(xml_data)
for item in root.findall(".//item"):
    title = item.find("title").text
    link = item.find("link").text
    items.append({"title": title, "url": link})
```

注意：用 subprocess curl 而非 urllib（macOS 有 SSL 证书问题）。

## 被阻塞站点处理

如果 curl 返回 HTTP 4xx/5xx 或 "Please enable JS"：

1. 不要反复重试——说明网站有反爬/JS渲染
2. 标记为 web_search 源
3. 在 source 表格中注明原因（JS渲染 / 反爬CDN / 付费墙 / 需登录）

已知被阻塞：
- bloomberg.com → 403 (Varnish CDN)
- wsj.com → 401 (付费墙)
- reuters.com → "Please enable JS" (JS渲染)
- theverge.com → JS渲染 (Next.js 无内容)
- aljazeera.com → JS渲染
- cn.nikkei.com → JS渲染
- caixin.com → 需登录
- jiqizhixin.com → HTML 可拿但标题提取不可靠

## 集成到脚本

新源验证通过后，在 `fetch_sources.py` 中添加：

1. 写一个 `fetch_<name>(max_items=N)` 函数，返回 `list[dict]`
2. 在 `SOURCES` 字典的对应类目列表里注册
3. 更新 `sources-reference.md` 和 `source-accessibility.md`
4. 运行 `python3 fetch_sources.py <category>` 确认输出正常
