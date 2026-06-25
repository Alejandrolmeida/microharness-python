#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  MICROHARNESS_AKV_SOURCED=1
else
  MICROHARNESS_AKV_SOURCED=0
  set -euo pipefail
fi

finish() {
  local status="$1"
  if [[ "$MICROHARNESS_AKV_SOURCED" == "1" ]]; then
    return "$status"
  fi
  exit "$status"
}

# Load the same Azurebrains custom model configuration used by local Copilot setup.
# Only local config and Key Vault secret names are read here; secret values are exported
# to the current child process and must never be committed.

CONFIG_FILE="${COPILOT_AZUREBRAINS_ENV_FILE:-$HOME/.config/azurebrains/copilot-azurebrains.env}"
if [[ -f "$CONFIG_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$CONFIG_FILE"
  set +a
fi

KEYVAULT_NAME="${AZURE_KEYVAULT_NAME:-${KEYVAULT_NAME:-}}"
KEYVAULT_SUBSCRIPTION_ID="${AZURE_KEYVAULT_SUBSCRIPTION_ID:-${KEYVAULT_SUBSCRIPTION_ID:-}}"

AZURE_OPENAI_BASE_URL_SECRET_NAME="${AZURE_OPENAI_BASE_URL_SECRET_NAME:-azure-openai-base-url}"
AZURE_OPENAI_MODEL_SECRET_NAME="${AZURE_OPENAI_MODEL_SECRET_NAME:-azure-openai-model}"
AZURE_OPENAI_API_KEY_SECRET_NAME="${AZURE_OPENAI_API_KEY_SECRET_NAME:-azure-openai-api-key}"
AZURE_OPENAI_MAX_COMPLETION_TOKENS_SECRET_NAME="${AZURE_OPENAI_MAX_COMPLETION_TOKENS_SECRET_NAME:-azure-openai-max-completion-tokens}"

if [[ -z "$KEYVAULT_NAME" ]]; then
  cat >&2 <<'EOF'
ERROR: falta AZURE_KEYVAULT_NAME.

Configura localmente ~/.config/azurebrains/copilot-azurebrains.env o exporta:
- AZURE_KEYVAULT_NAME
- AZURE_KEYVAULT_SUBSCRIPTION_ID (opcional)

El Key Vault debe contener estos secretos o los nombres que indiques con *_SECRET_NAME:
- azure-openai-base-url
- azure-openai-model
- azure-openai-api-key
- azure-openai-max-completion-tokens
EOF
  finish 2
  return $?
fi

get_secret() {
  local secret_name="$1"
  local -a subscription_args=()

  if [[ -n "$KEYVAULT_SUBSCRIPTION_ID" ]]; then
    subscription_args=(--subscription "$KEYVAULT_SUBSCRIPTION_ID")
  fi

  az keyvault secret show \
    "${subscription_args[@]}" \
    --vault-name "$KEYVAULT_NAME" \
    --name "$secret_name" \
    --query value -o tsv
}

load_secret_env() {
  local env_name="$1"
  local secret_name="$2"
  local secret_value=""

  if [[ -n "${!env_name:-}" ]]; then
    export "$env_name=${!env_name}"
    return 0
  fi

  if ! secret_value="$(get_secret "$secret_name")"; then
    echo "ERROR: no se pudo leer el secreto '$secret_name' desde Key Vault '$KEYVAULT_NAME'." >&2
    return 1
  fi

  export "$env_name=$secret_value"
}

if ! load_secret_env AZURE_OPENAI_BASE_URL "$AZURE_OPENAI_BASE_URL_SECRET_NAME"; then
  finish 1
  return $?
fi

if ! load_secret_env AZURE_OPENAI_MODEL "$AZURE_OPENAI_MODEL_SECRET_NAME"; then
  finish 1
  return $?
fi

export AZURE_OPENAI_CHAT_COMPLETION_MODEL="${AZURE_OPENAI_CHAT_COMPLETION_MODEL:-$AZURE_OPENAI_MODEL}"

if ! load_secret_env AZURE_OPENAI_API_KEY "$AZURE_OPENAI_API_KEY_SECRET_NAME"; then
  finish 1
  return $?
fi

if ! load_secret_env AZURE_OPENAI_MAX_COMPLETION_TOKENS "$AZURE_OPENAI_MAX_COMPLETION_TOKENS_SECRET_NAME"; then
  finish 1
  return $?
fi

if [[ $# -eq 0 ]]; then
  cat <<EOF
Config cargada para MicroHarness:
- AZURE_OPENAI_BASE_URL: ${AZURE_OPENAI_BASE_URL%/openai/v1}/openai/v1
- AZURE_OPENAI_CHAT_COMPLETION_MODEL: $AZURE_OPENAI_CHAT_COMPLETION_MODEL
- AZURE_OPENAI_API_KEY: <oculta>
- AZURE_OPENAI_MAX_COMPLETION_TOKENS: $AZURE_OPENAI_MAX_COMPLETION_TOKENS

Ejemplo:
  source scripts/load_model_from_akv.sh
  python -m microharness.server
EOF
else
  if [[ "$MICROHARNESS_AKV_SOURCED" == "1" ]]; then
    if "$@"; then
      finish 0
    else
      finish $?
    fi
    return $?
  fi
  exec "$@"
fi
