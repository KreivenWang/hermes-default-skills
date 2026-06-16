#!/usr/bin/env python3
"""
公众号文章生成器 — 将每日简报输出为 WeChat 兼容的 HTML 图文。

用法:
  python3 scripts/wechat_article.py                     # 生成 HTML 到桌面
  python3 scripts/wechat_article.py --date 2026-06-13   # 指定日期
  python3 scripts/wechat_article.py --open              # 生成后自动浏览器打开
  python3 scripts/wechat_article.py --no-images          # 纯文字版
  python3 scripts/wechat_article.py --publish            # 生成并推送到公众号草稿箱

首次发布需要配置凭据:
  1. 登录 mp.weixin.qq.com → 开发 → 基本配置 → 获取 AppID 和 AppSecret
  2. 设置白名单 IP: mp.weixin.qq.com → 开发 → 基本配置 → IP 白名单
     (运行 curl -s ifconfig.me 查看本机外网 IP)
  3. 运行 python3 scripts/wechat_article.py --setup   # 交互式配置 AppID/Secret

零外部依赖（仅 Python 3 标准库）。
"""

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

# ── 路径配置 ──────────────────────────────────────────────────────
SKILL_DIR = Path("/Users/kreiven/.hermes/profiles/public-daily-news/skills/daily-briefing")
REFERENCES = SKILL_DIR / "references"
OUTPUT_DIR = Path("/Users/kreiven/Desktop")
CONFIG_FILE = SKILL_DIR / "scripts" / ".wechat_config.json"
IMG_CACHE_DIR = SKILL_DIR / "scripts" / ".img_cache"
DATE_FORMAT = "%Y-%m-%d"

# ── WeChat API 端点 ───────────────────────────────────────────────
WX_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
WX_UPLOAD_IMG_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
WX_UPLOAD_MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
WX_DRAFT_ADD_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"

# ── 公众号排版配色 ────────────────────────────────────────────────
TITLE_BG = "#1a1a2e"
TITLE_TEXT = "#ffffff"
CAT_BLUE = "#2563eb"
CAT_PURPLE = "#7c3aed"
CAT_RED = "#dc2626"
PAGE_BG = "#f5f5f5"
ARTICLE_BG = "#ffffff"
TEXT_BODY = "#333333"
TEXT_DESC = "#555555"
TEXT_SOURCE = "#888888"
LINK_COLOR = "#1a73e8"
ITEM_BG = "#fafafa"


# ═══════════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════════

def log(msg):
    print(f"  ✓ {msg}", file=sys.stderr)


def warn(msg):
    print(f"  ⚠ {msg}", file=sys.stderr)


def step(msg):
    print(f"\n  ► {msg}", file=sys.stderr)


def h(s):
    """HTML 转义"""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _urlopen(url, data=None, timeout=15):
    """urllib 封装，跳过 SSL 验证。"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        },
    )
    try:
        return urllib.request.urlopen(req, timeout=timeout, context=ctx)
    except Exception:
        return urllib.request.urlopen(req, timeout=timeout, context=ctx)


# ═══════════════════════════════════════════════════════════════════
# 配置管理
# ═══════════════════════════════════════════════════════════════════

def load_config():
    """读取 WeChat 凭据配置。"""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(cfg):
    """保存 WeChat 凭据配置。"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    # 不输出明文到日志
    safe = {k: v for k, v in cfg.items() if k != "app_secret"}
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    log(f"配置已保存到 {CONFIG_FILE} (安全字段已隐藏)")
    log(f"内容: {json.dumps(safe)}")


def setup_interactive():
    """交互式配置 AppID / AppSecret。"""
    print("\n📝 公众号 API 配置", file=sys.stderr)
    print("=" * 40, file=sys.stderr)
    print("请登录 mp.weixin.qq.com → 开发 → 基本配置 查看以下信息：", file=sys.stderr)
    print("", file=sys.stderr)

    appid = input("AppID: ").strip()
    secret = input("AppSecret: ").strip()

    if not appid or not secret:
        print("❌ AppID 和 AppSecret 不能为空", file=sys.stderr)
        sys.exit(1)

    cfg = {"appid": appid, "app_secret": secret}

    # 测试 token 获取
    step("测试 AppID/AppSecret...")
    token = get_access_token(cfg, force=True)
    if token:
        log("✅ 凭据验证通过！")
        save_config(cfg)
        print(f"\n  下一步：将本机 IP 添加到微信 IP 白名单：", file=sys.stderr)
        print(f"    mp.weixin.qq.com → 开发 → 基本配置 → IP 白名单", file=sys.stderr)
        print(f"    本机 IP: {get_my_ip()}", file=sys.stderr)
    else:
        print("\n❌ 凭据验证失败，请检查 AppID 和 AppSecret 是否正确", file=sys.stderr)
        print("  常见问题：", file=sys.stderr)
        print("  1. AppSecret 可能被重置过，去公众号后台重新生成", file=sys.stderr)
        print("  2. 开发者密码(AppSecret) 需要启用", file=sys.stderr)
        sys.exit(1)


def get_my_ip():
    """获取本机外网 IP。"""
    try:
        resp = _urlopen("https://ifconfig.me", timeout=5)
        return resp.read().decode().strip()
    except Exception:
        try:
            resp = _urlopen("https://api.ipify.org", timeout=5)
            return resp.read().decode().strip()
        except Exception:
            return "(无法获取，请手动查看)"


# ═══════════════════════════════════════════════════════════════════
# WeChat API 调用
# ═══════════════════════════════════════════════════════════════════

def get_access_token(cfg, force=False):
    """获取 access_token，失败返回 None。"""
    url = f"{WX_TOKEN_URL}?grant_type=client_credential&appid={cfg['appid']}&secret={cfg['app_secret']}"
    try:
        resp = _urlopen(url)
        data = json.loads(resp.read())
        if "access_token" in data:
            token = data["access_token"]
            log(f"access_token 获取成功 (有效期{data.get('expires_in', 7200)}秒)")
            return token
        else:
            warn(f"获取 token 失败: {data}")
            return None
    except Exception as e:
        warn(f"token 请求异常: {e}")
        return None


def upload_image_to_wechat(image_path, token):
    """
    上传图片到微信图文素材（不占素材库配额）。
    返回 CDN URL（如 http://mmbiz.qpic.cn/...），失败返回 None。
    图片限制: < 1MB, jpg/png
    """
    url = f"{WX_UPLOAD_IMG_URL}?access_token={token}"
    try:
        import http.client
        # 手动构造 multipart/form-data
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        file_name = os.path.basename(image_path)
        with open(image_path, "rb") as f:
            file_data = f.read()

        body_parts = []
        body_parts.append(f"--{boundary}\r\n".encode())
        body_parts.append(
            f'Content-Disposition: form-data; name="media"; filename="{file_name}"\r\n'.encode()
        )
        body_parts.append(f"Content-Type: image/jpeg\r\n\r\n".encode())
        body_parts.append(file_data)
        body_parts.append(f"\r\n--{boundary}--\r\n".encode())
        body = b"".join(body_parts)

        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        resp = urllib.request.urlopen(req, timeout=30, context=ctx)
        result = json.loads(resp.read())
        if "url" in result:
            img_url = result["url"]
            log(f"上传成功 → {img_url[:80]}...")
            return img_url
        else:
            warn(f"上传失败: {result}")
            return None
    except Exception as e:
        warn(f"上传异常 ({image_path}): {e}")
        return None


def upload_cover_to_material(image_path, token):
    """
    上传封面图到永久素材库。
    返回 media_id（供 draft/add 的 thumb_media_id），失败返回 None。
    """
    url = f"{WX_UPLOAD_MATERIAL_URL}?access_token={token}&type=image"
    try:
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        file_name = os.path.basename(image_path)
        with open(image_path, "rb") as f:
            file_data = f.read()

        body_parts = []
        body_parts.append(f"--{boundary}\r\n".encode())
        body_parts.append(
            f'Content-Disposition: form-data; name="media"; filename="{file_name}"\r\n'.encode()
        )
        body_parts.append(f"Content-Type: image/jpeg\r\n\r\n".encode())
        body_parts.append(file_data)
        body_parts.append(f"\r\n--{boundary}--\r\n".encode())
        body = b"".join(body_parts)

        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        resp = urllib.request.urlopen(req, timeout=30, context=ctx)
        result = json.loads(resp.read())
        if "media_id" in result:
            log(f"封面图 media_id: {result['media_id'][:40]}...")
            return result["media_id"]
        else:
            warn(f"封面上传失败: {result}")
            return None
    except Exception as e:
        warn(f"封面上传异常: {e}")
        return None


def create_draft(title, html_content, author, digest, thumb_media_id, token):
    """
    创建公众号草稿。返回 media_id，失败返回 None。
    """
    url = f"{WX_DRAFT_ADD_URL}?access_token={token}"
    body = {
        "articles": [
            {
                "title": title[:64],
                "author": author[:16] if author else "",
                "digest": digest[:128] if digest else "",
                "content": html_content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }
        ]
    }
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    try:
        resp = _urlopen(url, data=data)
        result = json.loads(resp.read())
        if "media_id" in result:
            log(f"草稿创建成功！media_id: {result['media_id']}")
            return result["media_id"]
        else:
            warn(f"草稿创建失败: {result}")
            return None
    except Exception as e:
        warn(f"草稿创建异常: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════
# 简报解析
# ═══════════════════════════════════════════════════════════════════

def parse_briefing(audit_path, links_path):
    """解析审计文件 + 链接文件。"""
    with open(audit_path, "r", encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f]

    links_map = {}
    if links_path and links_path.exists():
        with open(links_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                m = re.match(r'(AI|国际|金融)\s*\|\s*【(.+?)】(.+)', line)
                if m:
                    links_map[(m.group(1), m.group(2))] = m.group(3).strip()

    date_str = ""
    categories = []
    current_cat = None
    cat_map = {"🌐": "国际", "🤖": "AI", "💰": "金融"}
    cat_key = {"🌐": "international", "🤖": "ai", "💰": "finance"}
    pending_desc = None

    for line in lines:
        m = re.match(r'📰\s*每日简报\s*[—\-]\s*(\d{4}-\d{2}-\d{2})', line)
        if m:
            date_str = m.group(1)
            continue

        is_cat = False
        stripped = line.strip()
        for emoji, name in cat_map.items():
            if stripped.startswith(emoji):
                current_cat = {"name": name, "emoji": emoji, "key": cat_key[emoji], "items": []}
                categories.append(current_cat)
                is_cat = True
                pending_desc = None
                break
        if is_cat:
            continue
        if current_cat is None:
            continue

        m2 = re.match(r'•\s*【(.+?)】\s*(.*)', line)
        if m2:
            title = m2.group(1)
            inline_desc = m2.group(2).strip()
            if inline_desc:
                source = ""
                src_m = re.search(r'\((.+?)\)\s*$', inline_desc)
                if src_m:
                    source = src_m.group(1)
                    inline_desc = inline_desc[:src_m.start()].strip()
                url = links_map.get((current_cat["name"], source), "")
                current_cat["items"].append({
                    "title": title, "desc": inline_desc,
                    "source": source, "url": url,
                    "image_local": None, "image_wx": None,
                })
            else:
                pending_desc = {"cat": current_cat, "title": title}
            continue

        if pending_desc is not None and line.startswith("  ") and stripped:
            cat = pending_desc["cat"]
            title = pending_desc["title"]
            desc = stripped
            source = ""
            src_m = re.search(r'\((.+?)\)\s*$', desc)
            if src_m:
                source = src_m.group(1)
                desc = desc[:src_m.start()].strip()
            url = links_map.get((cat["name"], source), "")
            cat["items"].append({
                "title": title, "desc": desc,
                "source": source, "url": url,
                "image_local": None, "image_wx": None,
            })
            pending_desc = None

    return {"date": date_str, "categories": categories}


def fetch_og_image(url):
    """从新闻原文提取 og:image。"""
    try:
        resp = _urlopen(url)
        html = resp.read().decode("utf-8", errors="replace")
        patterns = [
            r'<meta\s+[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
            r'<meta\s+[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']',
        ]
        for pat in patterns:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                img_url = m.group(1)
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif img_url.startswith("/"):
                    parsed = urllib.parse.urlparse(url)
                    img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
                return img_url
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
        for img in imgs:
            if any(kw in img.lower() for kw in ("hero", "featured", "main", "large", "header", "banner")):
                if img.startswith("//"):
                    img = "https:" + img
                elif img.startswith("/"):
                    parsed = urllib.parse.urlparse(url)
                    img = f"{parsed.scheme}://{parsed.netloc}{img}"
                return img
    except Exception:
        pass
    return None


def download_image(img_url, index, output_dir):
    """下载图片到本地。"""
    try:
        resp = _urlopen(img_url)
        data = resp.read()
        ct = resp.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "jpeg" in ct or "jpg" in ct:
            ext = ".jpg"
        elif "svg" in ct:
            ext = ".svg"
        local_path = output_dir / f"news_img_{index:02d}{ext}"
        with open(local_path, "wb") as f:
            f.write(data)
        return str(local_path)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════
# HTML 生成
# ═══════════════════════════════════════════════════════════════════

def build_html(data, use_wx_images=False):
    """生成公众号 HTML。use_wx_images=True 时使用微信 CDN 链接替换本地。"""
    cat_color_map = {"国际": CAT_BLUE, "AI": CAT_PURPLE, "金融": CAT_RED}

    title_block = (
        f'<div style="background-color:{TITLE_BG};border-radius:12px;'
        f'padding:28px 20px 20px;margin:0 0 20px;text-align:center;">'
        f'<h1 style="font-size:22px;color:{TITLE_TEXT};font-weight:700;'
        f'margin:0 0 4px;letter-spacing:2px;">📰 每日简报</h1>'
        f'<p style="font-size:14px;color:rgba(255,255,255,0.75);'
        f'margin:0;letter-spacing:1px;">{h(data["date"])}</p></div>'
    )

    sections = []
    for cat in data["categories"]:
        cc = cat_color_map.get(cat["name"], CAT_BLUE)
        parts = []

        parts.append(
            f'<div style="display:flex;align-items:center;margin:28px 0 14px;'
            f'padding:0 0 10px;border-bottom:2px solid {cc};">'
            f'<h2 style="font-size:18px;color:{cc};font-weight:700;'
            f'margin:0;letter-spacing:1px;">{cat["emoji"]} {h(cat["name"])}</h2>'
            f'<span style="font-size:12px;color:{TEXT_SOURCE};margin-left:8px;">'
            f'· {len(cat["items"])} 条</span></div>'
        )

        for item in cat["items"]:
            # 选择图片源
            img_src = item.get("image_wx") if use_wx_images else item.get("image_local")
            img_block = ""
            if img_src:
                img_block = (
                    f'<div style="margin:12px 0 10px;border-radius:8px;overflow:hidden;">'
                    f'<img src="{h(img_src)}" alt="{h(item["title"])}" '
                    f'style="width:100%;max-width:100%;display:block;'
                    f'border-radius:8px;" /></div>'
                )

            source_html = ""
            if item["url"]:
                source_html = (
                    f'<a href="{h(item["url"])}" '
                    f'style="color:{LINK_COLOR};text-decoration:none;font-size:13px;">'
                    f'{h(item["source"])} ↗</a>'
                )
            elif item["source"]:
                source_html = (
                    f'<span style="color:{TEXT_SOURCE};font-size:13px;">'
                    f'{h(item["source"])}</span>'
                )

            parts.append(
                f'<div style="margin-bottom:18px;padding:14px 16px;'
                f'background-color:{ITEM_BG};border-radius:10px;'
                f'border-left:3px solid {cc};">'
                f'{img_block}'
                f'<p style="margin:0 0 6px;font-size:15px;font-weight:600;'
                f'color:{TEXT_BODY};line-height:1.5;">{h(item["title"])}</p>'
                f'<p style="margin:0 0 8px;font-size:14px;color:{TEXT_DESC};'
                f'line-height:1.7;letter-spacing:0.3px;">{h(item["desc"])}</p>'
                f'<p style="margin:0;font-size:13px;color:{TEXT_SOURCE};">'
                f'{source_html}</p></div>'
            )

        sections.append("\n".join(parts))

    footer = (
        f'<div style="margin:30px 0 0;padding:16px 0 0;'
        f'border-top:1px solid #e0e0e0;text-align:center;">'
        f'<p style="font-size:12px;color:{TEXT_SOURCE};margin:0 0 4px;">'
        f'每日简报 · 由 Hermes Agent 自动生成</p>'
        f'<p style="font-size:12px;color:{TEXT_SOURCE};margin:0;">{h(data["date"])}</p></div>'
    )

    return (
        f'<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
        f'<meta charset="UTF-8">\n'
        f'<meta name="viewport" content="width=device-width, initial-scale=1.0, '
        f'maximum-scale=1.0, user-scalable=no">\n'
        f'<title>每日简报 {h(data["date"])}</title>\n</head>\n'
        f'<body style="margin:0;padding:0;background-color:{PAGE_BG};'
        f'font-family:-apple-system,BlinkMacSystemFont,'
        f'\'Helvetica Neue\',\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">\n'
        f'<div style="max-width:640px;margin:0 auto;padding:16px;'
        f'background-color:{ARTICLE_BG};min-height:100vh;">\n'
        f'{title_block}\n'
        f'{"".join(sections)}\n'
        f'{footer}\n'
        f'</div>\n</body>\n</html>'
    )


# ═══════════════════════════════════════════════════════════════════
# 发布到公众号
# ═══════════════════════════════════════════════════════════════════

def publish_to_wechat(data, date_str, cfg):
    """将简报发布为公众号草稿。"""
    step("获取 access_token...")
    token = get_access_token(cfg)
    if not token:
        print("  ❌ 无法获取 access_token，请检查凭据配置", file=sys.stderr)
        return False

    step("上传正文图片到微信 CDN...")
    total = sum(len(c["items"]) for c in data["categories"])
    idx = 1
    for cat in data["categories"]:
        for item in cat["items"]:
            local = item.get("image_local")
            if local and os.path.exists(local):
                log(f"[{idx}/{total}] {cat['name']} → {item['title'][:30]}...")
                wx_url = upload_image_to_wechat(local, token)
                if wx_url:
                    item["image_wx"] = wx_url
            idx += 1

    step("准备封面图...")
    # 用第一条新闻的配图做封面
    cover_local = None
    for cat in data["categories"]:
        for item in cat["items"]:
            if item.get("image_local") and os.path.exists(item["image_local"]):
                cover_local = item["image_local"]
                break
        if cover_local:
            break

    thumb_media_id = None
    if cover_local:
        log(f"上传封面: {cover_local}")
        thumb_media_id = upload_cover_to_material(cover_local, token)

    if not thumb_media_id:
        warn("封面图上传失败，使用默认封面（推文将无封面图，后台可补传）")

    step("创建草稿...")
    html_content = build_html(data, use_wx_images=True)
    title = f"📰 每日简报 — {date_str}"

    # 摘要：取前两条的简介核心
    digest_parts = []
    for cat in data["categories"]:
        for item in cat["items"][:1]:
            # 取前15字就够了
            short = item["desc"][:30]
            digest_parts.append(f"{cat['name']} {short}")
    digest = " · ".join(digest_parts)[:100]

    author = "Hermes 简报"

    media_id = create_draft(title, html_content, author, digest, thumb_media_id or "", token)

    if media_id:
        print(f"\n  ✅ 草稿发布成功！", file=sys.stderr)
        print(f"    标题: {title}", file=sys.stderr)
        print(f"    摘要: {digest}", file=sys.stderr)
        print(f"    查看: mp.weixin.qq.com → 草稿箱", file=sys.stderr)
        print(f"    media_id: {media_id}", file=sys.stderr)
        return True
    else:
        print("  ❌ 草稿创建失败", file=sys.stderr)
        return False


# ═══════════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="公众号文章生成器")
    parser.add_argument("--date", default="",
                        help=f"日期 (默认: 自动查找, 格式: {DATE_FORMAT})")
    parser.add_argument("--open", action="store_true", help="生成后用浏览器打开")
    parser.add_argument("--no-images", action="store_true", help="跳过配图")
    parser.add_argument("--publish", action="store_true",
                        help="生成并推送到公众号草稿箱")
    parser.add_argument("--setup", action="store_true",
                        help="交互式配置 AppID/AppSecret")
    args = parser.parse_args()

    # 配置模式
    if args.setup:
        setup_interactive()
        return

    # 确定日期
    date_str = args.date
    if not date_str:
        for d in range(3):
            candidate = (date.today() - timedelta(days=d)).strftime(DATE_FORMAT)
            if (REFERENCES / f"{candidate}-audit.md").exists():
                date_str = candidate
                break
        if not date_str:
            print("❌ 找不到简报文件。请指定 --date YYYY-MM-DD", file=sys.stderr)
            sys.exit(1)
    else:
        if not (REFERENCES / f"{date_str}-audit.md").exists():
            print(f"❌ 未找到 {date_str} 的简报文件", file=sys.stderr)
            sys.exit(1)

    audit_path = REFERENCES / f"{date_str}-audit.md"
    links_path = REFERENCES / f"{date_str}-links.md"

    print(f"\n📰 生成公众号文章 — {date_str}\n", file=sys.stderr)
    log(f"审计: {audit_path.name}")
    log(f"链接: {links_path.name}")

    # 解析
    data = parse_briefing(audit_path, links_path)
    total = sum(len(c["items"]) for c in data["categories"])
    log(f"解析: {total} 条 / {len(data['categories'])} 个类目")

    # 搜索配图
    output_dir = IMG_CACHE_DIR / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.no_images:
        step("搜索新闻配图 (og:image)...")
        idx = 1
        for cat in data["categories"]:
            for item in cat["items"]:
                title_short = item["title"][:30]
                log(f"[{idx}/{total}] {cat['name']} — {title_short}...")
                if item["url"]:
                    img_url = fetch_og_image(item["url"])
                    if img_url:
                        local = download_image(img_url, idx, output_dir)
                        if local:
                            item["image_local"] = local
                idx += 1

    # --publish 模式
    if args.publish:
        cfg = load_config()
        if not cfg.get("appid") or not cfg.get("app_secret"):
            print("", file=sys.stderr)
            print("❌ 未配置公众号凭据。请先运行:", file=sys.stderr)
            print("   python3 scripts/wechat_article.py --setup", file=sys.stderr)
            sys.exit(1)
        publish_to_wechat(data, date_str, cfg)
        # 也生成本地 HTML 备份
        html_local = build_html(data, use_wx_images=False)
        out_local = OUTPUT_DIR / f"每日简报_{date_str}.html"
        with open(out_local, "w", encoding="utf-8") as f:
            f.write(html_local)
        log(f"本地备份: {out_local}")
        return

    # 本地 HTML 模式
    html = build_html(data, use_wx_images=False)
    out = OUTPUT_DIR / f"每日简报_{date_str}.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out) / 1024
    log(f"已保存: {out} ({size_kb:.0f} KB)")

    print(f"\n📋 使用方法:", file=sys.stderr)
    print(f"   1. open {out}", file=sys.stderr)
    print(f"   2. Cmd+A 全选 → Cmd+C 复制", file=sys.stderr)
    print(f"   3. 公众号编辑器 → 源码模式 → 粘贴 → 保存", file=sys.stderr)
    if args.publish:
        pass  # already handled above
    elif not args.no_images and not args.publish:
        print(f"", file=sys.stderr)
        print(f"   💡 配好凭据后，可直接推送到草稿箱:", file=sys.stderr)
        print(f"      python3 scripts/wechat_article.py --setup", file=sys.stderr)
        print(f"      python3 scripts/wechat_article.py --publish", file=sys.stderr)

    if args.open:
        subprocess.run(["open", str(out)])


if __name__ == "__main__":
    main()
