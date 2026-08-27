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
    "zhangbei/overview_xiaodai_z16.jpg": {"lat": 41.1887, "lon": 114.8623, "z": 16, "half": 6},
    "zhangbei/xiaodai_z17.jpg": {"lat": 41.1887, "lon": 114.8623, "z": 17, "half": 5},
    "zhangbei/zhongdu_z17.jpg": {"lat": 41.2812, "lon": 114.6822, "z": 17, "half": 5},
    "zhangbei/miaotan_z17.jpg": {"lat": 41.191, "lon": 114.693, "z": 17, "half": 5},
    "zhangbei/osm_dc_z17.jpg": {"lat": 41.1834, "lon": 114.7302, "z": 17, "half": 5},
    "huailai/overview_donghuayuan_z16.jpg": {"lat": 40.327, "lon": 115.842, "z": 16, "half": 6},
    "huailai/tencent_z17.jpg": {"lat": 40.324848, "lon": 115.819336, "z": 17, "half": 5},
    "huailai/hoyinn_z17.jpg": {"lat": 40.329828, "lon": 115.864606, "z": 17, "half": 5},
    "huailai/cunrui_z17.jpg": {"lat": 40.487, "lon": 115.567, "z": 17, "half": 5},
    "qingyang/overview_wenquan_z16.jpg": {"lat": 35.7335, "lon": 107.7044, "z": 16, "half": 6},
    "qingyang/chindata_z17.jpg": {"lat": 35.7334, "lon": 107.7018, "z": 17, "half": 5},
    "qingyang/operators_z17.jpg": {"lat": 35.729, "lon": 107.698, "z": 17, "half": 5},
    "horinger/overview_yungu_z16.jpg": {"lat": 40.5390, "lon": 111.8230, "z": 16, "half": 6},
    "horinger/cmcc_z17.jpg": {"lat": 40.5369, "lon": 111.8164, "z": 17, "half": 5},
    "horinger/telecom_z17.jpg": {"lat": 40.5411, "lon": 111.8291, "z": 17, "half": 5},
    "shaoguan/overview_huashao_z16.jpg": {"lat": 24.7830, "lon": 113.5025, "z": 16, "half": 6},
    "shaoguan/huanan_z17.jpg": {"lat": 24.7887, "lon": 113.5003, "z": 17, "half": 5},
    "shaoguan/phase2_z17.jpg": {"lat": 24.7789, "lon": 113.5026, "z": 17, "half": 5},
    "wuhu/overview_cluster_z16.jpg": {"lat": 31.3455, "lon": 118.2900, "z": 16, "half": 6},
    "wuhu/huawei_z17.jpg": {"lat": 31.3484, "lon": 118.2862, "z": 17, "half": 5},
    "wuhu/zhisuan_z17.jpg": {"lat": 31.3424, "lon": 118.2971, "z": 17, "half": 5},
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
    {
        "src": "zhangbei/overview_xiaodai_z16.jpg",
        "dest": "zhangbei/ZB01_xiaodai_overview.jpg",
        "title": "ZB01  张北小二台 阿里数据港  ·  Esri z16",
        "caption": "圆心 41.1887°N 114.8623°E。围墙大院在风电和光伏之间，不是县城。西侧蓝/红顶厂房不算机房。",
        "boxes": [
            {"lat0": 41.186563, "lon0": 114.859448, "lat1": 41.190869, "lon1": 114.865054, "label": "1 阿里数据港（OSM）", "color": "#2ec4b6"},
            {"lat0": 41.185351, "lon0": 114.858847, "lat1": 41.188848, "lon1": 114.862874, "label": "2 上海数据港 A2", "color": "#c45c26"},
        ],
    },
    {
        "src": "zhangbei/xiaodai_z17.jpg",
        "dest": "zhangbei/ZB02_xiaodai_halls.jpg",
        "title": "ZB02  小二台两排大厅  ·  41.1887°N 114.8623°E",
        "caption": "两排各约 5 栋无内院长厅，屋顶深色机电/光伏条带。南端两栋更大白顶厅落在 A2 北缘。西侧蓝顶厂房排除。",
        "boxes": [
            {"lat0": 41.187617, "lon0": 114.860129, "lat1": 41.190604, "lon1": 114.864635, "label": "两排大厅（约 10 栋）", "color": "#2ec4b6"},
            {"lat0": 41.186406, "lon0": 114.860344, "lat1": 41.187617, "lon1": 114.862919, "label": "南端两栋白顶厅", "color": "#c23b22"},
        ],
    },
    {
        "src": "zhangbei/zhongdu_z17.jpg",
        "dest": "zhangbei/ZB03_zhongdu.jpg",
        "title": "ZB03  阿里巴巴张北中都草原  ·  41.2812°N 114.6822°E",
        "caption": "OSM way/1068446080。孤立方院约 8–10 栋白顶模组，西侧贴一块光伏。北侧村庄不算。",
        "boxes": [
            {"lat0": 41.279443, "lon0": 114.679823, "lat1": 41.282957, "lon1": 114.684517, "label": "中都草原机房（OSM）", "color": "#2ec4b6"},
            {"lat0": 41.278951, "lon0": 114.676173, "lat1": 41.282176, "lon1": 114.679713, "label": "西侧光伏", "color": "#7a7164"},
        ],
    },
    {
        "src": "zhangbei/miaotan_z17.jpg",
        "dest": "zhangbei/ZB04_miaotan.jpg",
        "title": "ZB04  庙滩互通机房组  ·  41.191°N 114.693°E",
        "caption": "无 OSM 业主名。互通东侧无内院长厅 + 蓝顶冷却/光伏，东北、东南还有模组。北侧大棚排除。",
        "boxes": [
            {"lat0": 41.187504, "lon0": 114.691451, "lat1": 41.191864, "lon1": 114.696815, "label": "1 大厅 + 蓝顶冷却", "color": "#c45c26"},
            {"lat0": 41.191864, "lon0": 114.695206, "lat1": 41.195739, "lon1": 114.700570, "label": "2 东北模组", "color": "#c23b22"},
            {"lat0": 41.183628, "lon0": 114.696279, "lat1": 41.188069, "lon1": 114.702716, "label": "3 东南模组", "color": "#c45c26"},
        ],
    },
    {
        "src": "zhangbei/osm_dc_z17.jpg",
        "dest": "zhangbei/ZB05_osm_dc.jpg",
        "title": "ZB05  OSM 张北数据中心  ·  41.1834°N 114.7302°E",
        "caption": "way/1256794600。两簇灰顶模组。南侧体育馆/住宅、东侧大棚、中间大跨白顶厂房不算机房。业主未标。",
        "boxes": [
            {"lat0": 41.181511, "lon0": 114.726821, "lat1": 41.185277, "lon1": 114.733574, "label": "OSM 张北数据中心", "color": "#2ec4b6"},
            {"lat0": 41.1835, "lon0": 114.7275, "lat1": 41.1863, "lon1": 114.7325, "label": "西簇灰顶模组", "color": "#c45c26"},
            {"lat0": 41.1835, "lon0": 114.7328, "lat1": 41.1861, "lon1": 114.7368, "label": "东簇灰顶模组", "color": "#c23b22"},
        ],
    },
    {
        "src": "huailai/overview_donghuayuan_z16.jpg",
        "dest": "huailai/HL01_donghuayuan_overview.jpg",
        "title": "HL01  怀来东花园葡萄大道  ·  Esri z16",
        "caption": "西端腾讯东园与中国移动紧邻，南侧秦淮东花园，东端合盈大厅网格。中间是大南辛堡村。",
        "boxes": [
            {"lat0": 40.322378, "lon0": 115.815366, "lat1": 40.327319, "lon1": 115.823306, "label": "1 腾讯东园", "color": "#c23b22"},
            {"lat0": 40.322904, "lon0": 115.812175, "lat1": 40.325645, "lon1": 115.815548, "label": "2 中国移动", "color": "#2ec4b6"},
            {"lat0": 40.312867, "lon0": 115.821761, "lat1": 40.317252, "lon1": 115.827126, "label": "3 秦淮东花园", "color": "#2ec4b6"},
            {"lat0": 40.3280, "lon0": 115.8514, "lat1": 40.3385, "lon1": 115.8665, "label": "4 合盈大厅网格", "color": "#c45c26"},
        ],
    },
    {
        "src": "huailai/tencent_z17.jpg",
        "dest": "huailai/HL02_tencent_cmcc.jpg",
        "title": "HL02  腾讯东园 × 中国移动  ·  Esri z17",
        "caption": "OSM：腾讯 landuse=construction，移动 landuse=industrial。东侧约六栋光伏条带大厅已封顶，北侧基坑/蓝水塘续建。",
        "boxes": [
            {"lat0": 40.322378, "lon0": 115.815366, "lat1": 40.327319, "lon1": 115.823306, "label": "腾讯华北东园（OSM）", "color": "#c23b22"},
            {"lat0": 40.323154, "lon0": 115.817549, "lat1": 40.326426, "lon1": 115.822914, "label": "光伏条带大厅", "color": "#2ec4b6"},
            {"lat0": 40.322904, "lon0": 115.812175, "lat1": 40.325645, "lon1": 115.815548, "label": "中国移动（OSM）", "color": "#2ec4b6"},
            {"lat0": 40.326426, "lon0": 115.816476, "lat1": 40.329125, "lon1": 115.822377, "label": "北侧基坑续建", "color": "#c45c26"},
        ],
    },
    {
        "src": "huailai/hoyinn_z17.jpg",
        "dest": "huailai/HL03_hoyinn.jpg",
        "title": "HL03  合盈数据（怀来）科技产业园  ·  40.3298°N 115.8646°E",
        "caption": "环评中心点。十余栋超大无内院矩形，屋顶机电。无 OSM 名。南侧葡萄大道，路南住宅不算机房。",
        "boxes": [
            {"lat0": 40.3280, "lon0": 115.8514, "lat1": 40.3385, "lon1": 115.8665, "label": "合盈大厅网格（环评）", "color": "#c45c26"},
        ],
    },
    {
        "src": "huailai/cunrui_z17.jpg",
        "dest": "huailai/HL04_cunrui.jpg",
        "title": "HL04  存瑞镇头二营北  ·  40.487°N 115.567°E",
        "caption": "路南四栋超大白顶条带大厅，路北多排模块化白顶机房。无 OSM 业主。路西体育场排除。",
        "boxes": [
            {"lat0": 40.484657, "lon0": 115.558105, "lat1": 40.487921, "lon1": 115.570228, "label": "路南四栋大厅", "color": "#c23b22"},
            {"lat0": 40.488411, "lon0": 115.561109, "lat1": 40.491838, "lon1": 115.569477, "label": "路北模组（业主候选）", "color": "#c45c26"},
            {"lat0": 40.486942, "lon0": 115.554135, "lat1": 40.489553, "lon1": 115.558105, "label": "体育场（排除）", "color": "#7a7164"},
        ],
    },
    {
        "src": "qingyang/overview_wenquan_z16.jpg",
        "dest": "qingyang/QY01_wenquan_overview.jpg",
        "title": "QY01  庆阳温泉镇东数西算园  ·  Esri z16",
        "caption": "圆心 35.7335°N 107.7044°E。图面正中是新旧瓦片接缝。接缝以东能看见秦淮大厅；以西 OSM 多边形仍是村庄。",
        "boxes": [
            {"lat0": 35.731741, "lon0": 107.700939, "lat1": 35.735355, "lon1": 107.707879, "label": "秦淮（OSM，可见大厅）", "color": "#c23b22"},
            {"lat0": 35.734761, "lon0": 107.696918, "lat1": 35.738841, "lon1": 107.700505, "label": "能建（OSM，未见大厅）", "color": "#c45c26"},
            {"lat0": 35.732226, "lon0": 107.695879, "lat1": 35.734264, "lon1": 107.700895, "label": "智慧蓝图（耕地）", "color": "#7a7164"},
        ],
    },
    {
        "src": "qingyang/chindata_z17.jpg",
        "dest": "qingyang/QY02_chindata.jpg",
        "title": "QY02  秦淮数据零碳数据中心产业基地  ·  Esri z17",
        "caption": "OSM way/1412509897。围栏内一栋无内院白顶大厅（屋面未完），东南蓝顶动力楼，东侧刮地垫层。仍在建。",
        "boxes": [
            {"lat0": 35.731741, "lon0": 107.700939, "lat1": 35.735355, "lon1": 107.707879, "label": "秦淮 OSM 工业用地", "color": "#c45c26"},
            {"lat0": 35.732579, "lon0": 107.700648, "lat1": 35.734146, "lon1": 107.702794, "label": "白顶大厅（在建）", "color": "#c23b22"},
            {"lat0": 35.732230, "lon0": 107.702579, "lat1": 35.733276, "lon1": 107.704082, "label": "蓝顶动力楼", "color": "#2ec4b6"},
        ],
    },
    {
        "src": "horinger/overview_yungu_z16.jpg",
        "dest": "horinger/HG01_yungu_overview.jpg",
        "title": "HG01  和林格尔盛乐园区  ·  Esri z16",
        "caption": "圆心 40.539°N 111.823°E。西侧移动白顶大厅最典型，东侧电信信息园。右下大跨蓝顶厂房排除。",
        "boxes": [
            {"lat0": 40.531479, "lon0": 111.808712, "lat1": 40.542275, "lon1": 111.824007, "label": "1 中国移动（OSM）", "color": "#2ec4b6"},
            {"lat0": 40.536461, "lon0": 111.822759, "lat1": 40.545724, "lon1": 111.835348, "label": "2 中国电信（OSM）", "color": "#c45c26"},
        ],
    },
    {
        "src": "horinger/cmcc_z17.jpg",
        "dest": "horinger/HG02_cmcc.jpg",
        "title": "HG02  中国移动呼和浩特数据中心  ·  40.5369°N 111.8164°E",
        "caption": "OSM way/699967332。北半无内院白顶/灰顶大厅并排，南半基坑续建。北侧黑顶模组无 OSM 名。",
        "boxes": [
            {"lat0": 40.531479, "lon0": 111.808712, "lat1": 40.542275, "lon1": 111.824007, "label": "移动 OSM 工业用地", "color": "#c45c26"},
            {"lat0": 40.5348, "lon0": 111.8115, "lat1": 40.5398, "lon1": 111.8205, "label": "白顶大厅组", "color": "#2ec4b6"},
            {"lat0": 40.5398, "lon0": 111.8095, "lat1": 40.5435, "lon1": 111.8160, "label": "北侧黑顶模组（候选）", "color": "#c23b22"},
        ],
    },
    {
        "src": "horinger/telecom_z17.jpg",
        "dest": "horinger/HG03_telecom.jpg",
        "title": "HG03  中国电信云计算内蒙古信息园  ·  40.5411°N 111.8291°E",
        "caption": "OSM way/566233416。环形广场北侧曲面楼偏办公。南侧土建。大厅不如西侧移动园区典型。",
        "boxes": [
            {"lat0": 40.536461, "lon0": 111.822759, "lat1": 40.545724, "lon1": 111.835348, "label": "电信 OSM 工业用地", "color": "#c45c26"},
            {"lat0": 40.5430, "lon0": 111.8265, "lat1": 40.5465, "lon1": 111.8320, "label": "曲面办公（不像机房）", "color": "#7a7164"},
        ],
    },
    {
        "src": "shaoguan/overview_huashao_z16.jpg",
        "dest": "shaoguan/SG01_huashao_overview.jpg",
        "title": "SG01  韶关沐溪湖西 华韶/华南数谷  ·  Esri z16",
        "caption": "圆心 24.783°N 113.5025°E。半岛在建大厅是最像机房的一处。沿路白顶厂房是工业园。",
        "boxes": [
            {"lat0": 24.786618, "lon0": 113.499166, "lat1": 24.790736, "lon1": 113.501360, "label": "1 华南数谷（在建）", "color": "#c23b22"},
            {"lat0": 24.780955, "lon0": 113.503692, "lat1": 24.782745, "lon1": 113.505767, "label": "2 华韶数据谷", "color": "#c45c26"},
            {"lat0": 24.776229, "lon0": 113.499946, "lat1": 24.781503, "lon1": 113.505250, "label": "3 华韶二期", "color": "#c45c26"},
        ],
    },
    {
        "src": "shaoguan/huanan_z17.jpg",
        "dest": "shaoguan/SG02_huanan.jpg",
        "title": "SG02  华南数谷智算中心  ·  24.7887°N 113.5003°E",
        "caption": "OSM way/1474786000。沐溪湖半岛超大矩形在建，屋面未完。东侧别墅和沿路厂房不算。",
        "boxes": [
            {"lat0": 24.786618, "lon0": 113.499166, "lat1": 24.790736, "lon1": 113.501360, "label": "半岛在建大厅（OSM）", "color": "#c23b22"},
        ],
    },
    {
        "src": "shaoguan/phase2_z17.jpg",
        "dest": "shaoguan/SG03_phase2.jpg",
        "title": "SG03  华韶数据谷二期  ·  24.7789°N 113.5026°E",
        "caption": "OSM way/1536927107 landuse=construction。多边形内主要是垫层和边坡。南侧大跨白顶厂房排除。",
        "boxes": [
            {"lat0": 24.776229, "lon0": 113.499946, "lat1": 24.781503, "lon1": 113.505250, "label": "二期 OSM construction", "color": "#c45c26"},
            {"lat0": 24.780955, "lon0": 113.503692, "lat1": 24.782745, "lon1": 113.505767, "label": "华韶一期方楼", "color": "#2ec4b6"},
        ],
    },
    {
        "src": "wuhu/overview_cluster_z16.jpg",
        "dest": "wuhu/WH01_cluster_overview.jpg",
        "title": "WH01  芜湖三山组团  ·  Esri z16",
        "caption": "圆心 31.3484°N 118.2862°E。田里独立在建的是华为云。右下冷却塔是电厂。右上罐区/大厂房排除。",
        "boxes": [
            {"lat0": 31.346782, "lon0": 118.283760, "lat1": 31.350043, "lon1": 118.288691, "label": "1 华为云（在建）", "color": "#c23b22"},
            {"lat0": 31.341998, "lon0": 118.296593, "lat1": 31.342829, "lon1": 118.297570, "label": "2 智算（OSM 小地块）", "color": "#c45c26"},
        ],
    },
    {
        "src": "wuhu/huawei_z17.jpg",
        "dest": "wuhu/WH02_huawei.jpg",
        "title": "WH02  华为云华东（芜湖）数据中心  ·  Esri z17",
        "caption": "OSM way/1341908908。水田中超大无内院矩形，钢结构+塔吊+垫层。典型机房土建。",
        "boxes": [
            {"lat0": 31.346782, "lon0": 118.283760, "lat1": 31.350043, "lon1": 118.288691, "label": "华为云 OSM（在建）", "color": "#c23b22"},
        ],
    },
    {
        "src": "wuhu/zhisuan_z17.jpg",
        "dest": "wuhu/WH03_zhisuan.jpg",
        "title": "WH03  芜湖一体化智算中心  ·  31.3424°N 118.2971°E",
        "caption": "OSM 多边形约 80 m。路西小白楼+基坑。接缝以东冷却塔是电厂，排除。左上是华为云在建。",
        "boxes": [
            {"lat0": 31.341998, "lon0": 118.296593, "lat1": 31.342829, "lon1": 118.297570, "label": "智算 OSM", "color": "#c45c26"},
            {"lat0": 31.346782, "lon0": 118.283760, "lat1": 31.350043, "lon1": 118.288691, "label": "华为云（同幅西北）", "color": "#c23b22"},
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
