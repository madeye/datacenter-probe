#!/usr/bin/env python3
"""Render 1200×630 PNG social cards for each city page."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <title>{city} social card</title>
  <meta name="robots" content="noindex">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500&family=Noto+Serif+SC:wght@700&display=block">
  <style>
    :root {{
      --darkroom: #12100c;
      --bone: #e8e1d4;
      --dust: #c9b896;
      --rust: #c45c26;
      --rule: rgba(201, 184, 150, 0.22);
      --serif: "Noto Serif SC", "Songti SC", serif;
      --sans: "Noto Sans SC", "PingFang SC", sans-serif;
      --mono: "IBM Plex Mono", ui-monospace, monospace;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0;
      width: 1200px;
      height: 630px;
      overflow: hidden;
      background: var(--darkroom);
      color: var(--bone);
    }}
    body {{
      display: grid;
      grid-template-columns: 548px 1fr;
      grid-template-rows: 630px;
    }}
    .copy {{
      display: flex;
      flex-direction: column;
      height: 630px;
      padding: 44px 48px 36px;
      border-right: 1px solid var(--rule);
    }}
    .brand {{
      font-family: var(--mono);
      font-size: 13px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--dust);
    }}
    .kicker {{
      margin: 32px 0 0;
      font-family: var(--mono);
      font-size: 13px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--rust);
    }}
    h1 {{
      font-family: var(--serif);
      font-weight: 700;
      font-size: 46px;
      line-height: 1.24;
      letter-spacing: 0.02em;
      margin: 14px 0 0;
    }}
    h1 span {{ display: block; white-space: nowrap; }}
    .lede {{
      margin: 18px 0 0;
      font-family: var(--sans);
      font-size: 18px;
      line-height: 1.5;
      color: var(--dust);
    }}
    .meta {{
      margin-top: auto;
      padding-top: 22px;
      border-top: 1px solid var(--rule);
      font-family: var(--mono);
      font-size: 14px;
      letter-spacing: 0.06em;
      color: var(--dust);
    }}
    .viz {{
      position: relative;
      height: 630px;
      overflow: hidden;
      background: #1a1712;
    }}
    .viz img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: {pos};
    }}
    .viz::before {{
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, rgba(18,16,12,0.28) 0%, transparent 28%);
      pointer-events: none;
    }}
    .caption {{
      position: absolute;
      left: 18px;
      bottom: 16px;
      font-family: var(--mono);
      font-size: 11px;
      letter-spacing: 0.08em;
      color: var(--bone);
      background: rgba(18,16,12,0.72);
      padding: 6px 10px;
    }}
  </style>
</head>
<body>
  <section class="copy">
    <div class="brand">Datacenter Probe</div>
    <p class="kicker">Satellite reconnaissance · {region}</p>
    <h1><span>{city}周边</span><span>数据中心建设情况</span></h1>
    <p class="lede">{lede}</p>
    <p class="meta">{meta}</p>
  </section>
  <div class="viz">
    <img src="{image}" alt="">
    <span class="caption">{caption}</span>
  </div>
  <script>
    (async () => {{
      const imgs = [...document.images].map((img) =>
        img.complete && img.naturalWidth
          ? Promise.resolve()
          : new Promise((res) => {{
              img.addEventListener("load", res, {{ once: true }});
              img.addEventListener("error", res, {{ once: true }});
            }})
      );
      await Promise.all([document.fonts.ready, ...imgs]);
      document.documentElement.dataset.ready = "1";
    }})();
    setTimeout(() => {{ document.documentElement.dataset.ready = "1"; }}, 8000);
  </script>
</body>
</html>
"""

CARDS = [
    dict(
        slug="guian",
        city="贵安",
        region="Guizhou",
        lede="数谷大道一条走廊。<br>华为、腾讯洞库、苹果两栋白顶已投运。",
        meta="26.3680°N  106.4900°E  ·  r = 50 km",
        image="../plates/guian/G01_cluster_overview.jpg",
        caption="贵安 · 数谷大道 · 华为 / 腾讯 / 苹果",
        pos="50% 48%",
    ),
    dict(
        slug="ulanqab",
        city="乌兰察布",
        region="Inner Mongolia",
        lede="以集宁城区为圆心，50 公里卫星核查。<br>机房全部落在东面 G110 走廊。",
        meta="41.0181°N  113.1155°E  ·  r = 50 km",
        image="../plates/ulanqab/hero_corridor.jpg",
        caption="乌兰察布 · 集宁 · G110 走廊",
        pos="72% 62%",
    ),
    dict(
        slug="yangquan",
        city="阳泉",
        region="Shanxi",
        lede="五座城里最小的一处。<br>大连街百度约 8 栋模组，云峰在北侧。",
        meta="37.8600°N  113.6230°E  ·  r = 50 km",
        image="../plates/yangquan/Y03_dalian_overview.jpg",
        caption="阳泉 · 大连街 · 百度 / 云峰",
        pos="50% 50%",
    ),
    dict(
        slug="zhongwei",
        city="中卫",
        region="Ningxia",
        lede="不在城区，在北面戈壁。<br>西部云基地六栋白顶大厅是典型风冷机房。",
        meta="37.6368°N  105.3468°E  ·  r = 50 km",
        image="../plates/zhongwei/Z01_cloudbase_overview.jpg",
        caption="中卫 · 西部云基地 · 六栋白顶大厅",
        pos="50% 42%",
    ),
    dict(
        slug="karamay",
        city="克拉玛依",
        region="Xinjiang",
        lede="六座机房都写在同一座园。卫星能确认园，钉不死楼。",
        meta="45.5450°N  84.8700°E  ·  r = 50 km",
        image="../plates/karamay/K01_park_overview.jpg",
        caption="克拉玛依 · 云计算产业园 · 楼未钉死",
        pos="50% 50%",
    ),
    dict(
        slug="zhangbei",
        city="张北",
        region="Hebei",
        lede="小二台阿里数据港两排大厅。<br>中都草原 8–10 栋白顶模组，庙滩业主未钉。",
        meta="41.1887°N  114.8623°E  ·  r = 50 km",
        image="../plates/zhangbei/ZB01_xiaodai_overview.jpg",
        caption="张北 · 小二台 · 阿里数据港",
        pos="50% 50%",
    ),
    dict(
        slug="huailai",
        city="怀来",
        region="Hebei",
        lede="东花园：腾讯东园与中国移动西邻。<br>秦淮在南，合盈在东。",
        meta="40.3248°N  115.8193°E  ·  r = 50 km",
        image="../plates/huailai/HL01_donghuayuan_overview.jpg",
        caption="怀来 · 东花园 · 腾讯 / 移动 / 秦淮 / 合盈",
        pos="50% 50%",
    ),
    dict(
        slug="qingyang",
        city="庆阳",
        region="Gansu",
        lede="温泉镇接缝以东，秦淮一栋在建白顶大厅。",
        meta="35.7335°N  107.7044°E  ·  r = 50 km",
        image="../plates/qingyang/QY01_wenquan_overview.jpg",
        caption="庆阳 · 温泉镇 · 秦淮在建大厅",
        pos="50% 50%",
    ),
    dict(
        slug="horinger",
        city="和林格尔",
        region="Inner Mongolia",
        lede="盛乐园区：移动白顶大厅可指认，电信信息园能钉园。",
        meta="40.5390°N  111.8230°E  ·  r = 50 km",
        image="../plates/horinger/HG01_yungu_overview.jpg",
        caption="和林格尔 · 盛乐 · 移动 / 电信",
        pos="50% 50%",
    ),
    dict(
        slug="shaoguan",
        city="韶关",
        region="Guangdong",
        lede="沐溪湖半岛一栋在建超大矩形。沿路白顶厂房不是机房。",
        meta="24.7830°N  113.5025°E  ·  r = 50 km",
        image="../plates/shaoguan/SG01_huashao_overview.jpg",
        caption="韶关 · 沐溪湖西 · 华南数谷",
        pos="50% 42%",
    ),
    dict(
        slug="wuhu",
        city="芜湖",
        region="Anhui",
        lede="田里一座华为云在建大厅，钢结构加塔吊。<br>智算 OSM 多边形很小。",
        meta="31.3484°N  118.2862°E  ·  r = 50 km",
        image="../plates/wuhu/WH02_huawei.jpg",
        caption="芜湖 · 三山 · 华为云华东",
        pos="50% 50%",
    ),
]


def write_html(card: dict) -> Path:
    out = DOCS / card["slug"] / "social-card.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    image = DOCS / card["slug"] / card["image"]
    if not image.resolve().is_file():
        raise FileNotFoundError(image.resolve())
    out.write_text(TEMPLATE.format(**card), encoding="utf-8")
    return out


def screenshot(html: Path, png: Path) -> None:
    cmd = [
        "playwright",
        "screenshot",
        "--viewport-size=1200,630",
        "--wait-for-selector=html[data-ready=\"1\"]",
        "--timeout=60000",
        html.resolve().as_uri(),
        str(png),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    slugs = set(sys.argv[1:])
    cards = [c for c in CARDS if not slugs or c["slug"] in slugs]
    if slugs:
        missing = slugs - {c["slug"] for c in cards}
        if missing:
            raise SystemExit(f"unknown slug(s): {', '.join(sorted(missing))}")
    for card in cards:
        html = write_html(card)
        png = html.with_suffix(".png")
        screenshot(html, png)
        print("wrote", png.relative_to(ROOT), png.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
