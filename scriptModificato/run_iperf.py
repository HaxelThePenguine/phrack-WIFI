#!/usr/bin/env python3
"""
Lancia lo script bash iperf3 per ogni elemento dell'array EXTRA_ARGS_LIST.
Per ogni parametro esegue RUNS run consecutive, salvando tutto sullo stesso file.
Uso: python3 run_iperf.py [percorso_script_bash] [config_file] [output_dir]
"""
import subprocess
import sys
import os
from pathlib import Path

# ── Array dei parametri extra da testare ──────────────────────────────────────
EXTRA_ARGS_LIST = [
    "-M 88",
    "-M 166",
    "-M 316",
    "-M 466",
    "-M 500",
    "-M 616",
    "-M 766",
    "-M 916",
    "-M 1066",
    "-M 1216",
    "-M 1366",
    "-M 1500",
]

RUNS = 10  # numero di registrazioni per ogni parametro

# ── Helper ─────────────────────────────────────────────────────────────────────
def _get_protocol(config_file):
    """Legge IPERF_PROTOCOL dal config .env e restituisce 'TCP' o 'UDP'."""
    try:
        with open(config_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("IPERF_PROTOCOL="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return val.upper()
    except OSError:
        pass
    return "TCP"

# ── Configurazione ─────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent.resolve()
BASH_SCRIPT = Path(sys.argv[1]) if len(sys.argv) > 1 else SCRIPT_DIR / "run_iperf.sh"
CONFIG_FILE = Path(sys.argv[2]) if len(sys.argv) > 2 else BASH_SCRIPT.parent.parent / "data_values" / "iperf.env"
OUTPUT_DIR  = Path(sys.argv[3]) if len(sys.argv) > 3 else BASH_SCRIPT.parent.parent / "data_values"

# ── Validazione ────────────────────────────────────────────────────────────────
if not BASH_SCRIPT.is_file():
    print(f"[ERRORE] Script bash non trovato: {BASH_SCRIPT}", file=sys.stderr)
    sys.exit(1)

if not CONFIG_FILE.is_file():
    print(f"[ERRORE] Config file non trovato: {CONFIG_FILE}", file=sys.stderr)
    sys.exit(1)

os.chmod(BASH_SCRIPT, 0o755)
OUTPUT_DIR = Path(OUTPUT_DIR).resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Protocollo (letto una volta sola dal config) ───────────────────────────────
PROTOCOL = _get_protocol(CONFIG_FILE)

# ── Costruzione comando base ───────────────────────────────────────────────────
base_cmd = ["bash", str(BASH_SCRIPT), str(CONFIG_FILE)]

# ── Esecuzione ─────────────────────────────────────────────────────────────────
total_params  = len(EXTRA_ARGS_LIST)
success_count = 0
fail_count    = 0

print(f"Avvio di {total_params} parametri × {RUNS} run = {total_params * RUNS} esecuzioni totali.")
print(f"Protocollo  : {PROTOCOL}")
print(f"Script bash : {BASH_SCRIPT}")
print(f"Config file : {CONFIG_FILE}")
print(f"Output dir  : {OUTPUT_DIR}")
print("=" * 60)

for idx, extra_args in enumerate(EXTRA_ARGS_LIST, start=1):
    suffix   = extra_args.replace(" ", "")
    log_name = f"{PROTOCOL}{suffix}.log"
    log_path = OUTPUT_DIR / log_name

    print(f"\n[Parametro {idx}/{total_params}] {extra_args!r}  →  {log_name}")
    print("=" * 60)

    for run in range(1, RUNS + 1):
        print(f"  [Run {run}/{RUNS}] avvio...")

        cmd = base_cmd.copy()
        cmd.append(str(log_path))  # $2 → LOG_FILE (stesso per tutte le run)
        cmd.append(extra_args)     # $3 → IPERF_EXTRA_ARGS override

        try:
            result = subprocess.run(cmd, check=False)
            if result.returncode == 0:
                success_count += 1
                print(f"  [Run {run}/{RUNS}] ✓ OK (exit code 0)")
            else:
                fail_count += 1
                print(f"  [Run {run}/{RUNS}] ✗ Errore (exit code {result.returncode})", file=sys.stderr)
        except FileNotFoundError as e:
            fail_count += 1
            print(f"  [Run {run}/{RUNS}] ✗ Impossibile avviare: {e}", file=sys.stderr)
        except KeyboardInterrupt:
            print(f"\n[INTERRUZIONE] Fermato dopo parametro {idx}, run {run - 1}.")
            sys.exit(130)

# ── Riepilogo ──────────────────────────────────────────────────────────────────
total = total_params * RUNS
print("\n" + "=" * 60)
print(f"Riepilogo: {success_count}/{total} run riuscite, {fail_count}/{total} fallite.")
sys.exit(0 if fail_count == 0 else 1)
