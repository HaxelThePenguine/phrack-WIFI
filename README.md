# phrack-WIFI

## Struttura per iperf

Sono state aggiunte due cartelle:

- `script/`: contiene gli script per eseguire `iperf3`
- `data_values/`: contiene i valori/configurazioni dati usati dagli script

### Esecuzione

1. Configura i valori in `data_values/iperf.env`
2. Esegui:

```bash
bash script/run_iperf.sh
```

Lo script legge la configurazione, avvia `iperf3` e gestisce l'output tramite pipe (`tee` + `awk`) per poterlo elaborare in tempo reale.
