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
    en_marea_sin_observador: "durante un viaje sin observador",
    en_marea_con_observador: "durante un viaje con observador a bordo",
    fuera_de_marea: "fuera de las fechas de viaje",
    sin_mareas_del_buque: "en un barco sin viajes informados",
  };

  // Una sola cifra de cortes por barco en todas las páginas: el total de la temporada (`apagones`).
  // Al lado, siempre el mismo desglose con las mismas palabras; las partes suman el total.
  const CUT_PARTS = [
    ["en_marea_sin_observador", "en viajes sin observador"],
    ["en_marea_con_observador", "en viajes con observador"],
    ["fuera_de_marea", "fuera de las fechas de viaje"],
    ["sin_mareas_del_buque", "sin viajes informados"],
  ];

  function cutsBreakdown(p) {
    return CUT_PARTS.filter(([key]) => Number(p[key]) > 0).map(([key, text]) => `${num(p[key])} ${text}`);
  }

  // "18 cortes de señal: 13 en viajes sin observador, 5 fuera de las fechas de viaje".
  function cutsLabel(p) {
    if (!Number(p.apagones)) return "sin cortes de señal";
    const parts = cutsBreakdown(p);
    const main = plural(p.apagones, "corte de señal", "cortes de señal");
    return parts.length ? `${main}: ${parts.join(", ")}` : main;
  }

  // Resumen en una frase de los cortes de un buque (fila del gold).
  function gapSummary(p, minHours) {
    if (!Number(p.apagones)) {
      return "Global Fishing Watch no registró cortes de señal en la temporada.";
    }
    const parts = cutsBreakdown(p);
    let text = `${plural(p.apagones, "corte de señal", "cortes de señal")} de ${num(minHours)} horas o más (${num(p.horas_sin_ais)} horas sin señal en total)${parts.length ? `: ${parts.join(", ")}` : ""}.`;
    if (Number(p.franja_milla_200) > 0) {
      text += ` ${plural(p.franja_milla_200, "empieza o termina", "empiezan o terminan")} cerca de la milla 200.`;
    }
    return text;
  }

  // Reglas del semáforo en palabras, a partir del umbral que publica el pipeline.
  function ruleTexts(rules) {
    const threshold = Number(rules?.umbral_senales_repetidas);
    if (!threshold) return null;
    const below = threshold - 1;
    const isolated =
      below > 2 ? `De 1 a ${num(below)} cortes así, o cortes` : below === 2 ? "1 o 2 cortes así, o cortes" : below === 1 ? "1 corte así, o cortes" : "Cortes";
    return {
      rojo: `${num(threshold)} o más cortes de señal en viajes sin observador o fuera de las fechas de viaje.`,
      amarillo: `${isolated} sólo en viajes con observador.`,
      verde: "Global Fishing Watch no registró cortes de señal.",
    };
  }

  // Sólo links https: un dato mal cargado no puede inyectar javascript: u otro esquema.
  const safeURL = (url) => (/^https:\/\//.test(String(url || "")) ? String(url) : null);

  const fichaURL = (name) => `buque.html?b=${encodeURIComponent(name)}`;

  const get = (data, path) => path.split(".").reduce((value, key) => (value == null ? value : value[key]), data);

  // Fechas ISO (AAAA-MM-DD) como días del calendario, sin correrse por la zona horaria.
  const isoDate = (iso, withYear) =>
    new Date(`${String(iso).slice(0, 10)}T00:00:00Z`).toLocaleDateString("es-AR", {
      day: "numeric", month: "long", ...(withYear ? { year: "numeric" } : {}), timeZone: "UTC",
    });

  const FORMATS = {
    fecha: (v) => isoDate(v, true),
    fechaCorta: (v) => isoDate(v, false),
    pct: (v) => `${num(v, 1)} %`,
    pct0: (v) => `${num(v)} %`,
    int: (v) => num(Math.round(Number(v))),
    dec2: (v) => num(v, 2),
  };

  function fillNumbers(data) {
    document.querySelectorAll("[data-n]").forEach((el) => {
      const value = get(data, el.dataset.n);
      if (value == null) {
        // Una frase marcada como opcional desaparece entera en vez de decir "s/d" a mitad de oración.
        const optional = el.closest("[data-opcional]");
        if (optional) {
          optional.hidden = true;
          return;
        }
        el.textContent = "s/d";
        el.title = "Dato no disponible";
        return;
      }
      const format = FORMATS[el.dataset.fmt];
      if (!format && typeof value === "string") {
        el.textContent = value;
        return;
      }
      el.textContent = (format || ((v) => num(v, 1)))(value);
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

  // Hasta cuándo llegan los viajes y qué dijo la prensa: los dos datos vienen del pipeline.
  function tripsItem(summary) {
    const season = summary.relato?.temporada || {};
    const until = season.fecha_corte ? `, con viajes hasta el ${FORMATS.fecha(season.fecha_corte)}` : "";
    const press = summary.relato?.prensa;
    const pressURL = safeURL(press?.url);
    const medium = press && (pressURL ? `<a href="${esc(pressURL)}" rel="noopener">${esc(press.medio)}</a>` : esc(press.medio));
    const pressText = press
      ? ` ${medium} (${esc(press.fecha)}) citó ${plural(press.viajes_con_observador, "viaje", "viajes")} con observador; este informe marca ${num(season.mareas_con_observador)}. La diferencia está sin resolver hasta que se publique el informe final.`
      : "";
    return `<strong>Viajes y observadores:</strong> vienen del informe técnico 026/2025 del INIDEP${until}. Los viajes posteriores no están.${pressText}`;
  }

  function limitItems(summary) {
    const missing = summary.sin_posicion || [];
    const noOwner = summary.sin_armador || [];
    const band = summary.reglas?.franja_milla_200_km || [];
    return [
      `<strong>${plural(missing.length, "barco pescó", "barcos pescaron")}</strong> según los datos oficiales de viajes, pero no tienen recorrido en Global Fishing Watch: no aparecen en el mapa (la lista está en el panel del mapa).`,
      `<strong>${plural(noOwner.length, "barco no figura", "barcos no figuran")}</strong> en el Registro de Flota Pesquera${noOwner.length ? `: ${noOwner.map(esc).join(", ")}` : ""}.`,
      "<strong>Dueños reales:</strong> el registro dice qué empresa es titular del permiso de pesca (el armador). Quiénes son sus socios no está publicado.",
      "<strong>Escalas en puerto:</strong> las detecta Global Fishing Watch con la señal abierta de posición, sólo en barcos que la tienen encendida. Una escala no es necesariamente una descarga (puede ser reparación, abastecimiento o cambio de tripulación), y los transbordos en el mar no se cuentan.",
      "<strong>Señal privada:</strong> las posiciones que los barcos le mandan al Estado por su señal privada no son públicas. openMar sólo usa la señal abierta, la que cualquiera puede seguir en internet.",
      `<strong>Cortes de señal:</strong> sólo cuentan los de ${num(summary.reglas?.horas_minimas_apagon)} horas o más en zonas con buena recepción satelital (criterio de Global Fishing Watch). Los cortes más cortos no aparecen.`,
      tripsItem(summary),
      `<strong>Posición:</strong> es el punto típico donde pescó cada barco en 2025 (la mediana de sus eventos de pesca), no dónde está hoy. La franja de la milla 200 es aproximada (${num(band[0])} a ${num(band[1])} km de la costa).`,
      "<strong>Alcance:</strong> sólo barcos calamareros con bandera argentina en la temporada de calamar 2025. La flota extranjera de la milla 201 no está incluida.",
      "<strong>Islas Malvinas:</strong> el límite de las 200 millas es el que publica Marine Regions, que deja fuera el área en disputa alrededor de las islas. Usarlo no implica una posición de openMar sobre la soberanía: la Argentina reclama esas aguas.",
    ];
  }

  window.openMar = Object.freeze({
    esc, num, plural, get, loadJSON, limitItems, cutsBreakdown, cutsLabel, ruleTexts, safeURL, fillNumbers, seriesHTML, LABELS, GAP_STATUS,
    gapSummary, fichaURL,
  });
})();
