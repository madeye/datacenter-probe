(function () {
  const lb = document.getElementById("lb");
  const lbImg = document.getElementById("lb-img");
  if (lb && lbImg) {
    let trigger;
    const closeBtn = document.getElementById("lb-close");
    lb.setAttribute("role", "dialog");
    lb.setAttribute("aria-modal", "true");
    lb.setAttribute("aria-label", "放大标注图");
    document.querySelectorAll("figure.plate img, figure.hero img").forEach((img) => {
      const button = document.createElement("button");
      button.className = "image-zoom";
      button.type = "button";
      button.setAttribute("aria-label", `放大：${img.alt}`);
      img.before(button);
      button.append(img);
      button.addEventListener("click", () => {
        trigger = button;
        lbImg.src = img.src;
        lbImg.alt = img.alt;
        lb.hidden = false;
        lb.classList.add("open");
        document.body.style.overflow = "hidden";
        closeBtn.focus();
      });
    });
    function closeLb() {
      if (lb.hidden) return;
      lb.classList.remove("open");
      lb.hidden = true;
      lbImg.removeAttribute("src");
      document.body.style.overflow = "";
      trigger?.focus();
    }
    closeBtn.addEventListener("click", closeLb);
    lb.addEventListener("click", (e) => { if (e.target === lb) closeLb(); });
    lb.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeLb();
      if (e.key === "Tab") { e.preventDefault(); closeBtn.focus(); }
    });
  }

  const mapEl = document.getElementById("map");
  if (!mapEl || !window.PROBE) return;
  const cfg = window.PROBE;
  const shell = document.createElement("section");
  shell.className = "map-shell";
  shell.setAttribute("aria-label", cfg.overview ? "城市地图浏览器" : "园区地图浏览器");
  mapEl.before(shell);
  const toolbar = document.createElement("div");
  toolbar.className = "map-toolbar";
  const title = document.createElement("strong");
  title.textContent = cfg.overview ? "核查城市" : "园区与核查范围";
  toolbar.append(title);
  shell.append(toolbar);
  const layout = document.createElement("div");
  layout.className = "map-layout";
  shell.append(layout);
  layout.append(mapEl);
  const sidebar = document.createElement("div");
  sidebar.className = "map-sites";
  sidebar.setAttribute("aria-label", cfg.overview ? "选择城市" : "选择核查点");
  layout.append(sidebar);
  const status = document.createElement("p");
  status.className = "map-status";
  status.setAttribute("role", "status");
  status.textContent = "选择点位查看详情；使用 + / − 缩放地图。";
  shell.append(status);

  function entry(site, index) {
    const row = document.createElement("div");
    row.className = "map-site";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "site-select";
    button.style.setProperty("--point", site.color);
    button.textContent = site.name;
    button.setAttribute("aria-label", site.name);
    button.dataset.index = index + 1;
    button.setAttribute("aria-pressed", "false");
    const link = document.createElement("a");
    link.href = site.href || `#${site.id}`;
    link.textContent = cfg.overview ? "打开详情" : "看标注图";
    link.setAttribute("aria-label", `${site.name}：${link.textContent}`);
    row.append(button, link);
    sidebar.append(row);
    return button;
  }
  const buttons = (cfg.sites || []).map(entry);
  if (typeof L === "undefined") {
    mapEl.textContent = "地图暂时无法加载，请通过右侧或下方链接查看详情与标注图。";
    buttons.forEach((button) => { button.disabled = true; });
    status.textContent = "地图服务连接失败。刷新页面可重试。";
    return;
  }
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const map = L.map(mapEl, { scrollWheelZoom: false, zoomAnimation: !reduceMotion, fadeAnimation: !reduceMotion, markerZoomAnimation: !reduceMotion }).setView(cfg.origin, cfg.zoom || 12);
  const satellite = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    attribution: "Imagery © Esri, Maxar, Earthstar Geographics", maxZoom: 18
  });
  const streets = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors', maxZoom: 19
  });
  (cfg.overview ? streets : satellite).addTo(map);
  [streets, satellite].forEach((layer) => {
    layer.on("tileerror", () => { status.textContent = "部分底图未能加载。可切换底图，或直接打开详情与标注图。"; });
  });
  L.control.layers({ "卫星影像": satellite, "街道地图": streets }, {}, { collapsed: false }).addTo(map);
  L.control.scale({ imperial: false, position: "bottomleft" }).addTo(map);
  let circle;
  if (cfg.radiusKm) {
    circle = L.circle(cfg.origin, { radius: cfg.radiusKm * 1000, color: "#167b83", weight: 2, dashArray: "6 6", fillOpacity: 0.04 }).addTo(map);
    L.circleMarker(cfg.origin, { radius: 4, color: "#fff", fillColor: "#167b83", fillOpacity: 1, weight: 2 })
      .addTo(map).bindTooltip(cfg.originName || "核查圆心");
  }
  const markers = (cfg.sites || []).map((site, index) => {
    const marker = L.marker(site.pos, {
      title: site.name,
      icon: L.divIcon({ className: "probe-pin", html: `<span style="--point:${site.color}">${index + 1}</span>`, iconSize: [28, 28], iconAnchor: [14, 14] })
    }).addTo(map);
    const popup = document.createElement("div");
    const heading = document.createElement("strong");
    heading.textContent = site.name;
    const note = document.createElement("p");
    note.textContent = site.note || "";
    const link = document.createElement("a");
    link.href = site.href || `#${site.id}`;
    link.textContent = cfg.overview ? "打开城市详情" : "查看标注图与核查依据";
    popup.append(heading, note, link);
    marker.bindPopup(popup);
    marker.bindTooltip(site.name, { direction: "top", offset: [0, -12] });
    function select() {
      buttons.forEach((button, i) => button.setAttribute("aria-pressed", String(i === index)));
      status.textContent = `${site.name}：${site.note || ""}`;
    }
    marker.on("popupopen", select);
    buttons[index].addEventListener("click", () => {
      map.setView(site.pos, cfg.overview ? 7 : Math.max(cfg.zoom || 12, 14), { animate: false });
      marker.openPopup();
    });
    return marker;
  });
  function fitSites() {
    map.closePopup();
    if (markers.length) map.fitBounds(L.featureGroup(markers).getBounds(), { padding: [36, 36], maxZoom: cfg.overview ? 5 : 14, animate: false });
    buttons.forEach((button) => button.setAttribute("aria-pressed", "false"));
    sidebar.scrollTop = 0;
  }
  function action(label, callback) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", callback);
    toolbar.append(button);
  }
  action("重置地图视野", () => {
    fitSites();
    status.textContent = cfg.overview
      ? `已重置地图视野，显示全部 ${markers.length} 座城市。点击城市名称可放大查看。`
      : `已重置地图视野，显示全部 ${markers.length} 个核查点。`;
  });
  if (circle) action(`${cfg.radiusKm} km 核查范围`, () => map.fitBounds(circle.getBounds(), { padding: [20, 20], animate: false }));
  fitSites();
})();
