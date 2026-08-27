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
  </nav>
  <footer>
    <div>
      Datacenter Probe  ·  {city}  ·  标注截图仅供复核，不是权属证明。
      影像 © Esri, Maxar, Earthstar Geographics。对照：智东西 2022-03-11《数据中心造就的五座城》。
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
    probe='{"origin":[45.545,84.870],"originName":"圆心 · 云计算产业园","radiusKm":50,"zoom":14,"sites":[{"id":"park","name":"云计算产业园","pos":[45.545,84.870],"color":"#c45c26","note":"园区确认、楼未钉死"}]}',
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
