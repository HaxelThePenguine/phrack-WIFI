#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${1:-$SCRIPT_DIR/../data_values/iperf.env}"
LOG_FILE="${2:-$SCRIPT_DIR/../data_values/iperf-output.log}"
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Config file non trovato: $CONFIG_FILE" >&2
  exit 1
fi
# shellcheck disable=SC1090
source "$CONFIG_FILE"
if ! command -v iperf3 >/dev/null 2>&1; then
  echo "iperf3 non installato" >&2
  exit 1
fi
IPERF_HOST="${IPERF_HOST:-127.0.0.1}"
IPERF_PORT="${IPERF_PORT:-5201}"
IPERF_DURATION="${IPERF_DURATION:-10}"
IPERF_INTERVAL="${IPERF_INTERVAL:-1}"
IPERF_PROTOCOL="${IPERF_PROTOCOL:-tcp}"
IPERF_BANDWIDTH="${IPERF_BANDWIDTH:-10M}"
IPERF_EXTRA_ARGS="${IPERF_EXTRA_ARGS:-}"
cmd=(iperf3 -c "$IPERF_HOST" -p "$IPERF_PORT" -t "$IPERF_DURATION" -i "$IPERF_INTERVAL" -M 1500 --json)
if [[ "${IPERF_PROTOCOL,,}" == "udp" ]]; then
  cmd+=(-u -b "$IPERF_BANDWIDTH")
fi
if [[ -n "$IPERF_EXTRA_ARGS" ]]; then
  read -r -a extra_args <<<"$IPERF_EXTRA_ARGS"
  cmd+=("${extra_args[@]}")
fi
echo "Esecuzione: ${cmd[*]}"
"${cmd[@]}" 2>&1 | tee -a "$LOG_FILE"
