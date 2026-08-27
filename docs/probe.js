(function () {
  const lb = document.getElementById("lb");
  const lbImg = document.getElementById("lb-img");
  if (lb && lbImg) {
    document.querySelectorAll("figure.plate img, figure.hero img").forEach((img) => {
      img.addEventListener("click", () => {
        lbImg.src = img.src;
        lbImg.alt = img.alt;
        lb.hidden = false;
        lb.classList.add("open");
      });
    });
    function closeLb() {
      lb.classList.remove("open");
      lb.hidden = true;
      lbImg.src = "";
    }
    const closeBtn = document.getElementById("lb-close");
    if (closeBtn) closeBtn.addEventListener("click", closeLb);
    lb.addEventListener("click", (e) => { if (e.target === lb) closeLb(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeLb(); });
  }

  const mapEl = document.getElementById("map");
  if (!mapEl || typeof L === "undefined" || !window.PROBE) return;
  const cfg = window.PROBE;
  const map = L.map("map", { scrollWheelZoom: false, zoomControl: true }).setView(cfg.origin, cfg.zoom || 12);
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
    attribution: "Tiles © Esri",
    maxZoom: 18
  }).addTo(map);
  if (cfg.radiusKm) {
    L.circle(cfg.origin, { radius: cfg.radiusKm * 1000, color: "#4a9b8c", weight: 1.2, fillOpacity: 0.04 }).addTo(map);
  }
  L.circleMarker(cfg.origin, { radius: 5, color: "#e8e1d4", fillColor: "#4a9b8c", fillOpacity: 1, weight: 1 })
    .addTo(map)
    .bindPopup(`<strong>${cfg.originName || "圆心"}</strong>${cfg.origin[0].toFixed(4)}°N ${cfg.origin[1].toFixed(4)}°E`);
  (cfg.sites || []).forEach((s) => {
    L.circleMarker(s.pos, { radius: 8, color: s.color, fillColor: s.color, fillOpacity: 0.9, weight: 1 })
      .addTo(map)
      .bindPopup(`<strong>${s.name}</strong>${s.note || ""}<br><a href="#${s.id}">看标注图</a>`);
  });
  function goHash() {
    const id = location.hash.replace("#", "");
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ block: "start" });
  }
  map.whenReady(() => setTimeout(goHash, 80));
  window.addEventListener("hashchange", goHash);
})();
