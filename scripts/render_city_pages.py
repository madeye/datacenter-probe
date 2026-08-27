#!/usr/bin/env python3
"""Render city survey pages from a small data dict."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"

HEAD = """<!DOCTYPE html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="https://madeye.github.io/datacenter-probe/{slug}/">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="zh_CN">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="https://madeye.github.io/datacenter-probe/{slug}/">
  <meta property="og:image" content="https://madeye.github.io/datacenter-probe/social-card.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;1,400&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@600;700&display=swap">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
  <link rel="stylesheet" href="../probe.css">
</head>
<body>
  <div class="neatline">
    <span><a href="../">Datacenter Probe</a>  ·  {city}</span>
    <span id="tick">{tick}</span>
    <span class="hide-narrow">Esri World Imagery  ·  2026-08-27</span>
  </div>
  <header class="mast">
    <p class="series">Satellite reconnaissance  ·  {region}</p>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
    <figure class="hero">
      <img src="{hero}" alt="{hero_alt}" width="1200" height="1200">
      <figcaption>{hero_cap}</figcaption>
    </figure>
  </header>
  <div id="map" role="region" aria-label="卫星地图"></div>
  <p class="map-caption">
    <span><i class="legend-chip" style="background:#c23b22"></i>在建 / 高置信机房</span>
    <span><i class="legend-chip" style="background:#2ec4b6"></i>已投运 / OSM 具名</span>
    <span><i class="legend-chip" style="background:#c45c26"></i>候选 / 业主待核</span>
    <span><i class="legend-chip" style="background:#7a7164"></i>排除或不像机房</span>
    <span>底图 Esri World Imagery（WGS84）</span>
  </p>
  <section class="findings" aria-label="候选">
{findings}
  </section>
{sites}
  <section class="method">
    <h2>怎么判，什么不算</h2>
    {method}
    <p><a href="{maps}" target="_blank" rel="noopener">在 Google 卫星图打开圆心 ↗</a></p>
  </section>
  <nav class="city-nav" aria-label="其他城市">
    <span>五座城</span>
    <a href="../guian/">贵安</a> · <a href="../ulanqab/">乌兰察布</a> · <a href="../yangquan/">阳泉</a> · <a href="../zhongwei/">中卫</a> · <a href="../karamay/">克拉玛依</a>
    <span>续卷</span>
    <a href="../zhangbei/">张北</a> · <a href="../huailai/">怀来</a> · <a href="../qingyang/">庆阳</a> · <a href="../horinger/">和林格尔</a> · <a href="../shaoguan/">韶关</a> · <a href="../wuhu/">芜湖</a>
  </nav>
  <footer>
    <div>
      Datacenter Probe  ·  {city}  ·  标注截图仅供复核，不是权属证明。
      影像 © Esri, Maxar, Earthstar Geographics。{footer}
    </div>
  </footer>
  <div class="lightbox" id="lb" hidden>
    <button type="button" id="lb-close">关闭</button>
    <img id="lb-img" alt="">
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <script>window.PROBE = {probe};</script>
  <script src="../probe.js"></script>
</body>
</html>
"""


def finding(fid, title, href, text, badge, klass):
    return f"""    <article class="finding">
      <div class="id">{fid}</div>
      <h2><a href="#{href}">{title}</a></h2>
      <p>{text}</p>
      <span class="badge {klass}">{badge}</span>
    </article>"""


def site(sid, coord, title, meta, badge, klass, bullets, ops, maps, plates):
    lis = "\n".join(f"        <li>{b}</li>" for b in bullets)
    op = "".join(f"<span>{o}</span>" for o in ops)
    figs = "\n".join(
        f"""      <figure class="plate">
        <img class="sat" src="{src}" alt="{alt}">
        <figcaption>{cap}</figcaption>
      </figure>"""
        for src, alt, cap in plates
    )
    return f"""  <section class="site" id="{sid}">
    <div class="site-rail">
      <p class="coord">{coord}</p>
      <h2>{title}</h2>
      <p class="meta">{meta}</p>
      <p class="badge {klass}">{badge}</p>
      <ul>
{lis}
      </ul>
      <div class="ops">{op}</div>
      <p><a class="maps-link" href="{maps}" target="_blank" rel="noopener">在 Google 卫星图打开 ↗</a></p>
    </div>
    <div class="plates">
{figs}
    </div>
  </section>"""


def gmaps(lat, lon, m=1200):
    return f"https://www.google.com/maps/@{lat},{lon},{m}m/data=!3m1!1e3"


PAGES = []

# --- Gui'an ---
PAGES.append(dict(
    slug="guian", city="贵安", region="Guizhou",
    title="贵安数据中心建设情况",
    desc="以数谷大道华为—腾讯组团为圆心，卫星核对腾讯七星洞库、华为云上屯、苹果 iCloud。",
    tick="26.3680°N  106.4900°E  ·  r = 50 km",
    h1="贵安周边数据中心建设情况",
    lede="智东西写「南贵北乌」，南贵就是贵安。能具名的机房收在数谷大道一条东西向走廊里：东端华为云上屯和腾讯七星隔路相望，西端是苹果 iCloud 两栋超大白顶矩形。腾讯主体在山体地下，地面只看得见洞库山丘和路西四栋大厅。走廊之外还有几处大白顶厂房，本次没有名称对应，不计入。",
    hero="../plates/guian/G01_cluster_overview.jpg",
    hero_alt="贵安数谷大道集群：华为、腾讯、苹果相对位置",
    hero_cap="HERO  ·  数谷大道  ·  1 华为云上屯 / 2 腾讯七星 / 3 苹果 iCloud",
    findings="\n".join([
        finding("G-HUAWEI  ·  已投运园区", "华为云上屯", "huawei", "环湖红顶园区，OSM 名称云上屯华为。园区本身是办公形态，机房楼未逐栋分出。", "高置信 · 已投运", "high"),
        finding("G-TENCENT  ·  地下洞库", "腾讯七星", "tencent", "OSM 标 layer=-1。卫星只见环路围着的山体和山脚一排圆罐；路西四栋白顶大厅是洞外候选。", "高 · 洞库", "high"),
        finding("G-APPLE  ·  两栋大厅", "苹果 iCloud", "apple", "OSM 具名。两栋并排超大白顶矩形，屋顶冷机成排，已投运。", "高置信 · 已投运", "high"),
        finding("G-SOUTH  ·  南侧混杂", "富士康 / 运营商", "south", "地面厂房和在建区混在一起，隧道机房从上面看不见。", "中 · 混杂", "mid"),
    ]),
    sites="\n".join([
        site("huawei", "26.3708°N  106.5082°E", "华为云上屯",
             "金马 / 数谷大道东端。公开报道里的七星湖园区，人工湖加红顶楼，不像普通仓储。",
             "高置信 · 已投运园区", "high",
             ["OSM：云上屯华为，landuse=commercial", "环湖低层红顶组团、人工湖，与报道的园区形态相符；没有超大白顶，机房楼不能从园区里单独指认", "马场 AZ3（兴安大道×金普路，2026 招标）本次图层未见典型超大机房"],
             ["华为云", "七星湖", "云上屯"],
             gmaps(26.3708, 106.5082, 800),
             [("../plates/guian/G02_huawei_tencent.jpg", "华为云上屯与腾讯七星隔路相望", "PLATE G02  ·  华为 × 腾讯  ·  Esri z17")]),
        site("tencent", "26.3696°N  106.5007°E", "腾讯七星洞库",
             "栖凤坡。OSM 把这座山标成腾讯贵安七星数据中心，building=yes 且 layer=-1，是洞库而不是地面大厅。",
             "高置信 · 地下", "high",
             ["卫星：环路围着的独立山丘，山脚一排圆罐（冷却/储水）", "路西四栋白顶大厅可能是洞外扩建，业主待核"],
             ["腾讯"],
             gmaps(26.3696, 106.5007, 700),
             [("../plates/guian/G02_huawei_tencent.jpg", "腾讯洞库山体与路西白顶大厅", "PLATE G02  ·  洞库山体  ·  26.3696°N 106.5007°E")]),
        site("apple", "26.3628°N  106.4672°E", "苹果 iCloud",
             "黔中 / 兴安大道一带。OSM 直接写 Apple iCloud Gui'An data center，和两栋超大白顶矩形对得上。",
             "高置信 · 已投运", "high",
             ["两栋并排、屋顶冷机成排，是走廊里最典型的超大型机房形态", "2021 年报道建成投运，影像符合"],
             ["苹果", "云上贵州"],
             gmaps(26.3628, 106.4672, 500),
             [("../plates/guian/G03_apple_icloud.jpg", "苹果 iCloud 两栋超大机房", "PLATE G03  ·  苹果 iCloud  ·  已投运")]),
        site("south", "26.3500°N  106.4774°E", "南侧大院",
             "富士康工业用地在此。绿色隧道数据中心在山里，地面影像不能当成机房。三大运营商信息园报道也在这条走廊，OSM 未逐栋标注。",
             "中置信 · 混杂", "mid",
             ["不要把普通厂房算作 IDC", "走廊北侧约 26.42°N 106.50°E 另有一处大白顶厂房，无名称对应，未计入", "华为 AZ3 马场续建需更新图层再查"],
             ["富士康？", "电信/移动/联通？"],
             gmaps(26.350, 106.477, 1500),
             [("../plates/guian/G01_cluster_overview.jpg", "数谷走廊南侧大院", "PLATE G01  ·  走廊总图  ·  南侧大院在苹果东南")]),
    ]),
    method="""<p>Esri World Imagery 对照 OSM 具名要素。腾讯是洞库，判据改成山体 + 洞外方仓，不能要求看见常规大厅。</p>
    <h3>算作机房</h3>
    <ul><li>超大无内院矩形、屋顶冷机</li><li>OSM telecom=data_center 或品牌名</li><li>洞库：layer=-1 的山体 + 洞外大厅</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>机场跑道</li><li>住宅和学校操场</li><li>富士康地面厂房本身</li></ul>""",
    maps=gmaps(26.368, 106.490, 8000),
    footer="对照：智东西 2022-03-11《数据中心造就的五座城》。",
    probe='{"origin":[26.368,106.490],"originName":"圆心 · 数谷组团","radiusKm":50,"zoom":13,"sites":[{"id":"huawei","name":"华为云上屯","pos":[26.3708,106.5082],"color":"#2ec4b6","note":"已投运园区"},{"id":"tencent","name":"腾讯七星","pos":[26.3696,106.5007],"color":"#c45c26","note":"洞库"},{"id":"apple","name":"苹果 iCloud","pos":[26.3628,106.4672],"color":"#2ec4b6","note":"两栋大厅已投运"},{"id":"south","name":"南侧大院","pos":[26.350,106.477],"color":"#7a7164","note":"混杂工业"}]}',
))

# --- Yangquan ---
PAGES.append(dict(
    slug="yangquan", city="阳泉", region="Shanxi",
    title="阳泉数据中心建设情况",
    desc="以经开区东区大连街为圆心：百度云计算中心 8 栋模组可指认，云峰智算在北侧。",
    tick="37.8600°N  113.6230°E  ·  r = 50 km",
    h1="阳泉周边数据中心建设情况",
    lede="五座城里阳泉的机房最少，也最集中。能指认的只有大连街这一块：OSM 百度多边形南端三栋屋顶机电密布的楼，东北侧约 8 栋灰顶模组，模组东边一栋屋顶机电密布的新楼。再往北是 OSM 标的云峰智算，地块很小。50 公里圈里没有第二条走廊。",
    hero="../plates/yangquan/Y03_dalian_overview.jpg",
    hero_alt="阳泉经开区东区大连街：百度和云峰",
    hero_cap="HERO  ·  大连街  ·  百度在南、云峰在北",
    findings="\n".join([
        finding("Y-BAIDU  ·  8 栋模组", "百度云计算", "baidu", "OSM 带 telecom=data_center。多边形南端三栋 + 东北侧约 8 栋灰顶矩形是形态上的机房。", "高置信 · 已投运", "high"),
        finding("Y-YUNFENG  ·  北侧小地块", "云峰智算", "yunfeng", "OSM 有名，地块约 140×290 m。2024–2025 报道装柜测试；模组东侧那栋新楼是扩建候选。", "中高 · 部分建成", "mid"),
        finding("排除  ·  采坑", "采坑 / 蓝顶厂房", "baidu", "右上采坑、模组南边两栋蓝顶厂房、铁路南普通厂房不算机房。", "排除", "low"),
        finding("50 km  ·  无第二走廊", "其余方向", "baidu", "城区、荫营、白泉方向未见同等超大矩形阵列。", "未确认", "low"),
    ]),
    sites="\n".join([
        site("baidu", "37.8597°N  113.6225°E", "百度云计算中心",
             "经开区东区，大连街两侧。OSM 多边形罩住环形广场（云谷创新园办公），但多边形南端三栋屋顶机电密布的楼已经是机房形态；约 8 栋灰顶模组在多边形东北外侧。",
             "高置信 · 已投运", "high",
             ["公开报道 8 个高标准模组楼，和东北侧约 8 栋灰顶大厅对应", "南端三栋屋顶机电密布，不是普通厂房", "模组南边两栋蓝顶厂房不计"],
             ["百度"],
             gmaps(37.8597, 113.6225, 600),
             [("../plates/yangquan/Y01_baidu.jpg", "百度 OSM 多边形与东北 8 栋模组", "PLATE Y01  ·  百度  ·  37.8597°N 113.6225°E")]),
        site("yunfeng", "37.8693°N  113.6273°E", "云峰智算",
             "百度模组北侧、隔一条路。OSM 地块约 140×290 m，一栋主楼。报道 2024 年起建设、2025 装柜测试。",
             "中高置信 · 部分建成", "mid",
             ["模组东侧一栋深色新楼屋顶机电密布，是云峰或百度扩建候选，本次无法分归属", "右上采坑排除"],
             ["云峰", "云山数据"],
             gmaps(37.8693, 113.6273, 600),
             [("../plates/yangquan/Y02_yunfeng.jpg", "云峰小地块与 8 栋模组", "PLATE Y02  ·  云峰  ·  北侧土建")]),
    ]),
    method="""<p>阳泉不像乌兰察布或贵安那样铺开。50 km 圈里能指认的机房就这一块。</p>
    <h3>算作机房</h3>
    <ul><li>并排灰顶大矩形</li><li>屋顶机电密布的方楼</li><li>OSM telecom=data_center</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>采坑</li><li>蓝顶厂房、铁路南侧普通厂房</li><li>环形广场办公（云谷）不要单独当机房</li></ul>""",
    maps=gmaps(37.860, 113.623, 5000),
    footer="对照：智东西 2022-03-11《数据中心造就的五座城》。",
    probe='{"origin":[37.860,113.623],"originName":"圆心 · 大连街百度","radiusKm":50,"zoom":14,"sites":[{"id":"baidu","name":"百度云计算","pos":[37.8597,113.6225],"color":"#2ec4b6","note":"南端三栋 + 东北约 8 栋模组"},{"id":"yunfeng","name":"云峰智算","pos":[37.8693,113.6273],"color":"#c45c26","note":"部分建成"}]}',
))

# --- Zhongwei ---
PAGES.append(dict(
    slug="zhongwei", city="中卫", region="Ningxia",
    title="中卫数据中心建设情况",
    desc="西部云基地在城北戈壁。六栋白顶大厅是典型风冷机房，OSM 把整条带标成 AWS。",
    tick="37.6368°N  105.3468°E  ·  r = 50 km",
    h1="中卫周边数据中心建设情况",
    lede="中卫的机房不在沙坡头城区，而在北面戈壁上的西部云基地。Esri 图上是一条东西向、光伏夹着的园区：六栋白顶大厅并排是主体，紧邻东侧两栋带屋顶机电，再往东一栋，西侧在建，路南另有一组；东端还有整平垫层空着。OSM 把整条带写成 AWS，实际上美利云和三大运营商也在同一个园。",
    hero="../plates/zhongwei/Z01_cloudbase_overview.jpg",
    hero_alt="中卫西部云基地戈壁园区总览",
    hero_cap="HERO  ·  西部云基地  ·  OSM 标注为 AWS 的整条工业用地",
    findings="\n".join([
        finding("Z-HALLS  ·  六栋白顶", "云基地机房组", "halls", "并排白顶大厅 + 冷机，典型风冷机房。业主未逐栋标出。", "高 · 是机房", "high"),
        finding("Z-EAST  ·  东侧三栋", "中间两栋 + 东侧一栋", "halls", "六栋东邻两栋带屋顶机电，再往东一栋独立大厅，旁边整平垫层。", "高 · 已建+垫层", "high"),
        finding("Z-WEST  ·  续建", "西侧 / 路南", "halls", "西侧有塔吊、部分封顶；路南一组带圆池和条状机房。符合续建报道。", "中高 · 在建", "mid"),
        finding("排除  ·  化工厂", "南侧化工", "halls", "储罐管廊，不是机房。", "排除", "low"),
    ]),
    sites="\n".join([
        site("halls", "37.6372°N  105.3445°E", "西部云基地",
             "中卫工业园凤云路一带。OSM 名称 Amazon Web Services China (Ningxia) Data Centre，多边形宽约 2.5 km，覆盖整园。",
             "高置信 · 机房形态 / 中 · 业主", "high",
             ["六栋白顶大厅是影像上最像美利云/AWS 风冷机房的一组", "东邻两栋、再东一栋都带屋顶机电，同一园区连片", "东端垫层说明还在扩", "迎水桥、寺口子分园在 50 km 圈内，本次未出特写"],
             ["AWS？", "美利云？", "移动/联通/电信？", "天云？"],
             gmaps(37.6368, 105.3468, 800),
             [("../plates/zhongwei/Z02_white_halls.jpg", "西部云基地六栋白顶大厅", "PLATE Z02  ·  白顶机房组  ·  Esri z17"),
              ("../plates/zhongwei/Z01_cloudbase_overview.jpg", "西部云基地戈壁总图", "PLATE Z01  ·  总图  ·  光伏围着园区")]),
    ]),
    method="""<p>圆心不在中卫城区，在城北戈壁。南侧化工厂容易被 OSM 工业用地带进来，必须看储罐。</p>
    <h3>算作机房</h3>
    <ul><li>戈壁上超大白顶无内院矩形、模块化并排</li><li>旁边光伏可以当配套，本身不是机房</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>储罐、管廊、排烟</li><li>城区政府办公楼（云计算大数据发展局）</li></ul>""",
    maps=gmaps(37.6368, 105.3468, 8000),
    footer="对照：智东西 2022-03-11《数据中心造就的五座城》。",
    probe='{"origin":[37.6368,105.3468],"originName":"圆心 · 西部云基地","radiusKm":50,"zoom":13,"sites":[{"id":"halls","name":"白顶机房组","pos":[37.6372,105.3445],"color":"#c23b22","note":"六栋白顶大厅"}]}',
))

# --- Karamay ---
PAGES.append(dict(
    slug="karamay", city="克拉玛依", region="Xinjiang",
    title="克拉玛依数据中心建设情况",
    desc="城区西南云计算产业园可确认，但 OSM 没有逐栋机房名，体量小于贵安和中卫。",
    tick="45.5450°N  84.8700°E  ·  r = 50 km",
    h1="克拉玛依周边数据中心建设情况",
    lede="克拉玛依把六座机房写在同一座 15 平方公里的园里。卫星能确认园在城区西南、世纪大道以南、铁路以北，格子路网里散着若干蓝顶、灰顶矩形。可是 OSM 没有 data_centre 名称，单栋体量也明显小于贵安苹果或中卫的六栋大厅。哪栋是谁的，要靠规划图或牌匾。",
    hero="../plates/karamay/K01_park_overview.jpg",
    hero_alt="克拉玛依云计算产业园总览",
    hero_cap="HERO  ·  云计算产业园  ·  世纪大道以南、临湖、铁路以北",
    findings="\n".join([
        finding("K-PARK  ·  整园", "云计算产业园", "park", "位置与政府稿一致。格子地块，没有超大白顶阵列。", "中 · 园区确认", "mid"),
        finding("K-HALLS  ·  矩形厂房", "矩形厂房组", "park", "蓝顶/灰顶无内院矩形，可能是六座中的若干，业主未标。", "中 · 候选", "mid"),
        finding("排除  ·  弧形楼", "弧形办公", "park", "西侧弧形楼更像办公或培训，不像机房。", "排除", "low"),
        finding("排除  ·  油田", "油田罐区", "park", "罐区不在本园，不要算进来。", "排除", "low"),
    ]),
    sites="\n".join([
        site("park", "45.5450°N  84.8700°E", "云计算产业园",
             "政府稿：东起彩云路（幸福路），北到世纪大道，南至奎北铁路。华为云、移动智算、中石油、灾备、碳和液冷、丝路新云都写在这个园里。",
             "中置信 · 园区确认、楼未钉死", "mid",
             ["移动智算报道有「玻璃立方」，本次图层未单独指认", "碳和液冷二期报道在筹备，卫星上还不能当已开工"],
             ["华为云？", "移动智算？", "中石油？", "碳和？", "丝路新云？"],
             gmaps(45.545, 84.870, 2000),
             [("../plates/karamay/K01_park_overview.jpg", "克拉玛依云计算产业园总图", "PLATE K01  ·  园区总图"),
              ("../plates/karamay/K02_halls_candidate.jpg", "园区中部矩形厂房候选", "PLATE K02  ·  矩形厂房候选  ·  业主待核")]),
    ]),
    method="""<p>克拉玛依和另外四座城不一样：机房藏在城市产业园格子里，不是戈壁上的超大白盒子。没有 OSM 名称就只标候选。</p>
    <h3>算作候选</h3>
    <ul><li>无内院矩形、蓝/灰顶、在世纪大道南规划范围内</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>弧形办公楼</li><li>体育场</li><li>油田储罐</li></ul>""",
    maps=gmaps(45.545, 84.870, 4000),
    footer="对照：智东西 2022-03-11《数据中心造就的五座城》。",
    probe='{"origin":[45.545,84.870],"originName":"圆心 · 云计算产业园","radiusKm":50,"zoom":14,"sites":[{"id":"park","name":"云计算产业园","pos":[45.545,84.870],"color":"#c45c26","note":"园区确认、楼未钉死"}]}',
))

# --- Zhangbei ---
PAGES.append(dict(
    slug="zhangbei", city="张北", region="Hebei",
    title="张北数据中心建设情况",
    desc="以小二台阿里数据港为圆心：两排大厅可指认，中都草原 8–10 栋白顶模组，庙滩互通大厅业主待核。",
    tick="41.1887°N  114.8623°E  ·  r = 50 km",
    h1="张北周边数据中心建设情况",
    lede="张北的机房不在县城里。圆心取 OSM way/699984315 阿里数据港：小二台围墙里两排各约五栋无内院长厅，南端两栋更大白顶。馒头营东、中都草原南还有一处孤立方院，约八到十栋白顶模组。县城北高速互通旁（庙滩）和 OSM 具名「张北数据中心」另有两组大厅，业主未钉。腾讯、秦淮的公开项目在怀来，不写入张北。",
    hero="../plates/zhangbei/ZB01_xiaodai_overview.jpg",
    hero_alt="张北小二台阿里数据港总览",
    hero_cap="HERO  ·  小二台  ·  OSM 阿里数据港 / 上海数据港 A2",
    findings="\n".join([
        finding("ZB-DATAPORT  ·  两排大厅", "小二台阿里数据港", "xiaodai", "OSM 两块相邻工业用地。两排各约 5 栋无内院长厅，南端两栋白顶厅。", "高置信 · 已投运", "high"),
        finding("ZB-ALI-ZHONGDU  ·  8–10 栋", "中都草原", "zhongdu", "OSM 具名孤立方院。白顶模组 + 西侧光伏。", "高置信 · 已投运", "high"),
        finding("ZB-MIAOTAN  ·  互通旁", "庙滩机房组", "miaotan", "无 OSM 业主。多组无内院长厅 + 蓝顶冷却/光伏，大厅算机房。", "高 · 形态 / 候选 · 业主", "mid"),
        finding("ZB-OSM-DC  ·  县城北", "张北数据中心", "osmdc", "OSM way/1256794600。两簇灰顶模组；体育馆/大棚/大跨厂房排除。", "中高 · 业主未标", "mid"),
    ]),
    sites="\n".join([
        site("xiaodai", "41.1887°N  114.8623°E", "小二台阿里数据港",
             "小二台数据街。OSM：阿里数据港张家口张北数据中心 + 上海数据港张北A2。河北日报 2025-06 把灰色与橘色建筑写成阿里数据港，是线索不是牌匾。",
             "高置信 · 已投运", "high",
             ["两排各约 5 栋无内院长厅，屋顶深色机电/光伏条带（41.1876–41.1906N 114.8601–114.8646E）", "南端两栋更大白顶厅落在 A2 多边形北缘", "西侧蓝/红顶厂房按仓储/工厂排除"],
             ["阿里巴巴", "上海数据港"],
             gmaps(41.1887, 114.8623, 800),
             [("../plates/zhangbei/ZB02_xiaodai_halls.jpg", "小二台两排大厅与南端白顶厅", "PLATE ZB02  ·  小二台大厅  ·  Esri z17"),
              ("../plates/zhangbei/ZB01_xiaodai_overview.jpg", "小二台阿里数据港总图", "PLATE ZB01  ·  总图  ·  风电光伏之间")]),
        site("zhongdu", "41.2812°N  114.6822°E", "中都草原",
             "馒头营乡以东。OSM way/1068446080 阿里巴巴张北中都草原数据中心，41.2794–41.2830N 114.6798–114.6845E。",
             "高置信 · 已投运", "high",
             ["孤立方院约 8–10 栋白顶矩形模组，屋顶设备条带", "西侧贴一块光伏，本身不是机房", "形态与报道里阿里「一点三中心」的中都草原备份点一致"],
             ["阿里巴巴"],
             gmaps(41.2812, 114.6822, 800),
             [("../plates/zhangbei/ZB03_zhongdu.jpg", "中都草原孤立方院", "PLATE ZB03  ·  中都草原  ·  41.2812°N 114.6822°E")]),
        site("miaotan", "41.1910°N  114.6930°E", "庙滩 / 县城北",
             "庙滩村东南、县城北高速互通旁。无 OSM 业主名。东 2.7 km 是 way/1256794600 张北数据中心。",
             "高 · 是机房 / 候选 · 业主", "mid",
             ["互通东侧无内院长厅 + 蓝顶冷却/光伏（41.1875–41.1919N 114.6915–114.6968E）", "东北、东南还有模组；北侧大棚不计", "OSM「张北数据中心」两簇灰顶模组，体育馆/住宅/大跨白顶厂房排除", "阿里云联/庙滩、万国、榕泰都只是报道线索"],
             ["业主待核"],
             gmaps(41.191, 114.693, 1200),
             [("../plates/zhangbei/ZB04_miaotan.jpg", "庙滩互通旁机房组", "PLATE ZB04  ·  庙滩互通  ·  业主待核")]),
        site("osmdc", "41.1834°N  114.7302°E", "张北数据中心（OSM）",
             "县城北、距庙滩互通约 2.7 km。OSM way/1256794600 landuse=industrial，41.1815–41.1853N 114.7268–114.7336E。无 operator 标签。",
             "中高 · 是机房 / 业主未标", "mid",
             ["两簇灰顶模组大厅、屋顶深色条带（西簇 41.1835–41.1863N 114.7275–114.7325E；东簇 41.1835–41.1861N 114.7328–114.7368E）", "南侧体育馆/住宅、东侧大棚、中间大跨白顶厂房排除", "万国/榕泰/阿里庙滩二期都只是报道线索"],
             ["业主待核"],
             gmaps(41.1834, 114.7302, 800),
             [("../plates/zhangbei/ZB05_osm_dc.jpg", "OSM 具名张北数据中心两簇模组", "PLATE ZB05  ·  OSM 张北数据中心  ·  业主未标")]),
    ]),
    method="""<p>圆心在小二台园区，不在张北县城。中都、庙滩相距十余公里，不能指望一张 z16 总图罩住。</p>
    <h3>算作机房</h3>
    <ul><li>无内院矩形大厅、屋顶机电/光伏条带、模块化并排</li><li>OSM 具名 industrial（数据中心/数据港）</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>蓝/红顶仓储厂房</li><li>体育馆、住宅、大棚、大跨白顶厂房</li><li>风电和光伏阵列本身</li><li>腾讯/秦淮（在怀来，不写入张北）</li></ul>""",
    maps=gmaps(41.1887, 114.8623, 8000),
    footer="续卷 · 东数西算枢纽，不是 2022 智东西原文里的五座城。",
    probe='{"origin":[41.1887,114.8623],"originName":"圆心 · 小二台阿里数据港","radiusKm":50,"zoom":12,"sites":[{"id":"xiaodai","name":"小二台阿里数据港","pos":[41.1887,114.8623],"color":"#2ec4b6","note":"两排大厅 + 南端白顶"},{"id":"zhongdu","name":"中都草原","pos":[41.2812,114.6822],"color":"#2ec4b6","note":"8–10 栋白顶模组"},{"id":"miaotan","name":"庙滩机房组","pos":[41.191,114.693],"color":"#c45c26","note":"大厅形态、业主待核"},{"id":"osmdc","name":"张北数据中心","pos":[41.1834,114.7302],"color":"#2ec4b6","note":"OSM 具名、两簇灰顶"}]}',
))

# --- Huailai ---
PAGES.append(dict(
    slug="huailai", city="怀来", region="Hebei",
    title="怀来数据中心建设情况",
    desc="以东花园腾讯华北东园为圆心：腾讯、中国移动、秦淮 OSM 具名，合盈环评坐标有大厅网格。",
    tick="40.3248°N  115.8193°E  ·  r = 50 km",
    h1="怀来周边数据中心建设情况",
    lede="怀来东花园在官厅水库北岸，和张北不是同一条走廊。圆心取 OSM 腾讯华北东园：多栋无内院大厅、屋顶光伏/冷机条带，北侧基坑还在挖。紧贴西侧是中国移动京津冀（张家口）数据中心。葡萄大道南是 OSM 秦淮东花园。再往东约 4 km 是合盈环评坐标，十余栋大厅网格。存瑞镇头二营北另有一组：路南四栋超大白顶、路北多排模组，业主保持候选。",
    hero="../plates/huailai/HL01_donghuayuan_overview.jpg",
    hero_alt="怀来东花园：腾讯、移动、秦淮、合盈相对位置",
    hero_cap="HERO  ·  东花园葡萄大道  ·  西腾讯/移动，南秦淮，东合盈",
    findings="\n".join([
        finding("HL-TENCENT  ·  东园", "腾讯华北东园", "tencent", "OSM landuse=construction。约六栋光伏条带大厅已封顶，北侧基坑续建。", "高 · 在建+投运", "high"),
        finding("HL-CMCC  ·  西邻", "中国移动张家口", "cmcc", "OSM 工业用地，紧贴东园西侧，同规格大厅。", "高置信 · 已投运", "high"),
        finding("HL-QINHUAI  ·  南 1.1 km", "秦淮东花园", "qinhuai", "OSM way/867231233。葡萄大道南独立大院，白顶大厅。", "高置信 · 已投运", "high"),
        finding("HL-HOYINN  ·  十余栋", "合盈数据", "hoyinn", "环评中心点 40.3298,115.8646。大厅网格清楚，无 OSM 名。", "中高 · 形态", "mid"),
    ]),
    sites="\n".join([
        site("tencent", "40.3248°N  115.8193°E", "腾讯华北东园",
             "东花园葡萄大道北、京藏 G6 南。OSM way/867231234，40.3224–40.3273N 115.8154–115.8233E。",
             "高置信 · 在建 + 已投运", "high",
             ["多边形内多栋无内院大厅；东侧约六栋屋顶光伏条带（40.3232–40.3264N 115.8175–115.8229E）", "北侧基坑、蓝水塘、柴发院续建", "南约 1.1 km 是 OSM way/867231233 河北秦淮数据东花园基地（40.3129–40.3173N 115.8218–115.8271E）", "报道称腾讯怀来东园/瑞北，东园已钉在此多边形"],
             ["腾讯"],
             gmaps(40.324848, 115.819336, 800),
             [("../plates/huailai/HL02_tencent_cmcc.jpg", "腾讯东园与中国移动西邻", "PLATE HL02  ·  腾讯 × 移动  ·  Esri z17")]),
        site("cmcc", "40.3243°N  115.8139°E", "中国移动京津冀（张家口）",
             "紧贴腾讯东园西侧。OSM way/1481173783 landuse=industrial，40.3229–40.3256N 115.8122–115.8155E。",
             "高置信 · 已投运", "high",
             ["同规格白顶/条带屋顶大厅", "同属东花园葡萄大道组团，不是张北"],
             ["中国移动"],
             gmaps(40.324274, 115.813861, 700),
             [("../plates/huailai/HL02_tencent_cmcc.jpg", "中国移动机房在腾讯西侧", "PLATE HL02  ·  中国移动  ·  东园西邻")]),
        site("qinhuai", "40.3151°N  115.8244°E", "河北秦淮数据东花园基地",
             "葡萄大道南、腾讯东园南约 1.1 km。OSM way/867231233 landuse=industrial，40.3129–40.3173N 115.8218–115.8271E。",
             "高置信 · 已投运", "high",
             ["独立大院与白顶大厅，和东园不是同一块多边形", "总图 HL01 框 3", "不要和存瑞镇报道里的秦淮存瑞混成一个园"],
             ["秦淮数据"],
             gmaps(40.315059, 115.824444, 700),
             [("../plates/huailai/HL01_donghuayuan_overview.jpg", "东花园总图上的秦淮南院", "PLATE HL01  ·  秦淮东花园  ·  框 3")]),
        site("hoyinn", "40.3298°N  115.8646°E", "合盈数据科技产业园",
             "2022-01 环评第二次公示中心点 40°19′47.38″N 115°51′52.58″E。无 OSM 名。与腾讯组团隔大南辛堡村约 4 km。",
             "中高置信 · 大厅网格 / 业主按环评", "mid",
             ["十余栋超大无内院矩形网格、屋顶机电（约 40.328–40.338N 115.851–115.867E）", "西/北侧垫层续建", "南侧葡萄大道，路南住宅不算机房"],
             ["合盈数据"],
             gmaps(40.329828, 115.864606, 800),
             [("../plates/huailai/HL03_hoyinn.jpg", "合盈十余栋大厅网格", "PLATE HL03  ·  合盈  ·  环评坐标")]),
        site("cunrui", "40.4870°N  115.5670°E", "存瑞镇头二营北",
             "头二营村（OSM node/6541383304 40.4758,115.5596）北侧田间独立大院。图上无牌匾。",
             "中高 · 是机房 / 候选 · 业主", "mid",
             ["路南四栋超大白顶条带大厅（40.4847–40.4879N 115.5581–115.5702E）", "路北多排模块化白顶机房+屋顶机电", "报道腾讯瑞北在头二营/葫芦套、秦淮存瑞在 G239，业主保持候选", "路西体育场排除"],
             ["业主待核"],
             gmaps(40.487, 115.567, 1000),
             [("../plates/huailai/HL04_cunrui.jpg", "头二营北路南四栋大厅", "PLATE HL04  ·  头二营北  ·  业主待核")]),
    ]),
    method="""<p>圆心在东花园园区，不在怀来县城。50 km 圈东缘会扫进北京昌平的银行数据中心，那些不算怀来。</p>
    <h3>算作机房</h3>
    <ul><li>超大无内院矩形、屋顶光伏/冷机条带</li><li>OSM 具名（腾讯东园、中国移动、秦淮东花园）</li><li>环评坐标对得上的大厅网格（合盈）</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>北京昌平中行/建行/农行/人行/国开行/中石油数据中心</li><li>大南辛堡村住宅、葡萄园</li><li>头二营路西体育场</li><li>阿里（在张北，不写入怀来）</li></ul>""",
    maps=gmaps(40.324848, 115.819336, 8000),
    footer="续卷 · 东数西算枢纽，不是 2022 智东西原文里的五座城。",
    probe='{"origin":[40.324848,115.819336],"originName":"圆心 · 腾讯华北东园","radiusKm":50,"zoom":12,"sites":[{"id":"tencent","name":"腾讯东园","pos":[40.324848,115.819336],"color":"#c23b22","note":"大厅+北侧基坑"},{"id":"cmcc","name":"中国移动","pos":[40.324274,115.813861],"color":"#2ec4b6","note":"OSM 具名已投运"},{"id":"qinhuai","name":"秦淮东花园","pos":[40.315059,115.824444],"color":"#2ec4b6","note":"OSM way/867231233"},{"id":"hoyinn","name":"合盈数据","pos":[40.329828,115.864606],"color":"#c45c26","note":"环评坐标、大厅网格"},{"id":"cunrui","name":"头二营北","pos":[40.487,115.567],"color":"#c45c26","note":"路南四栋、业主待核"}]}',
))

# --- Qingyang ---
PAGES.append(dict(
    slug="qingyang", city="庆阳", region="Gansu",
    title="庆阳数据中心建设情况",
    desc="西峰温泉镇新桥村：OSM 秦淮地块可见一栋在建白顶大厅和动力楼；其余运营商多边形仍落在旧影像上。",
    tick="35.7335°N  107.7044°E  ·  r = 50 km",
    h1="庆阳周边数据中心建设情况",
    lede="庆阳枢纽在西峰区温泉镇新桥村黄土塬上，距中卫约 280 km。OSM 把秦淮、能建、移动、电信、联通、智慧蓝图都标在园里。本幅 Esri 有一道南北向新旧瓦片接缝：接缝以东能看见秦淮地块一栋无内院白顶大厅（屋面未完）加东南蓝顶动力楼和垫层；接缝以西的运营商多边形仍落在村庄条田上，不能当已建大厅。",
    hero="../plates/qingyang/QY01_wenquan_overview.jpg",
    hero_alt="庆阳温泉镇东数西算园总览，可见瓦片接缝",
    hero_cap="HERO  ·  温泉镇  ·  接缝以东是秦淮大厅，以西仍是村庄",
    findings="\n".join([
        finding("QY-CHINDATA  ·  一栋大厅", "秦淮零碳基地", "chindata", "OSM 有名。围栏内白顶大厅（屋面未完）+ 蓝顶动力楼 + 垫层。仍在建。", "中高 · 在建", "high"),
        finding("QY-CEEC 等  ·  OSM 名", "能建/运营商多边形", "chindata", "能建、移动、电信、联通、智慧蓝图 OSM 有名；本幅 Esri 仍是耕地村庄。", "中 · 候选", "mid"),
        finding("排除  ·  城区", "庆阳数据中心", "chindata", "way/1339493828 在西峰城区，住宅空地。", "排除", "low"),
        finding("排除  ·  华为", "华为数字能源", "chindata", "供电方案报道，无 OSM 名、无牌匾机房，不记为业主。", "排除", "low"),
    ]),
    sites="\n".join([
        site("chindata", "35.7334°N  107.7018°E", "秦淮数据零碳基地",
             "兰州路北、纵二路东。OSM way/1412509897，35.7317–35.7354N 107.7009–107.7079E。2024-07 报道一期 A 模组验收，本幅 Esri 仍是在建。",
             "中高置信 · 大厅形态 / 在建", "high",
             ["围栏内无内院白顶大厅，屋面未完（35.7326–35.7341N 107.7006–107.7028E）", "东南蓝顶动力楼 + 东侧刮地垫层", "能建/移动/电信/联通/智慧蓝图 OSM 多边形在接缝以西，本幅未见大厅", "城区 way/1339493828 庆阳数据中心是住宅空地，排除"],
             ["秦淮数据"],
             gmaps(35.7334, 107.7018, 800),
             [("../plates/qingyang/QY02_chindata.jpg", "秦淮在建白顶大厅与动力楼", "PLATE QY02  ·  秦淮  ·  Esri z17"),
              ("../plates/qingyang/QY01_wenquan_overview.jpg", "温泉镇园总图与瓦片接缝", "PLATE QY01  ·  总图  ·  接缝以东才有大厅")]),
    ]),
    method="""<p>圆心在温泉镇园区，不在西峰城区。Esri 瓦片接缝是这次判断的硬约束：旧瓦片上的 OSM 名不能当成已建大厅。</p>
    <h3>算作机房</h3>
    <ul><li>无内院白顶大厅 + 动力楼 + 垫层（秦淮，在建）</li><li>OSM 具名只当作选址线索，必须看见大厅才升级</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>城区「庆阳数据中心」住宅空地</li><li>接缝以西尚未出大厅的 OSM 多边形</li><li>华为数字能源供电方案</li><li>民房、条田、体育场</li></ul>""",
    maps=gmaps(35.7335, 107.7044, 5000),
    footer="续卷 · 东数西算枢纽，不是 2022 智东西原文里的五座城。",
    probe='{"origin":[35.7335,107.7044],"originName":"圆心 · 秦淮零碳基地","radiusKm":50,"zoom":14,"sites":[{"id":"chindata","name":"秦淮零碳基地","pos":[35.7334,107.7018],"color":"#c23b22","note":"一栋在建白顶大厅"},{"id":"chindata","name":"能建多边形","pos":[35.7368,107.6987],"color":"#c45c26","note":"OSM 有名、本幅未见大厅"}]}',
))

# --- Horinger ---
PAGES.append(dict(
    slug="horinger", city="和林格尔", region="Inner Mongolia",
    title="和林格尔数据中心建设情况",
    desc="盛乐园区：中国移动白顶大厅可指认，中国电信信息园能钉园。不是乌兰察布走廊。",
    tick="40.5390°N  111.8230°E  ·  r = 50 km",
    h1="和林格尔周边数据中心建设情况",
    lede="和林格尔是内蒙古枢纽的呼和浩特翼，机房在盛乐经济园区格子里，不在县城。西侧 OSM 中国移动呼和浩特数据中心是最典型的一处：北半无内院白顶大厅并排，南半还在挖。东侧中国电信云计算内蒙古信息园能钉园，环形广场那几栋曲面楼更像办公。华为云报道没有 OSM 名，不写入业主。",
    hero="../plates/horinger/HG01_yungu_overview.jpg",
    hero_alt="和林格尔盛乐园区：移动与电信相对位置",
    hero_cap="HERO  ·  盛乐园区  ·  西移动 / 东电信",
    findings="\n".join([
        finding("HG-CMCC  ·  白顶大厅", "中国移动呼和浩特", "cmcc", "OSM 具名。北半无内院大厅并排，南半基坑续建。", "高置信 · 投运+在建", "high"),
        finding("HG-CT  ·  东邻", "中国电信信息园", "telecom", "OSM 具名。环形广场偏办公，南侧土建。", "中高 · 园可钉", "mid"),
        finding("HG-NORTH  ·  候选", "北侧黑顶模组", "cmcc", "移动多边形北外侧模块化黑顶，无 OSM 名。", "中 · 候选", "mid"),
        finding("排除  ·  厂房", "蓝顶大跨 / 办公", "telecom", "右下仓储厂房、广场曲面楼不算机房。", "排除", "low"),
    ]),
    sites="\n".join([
        site("cmcc", "40.5369°N  111.8164°E", "中国移动呼和浩特数据中心",
             "盛乐园区西。OSM way/699967332，40.5315–40.5423N 111.8087–111.8240E。",
             "高置信 · 已投运 + 南扩", "high",
             ["北半多栋无内院白顶/灰顶大厅，屋顶机电密布", "南半基坑、蓝顶临建", "北侧黑顶模组组无 OSM 名，只标候选"],
             ["中国移动"],
             gmaps(40.5369, 111.8164, 800),
             [("../plates/horinger/HG02_cmcc.jpg", "移动园区白顶大厅与南侧土建", "PLATE HG02  ·  移动  ·  Esri z17")]),
        site("telecom", "40.5411°N  111.8291°E", "中国电信云计算内蒙古信息园",
             "紧贴移动东侧。OSM way/566233416，40.5365–40.5457N 111.8228–111.8353E。",
             "中高 · 园可钉 / 楼要分", "mid",
             ["环形广场北侧曲面楼偏办公，不单独当机房", "南侧仍有土建", "大厅形态不如西侧移动园区典型"],
             ["中国电信"],
             gmaps(40.5411, 111.8291, 800),
             [("../plates/horinger/HG03_telecom.jpg", "电信信息园环形广场", "PLATE HG03  ·  电信  ·  广场偏办公")]),
    ]),
    method="""<p>圆心在盛乐园区，不在和林格尔县城，也不是乌兰察布。</p>
    <h3>算作机房</h3>
    <ul><li>无内院白顶/灰顶大厅并排、屋顶机电</li><li>OSM 具名 industrial（移动、电信）</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>曲面办公楼、体育场、住宅</li><li>大跨蓝顶仓储厂房</li><li>没有 OSM 名的华为报道</li></ul>""",
    maps=gmaps(40.539, 111.823, 8000),
    footer="续卷 · 东数西算枢纽，不是 2022 智东西原文里的五座城。",
    probe='{"origin":[40.539,111.823],"originName":"圆心 · 盛乐园区","radiusKm":50,"zoom":13,"sites":[{"id":"cmcc","name":"中国移动","pos":[40.5369,111.8164],"color":"#2ec4b6","note":"白顶大厅+南扩"},{"id":"telecom","name":"中国电信信息园","pos":[40.5411,111.8291],"color":"#c45c26","note":"园可钉、楼要分"}]}',
))

# --- Shaoguan ---
PAGES.append(dict(
    slug="shaoguan", city="韶关", region="Guangdong",
    title="韶关数据中心建设情况",
    desc="沐溪湖西：华南数谷半岛在建超大矩形可指认。沿路白顶厂房不是机房。",
    tick="24.7830°N  113.5025°E  ·  r = 50 km",
    h1="韶关周边数据中心建设情况",
    lede="韶关枢纽不在市政府。圆心取高新区西联、沐溪湖西的华韶—华南数谷组团。卫星上最像机房的是湖心半岛那栋在建超大矩形（OSM 华南数谷智算中心）。华韶一期是路口小地块，二期 OSM 标 construction、地面主要是垫层。沿路白顶大跨厂房是普通工业。城区粤北云只有 150 m 级多边形，没有大厅。",
    hero="../plates/shaoguan/SG01_huashao_overview.jpg",
    hero_alt="韶关沐溪湖西：华南数谷与华韶相对位置",
    hero_cap="HERO  ·  沐溪湖西  ·  半岛在建大厅",
    findings="\n".join([
        finding("SG-HUANAN  ·  半岛", "华南数谷智算", "huanan", "OSM 具名。湖心半岛超大矩形在建，屋面未完。", "中高 · 在建", "high"),
        finding("SG-HUASHAO  ·  路口", "华韶数据谷", "huanan", "OSM 约 200 m 地块。方楼 + 北侧在建，体量小。", "中 · 小地块", "mid"),
        finding("SG-PHASE2  ·  垫层", "华韶二期", "phase2", "OSM construction。多边形内主要是垫层。", "中 · 垫层", "mid"),
        finding("SG-YUEBEI  ·  城区", "粤北云数据中心", "huanan", "OSM 有名，150 m 级，立交旁看不见大厅。", "低", "low"),
    ]),
    sites="\n".join([
        site("huanan", "24.7887°N  113.5003°E", "华南数谷智算中心",
             "沐溪湖半岛。OSM way/1474786000，24.7866–24.7907N 113.4992–113.5014E。",
             "中高置信 · 在建大厅", "high",
             ["超大矩形、脚手架、屋面未完，形态像机房而不是住宅", "东侧山坡别墅不计", "路口华韶一期是另一块约 200 m OSM 多边形"],
             ["业主待核"],
             gmaps(24.7887, 113.5003, 700),
             [("../plates/shaoguan/SG02_huanan.jpg", "沐溪湖半岛在建大厅", "PLATE SG02  ·  华南数谷  ·  Esri z17")]),
        site("phase2", "24.7789°N  113.5026°E", "华韶数据谷二期",
             "OSM way/1536927107 landuse=construction，24.7762–24.7815N 113.4999–113.5053E。",
             "中 · 垫层 / OSM 在建", "mid",
             ["多边形内整平垫层和边坡，大厅尚未出", "南侧大跨白顶厂房按普通工业排除"],
             ["业主待核"],
             gmaps(24.7789, 113.5026, 800),
             [("../plates/shaoguan/SG03_phase2.jpg", "华韶二期垫层与沿路厂房", "PLATE SG03  ·  二期  ·  厂房排除")]),
    ]),
    method="""<p>圆心在沐溪湖西园区，不在韶关市政府。职业中学那个 telecom=data_center 节点排除。</p>
    <h3>算作机房</h3>
    <ul><li>半岛超大无内院矩形（在建）</li><li>OSM 具名（华南数谷、华韶）须对照形态</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>沿路白顶大跨厂房、采石场</li><li>山坡别墅、城区立交住宅</li><li>职业中学信息中心</li></ul>""",
    maps=gmaps(24.783, 113.5025, 8000),
    footer="续卷 · 东数西算枢纽，不是 2022 智东西原文里的五座城。",
    probe='{"origin":[24.783,113.5025],"originName":"圆心 · 华韶/华南数谷","radiusKm":50,"zoom":13,"sites":[{"id":"huanan","name":"华南数谷","pos":[24.7887,113.5003],"color":"#c23b22","note":"半岛在建大厅"},{"id":"phase2","name":"华韶二期","pos":[24.7789,113.5026],"color":"#c45c26","note":"垫层"}]}',
))

# --- Wuhu ---
PAGES.append(dict(
    slug="wuhu", city="芜湖", region="Anhui",
    title="芜湖数据中心建设情况",
    desc="三山田里：华为云华东超大矩形在建可指认。智算中心 OSM 多边形很小。冷却塔是电厂。",
    tick="31.3484°N  118.2862°E  ·  r = 50 km",
    h1="芜湖周边数据中心建设情况",
    lede="芜湖集群目前卫星上能钉死的是三山峨溪路一带、水田里那座华为云在建大厅：独立超大矩形、钢结构、塔吊、东侧垫层。东约 1.2 km 的一体化智算中心 OSM 多边形只有约 80 m，地面是小白楼加基坑。同幅接缝以东冷却塔是电厂。沿江罐区和大跨厂房不算机房。",
    hero="../plates/wuhu/WH02_huawei.jpg",
    hero_alt="芜湖华为云华东数据中心在建大厅",
    hero_cap="HERO  ·  华为云华东（芜湖）  ·  水田中的超大矩形",
    findings="\n".join([
        finding("WH-HUAWEI  ·  在建大厅", "华为云华东（芜湖）", "huawei", "OSM 具名。水田中超大无内院矩形，塔吊+垫层。", "高 · 在建", "high"),
        finding("WH-ZHISUAN  ·  小地块", "一体化智算 / 硅立方", "zhisuan", "OSM 三块嵌套约 80 m。白顶小楼 + 基坑。", "中 · 小", "mid"),
        finding("排除  ·  电厂", "冷却塔", "zhisuan", "智算那幅接缝以东是电厂，不是机房。", "排除", "low"),
        finding("WH-DONGHUA  ·  圈缘", "东华金融云计算", "huawei", "OSM 有名，距圆心约 47 km，本次未出图。", "低", "low"),
    ]),
    sites="\n".join([
        site("huawei", "31.3484°N  118.2862°E", "华为云华东（芜湖）数据中心",
             "三山峨溪路南、水田中。OSM way/1341908908，31.3468–31.3500N 118.2838–118.2887E。",
             "高置信 · 在建", "high",
             ["超大无内院矩形，钢结构、塔吊、部分封顶", "东侧刮地垫层说明还在扩", "不是沿江厂房"],
             ["华为云"],
             gmaps(31.3484, 118.2862, 700),
             [("../plates/wuhu/WH02_huawei.jpg", "华为云在建大厅特写", "PLATE WH02  ·  华为云  ·  Esri z17"),
              ("../plates/wuhu/WH01_cluster_overview.jpg", "三山组团总图", "PLATE WH01  ·  总图  ·  田里那一座")]),
        site("zhisuan", "31.3424°N  118.2971°E", "芜湖一体化智算中心",
             "华为云东南约 1.2 km。OSM way/1341908877 及嵌套的硅立方/数据中心楼，约 80–100 m。",
             "中 · OSM 小地块", "mid",
             ["路西一栋白顶小楼 + 基坑/垫层，不是超大阵列", "接缝以东冷却塔排除", "东华金融云计算中心在圈东北缘，未出图"],
             ["业主待核"],
             gmaps(31.3424, 118.2971, 600),
             [("../plates/wuhu/WH03_zhisuan.jpg", "智算小地块与接缝以东电厂", "PLATE WH03  ·  智算  ·  冷却塔排除")]),
    ]),
    method="""<p>圆心在三山田里的华为云地块，不在芜湖市政府。Esri 接缝以东的冷却塔不要算进来。</p>
    <h3>算作机房</h3>
    <ul><li>水田中超大无内院矩形（华为云，在建）</li><li>OSM 具名须对照体量</li></ul>
    <h3>明确排除</h3>
    <ul class="exclude"><li>冷却塔 / 电厂</li><li>罐区、大跨白顶厂房</li><li>蔬菜大棚、水田、住宅</li></ul>""",
    maps=gmaps(31.3484, 118.2862, 6000),
    footer="续卷 · 东数西算枢纽，不是 2022 智东西原文里的五座城。",
    probe='{"origin":[31.3484,118.2862],"originName":"圆心 · 华为云华东芜湖","radiusKm":50,"zoom":13,"sites":[{"id":"huawei","name":"华为云","pos":[31.3484,118.2862],"color":"#c23b22","note":"超大矩形在建"},{"id":"zhisuan","name":"一体化智算","pos":[31.3424,118.2971],"color":"#c45c26","note":"OSM 小地块"}]}',
))


def main():
    for p in PAGES:
        out = ROOT / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        html = HEAD.format(**p)
        out.write_text(html)
        print("wrote", out, len(html))


if __name__ == "__main__":
    main()
