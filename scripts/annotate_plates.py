#!/usr/bin/env python3
"""Draw labeled boxes on Esri mosaics. Coordinates are WGS84."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
PLATES = ROOT / "docs" / "plates"
TILE = 256
HEADER = 72
FOOTER = 56

FONT_PATHS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def font(size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size=size, index=index)
        except OSError:
            continue
    return ImageFont.load_default()


def deg2num(lat: float, lon: float, z: int) -> tuple[float, float]:
    lat_r = math.radians(lat)
    n = 2.0**z
    xtile = (lon + 180.0) / 360.0 * n
    ytile = (1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return xtile, ytile


def mosaic_origin(lat: float, lon: float, z: int, half: int) -> tuple[int, int]:
    cx, cy = deg2num(lat, lon, z)
    return int(math.floor(cx - half)), int(math.floor(cy - half))


def lonlat_to_px(lat: float, lon: float, z: int, x0: int, y0: int) -> tuple[float, float]:
    x, y = deg2num(lat, lon, z)
    return (x - x0) * TILE, (y - y0) * TILE


def box_px(lat0: float, lon0: float, lat1: float, lon1: float, z: int, x0: int, y0: int):
    p1 = lonlat_to_px(lat0, lon0, z, x0, y0)
    p2 = lonlat_to_px(lat1, lon1, z, x0, y0)
    return [min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1])]


def draw_box(draw: ImageDraw.ImageDraw, xy, color, label, fnt, width=4):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0, y0, x1, y1], outline=color, width=width)
    if not label:
        return
    pad = 6
    tb = draw.textbbox((0, 0), label, font=fnt)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    tx, ty = x0, max(0, y0 - th - pad * 2)
    draw.rectangle([tx, ty, tx + tw + pad * 2, ty + th + pad * 2], fill=color)
    draw.text((tx + pad, ty + pad - 1), label, fill="#111111", font=fnt)


def compose(src: Path, dest: Path, title: str, caption: str, boxes, meta):
    im = Image.open(src).convert("RGB")
    x0, y0 = mosaic_origin(meta["lat"], meta["lon"], meta["z"], meta["half"])
    z = meta["z"]
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    fnt = font(28)
    for b in boxes:
        xy = box_px(b["lat0"], b["lon0"], b["lat1"], b["lon1"], z, x0, y0)
        col = b.get("color", "#2ec4b6")
        # convert hex to rgba
        rgb = tuple(int(col.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)) + (255,)
        draw_box(d, xy, rgb, b.get("label", ""), fnt, width=b.get("width", 5))
    im = im.convert("RGBA")
    im = Image.alpha_composite(im, overlay).convert("RGB")

    canvas = Image.new("RGB", (im.width, im.height + HEADER + FOOTER), "#12100c")
    canvas.paste(im, (0, HEADER))
    d2 = ImageDraw.Draw(canvas)
    d2.text((24, 18), title, fill="#e8e1d4", font=font(32))
    d2.text((24, im.height + HEADER + 14), caption, fill="#c9b896", font=font(22))
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, "JPEG", quality=88, optimize=True)
    print("wrote", dest, canvas.size)


# Mosaic metadata must match scripts that downloaded the files.
MOSAICS = {
    "guian/overview_shugu_z15.jpg": {"lat": 26.365, "lon": 106.490, "z": 15, "half": 6},
    "guian/huawei_yunshangtun_z17.jpg": {"lat": 26.3708, "lon": 106.5082, "z": 17, "half": 5},
    "guian/tencent_qixing_z17.jpg": {"lat": 26.3696, "lon": 106.5007, "z": 17, "half": 5},
    "guian/apple_icloud_z17.jpg": {"lat": 26.3628, "lon": 106.4672, "z": 17, "half": 5},
    "guian/foxconn_z16.jpg": {"lat": 26.3500, "lon": 106.4774, "z": 16, "half": 4},
    "guian/xingan_huawei_az3_z16.jpg": {"lat": 26.393, "lon": 106.470, "z": 16, "half": 5},
    "yangquan/overview_dalian_z16.jpg": {"lat": 37.864, "lon": 113.625, "z": 16, "half": 5},
    "yangquan/baidu_z17.jpg": {"lat": 37.8597, "lon": 113.6225, "z": 17, "half": 5},
    "yangquan/yunfeng_z17.jpg": {"lat": 37.8693, "lon": 113.6273, "z": 17, "half": 5},
    "zhongwei/overview_cloudbase_z15.jpg": {"lat": 37.622, "lon": 105.328, "z": 15, "half": 6},
    "zhongwei/aws_z17.jpg": {"lat": 37.6368, "lon": 105.3468, "z": 17, "half": 5},
    "zhongwei/industrial_south_z16.jpg": {"lat": 37.6072, "lon": 105.3099, "z": 16, "half": 5},
    "karamay/overview_park_z16.jpg": {"lat": 45.545, "lon": 84.870, "z": 16, "half": 6},
    "karamay/core_industrial_z17.jpg": {"lat": 45.546, "lon": 84.868, "z": 17, "half": 5},
    "karamay/century_south_z16.jpg": {"lat": 45.555, "lon": 84.872, "z": 16, "half": 5},
}

PLATESPEC = [
    {
        "src": "guian/overview_shugu_z15.jpg",
        "dest": "guian/G01_cluster_overview.jpg",
        "title": "G01  贵安数谷大道集群  ·  Esri z15",
        "caption": "圆心 26.365°N 106.490°E。华为云上屯 / 腾讯七星隔路相望，苹果在西，南侧还有大院。",
        "boxes": [
            {"lat0": 26.3665, "lon0": 106.5036, "lat1": 26.3751, "lon1": 106.5128, "label": "1 华为云上屯", "color": "#2ec4b6"},
            {"lat0": 26.3679, "lon0": 106.4985, "lat1": 26.3713, "lon1": 106.5029, "label": "2 腾讯七星洞库", "color": "#c45c26"},
            {"lat0": 26.3601, "lon0": 106.4649, "lat1": 26.3656, "lon1": 106.4695, "label": "3 苹果 iCloud", "color": "#e8e1d4"},
        ],
    },
    {
        "src": "guian/tencent_qixing_z17.jpg",
        "dest": "guian/G02_huawei_tencent.jpg",
        "title": "G02  华为云上屯 × 腾讯七星  ·  Esri z17",
        "caption": "OSM：腾讯为地下洞库（layer=-1）。路西四栋白顶大厅是洞外扩建候选，路东环湖园区是华为云上屯。",
        "boxes": [
            {"lat0": 26.3665, "lon0": 106.5036, "lat1": 26.3751, "lon1": 106.5128, "label": "华为云上屯（已投运园区）", "color": "#2ec4b6"},
            {"lat0": 26.3679, "lon0": 106.4985, "lat1": 26.3713, "lon1": 106.5029, "label": "腾讯七星洞库山体", "color": "#c45c26"},
            {"lat0": 26.3688, "lon0": 106.4928, "lat1": 26.3726, "lon1": 106.4980, "label": "路西白顶大厅（洞外扩建候选）", "color": "#c23b22"},
        ],
    },
    {
        "src": "guian/apple_icloud_z17.jpg",
        "dest": "guian/G03_apple_icloud.jpg",
        "title": "G03  苹果 iCloud 贵安  ·  26.3628°N 106.4672°E",
        "caption": "OSM 标注 Apple iCloud Gui'An data center。两栋超大白顶矩形 + 冷机，典型超算/存储机房，已投运。",
        "boxes": [
            {"lat0": 26.3601, "lon0": 106.4649, "lat1": 26.3656, "lon1": 106.4695, "label": "苹果 iCloud（已投运）", "color": "#2ec4b6"},
        ],
    },
    {
        "src": "yangquan/baidu_z17.jpg",
        "dest": "yangquan/Y01_baidu.jpg",
        "title": "Y01  百度云计算（阳泉）中心  ·  37.8597°N 113.6225°E",
        "caption": "OSM 工业用地带 telecom=data_center。环形广场是云谷创新园办公；多边形南端三栋屋顶机电密布，东北侧另有 8 栋灰顶模组。",
        "boxes": [
            {"lat0": 37.8566, "lon0": 113.6202, "lat1": 37.8628, "lon1": 113.6249, "label": "OSM 百度云计算中心", "color": "#2ec4b6"},
            {"lat0": 37.8576, "lon0": 113.6204, "lat1": 37.8590, "lon1": 113.6244, "label": "南端三栋（屋顶机电）", "color": "#c23b22"},
            {"lat0": 37.8658, "lon0": 113.6252, "lat1": 37.8680, "lon1": 113.6310, "label": "8 栋灰顶模组（形态像机房）", "color": "#c45c26"},
        ],
    },
    {
        "src": "yangquan/yunfeng_z17.jpg",
        "dest": "yangquan/Y02_yunfeng.jpg",
        "title": "Y02  云峰智算 + 百度北侧模组  ·  37.8693°N 113.6273°E",
        "caption": "OSM 云峰地块只有约 140×290 m。模组东侧那栋深色新楼屋顶机电密布，是 2024–2025 扩建候选。右上采坑、下方两栋蓝顶厂房不算机房。",
        "boxes": [
            {"lat0": 37.8687, "lon0": 113.6256, "lat1": 37.8699, "lon1": 113.6289, "label": "OSM 云峰智算", "color": "#c45c26"},
            {"lat0": 37.8658, "lon0": 113.6252, "lat1": 37.8680, "lon1": 113.6310, "label": "8 栋灰顶模组", "color": "#2ec4b6"},
            {"lat0": 37.8653, "lon0": 113.6285, "lat1": 37.8660, "lon1": 113.6301, "label": "新楼（扩建候选）", "color": "#c23b22"},
        ],
    },
    {
        "src": "yangquan/overview_dalian_z16.jpg",
        "dest": "yangquan/Y03_dalian_overview.jpg",
        "title": "Y03  阳泉经开区东区 大连街  ·  Esri z16",
        "caption": "机房集中在大连街南。城区和铁路南侧没有同类超大矩形。右上采坑排除。",
        "boxes": [
            {"lat0": 37.8566, "lon0": 113.6202, "lat1": 37.8628, "lon1": 113.6249, "label": "百度", "color": "#2ec4b6"},
            {"lat0": 37.8687, "lon0": 113.6256, "lat1": 37.8699, "lon1": 113.6289, "label": "云峰", "color": "#c45c26"},
        ],
    },
    {
        "src": "zhongwei/overview_cloudbase_z15.jpg",
        "dest": "zhongwei/Z01_cloudbase_overview.jpg",
        "title": "Z01  中卫西部云基地  ·  37.637°N 105.347°E",
        "caption": "戈壁上的东西向园区，光伏围一圈。OSM 把整条带标成 AWS，实际是多业主机房并列。南侧化工厂不算。",
        "boxes": [
            {"lat0": 37.6345, "lon0": 105.3326, "lat1": 37.6391, "lon1": 105.3610, "label": "OSM AWS 工业用地（整条带）", "color": "#c45c26"},
        ],
    },
    {
        "src": "zhongwei/aws_z17.jpg",
        "dest": "zhongwei/Z02_white_halls.jpg",
        "title": "Z02  西部云基地白顶机房组  ·  Esri z17",
        "caption": "六栋并排白顶大厅是典型风冷机房（美利云/AWS 候选）。紧邻东侧还有两栋带屋顶机电的大厅，再往东一栋；西侧在建，路南另有一组。业主未在图上标出。",
        "boxes": [
            {"lat0": 37.6356, "lon0": 105.3422, "lat1": 37.6388, "lon1": 105.3468, "label": "1 六栋白顶大厅", "color": "#c23b22"},
            {"lat0": 37.6356, "lon0": 105.3510, "lat1": 37.6386, "lon1": 105.3558, "label": "2 东侧大厅", "color": "#2ec4b6"},
            {"lat0": 37.6352, "lon0": 105.3375, "lat1": 37.6388, "lon1": 105.3435, "label": "3 西侧在建/已建", "color": "#c45c26"},
            {"lat0": 37.6359, "lon0": 105.3458, "lat1": 37.6389, "lon1": 105.3476, "label": "5 中间两栋", "color": "#c45c26"},
            {"lat0": 37.6310, "lon0": 105.3338, "lat1": 37.6332, "lon1": 105.3388, "label": "4 路南一组", "color": "#e8e1d4"},
        ],
    },
    {
        "src": "karamay/overview_park_z16.jpg",
        "dest": "karamay/K01_park_overview.jpg",
        "title": "K01  克拉玛依云计算产业园  ·  城区西南",
        "caption": "北到世纪大道、西侧临湖、南到铁路。园区是格子地块，没有中卫那种六栋超大白顶。业主未在 OSM 标出。",
        "boxes": [
            {"lat0": 45.538, "lon0": 84.858, "lat1": 45.560, "lon1": 84.888, "label": "云计算产业园（规划范围）", "color": "#c45c26"},
        ],
    },
    {
        "src": "karamay/core_industrial_z17.jpg",
        "dest": "karamay/K02_halls_candidate.jpg",
        "title": "K02  园区中部矩形厂房  ·  Esri z17",
        "caption": "若干蓝顶/灰顶无内院矩形，体量小于贵安苹果或中卫六栋大厅。可能是华为/移动/碳和等，必须用牌匾核对。西侧弧形楼更像办公。",
        "boxes": [
            {"lat0": 45.5440, "lon0": 84.8645, "lat1": 45.5485, "lon1": 84.8725, "label": "矩形厂房组（机房候选）", "color": "#c45c26"},
            {"lat0": 45.5475, "lon0": 84.8580, "lat1": 45.5520, "lon1": 84.8640, "label": "弧形办公楼（不像机房）", "color": "#7a7164"},
        ],
    },
]


def main():
    for spec in PLATESPEC:
        src = SHOTS / spec["src"]
        if not src.exists():
            print("skip missing", src)
            continue
        compose(src, PLATES / spec["dest"], spec["title"], spec["caption"], spec["boxes"], MOSAICS[spec["src"]])


if __name__ == "__main__":
    main()
