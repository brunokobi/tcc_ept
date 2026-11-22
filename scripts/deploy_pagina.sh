#!/usr/bin/env bash
# Publishes the advisor's page at https://tccept.brunokobi.tech (vpsrafa, container tccept-web).
# Run after `python scripts/make_figures.py`. Needs SSH access to the VPS:
#   TCCEPT_SSH_KEY=<path to key> scripts/deploy_pagina.sh
# The page is public: it must stay descriptive (no outcome × Q/S/B before the OSF registration).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${TCCEPT_HOST:-ubuntu@130.61.140.66}"
KEY="${TCCEPT_SSH_KEY:?set TCCEPT_SSH_KEY to the VPS SSH key path}"
SSH_OPTS=(-i "$KEY" -o BatchMode=yes -o IdentitiesOnly=yes)
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT

# index.html is written for the Claude artifact host, which adds the document skeleton;
# a plain web server needs it in the file.
{
  printf '<!doctype html>\n<html lang="pt-BR">\n<head>\n'
  printf '<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<meta name="description" content="Aderência territorial dos cursos técnicos da Rede Federal: classificador CNAE → curso, índice Q, convergência T × O, poder e revisão sistemática (TCC, IFSul).">\n'
  printf '%s\n' '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 16 16%27%3E%3Crect width=%2716%27 height=%2716%27 rx=%273%27 fill=%27%231c5cab%27/%3E%3Cpath d=%27M3 12V8M6.5 12V5M10 12V7M13 12V3%27 stroke=%27white%27 stroke-width=%271.6%27 stroke-linecap=%27round%27/%3E%3C/svg%3E">'
  printf '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%%}[hidden]{display:none!important}</style>\n'
  printf '</head>\n<body>\n'
  grep -v '^<meta charset' "$ROOT/reports/pagina/index.html"
  printf '\n</body>\n</html>\n'
} > "$BUILD/index.html"
cp "$ROOT/reports/figures/pagina_dados.json" "$BUILD/dados.json"

scp -q "${SSH_OPTS[@]}" "$BUILD/index.html" "$BUILD/dados.json" "$HOST:/var/www/tccept/web/"
code=$(curl -s -o /dev/null -w '%{http_code}' https://tccept.brunokobi.tech/)
echo "https://tccept.brunokobi.tech -> HTTP $code"
