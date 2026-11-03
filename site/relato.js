/* openMar · portada: el relato con los números de resumen.json (ADR 0008 y 0010). */
(() => {
  "use strict";

  const { esc, num, plural, loadJSON, limitItems } = window.openMar;
  const $ = (selector) => document.querySelector(selector);
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const get = (data, path) => path.split(".").reduce((value, key) => (value == null ? value : value[key]), data);

  const FORMATS = {
    pct: (v) => `${num(v, 1)} %`,
    pct0: (v) => `${num(v)} %`,
    int: (v) => num(Math.round(Number(v))),
  };

  function withDerived(summary) {
    const season = summary.relato.temporada;
    return {
      ...summary,
      derivado: { pct_sin_observador: season.mareas ? (100 * season.mareas_sin_observador) / season.mareas : 0 },
    };
  }

  function fillNumbers(data) {
    document.querySelectorAll("[data-n]").forEach((el) => {
      const value = get(data, el.dataset.n);
      if (value == null) return;
      const format = FORMATS[el.dataset.fmt] || ((v) => num(v, 1));
      el.textContent = format(value);
    });
  }

  // Elige k posiciones de n con un sorteo fijo (siempre el mismo dibujo).
  // El orden de los cuadrados no representa nada: sólo importa cuántos se encienden.
  function spread(n, k) {
    let seed = 2025;
    const random = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
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

  function drawWaffle(season) {
    const lit = spread(season.mareas, season.mareas_con_observador);
    cells($("#waffle-mareas"), season.mareas, (i) => (lit.has(i) ? "cell cell--obs" : "cell"));
  }

  function drawFleet(history) {
    const observed = history.buques - history.buques_nunca_con_observador;
    cells($("#dots-buques"), history.buques, (i) => (i < observed ? "dot dot--obs" : "dot dot--never"));
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
  }

  function card(v) {
    const parts = [plural(v.en_marea_sin_observador, "en marea sin observador", "en mareas sin observador")];
    if (Number(v.fuera_de_marea)) parts.push(`${num(v.fuera_de_marea)} fuera de las fechas de marea`);
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
      { threshold: 0.25 },
    );
    chapters.forEach((c) => observer.observe(c));
  }

  async function main() {
    const summary = withDerived(await loadJSON("data/resumen.json"));
    fillNumbers(summary);
    drawWaffle(summary.relato.temporada);
    drawFleet(summary.relato.historico_2021_2024);
    drawGaps(summary.apagones_por_estado);
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
