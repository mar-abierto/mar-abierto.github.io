#!/usr/bin/env bash
# Chequeo antes de abrir el sitio al público: falla si quedan valores provisorios
# o marcas de borrador. Ver docs/pendientes-lanzamiento.md y docs/despliegue.md.
set -u
cd "$(dirname "$0")/.."
fallas=0
revisar() { # $1 descripción, $2 patrón
  if grep -rnI --exclude-dir=data --exclude-dir=vendor -e "$2" site src/openmar >/dev/null; then
    echo "FALTA: $1"; grep -rnI --exclude-dir=data --exclude-dir=vendor -e "$2" site src/openmar | sed 's/^/   /'
    fallas=1
  fi
}
revisar "dominio provisorio" "openmar.example"
revisar "valores PENDIENTE" "PENDIENTE"
revisar "noindex en páginas o cabeceras" "noindex"
revisar "cartel de borrador" "top__draft\""
grep -q 'Disallow: /$' site/robots.txt && { echo "FALTA: robots.txt sigue cerrado"; fallas=1; }
grep -q 'cafecito: ""' site/enlaces.js && { echo "FALTA: link de Cafecito vacío"; fallas=1; }
grep -q 'correo: ""' site/enlaces.js && { echo "FALTA: correo público vacío"; fallas=1; }
[ "$fallas" = 0 ] && echo "Listo para abrir." || exit 1
