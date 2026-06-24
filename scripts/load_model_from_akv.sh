#!/usr/bin/env bash
set -euo pipefail

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
  exit 2
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

export AZURE_OPENAI_BASE_URL="${AZURE_OPENAI_BASE_URL:-$(get_secret "$AZURE_OPENAI_BASE_URL_SECRET_NAME")}" 
export AZURE_OPENAI_MODEL="${AZURE_OPENAI_MODEL:-$(get_secret "$AZURE_OPENAI_MODEL_SECRET_NAME")}" 
export AZURE_OPENAI_CHAT_COMPLETION_MODEL="${AZURE_OPENAI_CHAT_COMPLETION_MODEL:-$AZURE_OPENAI_MODEL}"
export AZURE_OPENAI_API_KEY="${AZURE_OPENAI_API_KEY:-$(get_secret "$AZURE_OPENAI_API_KEY_SECRET_NAME")}" 
export AZURE_OPENAI_MAX_COMPLETION_TOKENS="${AZURE_OPENAI_MAX_COMPLETION_TOKENS:-$(get_secret "$AZURE_OPENAI_MAX_COMPLETION_TOKENS_SECRET_NAME")}" 

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
  exec "$@"
fi
