/* openMar · mapa de la flota potera (ADR 0008 y 0009). Sin build: JavaScript plano. */
(() => {
  "use strict";

  const COLORS = { rojo: "#fb5a6e", amarillo: "#fbbf24", verde: "#34d399" };
  const ORDER = { rojo: 0, amarillo: 1, verde: 2 };
  const LABELS = { rojo: "Señales repetidas", amarillo: "Señales aisladas", verde: "Sin señales" };
  const GAP_STATUS = {
    en_marea_sin_observador: "en marea sin observador",
    en_marea_con_observador: "en marea con observador a bordo",
    fuera_de_marea: "fuera de las fechas de marea",
    sin_mareas_del_buque: "sin mareas informadas",
  };
  const BOUNDS = [[-68.5, -55.5], [-52.5, -36.5]];
  const FONT = ["Noto Sans Regular"];

  const $ = (selector) => document.querySelector(selector);
  const status = $("#map-status");
  const activeColors = new Set(["rojo", "amarillo", "verde"]);
  let vessels = [];
  let hoverPopup = null;
  let pinnedPopup = null;

  const { esc, num, plural, limitItems, loadJSON } = window.openMar;

  // ---------- Textos ----------

  function vesselSummary(p) {
    if (!Number(p.apagones)) {
      return "Sin apagones de AIS registrados por Global Fishing Watch en la temporada.";
    }
    const parts = [
      [p.en_marea_sin_observador, "en mareas sin observador"],
      [p.en_marea_con_observador, "con observador a bordo"],
      [p.fuera_de_marea, "fuera de las fechas de marea"],
    ]
      .filter(([n]) => Number(n) > 0)
      .map(([n, text]) => `${num(n)} ${text}`);
    let text = `${plural(p.apagones, "apagón", "apagones")} de AIS de 12 h o más (${num(p.horas_sin_ais)} h sin señal en total): ${parts.join(", ")}.`;
    if (Number(p.franja_milla_200) > 0) {
      text += ` ${plural(p.franja_milla_200, "empieza o termina", "empiezan o terminan")} cerca de la milla 200.`;
    }
    return text;
  }

  function vesselCard(p) {
    const observed2124 =
      p.viajes_2021_2024 === "" ? "sin datos" : `${num(p.viajes_con_observador_2021_2024)} de ${num(p.viajes_2021_2024)}`;
    const sanctions = p.sanciones_registradas
      ? `Disp. ${esc(p.sanciones_registradas)}${p.fechas_sanciones ? ` (${esc(p.fechas_sanciones)})` : ""}`
      : "ninguna en el registro";
    const ports = Number(p.escalas)
      ? `${num(p.escalas)}, sobre todo en ${esc(p.puerto_principal)}${Number(p.escalas_exterior) ? `; ${num(p.escalas_exterior)} afuera: ${esc(p.puertos_exterior)}` : "; ninguna afuera"}`
      : "sin escalas detectadas";
    const position =
      p.posicion_segun === "apagones" ? "mediana de sus apagones" : `zona habitual de pesca (${num(p.eventos_de_pesca)} eventos)`;
    return `
      <article class="card">
        <header class="card__head">
          <span class="card__status"><span class="dot dot--${esc(p.semaforo)}"></span>${esc(LABELS[p.semaforo])}</span>
          <h3 class="card__name">${esc(p.buque)}</h3>
          <div class="card__owner">${p.armador ? esc(p.armador) : "Sin armador en el registro"}${p.matricula ? ` · Matrícula ${esc(p.matricula)}` : ""}</div>
        </header>
        <p class="card__summary">${esc(vesselSummary(p))}</p>
        <dl class="card__grid">
          <dt>Mareas 2025</dt><dd>${num(p.mareas_temporada)} (${num(p.mareas_con_observador)} con observador)</dd>
          <dt>Captura 2025</dt><dd>${num(p.captura_t)} t</dd>
          <dt>Viajes con observador 2021–24</dt><dd>${observed2124}</dd>
          <dt>Llegadas a puerto 2025</dt><dd>${ports}</dd>
          <dt>Sanciones</dt><dd>${sanctions}</dd>
          <dt>Posición</dt><dd>${position}</dd>
        </dl>
        <footer class="card__foot">Fuentes: Global Fishing Watch · INIDEP · Registro de Flota Pesquera</footer>
      </article>`;
  }

  function gapCard(p) {
    return `
      <article class="card card--gap">
        <header class="card__head">
          <span class="card__status">Apagón de AIS</span>
          <h3 class="card__name">${esc(p.buque || "Buque sin identificar")}</h3>
          <div class="card__owner">${esc(p.fecha_local)} · ${num(p.horas, 1)} h sin señal</div>
        </header>
        <p class="card__summary">Ocurrió ${esc(GAP_STATUS[p.estado] || p.estado)}${p.marea ? ` (marea ${esc(p.marea)})` : ""}.${
          String(p.franja_milla_200) === "true" ? " Cerca de la milla 200." : ""
        }</p>
        <footer class="card__foot">Fuente: Global Fishing Watch · cruce con mareas del INIDEP</footer>
      </article>`;
  }

  // ---------- Panel ----------

  function renderCounts(summary) {
    for (const [color, count] of Object.entries(summary.por_color || {})) {
      const el = document.querySelector(`[data-count="${color}"]`);
      if (el) el.textContent = num(count);
    }
  }

  function renderList(map) {
    const query = $("#search").value.trim().toLowerCase();
    const list = $("#vessels");
    const visible = vessels.filter(
      (f) =>
        activeColors.has(f.properties.semaforo) &&
        (!query || `${f.properties.buque} ${f.properties.armador}`.toLowerCase().includes(query)),
    );
    list.innerHTML = visible
      .map((f) => {
        const p = f.properties;
        const metric = Number(p.apagones) ? plural(p.apagones, "apagón", "apagones") : `${num(p.captura_t)} t`;
        return `<li><button class="vessel" data-name="${esc(p.buque)}">
          <span class="dot dot--${esc(p.semaforo)}" aria-hidden="true"></span>
          <span><span class="vessel__name">${esc(p.buque)}</span><span class="vessel__owner">${esc(p.armador || "Sin armador en el registro")}</span></span>
          <span class="vessel__metric">${metric}</span>
        </button></li>`;
      })
      .join("");
    $("#list-count").textContent = `${num(visible.length)} de ${num(vessels.length)} en el mapa`;
    list.querySelectorAll(".vessel").forEach((button) =>
      button.addEventListener("click", () => focusVessel(map, button.dataset.name)),
    );
  }

  function renderStatic(summary) {
    const missing = summary.sin_posicion || [];
    $("#missing-count").textContent = `(${num(missing.length)})`;
    $("#missing").innerHTML = missing
      .map((v) => `<li><span class="dot dot--${esc(v.semaforo)}"></span> ${esc(v.buque)} · ${esc(v.armador || "sin armador en el registro")}</li>`)
      .join("");
    $("#sources").innerHTML = (summary.fuentes || [])
      .filter((s) => /^https:\/\//.test(s.url || ""))
      .map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.nombre)}</a>: ${esc(s.aporta)}</li>`)
      .join("");
    const generated = summary.generado ? new Date(summary.generado) : null;
    $("#generated").textContent = generated ? `Datos generados el ${generated.toLocaleDateString("es-AR")}` : "";
    const items = limitItems(summary);
    $("#limits-list").innerHTML = items.map((item) => `<li>${item}</li>`).join("");
    $("#limits-short").textContent = `${plural(missing.length, "buque", "buques")} sin recorrido, ${plural(
      (summary.sin_armador || []).length,
      "buque",
      "buques",
    )} sin armador en el registro y otros límites de las fuentes.`;
  }

  // ---------- Mapa ----------

  // Mapa base abierto y sin clave (OpenFreeMap, datos de OpenStreetMap).
  const BASE_STYLE = "https://tiles.openfreemap.org/styles/dark";

  function tuneBase(map) {
    const paint = [
      ["background", "background-color", "#0d1624"],
      ["water", "fill-color", "#04080f"],
    ];
    for (const [id, property, value] of paint) {
      if (map.getLayer(id)) map.setPaintProperty(id, property, value);
    }
    // Etiquetas del mapa base en castellano: "Islas Malvinas", no "Falkland Islands".
    const spanish = ["coalesce", ["get", "name:es"], ["get", "name:latin"], ["get", "name"]];
    for (const layer of map.getStyle().layers) {
      if (layer.type === "symbol" && layer.layout && layer.layout["text-field"]) {
        map.setLayoutProperty(layer.id, "text-field", spanish);
      }
    }
  }

  const colorExpr = ["match", ["get", "semaforo"], "rojo", COLORS.rojo, "amarillo", COLORS.amarillo, COLORS.verde];
  const LAYER_GROUPS = {
    zee: ["zee-relleno", "zee-linea"],
    pesca: ["pesca-calor"],
    apagones: ["apagones"],
    buques: ["buques-halo", "buques", "buques-nombres"],
  };

  function addLayers(map, data) {
    map.addSource("zee", { type: "geojson", data: data.zee });
    map.addSource("pesca", { type: "geojson", data: data.pesca });
    map.addSource("apagones", { type: "geojson", data: data.apagones });
    map.addSource("buques", { type: "geojson", data: data.buques });

    map.addLayer({ id: "zee-relleno", type: "fill", source: "zee", paint: { "fill-color": "#5fb4d9", "fill-opacity": 0.035 } });
    map.addLayer({
      id: "zee-linea", type: "line", source: "zee",
      paint: { "line-color": "#5fb4d9", "line-opacity": 0.55, "line-width": 1.2, "line-dasharray": [3, 3] },
    });
    map.addLayer({
      id: "pesca-calor", type: "heatmap", source: "pesca", layout: { visibility: "none" },
      paint: {
        "heatmap-weight": ["interpolate", ["linear"], ["get", "eventos"], 1, 0.15, 40, 1],
        "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 3, 8, 8, 30],
        "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 3, 0.6, 8, 1.4],
        "heatmap-opacity": 0.7,
        "heatmap-color": [
          "interpolate", ["linear"], ["heatmap-density"],
          0, "rgba(0,0,0,0)", 0.2, "rgba(120,60,20,0.35)", 0.5, "rgba(255,140,60,0.55)", 0.8, "rgba(255,200,110,0.8)", 1, "#fff3cf",
        ],
      },
    });
    map.addLayer({
      id: "apagones", type: "circle", source: "apagones",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 3, 3, 8, 7],
        "circle-color": "rgba(251,146,60,0.08)",
        "circle-stroke-color": "#fb923c",
        "circle-stroke-width": 1.4,
        "circle-stroke-opacity": 0.85,
      },
    });
    map.addLayer({
      id: "buques-halo", type: "circle", source: "buques",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 3, ["match", ["get", "semaforo"], "rojo", 16, "amarillo", 12, 8], 8, ["match", ["get", "semaforo"], "rojo", 34, "amarillo", 26, 18]],
        "circle-color": colorExpr,
        "circle-opacity": ["match", ["get", "semaforo"], "verde", 0.18, 0.32],
        "circle-blur": 1,
      },
    });
    map.addLayer({
      id: "buques", type: "circle", source: "buques",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 3, ["match", ["get", "semaforo"], "verde", 3.5, 5], 8, ["match", ["get", "semaforo"], "verde", 6, 8]],
        "circle-color": colorExpr,
        "circle-stroke-color": "#04080f",
        "circle-stroke-width": 1,
      },
    });
    map.addLayer({
      id: "buques-nombres", type: "symbol", source: "buques",
      layout: {
        "text-field": ["get", "buque"],
        "text-font": FONT,
        "text-size": ["interpolate", ["linear"], ["zoom"], 3, 10, 8, 13],
        "text-offset": [0, 1.1],
        "text-anchor": "top",
        "text-max-width": 14,
        "text-optional": true,
        "symbol-sort-key": ["match", ["get", "semaforo"], "rojo", 0, "amarillo", 1, 2],
      },
      paint: {
        "text-color": ["match", ["get", "semaforo"], "verde", "#9fb0c4", "#e8eef6"],
        "text-halo-color": "#04080f",
        "text-halo-width": 1.4,
      },
    });
  }

  function applyColorFilter(map) {
    const filter = ["in", ["get", "semaforo"], ["literal", [...activeColors]]];
    for (const id of LAYER_GROUPS.buques) if (map.getLayer(id)) map.setFilter(id, filter);
  }

  function applyLayer(map, input) {
    for (const id of LAYER_GROUPS[input.dataset.layer]) {
      if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", input.checked ? "visible" : "none");
    }
  }

  function setPanelCollapsed(collapsed) {
    $("#panel").classList.toggle("is-collapsed", collapsed);
    $("#panel-toggle").setAttribute("aria-expanded", String(!collapsed));
    // Plegado, el contenido no debe recibir foco ni leerse con lector de pantalla.
    $("#panel-body").inert = collapsed && window.matchMedia("(max-width: 760px)").matches;
  }

  function showPopup(map, lngLat, html, pinned) {
    const popup = new maplibregl.Popup({ closeButton: pinned, closeOnClick: pinned, maxWidth: "320px", offset: 14 })
      .setLngLat(lngLat)
      .setHTML(html)
      .addTo(map);
    return popup;
  }

  function focusVessel(map, name) {
    const feature = vessels.find((f) => f.properties.buque === name);
    if (!feature) return;
    const coords = feature.geometry.coordinates;
    const mobile = window.matchMedia("(max-width: 760px)").matches;
    // El barco queda arriba del centro para que el tooltip no choque con el pie del mapa.
    const padding = mobile ? { top: 0, bottom: 260, left: 0, right: 0 } : { top: 0, bottom: 380, left: 0, right: 0 };
    map.flyTo({ center: coords, zoom: Math.max(map.getZoom(), 6.5), duration: 1200, essential: true, padding });
    if (pinnedPopup) pinnedPopup.remove();
    pinnedPopup = showPopup(map, coords, vesselCard(feature.properties), true);
    if (mobile) setPanelCollapsed(true);
  }

  function bindMapEvents(map) {
    const hover = (layer, card) => {
      map.on("mouseenter", layer, (e) => {
        map.getCanvas().style.cursor = "pointer";
        if (hoverPopup) hoverPopup.remove();
        const f = e.features[0];
        hoverPopup = showPopup(map, f.geometry.coordinates, card(f.properties), false);
      });
      map.on("mouseleave", layer, () => {
        map.getCanvas().style.cursor = "";
        if (hoverPopup) hoverPopup.remove();
        hoverPopup = null;
      });
      map.on("click", layer, (e) => {
        const f = e.features[0];
        if (hoverPopup) hoverPopup.remove();
        if (pinnedPopup) pinnedPopup.remove();
        pinnedPopup = showPopup(map, f.geometry.coordinates, card(f.properties), true);
      });
    };
    hover("buques", vesselCard);
    hover("apagones", gapCard);
  }

  function bindPanel(map) {
    document.querySelectorAll(".light").forEach((button) =>
      button.addEventListener("click", () => {
        const color = button.dataset.color;
        if (activeColors.has(color)) activeColors.delete(color);
        else activeColors.add(color);
        const on = activeColors.has(color);
        button.classList.toggle("is-on", on);
        button.setAttribute("aria-pressed", String(on));
        applyColorFilter(map);
        renderList(map);
      }),
    );
    document.querySelectorAll("[data-layer]").forEach((input) =>
      input.addEventListener("change", () => applyLayer(map, input)),
    );
    $("#search").addEventListener("input", () => renderList(map));
    $("#panel-toggle").addEventListener("click", () =>
      setPanelCollapsed(!$("#panel").classList.contains("is-collapsed")),
    );
    $("#limits-toggle").addEventListener("click", () => {
      const list = $("#limits-list");
      const open = list.hidden;
      list.hidden = !open;
      $("#limits-toggle").setAttribute("aria-expanded", String(open));
      $(".limits__more").textContent = open ? "Ocultar" : "Ver detalle";
    });
  }

  async function main() {
    const [summary, buques, apagones, pesca, zee] = await Promise.all(
      ["resumen.json", "buques.geojson", "apagones.geojson", "pesca.geojson", "zee.geojson"].map((f) => loadJSON(`data/${f}`)),
    );
    vessels = [...buques.features].sort(
      (a, b) =>
        ORDER[a.properties.semaforo] - ORDER[b.properties.semaforo] ||
        Number(b.properties.apagones) - Number(a.properties.apagones) ||
        a.properties.buque.localeCompare(b.properties.buque),
    );
    renderCounts(summary);
    renderStatic(summary);
    if (window.matchMedia("(max-width: 760px)").matches) setPanelCollapsed(true);

    const map = new maplibregl.Map({
      container: "map",
      style: BASE_STYLE,
      bounds: BOUNDS,
      fitBoundsOptions: { padding: { top: 40, bottom: 90, left: 40, right: 40 } },
      attributionControl: { compact: true },
      dragRotate: false,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    // El estilo base referencia íconos que no usamos: se reemplazan por una imagen vacía.
    map.on("styleimagemissing", (e) => {
      if (!map.hasImage(e.id)) map.addImage(e.id, { width: 1, height: 1, data: new Uint8Array(4) });
    });
    map.on("load", () => {
      tuneBase(map);
      addLayers(map, { buques, apagones, pesca, zee });
      bindMapEvents(map);
      // El panel pudo cambiar filtros o capas antes de que el mapa cargara.
      applyColorFilter(map);
      document.querySelectorAll("[data-layer]").forEach((input) => applyLayer(map, input));
      status.classList.add("is-hidden");
      const linked = new URLSearchParams(window.location.search).get("buque");
      if (linked) focusVessel(map, linked);
    });
    map.on("error", (event) => {
      if (map.loaded()) return; // un error aislado de una tesela no frena el mapa
      status.classList.remove("is-hidden");
      status.textContent = `No se pudo cargar el mapa base${event.error?.message ? `: ${event.error.message}` : ""}. Probá recargar la página.`;
    });
    bindPanel(map);
    renderList(map);
  }

  main().catch((error) => {
    status.textContent = `No se pudieron cargar los datos: ${error.message}`;
  });
})();
