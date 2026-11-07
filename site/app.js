/* openMar · mapa de la flota potera (ADR 0008 y 0009). Sin build: JavaScript plano. */
(() => {
  "use strict";

  const COLORS = { rojo: "#b3470f", amarillo: "#8a5a00", verde: "#6b7480" };
  const ORDER = { rojo: 0, amarillo: 1, verde: 2 };
  const BOUNDS = [[-68.5, -55.5], [-52.5, -36.5]];
  const FONT = ["Noto Sans Regular"];
  // Teselas del mapa base que pueden fallar antes de avisar: una suelta no merece un mensaje.
  const TILE_ERRORS_BEFORE_NOTICE = 5;

  const $ = (selector) => document.querySelector(selector);
  const status = $("#map-status");
  const activeColors = new Set(["rojo", "amarillo", "verde"]);
  let vessels = [];
  let hoverPopup = null;
  let pinnedPopup = null;
  let minGapHours = null;

  const { esc, num, plural, limitItems, loadJSON, fillNumbers, cutsBreakdown, ruleTexts, safeURL, LABELS, GAP_STATUS, gapSummary, fichaURL } =
    window.openMar;

  // ---------- Textos ----------

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
      p.posicion_segun === "apagones" ? "punto típico de sus cortes de señal" : `zona habitual de pesca (${num(p.eventos_de_pesca)} eventos)`;
    return `
      <article class="card">
        <header class="card__head">
          <span class="card__status"><span class="dot dot--${esc(p.semaforo)}"></span>${esc(LABELS[p.semaforo])}</span>
          <h3 class="card__name">${esc(p.buque)}</h3>
          <div class="card__owner">${p.armador ? esc(p.armador) : "Sin armador en el registro"}${p.matricula ? ` · Matrícula ${esc(p.matricula)}` : ""}</div>
          <a class="card__more" href="${fichaURL(p.buque)}">Ver la ficha completa →</a>
        </header>
        <p class="card__summary">${esc(gapSummary(p, minGapHours))}</p>
        <dl class="card__grid">
          <dt>Viajes 2025</dt><dd>${num(p.mareas_temporada)} (${num(p.mareas_con_observador)} con observador)</dd>
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
          <span class="card__status">Corte de señal</span>
          <h3 class="card__name">${esc(p.buque || "Barco sin identificar")}</h3>
          <div class="card__owner">${esc(p.fecha_local)} · ${num(p.horas, 1)} h sin señal</div>
        </header>
        <p class="card__summary">Ocurrió ${esc(GAP_STATUS[p.estado] || p.estado)}${p.marea ? ` (viaje ${esc(p.marea)})` : ""}.${
          String(p.franja_milla_200) === "true" ? " Cerca de la milla 200." : ""
        }</p>
        <footer class="card__foot">Fuente: Global Fishing Watch · cruce con viajes del INIDEP</footer>
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
        // El total a la derecha y, debajo del nombre, el mismo desglose que en el resto del sitio.
        const cuts = Number(p.apagones);
        const metric = cuts ? plural(cuts, "corte", "cortes") : `${num(p.captura_t)} t`;
        const detail = cuts ? `<span class="vessel__owner">${esc(cutsBreakdown(p).join(" · "))}</span>` : "";
        return `<li><button class="vessel" data-name="${esc(p.buque)}">
          <span class="dot dot--${esc(p.semaforo)}" aria-hidden="true"></span>
          <span><span class="vessel__name">${esc(p.buque)}</span><span class="vessel__owner">${esc(p.armador || "Sin armador en el registro")}</span>${detail}</span>
          <span class="vessel__metric">${esc(metric)}</span>
        </button></li>`;
      })
      .join("");
    $("#list-count").textContent = `${num(visible.length)} de ${num(vessels.length)} en el mapa`;
    list.querySelectorAll(".vessel").forEach((button) =>
      button.addEventListener("click", () => focusVessel(map, button.dataset.name, button)),
    );
  }

  function renderStatic(summary) {
    const missing = summary.sin_posicion || [];
    $("#missing-count").textContent = `(${num(missing.length)})`;
    $("#missing").innerHTML = missing
      .map((v) => `<li><span class="dot dot--${esc(v.semaforo)}"></span> <a href="${fichaURL(v.buque)}">${esc(v.buque)}</a> · ${esc(v.armador || "sin armador en el registro")}</li>`)
      .join("");
    $("#sources").innerHTML = (summary.fuentes || [])
      .filter((s) => safeURL(s.url))
      .map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.nombre)}</a>: ${esc(s.aporta)}</li>`)
      .join("");
    const generated = summary.generado ? new Date(summary.generado) : null;
    $("#generated").textContent = generated ? `Datos generados el ${generated.toLocaleDateString("es-AR")}` : "";
    const rules = ruleTexts(summary.reglas);
    if (rules) {
      $("#rule-rojo").textContent = rules.rojo;
      $("#rule-amarillo").textContent = rules.amarillo;
    }
    const items = limitItems(summary);
    $("#limits-list").innerHTML = items.map((item) => `<li>${item}</li>`).join("");
    $("#limits-short").textContent = `${plural(missing.length, "barco", "barcos")} sin recorrido, ${plural(
      (summary.sin_armador || []).length,
      "barco",
      "barcos",
    )} sin armador en el registro y otros límites de las fuentes.`;
  }

  // ---------- Mapa ----------

  // Mapa base abierto y sin clave (OpenFreeMap, datos de OpenStreetMap).
  const BASE_STYLE = "https://tiles.openfreemap.org/styles/positron";

  function tuneBase(map) {
    const paint = [
      ["background", "background-color", "#f6f7f8"],
      ["water", "fill-color", "#dce5ed"],
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

    map.addLayer({ id: "zee-relleno", type: "fill", source: "zee", paint: { "fill-color": "#1d5fa6", "fill-opacity": 0.04 } });
    map.addLayer({
      id: "zee-linea", type: "line", source: "zee",
      paint: { "line-color": "#1d5fa6", "line-opacity": 0.7, "line-width": 1.2, "line-dasharray": [3, 3] },
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
          0, "rgba(179,71,15,0)", 0.2, "rgba(179,71,15,0.15)", 0.5, "rgba(179,71,15,0.35)", 0.8, "rgba(179,71,15,0.6)", 1, "#8a3307",
        ],
      },
    });
    map.addLayer({
      id: "apagones", type: "circle", source: "apagones",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 3, 3, 8, 7],
        "circle-color": "rgba(179,71,15,0.06)",
        "circle-stroke-color": "#b3470f",
        "circle-stroke-width": 1,
        "circle-stroke-opacity": 0.5,
      },
    });
    map.addLayer({
      id: "buques-halo", type: "circle", source: "buques",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 3, ["match", ["get", "semaforo"], "rojo", 16, "amarillo", 12, 8], 8, ["match", ["get", "semaforo"], "rojo", 34, "amarillo", 26, 18]],
        "circle-color": colorExpr,
        "circle-opacity": 0,
      },
    });
    map.addLayer({
      id: "buques", type: "circle", source: "buques",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 3, ["match", ["get", "semaforo"], "verde", 3.5, 6], 8, ["match", ["get", "semaforo"], "verde", 6, 10]],
        "circle-color": colorExpr,
        "circle-stroke-color": "#ffffff",
        "circle-stroke-width": 1.5,
      },
    });
    map.addLayer({
      id: "buques-nombres", type: "symbol", source: "buques",
      layout: {
        // Con poco zoom sólo se nombran los barcos con señales; así no se pisan.
        "text-field": ["step", ["zoom"], ["match", ["get", "semaforo"], "verde", "", ["get", "buque"]], 6, ["get", "buque"]],
        "text-font": FONT,
        "text-size": ["interpolate", ["linear"], ["zoom"], 3, 10, 8, 13],
        "text-offset": [0, 1.1],
        "text-anchor": "top",
        "text-max-width": 14,
        "text-optional": true,
        "symbol-sort-key": ["match", ["get", "semaforo"], "rojo", 0, "amarillo", 1, 2],
      },
      paint: {
        "text-color": ["match", ["get", "semaforo"], "verde", "#5a6370", "#15191f"],
        "text-halo-color": "#ffffff",
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

  // Anuncia a los lectores de pantalla lo que muestra una tarjeta fijada.
  function announce(text) {
    const live = $("#map-announce");
    live.textContent = "";
    window.requestAnimationFrame(() => {
      live.textContent = text;
    });
  }

  // Las tarjetas fijadas son diálogos: reciben el foco, se anuncian, se cierran con Escape
  // y, al cerrarse, el foco vuelve a quien las abrió.
  function showPopup(map, lngLat, html, pinned, info = {}) {
    const popup = new maplibregl.Popup({
      closeButton: pinned, closeOnClick: pinned, focusAfterOpen: pinned, maxWidth: "320px", offset: 14,
    })
      .setLngLat(lngLat)
      .setHTML(html)
      .addTo(map);
    if (!pinned) return popup;
    const el = popup.getElement();
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-label", info.label || "Detalle");
    el.addEventListener("keydown", (e) => {
      if (e.key === "Escape") popup.remove();
    });
    if (info.opener) popup.on("close", () => info.opener.isConnected && info.opener.focus());
    if (info.text) announce(info.text);
    return popup;
  }

  const vesselInfo = (p, opener) => ({ label: `Barco ${p.buque}`, text: `${p.buque}. ${gapSummary(p, minGapHours)}`, opener });
  const gapInfo = (p) => ({
    label: `Corte de señal de ${p.buque || "un barco sin identificar"}`,
    text: `Corte de señal de ${p.buque || "un barco sin identificar"}, ${p.fecha_local}, ${num(p.horas, 1)} horas, ${GAP_STATUS[p.estado] || p.estado}.`,
  });

  function focusVessel(map, name, opener) {
    const feature = vessels.find((f) => f.properties.buque === name);
    if (!feature) return;
    const coords = feature.geometry.coordinates;
    const mobile = window.matchMedia("(max-width: 760px)").matches;
    // El barco queda arriba del centro para que el tooltip no choque con el pie del mapa.
    const padding = mobile ? { top: 0, bottom: 260, left: 0, right: 0 } : { top: 0, bottom: 380, left: 0, right: 0 };
    map.flyTo({ center: coords, zoom: Math.max(map.getZoom(), 6.5), duration: 1200, essential: true, padding });
    if (pinnedPopup) pinnedPopup.remove();
    // Plegado en el celular, el botón queda inerte: el foco no puede volver ahí.
    if (mobile) setPanelCollapsed(true);
    pinnedPopup = showPopup(map, coords, vesselCard(feature.properties), true, vesselInfo(feature.properties, mobile ? null : opener));
  }

  function bindMapEvents(map) {
    const hover = (layer, card, info) => {
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
        pinnedPopup = showPopup(map, f.geometry.coordinates, card(f.properties), true, info(f.properties));
      });
    };
    hover("buques", vesselCard, (p) => vesselInfo(p, null));
    hover("apagones", gapCard, gapInfo);
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

  // Una tesela que falla no es el mapa base caído: sólo se avisa si fallan varias,
  // y sin decir que el mapa no cargó. El mensaje fuerte queda para el estilo base.
  function bindMapErrors(map) {
    let tileErrors = 0;
    map.on("error", (event) => {
      if (event.tile || event.sourceId) {
        tileErrors += 1;
        if (tileErrors === TILE_ERRORS_BEFORE_NOTICE) {
          status.classList.remove("is-hidden");
          status.textContent = "Algunas partes del mapa base no cargaron. Los barcos y los cortes de señal se ven igual.";
        }
        return;
      }
      if (map.isStyleLoaded()) return;
      status.classList.remove("is-hidden");
      status.textContent = `No se pudo cargar el mapa base${event.error?.message ? `: ${event.error.message}` : ""}. Probá recargar la página.`;
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
    minGapHours = summary.reglas?.horas_minimas_apagon;
    fillNumbers(summary);
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
    bindMapErrors(map);
    bindPanel(map);
    renderList(map);
  }

  main().catch((error) => {
    status.textContent = `No se pudieron cargar los datos: ${error.message}`;
  });
})();
