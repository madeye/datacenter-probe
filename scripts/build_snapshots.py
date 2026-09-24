#!/usr/bin/env python3
"""Build dated GitHub Pages snapshots from first-parent Git history (stdlib only)."""
import argparse
from datetime import datetime
from html import escape
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://madeye.github.io/datacenter-probe/"
ZONE = ZoneInfo("Asia/Singapore")
MARKER = ".snapshot-build"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def revisions(repo):
    if git(repo, "rev-parse", "--is-shallow-repository") == "true":
        raise ValueError("Snapshot history requires a full clone (fetch-depth: 0).")
    history = git(repo, "log", "--first-parent", "--format=%H%x09%cI")
    days = {}
    for row in history.splitlines():
        revision, timestamp = row.split("\t")
        day = datetime.fromisoformat(timestamp).astimezone(ZONE).date().isoformat()
        if day not in days:
            exists = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{revision}:docs/index.html"], capture_output=True)
            if exists.returncode == 0:
                days[day] = revision
    if not days:
        raise ValueError("No site snapshots found in Git history.")
    return days


def export_docs(repo, revision, target):
    process = subprocess.Popen(["git", "-C", str(repo), "archive", revision, "docs"], stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                path = PurePosixPath(member.name)
                if path.parts[0] != "docs" or ".." in path.parts:
                    raise ValueError(f"Invalid archive path: {member.name}")
                if not member.isfile():
                    if member.isdir():
                        continue
                    raise ValueError(f"Unsupported archive entry: {member.name}")
                out = target.joinpath(*path.parts[1:])
                out.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, out.open("wb") as dest:
                    shutil.copyfileobj(source, dest)
    finally:
        process.stdout.close()
        code = process.wait()
    if code:
        raise RuntimeError(f"git archive failed for {revision}")
    if not (target / "index.html").is_file():
        raise ValueError(f"Snapshot {revision} has no docs/index.html")


def navigation(day, page, catalog):
    # Every destination is computed from the dated page, including project-subpath hosting.
    prefix = "../" * (len(PurePosixPath(page).parts))
    links = []
    latest = next(iter(catalog))
    for other, info in catalog.items():
        available = page in info["pages"]
        destination = page if available else "index.html"
        route = destination.removesuffix("index.html")
        label = other + (" · 最新" if other == latest else "")
        if not available:
            label += " · 总览"
        current = ' aria-current="date"' if day == other else ""
        links.append(f'<a href="{prefix}{other}/{route}"{current}>{escape(label)}</a>')
    return ('<nav class="snapshot-nav" aria-label="快照日期">'
            '<span>页面快照</span><div class="snapshot-dates">' + "".join(links) + '</div></nav>')


def redirect(target, canonical, source=""):
    # A no-JS fallback plus a JS redirect that retains inbound deep links and queries.
    url = SITE + canonical
    title = re.search(r"<title>.*?</title>", source, re.S)
    title = title[0] if title else "<title>最新快照 · Datacenter Probe</title>"
    metadata = "\n".join(tag for tag in re.findall(r"<meta\b[^>]*>", source)
                         if re.search(r'(?:name|property)="(?:description|og:[^"]+|twitter:[^"]+)"', tag))
    return f'''<!DOCTYPE html>
<html lang="zh-Hans"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{title}
{metadata}
<link rel="canonical" href="{escape(url, quote=True)}">
<noscript><meta http-equiv="refresh" content="0;url={escape(target, quote=True)}"></noscript>
<script>location.replace({json.dumps(target)} + location.search + location.hash);</script>
</head><body><p><a href="{escape(target, quote=True)}">打开最新日期快照</a></p></body></html>
'''


def build(repo, output, worktree=False, date=None):
    output = output.resolve()
    # Only replace directories this builder owns; never delete source files or unrelated output.
    if output == repo.resolve() or output == (repo / "docs").resolve() or (repo / "docs").resolve() in output.parents or output == (repo / ".git").resolve() or (repo / ".git").resolve() in output.parents or output in repo.resolve().parents:
        raise ValueError("Output must not replace the repository or source docs.")
    if output.exists() and not (output / MARKER).is_file():
        raise ValueError(f"Refusing to replace unmarked directory: {output}")
    days = revisions(repo)
    if date and not worktree:
        raise ValueError("--date is only available with --worktree for previews.")
    if worktree:
        day = date or datetime.now(ZONE).date().isoformat()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            raise ValueError("Expected an ISO date: YYYY-MM-DD")
        datetime.strptime(day, "%Y-%m-%d")
        days[day] = "worktree"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="probe-snapshots-", dir=output.parent) as temp:
        stage = Path(temp) / "site"
        stage.mkdir()
        catalog = {}
        for day, revision in sorted(days.items(), reverse=True):
            folder = stage / day
            if revision == "worktree":
                shutil.copytree(repo / "docs", folder)
            else:
                export_docs(repo, revision, folder)
            pages = sorted(p.relative_to(folder).as_posix() for p in folder.rglob("index.html"))
            catalog[day] = {"revision": revision, "pages": pages}
        for day, info in catalog.items():
            folder = stage / day
            for page in info["pages"]:
                path = folder / page
                html = path.read_text()
                html = html.replace(SITE, SITE + day + "/")
                prefix = "../" * len(PurePosixPath(page).parts)
                html = html.replace("</head>", f'<link rel="stylesheet" href="{prefix}snapshot-nav.css">\n</head>')
                html = re.sub(r"(<body\b[^>]*>)", lambda m: m[0] + "\n" + navigation(day, page, catalog), html, count=1)
                path.write_text(html)
        latest = next(iter(catalog))
        # Keep undated city links working, including cities absent from older snapshots.
        all_pages = {page for info in catalog.values() for page in info["pages"]}
        for page in all_pages:
            depth = len(PurePosixPath(page).parts) - 1
            destination = page if page in catalog[latest]["pages"] else "index.html"
            target = "../" * depth + latest + "/" + destination.removesuffix("index.html")
            path = stage / page
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(redirect(target, latest + "/" + destination.removesuffix("index.html"),
                                     (stage / latest / destination).read_text()))
        for image in (stage / latest).rglob("social-card.png"):
            dest = stage / image.relative_to(stage / latest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(image, dest)
        if (stage / latest / "404.html").exists():
            shutil.copyfile(stage / latest / "404.html", stage / "404.html")
        shutil.copyfile(ROOT / "scripts" / "snapshot-nav.css", stage / "snapshot-nav.css")
        (stage / "snapshots.json").write_text(json.dumps({"latest": latest, "timezone": str(ZONE), "snapshots": catalog}, ensure_ascii=False, indent=2) + "\n")
        (stage / ".nojekyll").touch()
        (stage / MARKER).touch()
        if output.exists():
            shutil.rmtree(output)
        shutil.move(str(stage), output)
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    parser.add_argument("--worktree", action="store_true", help="Include uncommitted docs as today's preview")
    parser.add_argument("--date", help="Preview date; requires --worktree")
    args = parser.parse_args()
    catalog = build(ROOT, args.output, args.worktree, args.date)
    print(f"Built {len(catalog)} snapshots; latest {next(iter(catalog))}; output {args.output}")


if __name__ == "__main__":
    main()
