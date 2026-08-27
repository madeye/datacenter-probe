# Datacenter Probe · 五座城

按智东西 [《数据中心造就的五座城》](https://zhidx.com/p/314607.html)（2022-03-11）做卫星核查：贵安、乌兰察布、阳泉、中卫、克拉玛依。每座城圆心取主园区，半径 50 km。

乌兰察布是第一卷（集宁以东 G110 走廊）。另外四座城 2026-08 补做，底图改为 Esri World Imagery 瓦片。

## GitHub Pages

静态站在 `docs/`。

```bash
python3 -m http.server 8080 --directory docs
# http://127.0.0.1:8080/
```

| 路径 | 内容 |
|---|---|
| `/` | 五座城目录 |
| `/ulanqab/` | 乌兰察布 50 km 走廊 |
| `/guian/` | 贵安数谷大道 |
| `/yangquan/` | 阳泉大连街 |
| `/zhongwei/` | 中卫西部云基地 |
| `/karamay/` | 克拉玛依云计算产业园 |

## 结论摘要

| 城市 | 圆心 | 卫星上能看见的 | 置信 |
|---|---|---|---|
| 贵安 | 26.368°N 106.490°E | 华为云上屯、腾讯七星洞库、苹果 iCloud 两栋大厅 | 高 |
| 乌兰察布 | 41.018°N 113.116°E | G110 走廊：益武堂、四号村、圣家营 | 高 / 中高 |
| 阳泉 | 37.860°N 113.623°E | 百度南端三栋 + 东北约 8 栋模组；云峰北侧小地块 | 高 / 中高 |
| 中卫 | 37.637°N 105.347°E | 戈壁上六栋白顶大厅、东邻三栋、西侧在建、路南一组 | 高（形态）/ 中（业主） |
| 克拉玛依 | 45.545°N 84.870°E | 园区确认，逐栋业主未标 | 中 |

## 目录

| 路径 | 内容 |
|---|---|
| `docs/` | GitHub Pages |
| `docs/plates/<city>/` | 标注卫星图 |
| `screenshots/<city>/` | Esri 拼接原图（`_tiles/` 不入库） |
| `notes/<city>/` | findings.json、Overpass、核查目录 |
| `scripts/annotate_plates.py` | 把 WGS84 框投到 Esri 拼接图上，出 `docs/plates/` |
| `scripts/render_city_pages.py` | 从脚本内数据渲染四座城的页面 |

标注图不是权属证明。没有牌匾或规划图，不把候选地块写成某家的产权。
