#!/usr/bin/env python3
"""Fetch current Esri tiles into an isolated run cache; publish only a complete set."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
import json
import re
from pathlib import Path
import shutil
import tempfile
from zoneinfo import ZoneInfo

from PIL import Image, ImageChops, ImageStat
from annotate_plates import MOSAICS, PLATESPEC, compose
from fetch_esri_mosaic import ESRI, TILE, fetch_tile, mosaic_origin

ROOT = Path(__file__).resolve().parents[1]
# Keep original Google evidence plates intact; these provide current Esri counterparts.
ULANQAB = [
    ("U01_corridor", "集宁以东走廊", 41.0, 113.25, 13, 5),
    ("U02_yiwutang", "益武堂", 40.985, 113.238, 16, 5),
    ("U03_sihao", "四号村 / 巴音东段", 40.990, 113.318, 16, 5),
    ("U04_shengjiaying", "圣家营北", 41.041, 113.310, 16, 5),
    ("U05_qianqi", "前旗土贵乌", 40.786, 113.221, 16, 5),
]


def specs():
    mosaics = {s["src"]: MOSAICS[s["src"]] for s in PLATESPEC}
    plates = list(PLATESPEC)
    boxes = [{"lat0": lat - .003, "lon0": lon - .004, "lat1": lat + .003, "lon1": lon + .004,
              "label": label + "（核查位置）", "color": "#2ec4b6"}
             for _, label, lat, lon, _, _ in ULANQAB[1:]]
    for index, (name, label, lat, lon, zoom, half) in enumerate(ULANQAB):
        src = f"ulanqab/{name}.jpg"
        mosaics[src] = dict(lat=lat, lon=lon, z=zoom, half=half)
        plates.append(dict(src=src, dest=src, title=f"{name.split('_')[0]}  {label} · Esri z{zoom}",
                           caption="框线仅标原核查位置，不代表地块边界或权属；建设状态需对照影像另行复核。",
                           boxes=boxes if index == 0 else [boxes[index - 1]]))
    return mosaics, plates


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh(workers=12):
    started = datetime.now(ZoneInfo("Asia/Singapore"))
    day = started.date().isoformat()
    mosaics, plates = specs()
    cache_root = ROOT / "screenshots" / "_tiles"
    cache_root.mkdir(parents=True, exist_ok=True)
    # A fresh directory per run prevents a prior run from supplying stale tiles.
    run = Path(tempfile.mkdtemp(prefix=started.strftime("%Y%m%d-%H%M%S-"), dir=cache_root))
    tiles = set()
    for meta in mosaics.values():
        x0, y0 = mosaic_origin(**{k: meta[k] for k in ("lat", "lon", "z", "half")})
        for dy in range(2 * meta["half"] + 1):
            for dx in range(2 * meta["half"] + 1):
                tiles.add((meta["z"], x0 + dx, y0 + dy))
    def tile_path(z, x, y):
        return run / "tiles" / f"{z}-{y}-{x}.jpg"
    def download(tile):
        z, x, y = tile
        fetch_tile(z, x, y, tile_path(z, x, y))
        return tile
    print(f"Fetching {len(tiles)} unique tiles for {len(mosaics)} mosaics; run {run.name}", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(download, tile) for tile in sorted(tiles)]
        for count, future in enumerate(as_completed(futures), 1):
            future.result()
            if count % 100 == 0 or count == len(tiles):
                print(f"tiles {count}/{len(tiles)}", flush=True)
    records = []
    for name, meta in mosaics.items():
        x0, y0 = mosaic_origin(meta["lat"], meta["lon"], meta["z"], meta["half"])
        n = 2 * meta["half"] + 1
        canvas = Image.new("RGB", (n * TILE, n * TILE))
        tile_hashes = []
        for dy in range(n):
            for dx in range(n):
                tile = tile_path(meta["z"], x0 + dx, y0 + dy)
                with Image.open(tile) as im:
                    canvas.paste(im, (dx * TILE, dy * TILE))
                tile_hashes.append(sha(tile))
        out = run / "mosaics" / name
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out, "JPEG", quality=90, optimize=True)
        previous = ROOT / "screenshots" / name
        record = dict(path=name, **meta, origin_tile=[x0, y0], size=list(canvas.size), sha256=sha(out),
                      tile_set_sha256=hashlib.sha256("".join(tile_hashes).encode()).hexdigest())
        if previous.exists():
            record["previous_sha256"] = sha(previous)
            with Image.open(previous) as old, Image.open(out) as current:
                if old.size == canvas.size:
                    delta = ImageChops.difference(old.convert("RGB").resize((256, 256)), current.convert("RGB").resize((256, 256)))
                    record["mean_pixel_difference_0_255"] = round(sum(ImageStat.Stat(delta).mean) / 3, 4)
        records.append(record)
    for spec in plates:
        compose(run / "mosaics" / spec["src"], run / "plates" / spec["dest"],
                spec["title"] + f" · 获取 {day} / 标注依据 2026-08", spec["caption"], spec["boxes"], mosaics[spec["src"]])
    # All fetches and renders have succeeded before changing published images.
    for record in records:
        target = ROOT / "screenshots" / record["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run / "mosaics" / record["path"], target)
    for spec in plates:
        target = ROOT / "docs" / "plates" / spec["dest"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run / "plates" / spec["dest"], target)
    manifest = dict(fetched_at=started.isoformat(), completed_at=datetime.now(ZoneInfo("Asia/Singapore")).isoformat(),
                    source="Esri World Imagery", tile_url=ESRI, acquisition_date="unknown; varies by tile",
                    note="获取日期不是拍摄日期；原核查文字与框线未因重新获取影像而自动更新。",
                    tile_count=len(tiles), mosaics=records,
                    plates=[dict(path=s["dest"], source=s["src"], sha256=sha(ROOT / "docs" / "plates" / s["dest"])) for s in plates])
    (ROOT / "docs" / "imagery.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    from render_city_pages import main as render_pages, imagery_note
    render_pages()
    for path in [ROOT / "docs/index.html", ROOT / "docs/ulanqab/index.html"]:
        html = path.read_text()
        html = re.sub(r'\s*<p class="imagery-note">.*?</p>', "", html)
        html = html.replace("  </header>", "    " + imagery_note() + "\n  </header>", 1)
        path.write_text(html)
    print(f"Updated {len(plates)} plates across 11 cities. Manifest: docs/imagery.json", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error("--workers must be between 1 and 16")
    refresh(args.workers)
