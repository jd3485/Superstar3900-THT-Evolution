# FRONT J1902: envelope termico resistivo con guasto di sovratensione esterna

Data: 16 novembre 2026. **Analisi di scenario, non qualifica hardware.** Il master KiCad9 FRONT collega J1902/1 al post-mute `AMP_INPUT_MUTED` (R1902/2, R1901/1), R1901=100 kΩ a `AF_GND`, e R1902=1 kΩ da post-mute a COM K1901/1. Quando il relè non è alimentato e NC è chiuso, COM→K1901/2→AF_GND è l'altro percorso di scarica. Il connettore non è meccanicamente qualificato; nessuna tensione massima di guasto cavo è stata approvata.

Se un guasto esterno **forza** J1902/1 a +V rispetto ad AF_GND intatta, con NC ideale chiuso, R1902 subisce V²/R e R1901 lo stesso V²/R in parallelo. I casi di screening adottano resistori a -5% rispetto al valore nominale, **senza fingere che esistano MPN o potenze qualificate**.

| Guasto forzato V | R1902 1 kΩ a -5%, W | R1901 100 kΩ a -5%, W |
|---|---:|---:|
| 6 V | 0,0379 | 0,000379 |
| 12 V | 0,1516 | 0,001516 |
| 15 V | 0,2368 | 0,002368 |
| 20 V | 0,4211 | 0,004211 |
| 24 V | 0,6063 | 0,006063 |
| 30 V | 0,9474 | 0,009474 |

Come mera soglia matematica, con una potenza ipotetica 0,25 W si ottiene V≤15,41 V; con 0,10 W deratati V≤9,75 V. **Nessuno dei due valori è un limite di prodotto:** mancano curva di derating reale, durata del guasto, temperatura e dinamica del contatto. Quando NC è aperto, il ramo serie R1902 non è obbligatoriamente chiuso su massa; non si può applicare automaticamente la potenza NC-chiuso. Un guasto AF_GND aperta richiede un modello di massa flottante diverso.

Il verificatore nativo `verify_front_mute_j1902_overvoltage_resistor_screen_native.py` controlla le reti di MAIN LM386, relè FRONT, master a 22 reti e valori simbolici prima dei calcoli; è aggiunto a `ci/full_regressions.py`. Il modello non prova sicurezza hardware o fail-safe. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
