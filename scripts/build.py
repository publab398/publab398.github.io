#!/usr/bin/env python3
"""Build the public site from explicit assets, JSON configuration and Markdown."""

import datetime as dt
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
from string import Template
import tomllib
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
SITE = json.loads((ROOT / "config/site.json").read_text(encoding="utf-8"))
SITE_ZONE = ZoneInfo(SITE.get("timezone", "Asia/Tokyo"))
PROJECTS = json.loads((ROOT / "config/projects.json").read_text(encoding="utf-8"))
MD = MarkdownIt("commonmark", {"html": False}).enable("table")
ROUTES = []


def asset_url(match):
    path = match.group(2)
    asset = ROOT / "public" / path.lstrip("/")
    if not asset.is_file():
        return match.group(0)
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
    return f"{match.group(1)}{path}?v={digest}{match.group(3)}"


def esc(value):
    return html.escape(str(value), quote=True)


def template(template_name, **values):
    source = (ROOT / "templates" / f"{template_name}.html").read_text(encoding="utf-8")
    return Template(source).substitute(values)


def date_text(value):
    return dt.date.fromisoformat(value).strftime("%Y.%m.%d")


def nav(project):
    base = f'/{project["slug"]}/'
    items = [
        ("about", "ゲーム紹介"),
        ("download", "ダウンロード"),
        ("features", "マップ・武器"),
        ("news", "お知らせ"),
    ]
    links = "".join(f'<a href="{base}#{key}">{label}</a>' for key, label in items)
    return f'<nav class="project-nav" aria-label="{esc(project["name"])} メニュー">{links}</nav>'


def breadcrumbs(items):
    parts = [
        (
            f'<li><a href="{esc(url)}">{esc(label)}</a></li>'
            if url
            else f'<li aria-current="page">{esc(label)}</li>'
        )
        for label, url in items
    ]
    return (
        '<nav aria-label="パンくず"><ol class="breadcrumbs">'
        + "".join(parts)
        + "</ol></nav>"
    )


def page(route, title, description, body):
    canonical = (
        ""
        if route == "/404.html"
        else f'<link rel="canonical" href="{esc(SITE["url"] + route)}">'
    )
    output = template(
        "base",
        title=esc(title),
        description=esc(description),
        canonical=canonical,
        body=body,
        home_current=' aria-current="page"' if route == "/" else "",
        project_current=' aria-current="page"' if route == "/project-cdx/" else "",
    )
    output = re.sub(r'(\b(?:src|href)=")(/assets/[^"?]+)(")', asset_url, output)
    destination = OUT / (
        route.lstrip("/") + "index.html" if route.endswith("/") else route.lstrip("/")
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output, encoding="utf-8")
    if route != "/404.html":
        ROUTES.append(route)


def load_entries(project, kind):
    entries = []
    directory = ROOT / "content" / project["slug"] / kind
    for source in sorted(directory.glob("*.md")):
        raw = source.read_text(encoding="utf-8")
        sections = raw.split("+++", 2)
        if len(sections) != 3 or sections[0].strip():
            raise ValueError(f"{source}: +++ TOML metadata is required")
        metadata = tomllib.loads(sections[1])
        for key in ("title", "date", "summary"):
            if not isinstance(metadata.get(key), str) or not metadata[key].strip():
                raise ValueError(f"{source}: {key} must be a nonempty string")
        date_text(metadata["date"])
        published = dt.datetime.fromisoformat(metadata["date"]).replace(
            tzinfo=SITE_ZONE
        )
        updated = metadata.get("updated")
        if updated is not None:
            if not isinstance(updated, str):
                raise ValueError(f"{source}: updated must be an ISO date or timestamp")
            modified = dt.datetime.fromisoformat(updated)
            if modified.date() < published.date():
                raise ValueError(f"{source}: updated cannot precede date")
            modified = modified.replace(tzinfo=modified.tzinfo or SITE_ZONE)
        else:
            modified = published
        if not isinstance(metadata.get("draft", False), bool):
            raise ValueError(f"{source}: draft must be true or false")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", source.stem):
            raise ValueError(f"{source}: use lowercase letters, digits and hyphens")
        if metadata.get("draft", False):
            continue
        entries.append(
            {
                **metadata,
                "sort_date": modified.astimezone(dt.timezone.utc),
                "body": MD.render(sections[2]),
                "url": f'/{project["slug"]}/{kind}/{source.stem}/',
                "project": project,
                "kind": kind,
            }
        )
    return sorted(entries, key=lambda e: (e["sort_date"], e["url"]), reverse=True)


def entry_row(entry, show_project=False):
    category = entry.get("label", "紹介" if entry["kind"] == "features" else "お知らせ")
    label = (
        esc(entry["project"]["name"]) + " / " + esc(category)
        if show_project
        else esc(category)
    )
    value = entry.get("updated", entry["date"])
    display = date_text(value[:10])
    if entry.get("updated"):
        display += ' <span class="entry-updated">更新</span>'
    return f"""<a class="entry-row" href="{entry['url']}"><time class="entry-date" datetime="{esc(value)}">{display}</time><div><h3>{esc(entry['title'])}</h3><p>{esc(entry['summary'])}</p></div><span class="entry-kind">{label}</span></a>"""


def project_card(project, index):
    return f"""<a class="project-card" href="/{project['slug']}/"><div class="project-card-media"><img src="{esc(project['cover'])}" alt="{esc(project['cover_alt'])}" width="1824" height="1368" fetchpriority="high"><span class="image-caption">{esc(project['name'])} / 開発中</span></div><div class="project-card-copy"><div class="tag-row"><span class="eyebrow">{esc(project['genre'])}</span><span class="status">{esc(project['status'])}</span></div><h3>{esc(project['name'])}</h3><p>{esc(project['description'])}</p><div class="card-foot"><span>{esc(project['platform'])} / PROJECT {index:02d}</span><strong>ゲーム紹介を見る</strong></div></div></a>"""


def spotlight(entry):
    cover = entry.get("cover", entry["project"]["cover"])
    alt = entry.get("cover_alt", entry["project"]["cover_alt"])
    return f"""<a class="spotlight-card" href="{entry['url']}"><img src="{esc(cover)}" alt="{esc(alt)}" loading="lazy"><div class="spotlight-copy"><span class="eyebrow">{esc(entry.get('label', '紹介'))}</span><h3>{esc(entry['title'])}</h3><p>{esc(entry['summary'])}</p><span class="text-link">紹介を読む</span></div></a>"""


def project_page(project, features_entries, news_entries):
    build = project["build"]
    url = build["drive_url"]
    if url:
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or parsed.netloc != "drive.google.com"
            or not parsed.path.startswith("/drive/")
        ):
            raise ValueError("drive_url must be an HTTPS Google Drive folder URL")
        action = f'<a class="button" href="{esc(url)}" target="_blank" rel="noopener noreferrer">Google Driveで開く<span class="sr-only">（新しいタブ）</span></a><p class="action-help">アクセスを許可された方のみ</p>'
    else:
        action = '<span class="button disabled">配布準備中</span><p class="action-help">リンクは配布開始時に掲載します</p>'
    facts = "".join(
        f'<div class="fact"><strong>{esc(f["value"])}</strong><span>{esc(f["label"])}</span></div>'
        for f in project["facts"]
    )
    features = "".join(
        f'<div><span class="feature-number">0{i}</span><h2>{esc(f["title"])}</h2><p>{esc(f["text"])}</p></div>'
        for i, f in enumerate(project["features"], 1)
    )
    meta = []
    if build.get("version"):
        meta.append(esc(build["version"]))
    if build.get("updated"):
        meta.append(f'更新 {date_text(build["updated"])}')
    base = f'/{project["slug"]}/'
    body = template(
        "project",
        **{
            key: esc(project[key])
            for key in (
                "name",
                "genre",
                "platform",
                "status",
                "tagline",
                "description",
                "cover",
                "cover_alt",
            )
        },
        breadcrumbs=breadcrumbs([("ゲーム一覧", "/"), (project["name"], None)]),
        project_nav=nav(project),
        facts=facts,
        features=features,
        build_meta=f'<p class="build-meta">{" / ".join(meta)}</p>' if meta else "",
        build_note=esc(build["note"]),
        download_action=action,
        overview=MD.render(
            (ROOT / "content" / project["slug"] / "overview.md").read_text(
                encoding="utf-8"
            )
        ),
        spotlights="".join(spotlight(e) for e in features_entries)
        or '<p class="empty-state">紹介記事はまだありません。</p>',
        news="".join(entry_row(e) for e in news_entries)
        or '<p class="news-empty">お知らせはまだありません。</p>',
    )
    page(base, project["name"] + " | " + SITE["name"], project["description"], body)


def articles(project, kind, entries):
    heading, category_en = (
        ("紹介記事", "GUIDES") if kind == "features" else ("お知らせ", "NEWS & UPDATES")
    )
    base = f'/{project["slug"]}/'
    for entry in entries:
        is_weapons = entry.get("gallery") == "weapons"
        cover = (
            f'<img class="article-cover" src="{esc(entry["cover"])}" alt="{esc(entry.get("cover_alt", entry["title"]))}" fetchpriority="high">'
            if entry.get("cover") and not is_weapons
            else ""
        )
        dates = (
            f'<time datetime="{esc(entry["date"])}">{date_text(entry["date"])}</time>'
        )
        if entry.get("updated"):
            dates += f'<span class="article-updated">更新 <time datetime="{esc(entry["updated"])}">{date_text(entry["updated"][:10])}</time></span>'
        body = template(
            "article",
            name=esc(project["name"]),
            category_en=esc(category_en),
            heading=esc(entry["title"]),
            dates=dates,
            article_class=" article-weapons" if is_weapons else "",
            summary=esc(entry["summary"]),
            content=entry["body"],
            gallery=guide_gallery(entry),
            category=heading,
            list_url=base + "#" + kind,
            project_url=base,
            cover=cover,
            breadcrumbs=breadcrumbs(
                [
                    ("ゲーム一覧", "/"),
                    (project["name"], base),
                    (heading, base + "#" + kind),
                    (entry["title"], None),
                ]
            ),
        )
        page(
            entry["url"],
            entry["title"] + " | " + project["name"] + " | " + SITE["name"],
            entry["summary"],
            body,
        )


def guide_gallery(entry):
    if entry.get("gallery") == "weapons":
        figures = []
        for item in entry["weapons"]:
            slug, name, weapon_type = item["image"], item["name"], item["type"]
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
                raise ValueError(f"Invalid weapon image slug: {slug}")
            src = "/assets/project-cdx-weapon-" + slug + ".png"
            if not (ROOT / "public" / src.lstrip("/")).is_file():
                raise ValueError(f"Missing weapon image: {src}")
            figures.append(
                f'<figure><a href="{src}" aria-label="{esc(name)}の画像を拡大"><img src="{src}" alt="{esc(name)}を構えたプレイ画面。{esc(weapon_type)}。" width="1920" height="1080" loading="lazy"><span class="weapon-zoom" aria-hidden="true">↗</span></a><figcaption><div class="weapon-heading"><strong>{esc(name)}</strong><span>{esc(weapon_type)}</span></div><p>{esc(item["description"])}</p></figcaption></figure>'
            )
        return (
            '<section class="weapon-lineup" aria-labelledby="weapon-lineup-title"><div class="weapon-lineup-heading"><h2 id="weapon-lineup-title">選べる武器</h2><span class="eyebrow">'
            + f"{len(figures):02d} MAIN WEAPONS"
            + '</span></div><p class="weapon-intro">メイン武器は1つ。<strong>LOADOUT → WEAPONS</strong>で選択し、試合中の変更は次のリスポーンから反映されます。</p><div class="weapon-gallery">'
            + "".join(figures)
            + "</div></section>"
        )
    return ""


def main():
    if urlsplit(SITE["url"]).scheme != "https":
        raise ValueError("site.url must use HTTPS")
    slugs = [p["slug"] for p in PROJECTS]
    if len(set(slugs)) != len(slugs) or any(
        not re.fullmatch(r"[a-z0-9][a-z0-9-]*", s) for s in slugs
    ):
        raise ValueError("Project slugs must be unique lowercase URL segments")
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "public", OUT)
    notes = []
    for project in PROJECTS:
        collections = {
            kind: load_entries(project, kind) for kind in ("features", "news")
        }
        project_page(project, collections["features"], collections["news"])
        for kind, entries in collections.items():
            articles(project, kind, entries)
            notes.extend(entries)
    notes.sort(key=lambda e: (e["sort_date"], e["url"]), reverse=True)
    body = template(
        "home",
        project_count=f"{len(PROJECTS):02d}",
        project_cards="".join(project_card(p, i) for i, p in enumerate(PROJECTS, 1)),
        latest_notes="".join(entry_row(e, True) for e in notes[:6])
        or '<p class="empty-state">紹介記事・お知らせはまだありません。</p>',
    )
    page("/", SITE["name"] + " | ゲーム置き場", SITE["description"], body)
    page(
        "/404.html",
        "ページが見つかりません | " + SITE["name"],
        "ゲーム一覧からお探しください。",
        template("404"),
    )
    urls = "".join(
        f'<url><loc>{esc(SITE["url"] + route)}</loc></url>' for route in sorted(ROUTES)
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + urls
        + "</urlset>",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(
        f'User-agent: *\nAllow: /\nSitemap: {SITE["url"]}/sitemap.xml\n',
        encoding="utf-8",
    )
    (OUT / ".nojekyll").touch()
    print(f"Built {len(ROUTES)} pages + 404 into {OUT}")


if __name__ == "__main__":
    main()
