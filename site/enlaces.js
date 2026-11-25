/* Enlaces de lanzamiento: el ÚNICO lugar con los datos que el dueño todavía no decidió
   (aporte, correo, dominio). Ver docs/pendientes-lanzamiento.md.
   Un valor vacío ("") esconde el enlace en todas las páginas. */
(() => {
  "use strict";

  const ENLACES = Object.freeze({
    // A decidir: link de Cafecito.
    cafecito: "https://cafecito.app/openmar",
    // A decidir: correo público (sin "mailto:").
    correo: "", // PENDIENTE: p. ej. "contacto@dominio"
    // A decidir: dominio. También está en el <head> de las 4 páginas, robots.txt,
    // sitemap.xml y src/openmar/application/exportar.py (mismo texto, se reemplaza junto).
    sitio: "https://mar-abierto.github.io",
  });

  const REPO = "https://github.com/mar-abierto/mar-abierto.github.io";

  const hrefs = {
    cafecito: () => ENLACES.cafecito,
    correo: () => (ENLACES.correo ? `mailto:${ENLACES.correo}` : ""),
  };

  // Elementos con data-enlace: si es un <a> recibe el href; si no, su primer <a>.
  // Empiezan con `hidden` y sólo aparecen si el valor está definido.
  function fillLinks() {
    document.querySelectorAll("[data-enlace]").forEach((el) => {
      const make = hrefs[el.dataset.enlace];
      const href = make ? make() : "";
      if (!href) return;
      const link = el.tagName === "A" ? el : el.querySelector("a");
      if (!link) return;
      link.href = href;
      if (el.dataset.enlace === "cafecito") link.rel = "noopener";
      el.hidden = false;
    });
  }

  // En la ficha de un barco, los formularios de corrección y réplica llegan con el nombre puesto.
  function prefillVessel() {
    const vessel = new URLSearchParams(window.location.search).get("b");
    if (!vessel) return;
    document.querySelectorAll("a[data-issue]").forEach((link) => {
      const url = new URL(`${REPO}/issues/new`);
      url.searchParams.set("template", `${link.dataset.issue}.yml`);
      url.searchParams.set("barco", vessel.slice(0, 120));
      link.href = url.toString();
    });
  }

  async function fillCitation() {
    const target = document.getElementById("cita");
    if (!target) return;
    try {
      const response = await fetch("data/publicacion.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const pub = await response.json();
      const date = pub.generado ? new Date(pub.generado).toLocaleDateString("es-AR") : "";
      target.textContent =
        `openMar (versión ${pub.version}). La flota calamarera argentina, barco por barco. ` +
        `${pub.temporada}, datos generados el ${date}. ${ENLACES.sitio}. ` +
        "Fuentes: INIDEP, Global Fishing Watch y Registro de Flota Pesquera.";
    } catch (error) {
      target.textContent = "No se pudo cargar la fecha y la versión de los datos. Citá openMar, la fecha en que lo consultaste y las fuentes: INIDEP, Global Fishing Watch y Registro de Flota Pesquera.";
      console.error("openMar: no se pudo leer data/publicacion.json", error);
    }
  }

  fillLinks();
  prefillVessel();
  fillCitation();
})();
