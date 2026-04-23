#!/usr/bin/env python3
"""
Lancia lo script bash iperf3 per 10 volte consecutive.
Uso: python3 run_iperf.py [percorso_script_bash] [config_file] [log_file]
"""
import subprocess
import sys
import os
from pathlib import Path

# ── Configurazione ─────────────────────────────────────────────────────────────
RUNS = 10
SCRIPT_DIR = Path(__file__).parent.resolve()
BASH_SCRIPT = Path(sys.argv[1]) if len(sys.argv) > 1 else SCRIPT_DIR / "run_iperf.sh"
CONFIG_FILE = sys.argv[2] if len(sys.argv) > 2 else None   # lascia il default bash se omesso
LOG_FILE    = sys.argv[3] if len(sys.argv) > 3 else None   # lascia il default bash se omesso

# ── Validazione ────────────────────────────────────────────────────────────────
if not BASH_SCRIPT.is_file():
    print(f"[ERRORE] Script bash non trovato: {BASH_SCRIPT}", file=sys.stderr)
    sys.exit(1)

# Assicura che lo script sia eseguibile
os.chmod(BASH_SCRIPT, 0o755)

# ── Costruzione comando base ───────────────────────────────────────────────────
base_cmd = ["bash", str(BASH_SCRIPT)]
if CONFIG_FILE:
    base_cmd.append(CONFIG_FILE)

# ── Esecuzione ─────────────────────────────────────────────────────────────────
print(f"Avvio di {RUNS} esecuzioni dello script: {BASH_SCRIPT}")
print(f"Comando base: {' '.join(base_cmd)}")
print("=" * 60)

success_count = 0
fail_count = 0

for i in range(1, RUNS + 1):
    # Determina il log file per questa run
    if LOG_FILE:
        log_path = Path(LOG_FILE)
        run_log = str(log_path.with_stem(f"{log_path.stem}_run{i}"))
    else:
        run_log = None

    print(f"\n[Run {i}/{RUNS}] Avvio...")
    if run_log:
        print(f"[Run {i}/{RUNS}] Log: {run_log}")
    print("-" * 40)

    # Costruisce il comando per questa specifica run
    cmd = base_cmd.copy()
    if run_log:
        cmd.append(run_log)

    try:
        result = subprocess.run(
            cmd,
            check=False,          # gestiamo noi il codice di uscita
        )
        if result.returncode == 0:
            success_count += 1
            print(f"[Run {i}/{RUNS}] ✓ Completata con successo (exit code 0)")
        else:
            fail_count += 1
            print(
                f"[Run {i}/{RUNS}] ✗ Terminata con errore "
                f"(exit code {result.returncode})",
                file=sys.stderr,
            )
    except FileNotFoundError as e:
        fail_count += 1
        print(f"[Run {i}/{RUNS}] ✗ Impossibile avviare il processo: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print(f"\n[INTERRUZIONE] Fermato dall'utente dopo {i - 1} run completate.")
        sys.exit(130)

# ── Riepilogo ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"Riepilogo: {success_count}/{RUNS} run riuscite, {fail_count}/{RUNS} fallite.")
sys.exit(0 if fail_count == 0 else 1)
