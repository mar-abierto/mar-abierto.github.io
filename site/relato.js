/* openMar · portada: el relato con los números de resumen.json (ADR 0008 y 0010). */
(() => {
  "use strict";

  const { esc, num, plural, loadJSON, limitItems, fillNumbers, seriesHTML } = window.openMar;
  const $ = (selector) => document.querySelector(selector);
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function withDerived(summary) {
    const season = summary.relato.temporada;
    return {
      ...summary,
      derivado: {
        pct_sin_observador: season.mareas ? (100 * season.mareas_sin_observador) / season.mareas : 0,
        apagones_fuera: (summary.apagones_por_estado.fuera_de_marea || 0) + (summary.apagones_por_estado.sin_mareas_del_buque || 0),
      },
    };
  }

  // Elige k posiciones de n con un sorteo fijo (siempre el mismo dibujo).
  // El orden de los cuadrados no representa nada: sólo importa cuántos se encienden.
  function spread(n, k) {
    let seed = 2025; // mulberry32: entero de 32 bits, sin pérdida de precisión
    const random = () => {
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    const positions = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [positions[i], positions[j]] = [positions[j], positions[i]];
    }
    return new Set(positions.slice(0, k));
  }

  function cells(container, n, classFor) {
    const html = [];
    for (let i = 0; i < n; i++) html.push(`<span class="${classFor(i)}" style="--i:${i}"></span>`);
    container.innerHTML = html.join("");
  }

  function label(selector, text) {
    $(selector).setAttribute("aria-label", text);
  }

  function drawWaffle(season) {
    const lit = spread(season.mareas, season.mareas_con_observador);
    cells($("#waffle-mareas"), season.mareas, (i) => (lit.has(i) ? "cell cell--obs" : "cell"));
    label("#waffle-mareas", `${num(season.mareas)} mareas en la temporada; ${num(season.mareas_con_observador)} con observador a bordo.`);
  }

  function drawFleet(history) {
    const observed = history.buques - history.buques_nunca_con_observador;
    cells($("#dots-buques"), history.buques, (i) => (i < observed ? "dot dot--obs" : "dot dot--never"));
    label("#dots-buques", `${num(history.buques)} buques entre 2021 y 2024; ${num(history.buques_nunca_con_observador)} nunca llevaron observador.`);
  }

  function drawGaps(byStatus) {
    const order = [
      ["en_marea_sin_observador", "sin"],
      ["en_marea_con_observador", "con"],
      ["fuera_de_marea", "fuera"],
      ["sin_mareas_del_buque", "fuera"],
    ];
    const classes = order.flatMap(([key, cls]) => Array(byStatus[key] || 0).fill(`gap gap--${cls}`));
    cells($("#strip-apagones"), classes.length, (i) => classes[i]);
    const outside = (byStatus.fuera_de_marea || 0) + (byStatus.sin_mareas_del_buque || 0);
    label(
      "#strip-apagones",
      `${num(classes.length)} apagones de AIS: ${num(byStatus.en_marea_sin_observador)} en mareas sin observador, ` +
        `${num(byStatus.en_marea_con_observador)} con observador y ${num(outside)} fuera de las fechas de marea.`,
    );
  }

  function drawSeries(series) {
    $("#series-anual").innerHTML = seriesHTML(series);
  }

  function drawRates(rates) {
    const max = Math.max(rates.sin_observador, rates.con_observador, 0.01);
    const bar = (label, value, cls) => `
      <div class="bar">
        <span class="bar__label">${label}</span>
        <span class="bar__track"><span class="bar__fill bar__fill--${cls}" style="--w:${(100 * value) / max}%"></span></span>
        <span class="bar__value">${num(value, 2)}</span>
      </div>`;
    $("#bars-tasa").innerHTML = `
      <p class="bars__title">Apagones por marea</p>
      ${bar("Sin observador", rates.sin_observador, "sin")}
      ${bar("Con observador", rates.con_observador, "con")}`;
    label(
      "#bars-tasa",
      `Apagones por marea: ${num(rates.sin_observador, 2)} en mareas sin observador y ${num(rates.con_observador, 2)} en mareas con observador.`,
    );
  }

  function card(v) {
    // El detalle suma el total: sin observador, con observador y fuera de marea.
    const parts = [`${num(v.en_marea_sin_observador)} sin observador`];
    if (Number(v.en_marea_con_observador)) parts.push(`${num(v.en_marea_con_observador)} con observador`);
    if (Number(v.fuera_de_marea)) parts.push(`${num(v.fuera_de_marea)} fuera de marea`);
    const history =
      v.viajes_2021_2024 === "" ? "Sin datos de 2021–2024" : `Observador en ${num(v.viajes_con_observador_2021_2024)} de ${plural(v.viajes_2021_2024, "viaje", "viajes")}, 2021–2024`;
    return `<li class="card">
      <a href="mapa.html?buque=${encodeURIComponent(v.buque)}">
        <span class="card__name">${esc(v.buque)}</span>
        <span class="card__owner">${esc(v.armador || "Sin armador en el registro")}</span>
        <span class="card__big">${plural(v.apagones, "apagón", "apagones")}</span>
        <span class="card__detail">${esc(parts.join(" · "))}</span>
        <span class="card__history">${esc(history)}</span>
      </a>
    </li>`;
  }

  function renderStatic(summary) {
    $("#cards-rojo").innerHTML = summary.relato.senales_repetidas.map(card).join("");
    $("#limits").innerHTML = limitItems(summary).map((item) => `<li>${item}</li>`).join("");
    $("#sources").innerHTML = summary.fuentes
      .map((s) => `<li><a href="${esc(s.url)}" rel="noopener">${esc(s.nombre)}</a>: ${esc(s.aporta)}</li>`)
      .join("");
    const date = new Date(summary.generado);
    $("#generated").textContent = `Datos generados el ${date.toLocaleDateString("es-AR")}`;
  }

  function revealOnScroll() {
    const chapters = document.querySelectorAll(".chapter");
    if (reducedMotion || !("IntersectionObserver" in window)) {
      chapters.forEach((c) => c.classList.add("is-in"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries) =>
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          observer.unobserve(entry.target);
        }),
      // Umbral 0 con margen: los capítulos más altos que la pantalla también se revelan.
      { threshold: 0, rootMargin: "0px 0px -15% 0px" },
    );
    chapters.forEach((c) => observer.observe(c));
  }

  async function main() {
    const summary = withDerived(await loadJSON("data/resumen.json"));
    fillNumbers(summary);
    drawWaffle(summary.relato.temporada);
    drawFleet(summary.relato.historico_2021_2024);
    drawGaps(summary.apagones_por_estado);
    drawSeries(summary.relato.cobertura_por_anio);
    drawRates(summary.relato.apagones_por_marea);
    renderStatic(summary);
    document.documentElement.classList.add("is-ready");
    revealOnScroll();
    $("#relato").removeAttribute("aria-busy");
  }

  main().catch((error) => {
    document.documentElement.classList.add("is-ready");
    document.querySelectorAll(".chapter").forEach((c) => c.classList.add("is-in"));
    const note = document.createElement("p");
    note.className = "error";
    note.setAttribute("role", "alert");
    note.textContent = `No se pudieron cargar los datos: ${error.message}. Las cifras que ves pueden estar desactualizadas.`;
    $("#relato").prepend(note);
  });
})();
