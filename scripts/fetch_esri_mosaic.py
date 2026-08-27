#!/usr/bin/env python3
"""Download an Esri World Imagery mosaic around a WGS84 point.

Grid size is 2*half+1 tiles (half=5 → 11×11 → 2816 px; half=6 → 13×13 → 3328 px),
matching scripts/annotate_plates.py MOSAICS.

Usage:
  python3 scripts/fetch_esri_mosaic.py --lat 41.16 --lon 114.72 --z 16 --half 5 \\
      --out screenshots/zhangbei/overview_z16.jpg
"""
from __future__ import annotations

import argparse
import io
import math
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

TILE = 256
UA = "DatacenterProbe/1.0 (research; https://github.com/madeye/datacenter-probe)"
ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"


def deg2num(lat: float, lon: float, z: int) -> tuple[float, float]:
    lat_r = math.radians(lat)
    n = 2.0**z
    xtile = (lon + 180.0) / 360.0 * n
    ytile = (1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return xtile, ytile


def mosaic_origin(lat: float, lon: float, z: int, half: int) -> tuple[int, int]:
    cx, cy = deg2num(lat, lon, z)
    return int(math.floor(cx - half)), int(math.floor(cy - half))


def fetch_tile(z: int, x: int, y: int, dest: Path, retries: int = 4) -> Image.Image:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 800:
        return Image.open(dest).convert("RGB")
    url = ESRI.format(z=z, x=x, y=y)
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            dest.write_bytes(data)
            return Image.open(io.BytesIO(data)).convert("RGB")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"tile z{z}/{y}/{x} failed: {last_err}") from last_err


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--z", type=int, default=16)
    ap.add_argument("--half", type=int, default=5, help="tiles from center; grid is 2*half+1")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sleep", type=float, default=0.08)
    args = ap.parse_args()

    x0, y0 = mosaic_origin(args.lat, args.lon, args.z, args.half)
    n = 2 * args.half + 1
    canvas = Image.new("RGB", (n * TILE, n * TILE), "#1a1712")
    tile_dir = args.out.parent / "_tiles" / f"z{args.z}_{x0}_{y0}"

    for dy in range(n):
        for dx in range(n):
            x, y = x0 + dx, y0 + dy
            tile_path = tile_dir / f"{args.z}-{y}-{x}.jpg"
            im = fetch_tile(args.z, x, y, tile_path)
            canvas.paste(im, (dx * TILE, dy * TILE))
            if args.sleep:
                time.sleep(args.sleep)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out, "JPEG", quality=90, optimize=True)
    print("wrote", args.out, canvas.size, f"origin_tile=({x0},{y0}) z={args.z}")


if __name__ == "__main__":
    main()
