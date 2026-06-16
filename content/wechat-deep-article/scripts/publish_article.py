#!/usr/bin/env python3
"""
公众号独立文章发布器 — 从文章 JSON 生成 WeChat 图文并推送到草稿箱。

用法:
  python3 scripts/publish_article.py scripts/.article_2026-06-13_mistral.json

文章 JSON 格式:
  {
    "date": "2026-06-13",
    "title": "文章标题",
    "author": "作者名",
    "digest": "摘要",
    "sections": [
      {"type": "heading", "content": "小标题"},
      {"type": "text", "content": "正文段落..."}
    ],
    "image_sources": ["url1", "url2"],
    "source_links": [{"source": "来源名", "url": "https://..."}]
  }
"""

import json
from datetime import datetime
import os
import re
import ssl
import sys
import urllib.request
from pathlib import Path

# ── 路径 ──────────────────────────────────────────────────────────
SKILL_DIR = Path("/Users/kreiven/.hermes/skills/daily-briefing")
CONFIG_FILE = SKILL_DIR / "scripts" / ".wechat_config.json"
OUTPUT_DIR = SKILL_DIR / "scripts" / ".article_output"

# ── WeChat API ────────────────────────────────────────────────────
WX_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
WX_UPLOAD_IMG_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
WX_UPLOAD_MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
WX_DRAFT_ADD_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"

# ── 样式 ──────────────────────────────────────────────────────────
TITLE_BG = "#1a1a2e"
TITLE_TEXT = "#ffffff"
PAGE_BG = "#f5f5f5"
ARTICLE_BG = "#ffffff"
TEXT_BODY = "#333333"
TEXT_DESC = "#555555"
LINK_COLOR = "#1a73e8"
HIGHLIGHT_BG = "#f0f5ff"
DIVIDER_COLOR = "#e0e0e0"

# ═══════════════════════════════════════════════════════════════════

def log(msg):
    print(f"  ✓ {msg}", file=sys.stderr)

def warn(msg):
    print(f"  ⚠ {msg}", file=sys.stderr)

def step(msg):
    print(f"\n  ► {msg}", file=sys.stderr)

def h(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def _urlopen(url, data=None, timeout=15):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url, data=data,
        headers={"User-Agent": "Mozilla/5.0 Chrome/120"}
    )
    try:
        return urllib.request.urlopen(req, timeout=timeout, context=ctx)
    except Exception:
        return urllib.request.urlopen(req, timeout=timeout, context=ctx)

# ── WeChat API ────────────────────────────────────────────────────

def get_token(cfg):
    url = f"{WX_TOKEN_URL}?grant_type=client_credential&appid={cfg['appid']}&secret={cfg['app_secret']}"
    try:
        resp = _urlopen(url)
        data = json.loads(resp.read())
        if "access_token" in data:
            log(f"access_token 获取成功")
            return data["access_token"]
        warn(f"获取 token 失败: {data}")
    except Exception as e:
        warn(f"token 异常: {e}")
    return None

def upload_img(image_path, token):
    """上传正文图片到微信 CDN，返回 CDN URL。"""
    url = f"{WX_UPLOAD_IMG_URL}?access_token={token}"
    try:
        boundary = "----Boundary7MA4YWxkTrZu0gW"
        with open(image_path, "rb") as f:
            file_data = f.read()
        fname = os.path.basename(image_path)
        body_parts = [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="media"; filename="{fname}"\r\n'.encode(),
            b"Content-Type: image/jpeg\r\n\r\n",
            file_data,
            f"\r\n--{boundary}--\r\n".encode(),
        ]
        body = b"".join(body_parts)
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        resp = urllib.request.urlopen(req, timeout=30, context=ctx)
        result = json.loads(resp.read())
        if "url" in result:
            return result["url"]
        warn(f"上传失败: {result}")
    except Exception as e:
        warn(f"上传异常: {e}")
    return None

def upload_material(image_path, token):
    """上传封面图到素材库，返回 media_id。"""
    url = f"{WX_UPLOAD_MATERIAL_URL}?access_token={token}&type=image"
    try:
        boundary = "----Boundary7MA4YWxkTrZu0gW"
        with open(image_path, "rb") as f:
            file_data = f.read()
        fname = os.path.basename(image_path)
        body_parts = [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="media"; filename="{fname}"\r\n'.encode(),
            b"Content-Type: image/jpeg\r\n\r\n",
            file_data,
            f"\r\n--{boundary}--\r\n".encode(),
        ]
        body = b"".join(body_parts)
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        resp = urllib.request.urlopen(req, timeout=30, context=ctx)
        result = json.loads(resp.read())
        if "media_id" in result:
            return result["media_id"]
        warn(f"封面上传失败: {result}")
    except Exception as e:
        warn(f"封面上传异常: {e}")
    return None

def create_draft(title, html, author, digest, thumb_id, token):
    url = f"{WX_DRAFT_ADD_URL}?access_token={token}"
    body = {
        "articles": [{
            "title": title[:64],
            "author": author[:16],
            "digest": digest[:128],
            "content": html,
            "thumb_media_id": thumb_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
        }]
    }
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    try:
        resp = _urlopen(url, data=data)
        result = json.loads(resp.read())
        if "media_id" in result:
            return result["media_id"]
        warn(f"草稿失败: {result}")
    except Exception as e:
        warn(f"草稿异常: {e}")
    return None

# ── HTML 生成 ─────────────────────────────────────────────────────

def download_img(url, index, cache_dir):
    """下载图片到缓存目录，返回本地路径。"""
    try:
        resp = _urlopen(url)
        data = resp.read()
        ct = resp.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ct: ext = ".png"
        elif "webp" in ct: ext = ".webp"
        path = cache_dir / f"art_img_{index:02d}{ext}"
        with open(path, "wb") as f:
            f.write(data)
        return str(path)
    except Exception:
        return None

def build_article_html(article_data, wx_image_urls):
    """生成公众号文章 HTML。wx_image_urls 是已上传到微信 CDN 的图片 URL 列表。"""
    has_images = bool(wx_image_urls)
    img_idx = 0

    parts = []

    # 封面图（第一张）
    if has_images:
        parts.append(
            f'<div style="margin:0 0 20px;border-radius:10px;overflow:hidden;">'
            f'<img src="{h(wx_image_urls[0])}" alt="cover" style="width:100%;max-width:100%;display:block;border-radius:10px;" /></div>'
        )
        img_idx = 1

    # 摘要
    if article_data.get("digest"):
        parts.append(
            f'<div style="margin:0 0 20px;padding:12px 16px;'
            f'background-color:{HIGHLIGHT_BG};border-radius:8px;'
            f'border-left:3px solid #2563eb;">'
            f'<p style="margin:0;font-size:14px;color:{TEXT_DESC};'
            f'line-height:1.6;">{h(article_data["digest"])}</p></div>'
        )

    # 正文段落
    for sec in article_data["sections"]:
        t = sec["type"]
        c = sec.get("content", "")

        if t == "heading":
            parts.append(
                f'<h2 style="font-size:17px;color:{TEXT_BODY};font-weight:700;'
                f'margin:24px 0 10px;line-height:1.5;">{h(c)}</h2>'
            )

        elif t == "datacard":
            items = sec.get("items", [])
            colors = {
                "purple": ("#667eea", "#764ba2"),
                "red": ("#f093fb", "#f5576c"),
                "blue": ("#4facfe", "#00f2fe"),
                "green": ("#43e97b", "#38f9d7"),
                "orange": ("#fa709a", "#fee140"),
                "teal": ("#11998e", "#38ef7d"),
            }
            cards_html = ""
            for item in items:
                c1, c2 = colors.get(item.get("color", "purple"), colors["purple"])
                cards_html += (
                    f'<div style="flex:1;min-width:100px;background:linear-gradient(135deg,{c1},{c2});'
                    f'border-radius:10px;padding:14px 10px;text-align:center;">'
                    f'<div style="font-size:24px;font-weight:800;color:#fff;letter-spacing:-0.5px;">{h(item["value"])}</div>'
                    f'<div style="font-size:11px;color:rgba(255,255,255,0.8);margin-top:4px;">{h(item["label"])}</div>'
                    f'</div>'
                )
            parts.append(
                f'<div style="display:flex;gap:10px;margin:16px 0;flex-wrap:wrap;">{cards_html}</div>'
            )

        elif t == "quote":
            parts.append(
                f'<div style="position:relative;padding:20px 0;margin:16px 0;text-align:center;'
                f'background:#fafafa;border-radius:10px;">'
                f'<div style="font-size:32px;color:#667eea;opacity:0.2;position:absolute;top:-2px;'
                f'left:50%;transform:translateX(-50%);">&ldquo;</div>'
                f'<p style="font-size:16px;color:{TEXT_BODY};line-height:1.7;font-weight:500;'
                f'margin:0;padding:0 20px;">{h(c)}</p>'
                f'<div style="font-size:32px;color:#667eea;opacity:0.2;position:absolute;'
                f'bottom:-8px;right:50%;transform:translateX(50%);">&rdquo;</div>'
                f'<div style="width:40px;height:2px;background:linear-gradient(90deg,transparent,#667eea,transparent);'
                f'margin:10px auto 0;"></div></div>'
            )

        elif t == "timeline":
            items = sec.get("items", [])
            colors = ["#667eea", "#f5576c", "#ff6b6b", "#4facfe", "#43e97b"]
            tl_html = '<div style="position:relative;padding-left:28px;margin:16px 0;">'
            n = len(items)
            if n > 1:
                tl_html += (
                    f'<div style="position:absolute;left:10px;top:6px;bottom:6px;width:2px;'
                    f'background:linear-gradient(180deg,{",".join(colors[:n])});border-radius:1px;"></div>'
                )
            for i, item in enumerate(items):
                clr = colors[i % len(colors)]
                tl_html += (
                    f'<div style="margin-bottom:16px;position:relative;">'
                    f'<div style="position:absolute;left:-22px;top:2px;width:18px;height:18px;'
                    f'border-radius:50%;background:{clr};color:#fff;font-size:9px;font-weight:700;'
                    f'display:flex;align-items:center;justify-content:center;">{h(item["phase"])}</div>'
                    f'<div style="font-size:12px;color:{clr};font-weight:600;">{h(item["title"])}</div>'
                    f'<div style="font-size:13px;color:{TEXT_DESC};line-height:1.5;margin-top:2px;">{h(item["desc"])}</div>'
                    f'</div>'
                )
            tl_html += '</div>'
            parts.append(tl_html)

        elif t == "compare":
            sides = sec.get("sides", [])
            if len(sides) >= 2:
                colors_map = {"blue": ("#f0f5ff", "#d6e4ff", "#1a73e8"), "green": ("#f0fff4", "#b7eb8f", "#389e0d"),
                              "red": ("#fff1f0", "#ffa39e", "#cf1322"), "orange": ("#fff7e6", "#ffd591", "#d46b08")}
                left = sides[0]; right = sides[1]
                def side_box(s, key):
                    bg, border, txt = colors_map.get(s.get("color", "blue"), colors_map["blue"])
                    pts = "".join(f'<div style="font-size:13px;color:#333;line-height:1.5;">· {h(p)}</div>' for p in s.get("points", []))
                    return (
                        f'<div style="flex:1;background:{bg};border-radius:8px;padding:10px 12px;border:1px solid {border};">'
                        f'<div style="font-size:12px;color:{txt};font-weight:600;margin-bottom:4px;">'
                        f'{s.get("icon","")} {h(s["title"])}</div>{pts}</div>'
                    )
                parts.append(
                    f'<div style="display:flex;gap:10px;margin:16px 0;">{side_box(left,"l")}{side_box(right,"r")}</div>'
                )

        elif t == "infobox":
            styles_map = {
                "info": ("#f0f5ff", "#adc6ff", "#1a73e8"),
                "warning": ("#fff7e6", "#ffd591", "#d46b08"),
                "tip": ("#f0fff4", "#b7eb8f", "#389e0d"),
            }
            st = sec.get("style", "info")
            bg, border, txt = styles_map.get(st, styles_map["info"])
            parts.append(
                f'<div style="background:{bg};border:1px solid {border};border-radius:8px;'
                f'padding:10px 14px;margin:12px 0;">'
                f'<div style="font-size:12px;color:{txt};font-weight:600;">{h(sec.get("title",""))}</div>'
                f'<div style="font-size:14px;color:#333;line-height:1.6;margin-top:4px;">{h(sec.get("content",""))}</div>'
                f'</div>'
            )

        elif t == "highlights":
            items = sec.get("items", [])
            colors_map = {"purple": "#667eea", "red": "#f5576c", "blue": "#4facfe",
                          "green": "#43e97b", "orange": "#fa709a"}
            hl_html = ""
            for item in items:
                clr = colors_map.get(item.get("color", "purple"), "#667eea")
                hl_html += (
                    f'<div style="background:#fafafa;border-radius:6px;padding:8px 12px;'
                    f'border-left:3px solid {clr};">'
                    f'<span style="color:{clr};font-weight:600;font-size:12px;">{h(item["title"])} · </span>'
                    f'<span style="color:#333;font-size:14px;">{h(item["content"])}</span></div>'
                )
            parts.append(
                f'<div style="display:flex;flex-direction:column;gap:6px;margin:14px 0;">{hl_html}</div>'
            )

        elif t == "text":
            # 每2-3段后插一张图
            if has_images and img_idx < len(wx_image_urls):
                # 判断是否该插图：段落包含关键分析内容
                insert_img = False
                keywords = ["风险", "挑战", "全栈", "开源", "主权", "三张", "不言而喻"]
                for kw in keywords:
                    if kw in c:
                        insert_img = True
                        break
                if insert_img:
                    parts.append(
                        f'<div style="margin:16px 0;border-radius:8px;overflow:hidden;">'
                        f'<img src="{h(wx_image_urls[img_idx])}" alt="illustration" '
                        f'style="width:100%;max-width:100%;display:block;border-radius:8px;" /></div>'
                    )
                    img_idx += 1

            # 高亮处理：**关键词** → 蓝色粗体
            import re as _re
            c_hl = _re.sub(r'\*\*(.+?)\*\*', r'<span style="color:#2563eb;font-weight:600;">\1</span>', c)

            parts.append(
                f'<p style="font-size:15px;color:{TEXT_BODY};line-height:1.8;'
                f'margin:0 0 14px;letter-spacing:0.3px;">{c_hl}</p>'
            )

        else:
            # fallback: 未知 type 按 text 渲染
            parts.append(
                f'<p style="font-size:15px;color:{TEXT_BODY};line-height:1.8;'
                f'margin:0 0 14px;letter-spacing:0.3px;">{h(c)}</p>'
            )

    # 分隔线
    parts.append(f'<hr style="border:none;border-top:1px solid {DIVIDER_COLOR};margin:24px 0 16px;" />')

    # 底部
    parts.append(
        f'<div style="margin:20px 0 0;padding:12px 0 0;border-top:1px solid {DIVIDER_COLOR};text-align:center;">'
        f'<p style="font-size:11px;color:#bbb;margin:0;">内容仅供参考 · 不构成投资建议</p></div>'
    )

    body = "\n".join(parts)

    return (
        f'<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
        f'<meta charset="UTF-8">\n'
        f'<meta name="viewport" content="width=device-width, initial-scale=1.0, '
        f'maximum-scale=1.0, user-scalable=no">\n'
        f'<title>{h(article_data["title"])}</title>\n</head>\n'
        f'<body style="margin:0;padding:0;background-color:{PAGE_BG};'
        f'font-family:-apple-system,BlinkMacSystemFont,'
        f'\'Helvetica Neue\',\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">\n'
        f'<div style="max-width:640px;margin:0 auto;padding:16px;'
        f'background-color:{ARTICLE_BG};min-height:100vh;">\n{body}\n'
        f'</div>\n</body>\n</html>'
    )

# ── 主入口 ─────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法: python3 publish_article.py <article.json>", file=sys.stderr)
        sys.exit(1)

    article_path = Path(sys.argv[1])
    if not article_path.exists():
        print(f"❌ 找不到文章文件: {article_path}", file=sys.stderr)
        sys.exit(1)

    with open(article_path, "r", encoding="utf-8") as f:
        article_data = json.load(f)

    print(f"\n📰 发布公众号文章", file=sys.stderr)
    log(f"标题: {article_data['title'][:50]}...")

    # 保存来源链接到同目录下的 .md 文件
    sources_md = f"# 素材来源 — {article_data['title']}\n\n"
    sources_md += f"**事件日期**：{article_data.get('event_date', article_data['date'])}\n\n"
    sources_md += "| 来源 | URL |\n|------|-----|\n"
    for link in article_data.get("source_links", []):
        sources_md += f"| {link['source']} | {link['url']} |\n"
    sources_md += f"\n_生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"
    sources_path = article_path.with_suffix(".sources.md")
    with open(sources_path, "w", encoding="utf-8") as f:
        f.write(sources_md)
    log(f"来源: {sources_path.name}")

    # 读取凭据
    if not CONFIG_FILE.exists():
        print("❌ 未配置公众号凭据。请先运行 python3 scripts/wechat_article.py --setup", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)

    token = get_token(cfg)
    if not token:
        sys.exit(1)

    # 下载并上传配图
    cache_dir = SKILL_DIR / "scripts" / ".img_cache" / f"article_{article_data['date']}"
    cache_dir.mkdir(parents=True, exist_ok=True)

    step("上传配图到微信 CDN...")
    wx_urls = []
    for i, img_src in enumerate(article_data.get("image_sources", [])):
        log(f"[{i+1}/{len(article_data.get('image_sources', []))}] 下载并上传...")
        local = download_img(img_src, i + 1, cache_dir)
        if local:
            wx_url = upload_img(local, token)
            if wx_url:
                wx_urls.append(wx_url)

    # 封面图：用第一张
    step("上传封面图...")
    thumb_id = None
    if wx_urls:
        first_local = cache_dir / f"art_img_01.jpg"
        if first_local.exists():
            thumb_id = upload_material(str(first_local), token)
        elif cache_dir.exists():
            # 找第一张存在的图片
            for f in sorted(cache_dir.iterdir()):
                if f.is_file():
                    thumb_id = upload_material(str(f), token)
                    break

    # 生成 HTML
    step("生成文章 HTML...")
    html = build_article_html(article_data, wx_urls)

    # 保存本地副本
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = article_data["date"]
    # 文件名：用标题前20字
    safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', article_data["title"])[:20]
    out = OUTPUT_DIR / f"article_{date_str}_{safe_title}.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"本地备份: {out}")

    # 创建草稿
    step("创建公众号草稿...")
    mid = create_draft(
        title=article_data["title"],
        html=html,
        author=article_data.get("author", "Hermes 简报"),
        digest=article_data.get("digest", ""),
        thumb_id=thumb_id or "",
        token=token,
    )

    if mid:
        print(f"\n  ✅ 文章发布成功！", file=sys.stderr)
        print(f"    标题: {article_data['title']}", file=sys.stderr)
        print(f"    图片: {len(wx_urls)} 张", file=sys.stderr)
        print(f"    media_id: {mid}", file=sys.stderr)
        print(f"    查看: mp.weixin.qq.com → 草稿箱", file=sys.stderr)
    else:
        print(f"\n  ❌ 发布失败", file=sys.stderr)
        print(f"     本地 HTML 已保存: {out}", file=sys.stderr)

if __name__ == "__main__":
    main()
