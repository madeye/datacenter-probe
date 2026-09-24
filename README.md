# Datacenter Probe · 十一座城市卫星核查

按智东西 [《数据中心造就的五座城》](https://zhidx.com/p/314607.html)（2022-03-11）做卫星核查：贵安、乌兰察布、阳泉、中卫、克拉玛依。每座城圆心取主园区，半径 50 km。

乌兰察布最早完成核查（集宁以东 G110 走廊）。另外四座城 2026-08 补做，底图改为 Esri World Imagery 瓦片。

核查范围包括张北、怀来、和林格尔、庆阳、韶关、芜湖：东数西算张家口集群、内蒙古另一翼、甘肃/粤北/长三角枢纽，不是 2022 原文里的五座城。判据相同。

## GitHub Pages

页面源文件在 `docs/`，GitHub Pages 发布目录由构建生成到 `_site/`。首页地图收录 11 座核查城市；城市地图支持点位选择、卫星 / 街道底图切换和 50 km 核查范围。

修改城市数据或模板后运行 `python3 scripts/render_city_pages.py`，同步生成城市页与首页地图数据 `docs/cities.js`。乌兰察布页保留独立 HTML，使用同一份 `probe.css` 和 `probe.js`。

每次更新页面，都必须同步更新对应的 social card（文案、影像及 PNG），发布时一起提交。运行 `python3 scripts/render_social_cards.py` 重新生成首页与全部 11 座城市的 1200×630 图片；只更新指定页面可传入 `index` 或城市 slug。首次使用需安装 Playwright CLI 和 Chromium：`pipx install playwright && playwright install chromium`。

```bash
python3 scripts/build_snapshots.py --worktree
python3 -m http.server 8085 --bind 127.0.0.1 --directory _site
# http://127.0.0.1:8085/
```

### 日期快照

- 每次从 `main` 部署时，构建器读取完整 Git 历史，以新加坡时区的提交日期生成 `YYYY-MM-DD/`。同一天保留最后一个版本；重复部署同一提交不会新增日期。
- `/` 自动进入最新日期；原来的 `/guian/` 等地址进入最新日期的对应城市，并保留查询参数和锚点。
- 顶部“页面快照”导航切换日期，并保留当前城市。目标日期没有该城市时，链接标为“总览”并进入该日期首页。关闭 JavaScript 后也能跳转和切换日期。
- 历史正文、CSS、JavaScript 和本地图像来自对应 Git 提交。日期导航随部署更新。日期指页面版本，不是卫星影像拍摄日期；在线地图瓦片仍由地图服务实时提供。
- 历史按 `main` 的 first-parent 提交记录回填，从包含 `docs/index.html` 的版本开始。仅修改构建脚本的发布也会保留对应日期。历史重建依赖完整且未改写的 Git 历史，CI 使用 `fetch-depth: 0`，浅克隆会明确报错。
- `_site/snapshots.json` 记录日期、来源提交及可用页面。`_site/` 是生成目录，不提交到 Git；构建器只覆盖自己创建的目录。

本地 `--worktree` 将未提交的 `docs/` 作为今天的快照加入预览；可用 `--date YYYY-MM-DD` 模拟新日期。正式部署不传这两个参数，使用提交中的内容和日期。

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 scripts/build_snapshots.py
```

下表中的无日期地址始终跳转到最新快照，也可以在地址前加 `YYYY-MM-DD/` 访问历史版本。

| 路径 | 内容 |
|---|---|
| `/` | 十一座城市目录 |
| `/ulanqab/` | 乌兰察布 50 km 走廊 |
| `/guian/` | 贵安数谷大道 |
| `/yangquan/` | 阳泉大连街 |
| `/zhongwei/` | 中卫西部云基地 |
| `/karamay/` | 克拉玛依云计算产业园 |
| `/zhangbei/` | 张北小二台 / 中都草原 |
| `/huailai/` | 怀来东花园 |
| `/qingyang/` | 庆阳温泉镇 |
| `/horinger/` | 和林格尔盛乐园区 |
| `/shaoguan/` | 韶关沐溪湖西 |
| `/wuhu/` | 芜湖三山华为云 |

## 结论摘要

| 城市 | 圆心 | 卫星上能看见的 | 置信 |
|---|---|---|---|
| 贵安 | 26.368°N 106.490°E | 华为云上屯、腾讯七星洞库、苹果 iCloud 两栋大厅 | 高 |
| 乌兰察布 | 41.018°N 113.116°E | G110 走廊：益武堂、四号村、圣家营 | 高 / 中高 |
| 阳泉 | 37.860°N 113.623°E | 百度南端三栋 + 东北约 8 栋模组；云峰北侧小地块 | 高 / 中高 |
| 中卫 | 37.637°N 105.347°E | 戈壁上六栋白顶大厅、东邻三栋、西侧在建、路南一组 | 高（形态）/ 中（业主） |
| 克拉玛依 | 45.545°N 84.870°E | 园区确认，逐栋业主未标 | 中 |
| 张北 | 41.189°N 114.862°E | 小二台两排大厅、中都草原 8–10 栋白顶模组；庙滩业主未钉 | 高 / 中高 |
| 怀来 | 40.325°N 115.819°E | 腾讯东园、中国移动、秦淮东花园；合盈大厅网格；头二营北候选 | 高 / 中高 |
| 庆阳 | 35.734°N 107.704°E | 秦淮一栋在建白顶大厅 + 动力楼；其余 OSM 名落在旧瓦片上 | 中高（秦淮）/ 中（其余） |
| 和林格尔 | 40.539°N 111.823°E | 盛乐：移动白顶大厅并排、电信信息园；华为无 OSM 名 | 高 / 中高 |
| 韶关 | 24.783°N 113.503°E | 沐溪湖半岛一栋在建超大矩形；沿路厂房排除 | 中高 / 中 |
| 芜湖 | 31.348°N 118.286°E | 华为云超大矩形在建；智算 OSM 多边形很小 | 高 / 中 |

## 目录

| 路径 | 内容 |
|---|---|
| `docs/` | GitHub Pages |
| `docs/plates/<city>/` | 标注卫星图 |
| `screenshots/<city>/` | Esri 拼接原图（`_tiles/` 不入库） |
| `notes/<city>/` | findings.json、Overpass、核查目录 |
| `scripts/annotate_plates.py` | 把 WGS84 框投到 Esri 拼接图上，出 `docs/plates/` |
| `scripts/fetch_esri_mosaic.py` | 按圆心拉 Esri World Imagery 拼接图 |
| `scripts/render_city_pages.py` | 从脚本内数据渲染城页 |

标注图不是权属证明。没有牌匾或规划图，不把候选地块写成某家的产权。

## 刷新卫星影像

```bash
python3 -m pip install -r requirements.txt
python3 scripts/refresh_imagery.py
python3 scripts/build_snapshots.py --worktree
```

刷新脚本为每次运行建立独立瓦片缓存，按现有核查坐标下载 Esri 当前提供的影像；全部下载和渲染成功后才替换页面图像。`docs/imagery.json` 记录获取时间、坐标、缩放级别、文件哈希和旧图对比。下载时间不等于拍摄时间，服务可能继续返回与上次相同的影像。

乌兰察布使用新 Esri 图与可展开的 2026-08 历史标注作对照。现有核查文字、业主判断及其他城市的标注框沿用原记录，刷新图像不自动推断建设状态变化。正式发布仍需提交源文件和生成图像，历史快照从已提交版本重建。
