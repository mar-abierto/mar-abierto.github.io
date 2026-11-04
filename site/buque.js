/* openMar · ficha por buque. Sin ?b= muestra el índice de buques. Todo sale de data/. */
(() => {
  "use strict";

  const { esc, num, plural, loadJSON, limitItems, fillNumbers, seriesHTML, LABELS, GAP_STATUS, gapSummary, fichaURL } =
    window.openMar;
  const $ = (selector) => document.querySelector(selector);
  const ORDER = { rojo: 0, amarillo: 1, verde: 2 };
  const MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

  // ---------- Fechas ----------

  // Fechas ISO (AAAA-MM-DD) como días del calendario, sin zona horaria.
  const dayOf = (iso) => Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10)) / 864e5;
  const shortDate = (iso) => `${+iso.slice(8, 10)} ${MONTHS[+iso.slice(5, 7) - 1]}`;

  // ---------- Encabezado y KPIs ----------

  function statusText(p, rules) {
    const threshold = rules?.umbral_senales_repetidas;
    const why = {
      rojo: `${num(threshold)} o más apagones de AIS sin observador a bordo.`,
      amarillo: `Tuvo apagones de AIS, pero menos de ${num(threshold)} sin observador a bordo.`,
      verde: "Sin apagones de AIS registrados en la temporada.",
    }[p.semaforo];
    return `<span class="dot dot--${esc(p.semaforo)}"></span><b>${esc(LABELS[p.semaforo])}.</b> ${esc(why)} El color dice dónde mirar primero, no quién es culpable.`;
  }

  function kpi(value, label, meta, tone = "") {
    return `<article class="kpi">
      <p class="kpi__value ${tone}">${value}</p>
      <p class="kpi__label">${label}</p>
      <p class="kpi__meta">${meta}</p>
    </article>`;
  }

  function portsMeta(p) {
    const unknown = Number(p.escalas_pais_desconocido);
    if (Number(p.escalas_exterior)) return `<b class="hl-warn">${num(p.escalas_exterior)} fuera del país</b>: ${esc(p.puertos_exterior)}`;
    if (!Number(p.escalas)) return "Sin escalas detectadas";
    if (unknown) return `Ninguna en el exterior identificada; ${plural(unknown, "escala", "escalas")} sin país · sobre todo en ${esc(p.puerto_principal)}`;
    return `Ninguna fuera del país · sobre todo en ${esc(p.puerto_principal)}`;
  }

  function renderKpis(f) {
    const p = f.datos;
    const c = f.comparacion;
    const noTrips = c.pct_con_observador == null;
    const abroad = Number(p.escalas_exterior);
    $("#v-kpis").innerHTML = [
      kpi(
        noTrips ? "s/d" : `${num(c.pct_con_observador, 1)} %`,
        "de sus mareas de la temporada con observador",
        noTrips ? "Sin mareas en el informe del INIDEP" : `${num(p.mareas_con_observador)} de ${plural(p.mareas_temporada, "marea", "mareas")} · flota: ${num(c.pct_con_observador_flota, 1)} %`,
        "kpi__value--obs",
      ),
      kpi(
        noTrips ? num(p.apagones) : num(c.apagones_por_marea, 2),
        noTrips ? "apagones de AIS en la temporada" : "apagones de AIS por marea",
        noTrips
          ? "Sin mareas informadas para comparar"
          : `${plural(c.apagones_en_marea, "apagón", "apagones")} durante sus mareas${Number(p.fuera_de_marea) ? ` y ${num(p.fuera_de_marea)} fuera de ellas` : ""} · flota: ${num(c.apagones_por_marea_flota, 2)} por marea`,
        "kpi__value--gap",
      ),
      kpi(
        `${num(p.escalas)}`,
        "llegadas a puerto detectadas",
        portsMeta(p),
        "kpi__value--port",
      ),
      kpi(`${num(p.captura_t)}<small> t</small>`, "de captura declarada en la temporada", "INIDEP, Anexo 1"),
    ].join("");
  }

  // ---------- Línea de tiempo ----------

  function timeline(f, year) {
    const start = dayOf(`${year}-01-01`);
    const span = dayOf(`${year + 1}-01-01`) - start;
    const x = (iso) => Math.min(100, Math.max(0, ((dayOf(iso) - start) / span) * 100));
    const inYear = (iso) => iso.startsWith(String(year));

    const months = MONTHS.map((m, i) => {
      const iso = `${year}-${String(i + 1).padStart(2, "0")}-01`;
      return `<span class="tl-month" style="--x:${x(iso)}%">${m}</span>`;
    }).join("");

    const trips = f.mareas
      .map((t) => {
        const left = x(t.inicio);
        const width = Math.max(0.6, x(t.fin) - left + 100 / span);
        const label = `Marea ${t.marea}: ${shortDate(t.inicio)} al ${shortDate(t.fin)}, ${t.observador ? "con" : "sin"} observador${t.apagones ? `, ${plural(t.apagones, "apagón", "apagones")}` : ""}`;
        return `<li class="tl-trip${t.observador ? " tl-trip--obs" : ""}" style="--x:${left}%;--w:${width}%" title="${esc(label)}"><span class="sr-only">${esc(label)}</span></li>`;
      })
      .join("");

    const gaps = f.apagones_detalle
      .filter((g) => inYear(g.fecha_local))
      .map((g) => {
        const label = `Apagón del ${shortDate(g.fecha_local)}: ${num(g.horas, 1)} h, ${GAP_STATUS[g.estado] || g.estado}`;
        return `<li class="tl-gap tl-gap--${g.estado === "en_marea_con_observador" ? "con" : "sin"}" style="--x:${x(g.fecha_local)}%" title="${esc(label)}"><span class="sr-only">${esc(label)}</span></li>`;
      })
      .join("");

    const ports = f.escalas_detalle
      .filter((e) => inYear(e.llegada))
      .map((e) => {
        const label = `Llegada a ${e.puerto}${e.exterior ? ` (${e.pais})` : ""} el ${shortDate(e.llegada)}`;
        const tag = e.exterior ? `<span class="tl-port__tag" aria-hidden="true">${esc(e.pais)}</span>` : "";
        return `<li class="tl-port${e.exterior ? " tl-port--abroad" : ""}" style="--x:${x(e.llegada)}%" title="${esc(label)}">${tag}<span class="sr-only">${esc(label)}</span></li>`;
      })
      .join("");

    const lane = (id, name, items, empty) =>
      `<div class="tl-lane"><span class="tl-lane__name" id="tl-${id}">${name}</span><ol class="tl-track" aria-labelledby="tl-${id}">${items || `<li class="tl-empty">${empty}</li>`}</ol></div>`;

    $("#timeline").innerHTML = `
      ${lane("mareas", "Mareas", trips, "Sin mareas en el informe")}
      ${lane("apagones", "Apagones", gaps, "Ninguno")}
      ${lane("puertos", "Puertos", ports, "Sin escalas detectadas")}
      <div class="tl-axis" aria-hidden="true">${months}</div>`;

    $("#tl-legend").innerHTML = [
      ["tl-sw tl-sw--trip", "Marea sin observador"],
      ["tl-sw tl-sw--obs", "Marea con observador"],
      ["tl-sw tl-sw--gap", "Apagón de AIS"],
      ["tl-sw tl-sw--port", "Llegada a puerto argentino"],
      ["tl-sw tl-sw--abroad", "Llegada a puerto del exterior"],
    ]
      .map(([cls, text]) => `<li><span class="${cls}"></span>${text}</li>`)
      .join("");
  }

  // ---------- Tablas ----------

  function table(el, headers, rows, empty) {
    if (!rows.length) {
      el.innerHTML = `<tbody><tr><td class="table__empty" colspan="${headers.length}">${empty}</td></tr></tbody>`;
      return;
    }
    // Un encabezado con "#" adelante es una columna numérica: va alineada a la derecha.
    const head = headers.map((h) => (h.startsWith("#") ? `<th scope="col" class="n">${h.slice(1)}</th>` : `<th scope="col">${h}</th>`)).join("");
    el.innerHTML = `<thead><tr>${head}</tr></thead><tbody>${rows.map((r) => `<tr>${r.join("")}</tr>`).join("")}</tbody>`;
  }

  const th = (v) => `<th scope="row">${v}</th>`;
  const td = (v) => `<td>${v}</td>`;
  const tdn = (v) => `<td class="n">${v}</td>`;
  // Estadías largas (amarre, reparación) se leen mejor en días.
  const stay = (hours) => (hours >= 72 ? plural(Math.round(hours / 24), "día", "días") : `${num(hours, 1)} h`);

  function renderTables(f, rules) {
    table(
      $("#v-trips"),
      ["Marea", "Salida", "Regreso", "#Días", "Observador", "#Captura (t)", "#Apagones"],
      f.mareas.map((t) => [
        th(num(t.marea)), td(shortDate(t.inicio)), td(shortDate(t.fin)), tdn(num(t.dias)),
        td(t.observador ? '<span class="pill pill--obs">Sí</span>' : "No"),
        tdn(num(t.captura_t, 1)), tdn(t.apagones ? `<span class="pill pill--gap">${num(t.apagones)}</span>` : "0"),
      ]),
      "El informe del INIDEP no registra mareas de este buque en la temporada.",
    );

    table(
      $("#v-gaps"),
      ["Fecha", "#Horas sin señal", "Cuándo", "#Distancia a la costa al cortarse", "Cerca de la milla 200"],
      f.apagones_detalle.map((g) => [
        th(shortDate(g.fecha_local)), tdn(num(g.horas, 1)),
        td(`${esc(GAP_STATUS[g.estado] || g.estado)}${g.marea !== "" ? ` (marea ${esc(g.marea)})` : ""}`),
        tdn(g.km_costa_inicio == null ? "s/d" : `${num(g.km_costa_inicio)} km`),
        td(g.franja_milla_200 ? "Sí" : "No"),
      ]),
      `Global Fishing Watch no registra apagones de ${num(rules?.horas_minimas_apagon)} horas o más de este buque.`,
    );

    table(
      $("#v-ports"),
      ["Llegada", "Puerto", "País", "#Tiempo en puerto"],
      f.escalas_detalle.map((e) => [
        th(shortDate(e.llegada)),
        td(`${esc(e.puerto)}${e.nombre_completado ? ' <span class="muted" title="Nombre completado con otras escalas del mismo puerto">*</span>' : ""}`),
        td(e.exterior ? `<span class="pill pill--warn">${esc(e.pais)}</span>` : esc(e.pais || "s/d")),
        tdn(stay(e.horas)),
      ]),
      "Global Fishing Watch no detectó llegadas a puerto de confianza alta en el año.",
    );
    const inferred = f.escalas_detalle.some((e) => e.nombre_completado);
    $("#ports-note").hidden = !inferred;
  }

  function renderRegistry(p) {
    const rows = [
      ["Armador", p.armador ? esc(p.armador) : "No figura en el registro"],
      ["Matrícula", p.matricula ? esc(p.matricula) : "s/d"],
      ["Sanciones registradas", p.sanciones_registradas ? `Disp. ${esc(p.sanciones_registradas)}${p.fechas_sanciones ? ` <span class="muted">(${esc(p.fechas_sanciones)})</span>` : ""}` : "Ninguna en el registro"],
      ["Viajes 2021–2024", p.viajes_2021_2024 === "" ? "Sin datos" : `${num(p.viajes_2021_2024)}, ${num(p.viajes_con_observador_2021_2024)} con observador`],
    ];
    $("#v-registry").innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
  }

  // ---------- Ficha ----------

  function renderVessel(f, summary) {
    const p = f.datos;
    const year = Number(String(summary.temporada).match(/\d{4}/)?.[0]);
    document.title = `openMar · ${p.buque}`;
    $("#v-name").textContent = p.buque;
    $("#v-meta").textContent = [p.armador || "Sin armador en el registro", p.matricula && `Matrícula ${p.matricula}`]
      .filter(Boolean)
      .join(" · ");
    $("#v-status").innerHTML = statusText(p, summary.reglas);
    $("#v-status").className = `vhead__status vhead__status--${p.semaforo}`;
    // En verde la frase repetiría el estado: sólo se muestra si hubo apagones.
    $("#v-summary").textContent = Number(p.apagones) ? gapSummary(p, summary.reglas?.horas_minimas_apagon) : "";
    $("#v-summary").hidden = !Number(p.apagones);
    const map = $("#v-map");
    if (p.lat_zona_pesca === "") map.replaceWith(Object.assign(document.createElement("span"), { className: "muted", textContent: "Sin recorrido en Global Fishing Watch: no aparece en el mapa." }));
    else map.href = `mapa.html?buque=${encodeURIComponent(p.buque)}`;
    renderKpis(f);
    if (year) timeline(f, year);
    $("#v-series").innerHTML = seriesHTML(f.observador_por_anio);
    renderRegistry(p);
    renderTables(f, summary.reglas);
    $("#vessel").hidden = false;
  }

  // ---------- Índice ----------

  function renderDirectory(fichas, missing) {
    const all = Object.values(fichas.buques)
      .map((f) => f.datos)
      .sort((a, b) => ORDER[a.semaforo] - ORDER[b.semaforo] || Number(b.apagones) - Number(a.apagones) || a.buque.localeCompare(b.buque));
    if (missing) {
      $("#dir-notice").textContent = `No encontramos el buque "${missing}". Elegilo de la lista.`;
      $("#dir-notice").hidden = false;
    }
    const item = (p) => `<li><a class="dir-item" href="${fichaURL(p.buque)}">
      <span class="dot dot--${esc(p.semaforo)}" title="${esc(LABELS[p.semaforo])}"></span>
      <span class="dir-item__name">${esc(p.buque)}</span>
      <span class="dir-item__owner">${esc(p.armador || "Sin armador en el registro")}</span>
      <span class="dir-item__meta">${plural(p.mareas_temporada, "marea", "mareas")} · ${num(p.mareas_con_observador)} con observador · ${plural(p.apagones, "apagón", "apagones")}</span>
    </a></li>`;
    const render = (query) => {
      const shown = all.filter((p) => !query || `${p.buque} ${p.armador}`.toLowerCase().includes(query));
      $("#dir-list").innerHTML = shown.map(item).join("");
      $("#dir-count").textContent = `${plural(shown.length, "buque", "buques")}${query ? ` de ${num(all.length)}` : ""}. Primero los que tienen señales repetidas.`;
    };
    $("#dir-search").addEventListener("input", (e) => render(e.target.value.trim().toLowerCase()));
    render("");
    $("#directory").hidden = false;
  }

  async function main() {
    const [summary, fichas] = await Promise.all([loadJSON("data/resumen.json"), loadJSON("data/fichas.json")]);
    fillNumbers(summary);
    const wanted = new URLSearchParams(window.location.search).get("b");
    const byKey = wanted && Object.hasOwn(fichas.buques, wanted) ? fichas.buques[wanted] : null;
    const ficha = wanted && (byKey || Object.values(fichas.buques).find((f) => f.datos.buque === wanted));
    if (ficha) {
      renderVessel(ficha, summary);
      document.querySelector('.top__nav a[href="buque.html"]').setAttribute("aria-current", "true"); // dentro de la sección, no la página índice
    } else {
      renderDirectory(fichas, wanted);
    }
    $("#limits").innerHTML = limitItems(summary).map((i) => `<li>${i}</li>`).join("");
    $("#generated").textContent = `Datos generados el ${new Date(summary.generado).toLocaleDateString("es-AR")}`;
    document.querySelectorAll(".chapter").forEach((c) => c.classList.add("is-in"));
    $("#ficha").removeAttribute("aria-busy");
  }

  main().catch((error) => {
    const note = document.createElement("p");
    note.className = "error";
    note.setAttribute("role", "alert");
    note.textContent = `No se pudieron cargar los datos: ${error.message}.`;
    $("#ficha").prepend(note);
  });
})();
