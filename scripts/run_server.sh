#!/usr/bin/env bash
set -euo pipefail

# Arranca la demo local. Carga .env si existe; para Key Vault usa primero:
# source scripts/load_model_from_akv.sh
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

python -m microharness.server
