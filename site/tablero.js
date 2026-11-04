/* openMar · tablero: indicadores comparables entre empresas (ADR 0008 y 0010). */
(() => {
  "use strict";

  const { esc, num, loadJSON, limitItems, fillNumbers, seriesHTML } = window.openMar;
  const $ = (selector) => document.querySelector(selector);

  const GAP_PARTS = [
    { key: "en_marea_sin_observador", label: "en viajes sin observador", cls: "sin" },
    { key: "en_marea_con_observador", label: "en viajes con observador", cls: "con" },
    { key: "fuera_de_marea", label: "fuera de las fechas de viaje", cls: "fuera" },
    { key: "sin_mareas_del_buque", label: "en barcos sin viajes informados", cls: "fuera" },
  ];

  const COLUMNS = {
    armador: (o) => esc(o.armador),
    buques: (o) => num(o.buques),
    mareas: (o) => num(o.mareas),
    pct_con_observador: (o) =>
      `<span class="meter" style="--w:${Number(o.pct_con_observador)}%"></span>${num(o.pct_con_observador, 1)} %`,
    apagones_sin_observador: (o) => num(o.apagones_sin_observador),
    buques_senales_repetidas: (o) =>
      o.buques_senales_repetidas ? `<span class="pill pill--rojo">${num(o.buques_senales_repetidas)}</span>` : "0",
    escalas_exterior: (o) => num(o.escalas_exterior),
    captura_t: (o) => num(o.captura_t),
  };

  const NO_OWNER = "Sin armador en el registro"; // fila que agrupa buques sin armador, no es una empresa

  const state = { owners: [], key: "mareas", dir: "descending", query: "" };

  function drawStack(byStatus) {
    const parts = GAP_PARTS.filter((p) => byStatus[p.key]);
    const total = parts.reduce((sum, p) => sum + byStatus[p.key], 0) || 1;
    $("#stack-apagones").innerHTML = parts
      .map((p) => `<span class="stack__part stack__part--${p.cls}" style="--w:${Number((100 * byStatus[p.key]) / total)}%"></span>`)
      .join("");
    $("#stack-apagones").setAttribute("role", "img");
    $("#stack-apagones").setAttribute(
      "aria-label",
      parts.map((p) => `${num(byStatus[p.key])} ${p.label}`).join(", "),
    );
    $("#stack-legend").innerHTML = parts
      .map((p) => `<li><span class="sw sw--${p.cls}"></span><b>${num(byStatus[p.key])}</b> ${p.label}</li>`)
      .join("");
  }

  function drawPorts(ports) {
    const max = Math.max(...ports.map((p) => p.escalas), 1);
    $("#ports").innerHTML = ports
      .map((p) => {
        const abroad = p.pais !== "ARG";
        return `<li class="port${abroad ? " port--abroad" : ""}">
          <span class="port__name">${esc(p.puerto)}${abroad ? ` <em>(${esc(p.pais)})</em>` : ""}</span>
          <span class="port__track"><span class="port__fill" style="--w:${Number((100 * p.escalas) / max)}%"></span></span>
          <span class="port__value">${num(p.escalas)}<small> · ${num(p.buques)} ${p.buques === 1 ? "barco" : "barcos"}</small></span>
        </li>`;
      })
      .join("");
  }

  function sortedOwners() {
    const { key, dir, query } = state;
    const sign = dir === "ascending" ? 1 : -1;
    return state.owners
      .filter((o) => !query || o.armador.toLowerCase().includes(query))
      .sort(
        (a, b) =>
          // La fila de buques sin armador no es una empresa: siempre al final.
          (a.armador === NO_OWNER) - (b.armador === NO_OWNER) ||
          (typeof a[key] === "string" ? sign * a[key].localeCompare(b[key]) : sign * (a[key] - b[key]) || b.mareas - a.mareas),
      );
  }

  function renderTable() {
    const rows = sortedOwners();
    $("#owners-table tbody").innerHTML = rows
      .map(
        (o) => `<tr${o.armador === NO_OWNER ? ' class="is-aggregate"' : ""}>${Object.entries(COLUMNS)
          .map(([key, cell]) => (key === "armador" ? `<th scope="row">${cell(o)}</th>` : `<td>${cell(o)}</td>`))
          .join("")}</tr>`,
      )
      .join("");
    document.querySelectorAll("#owners-table thead th").forEach((th) => {
      if (th.dataset.key === state.key) th.setAttribute("aria-sort", state.dir);
      else th.removeAttribute("aria-sort");
    });
    const column = document.querySelector(`#owners-table thead th[data-key="${state.key}"]`)?.textContent.trim() || "";
    const order = state.dir === "ascending" ? "de menor a mayor" : "de mayor a menor";
    $("#owners-count").textContent = `${num(rows.length)} de ${num(state.owners.length)} filas, ordenadas por ${column.toLowerCase()} ${order}.`;
  }

  function bindTable() {
    document.querySelectorAll("#owners-table thead th").forEach((th) => {
      const label = th.textContent;
      th.innerHTML = `<button type="button">${esc(label)}<span class="sort" aria-hidden="true"></span></button>`;
      th.querySelector("button").addEventListener("click", () => {
        const key = th.dataset.key;
        const text = th.dataset.type === "text";
        state.dir = state.key === key ? (state.dir === "descending" ? "ascending" : "descending") : text ? "ascending" : "descending";
        state.key = key;
        renderTable();
      });
    });
    $("#owner-search").addEventListener("input", (e) => {
      state.query = e.target.value.trim().toLowerCase();
      renderTable();
    });
  }

  async function main() {
    const summary = await loadJSON("data/resumen.json");
    fillNumbers(summary);
    $("#series-anual").innerHTML = seriesHTML(summary.relato.cobertura_por_anio);
    drawStack(summary.apagones_por_estado);
    drawPorts(summary.tablero.puertos);
    state.owners = summary.tablero.por_armador;
    bindTable();
    renderTable();
    $("#limits").innerHTML = limitItems(summary).map((item) => `<li>${item}</li>`).join("");
    $("#generated").textContent = `Datos generados el ${new Date(summary.generado).toLocaleDateString("es-AR")}`;
    document.querySelectorAll(".chapter").forEach((c) => c.classList.add("is-in"));
    $("#tablero").removeAttribute("aria-busy");
  }

  main().catch((error) => {
    const note = document.createElement("p");
    note.className = "error";
    note.setAttribute("role", "alert");
    note.textContent = `No se pudieron cargar los datos: ${error.message}.`;
    $("#tablero").prepend(note);
  });
})();
