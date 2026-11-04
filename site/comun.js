/* openMar · funciones compartidas por la portada, el tablero y el mapa. */
(() => {
  "use strict";

  const esc = (value) =>
    String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const num = (value, digits = 0) =>
    Number(value || 0).toLocaleString("es-AR", { maximumFractionDigits: digits, minimumFractionDigits: 0 });
  const plural = (n, one, many) => `${num(n)} ${Number(n) === 1 ? one : many}`;

  const LABELS = { rojo: "Señales repetidas", amarillo: "Señales aisladas", verde: "Sin señales" };
  const GAP_STATUS = {
    en_marea_sin_observador: "en marea sin observador",
    en_marea_con_observador: "en marea con observador a bordo",
    fuera_de_marea: "fuera de las fechas de marea",
    sin_mareas_del_buque: "sin mareas informadas",
  };

  // Resumen en una frase de los apagones de un buque (fila del gold).
  function gapSummary(p, minHours) {
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
    let text = `${plural(p.apagones, "apagón", "apagones")} de AIS de ${num(minHours)} h o más (${num(p.horas_sin_ais)} h sin señal en total): ${parts.join(", ")}.`;
    if (Number(p.franja_milla_200) > 0) {
      text += ` ${plural(p.franja_milla_200, "empieza o termina", "empiezan o terminan")} cerca de la milla 200.`;
    }
    return text;
  }

  const fichaURL = (name) => `buque.html?b=${encodeURIComponent(name)}`;

  const get = (data, path) => path.split(".").reduce((value, key) => (value == null ? value : value[key]), data);

  const FORMATS = {
    pct: (v) => `${num(v, 1)} %`,
    pct0: (v) => `${num(v)} %`,
    int: (v) => num(Math.round(Number(v))),
    dec2: (v) => num(v, 2),
  };

  function fillNumbers(data) {
    document.querySelectorAll("[data-n]").forEach((el) => {
      const value = get(data, el.dataset.n);
      if (value == null) {
        el.textContent = "s/d";
        el.title = "Dato no disponible";
        return;
      }
      if (typeof value === "string") {
        el.textContent = value;
        return;
      }
      const format = FORMATS[el.dataset.fmt] || ((v) => num(v, 1));
      el.textContent = format(value);
    });
  }

  // Barras verticales en escala real: la barra entera es el 100 % de los viajes de ese año.
  function seriesHTML(series) {
    return series
      .map(
        (y) => `<li class="series__year">
          <span class="series__track"><span class="series__fill" style="--h:${Number(y.pct_con_observador)}%"></span></span>
          <span class="series__pct">${num(y.pct_con_observador, 1)} %</span>
          <span class="series__label">${esc(y.anio)}</span>
          <span class="sr-only">: ${num(y.con_observador)} de ${num(y.viajes)} viajes con observador</span>
        </li>`,
      )
      .join("");
  }

  async function loadJSON(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`No se pudo leer ${path} (${response.status})`);
    return response.json();
  }

  function limitItems(summary) {
    const missing = summary.sin_posicion || [];
    const noOwner = summary.sin_armador || [];
    return [
      `<strong>${plural(missing.length, "buque pescó", "buques pescaron")}</strong> según el INIDEP pero no tienen recorrido en Global Fishing Watch: no aparecen en el mapa (la lista está en el panel del mapa).`,
      `<strong>${plural(noOwner.length, "buque no figura", "buques no figuran")}</strong> en el Registro de Flota Pesquera${noOwner.length ? `: ${noOwner.map(esc).join(", ")}` : ""}.`,
      "<strong>Dueños reales:</strong> el armador es la empresa titular del permiso. Quiénes son sus socios no está publicado.",
      "<strong>Escalas en puerto:</strong> las detecta Global Fishing Watch por AIS, sólo en buques que lo tienen encendido. Una escala no es necesariamente una descarga (puede ser reparación, abastecimiento o cambio de tripulación), y los transbordos en el mar no se cuentan.",
      "<strong>VMS:</strong> las posiciones que los buques reportan a las autoridades no son públicas. Este mapa sólo usa AIS.",
      `<strong>Apagones:</strong> sólo cortes de ${num(summary.reglas?.horas_minimas_apagon)} horas o más en zonas con buena recepción satelital (criterio de Global Fishing Watch). Los cortes más cortos no aparecen.`,
      `<strong>Mareas y observadores:</strong> vienen del informe técnico 026/2025 del INIDEP, con datos hasta el 5 de junio de 2025. Las mareas posteriores no están. La prensa citó 9 mareas con observador; este informe marca ${num(summary.relato?.temporada?.mareas_con_observador)}. La diferencia está sin resolver hasta que se publique el informe final.`,
      "<strong>Posición:</strong> es la mediana de los eventos de pesca de 2025, no dónde está hoy el buque. La franja de la milla 200 es aproximada (300 a 450 km de la costa).",
      "<strong>Alcance:</strong> sólo poteros con bandera argentina en la temporada de calamar 2025. La flota extranjera de la milla 201 no está incluida.",
      "<strong>Islas Malvinas:</strong> el límite de la ZEE es el que publica Marine Regions, que deja fuera el área en disputa alrededor de las islas. No es una posición de openMar sobre la soberanía: la Argentina reclama esas aguas.",
    ];
  }

  window.openMar = Object.freeze({
    esc, num, plural, get, loadJSON, limitItems, fillNumbers, seriesHTML, LABELS, GAP_STATUS, gapSummary, fichaURL,
  });
})();
