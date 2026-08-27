# Datacenter Probe · 乌兰察布

以集宁城区 `41.0181°N, 113.1155°E` 为圆心，用 Chrome 打开 Google 卫星图，标注 **50 公里内在建数据中心** 候选地块。

## GitHub Pages

静态站在 `docs/`。开启方式：

1. 把仓库推到 GitHub
2. **Settings → Pages → Build and deployment**
3. Source 选 **GitHub Actions**（仓库已带 `.github/workflows/pages.yml`）  
   或 Source 选 **Deploy from a branch**，Branch 选 `main` / `docs/`
4. 站点地址：`https://<user>.github.io/datacenter-probe/`

本地预览：

```bash
python3 -m http.server 8080 --directory docs
# http://127.0.0.1:8080/
```

## 目录

| 路径 | 内容 |
|---|---|
| `docs/` | GitHub Pages 站点 |
| `docs/plates/` | 裁切后的标注卫星图 |
| `screenshots/` | Chrome 窗口原图（含界面） |
| `screenshots/annotated/` | 标注图版 A01–A10 |
| `notes/findings.json` | 结构化结论（坐标、距离、证据） |
| `notes/overpass.json` | OSM Overpass 原始查询结果 |
| `notes/VERIFICATION_CATALOG.md` | 核查目录 |

## 结论摘要

在建机房不在给定的城区原点，而在集宁以东 G110 走廊：

- **益武堂**（苹果大道 / 阿里大道，10.9 km）— 高置信在建
- **四号村**（巴音东段候选，17.3 km）— 中高，东扩施工
- **圣家营北**（万润 / 快手星河报道选址，16.5 km）— 本月影像已出楼：15+ 栋白顶矩形，业主待核
- **前旗土贵乌**（27.3 km）— 规划有项目，本次未确认机房
