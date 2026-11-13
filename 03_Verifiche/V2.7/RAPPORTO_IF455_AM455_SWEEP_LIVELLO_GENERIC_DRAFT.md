# V2.7 — sweep livello IF455 → demodulatore AM455 generico

**13 novembre 2026.** Revisione successiva alla PR #94, **solo studio di simulazione**. Il nuovo verificatore esegue realmente quattro transienti ngspice della stessa netlist filtro IF455 + DGENERIC + AM455 integrata, variando l'ampiezza di picco ideale della sorgente AM a **0,2 / 0,5 / 1,0 / 2,0 V**. Fissati modulazione 1kHz al 50%, impedenza sorgente ipotizzata 50Ω, 455kHz carrier, tank con 1mH, 82pF+30pF e Rcoil 16,5Ω assunta. L'uscita di ogni simulazione comprende AF picco-picco al rivelatore accoppiato e a quello diretto, entrambi modelli illustrativi.

**Finalità:** non estrapolare il valore misurato nella PR #94 (sorgente 2 V picco) a segnali più deboli. La risposta non lineare può cambiare in modo significativo con l'ampiezza; lo script confronta separatamente i risultati dei quattro transienti, verifica che siano numerici/positivi e nel *solo modello* che l'ampiezza AF cresca all'aumentare del segnale. Risultati numerici e PASS verificati nella CI FULL e riportati in calce. Se la condizione non è soddisfatta, la suite deve fallire e il modello va analizzato, non aggirato.

**Limiti obbligatori:** sorgente e livello IF reali, temperatura, dispersioni, modelli OEM e parametri PVT del diodo 1N4148 ancora sconosciuti. Non sono misurate sensibilità, rumore/SINAD, selettività, soglia di demodulazione reale, AGC, distorsione o risposta di un ricevitore operativo. La prova non autorizza integrazione del filtro/rivelatore o scelta definitiva di buffer. Riutilizzato l'esistente runner FULL KiCad9/ngspice, **zero nuovi workflow GitHub Actions**. Master V2.6 non modificato, PCB fisiche assenti, **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

## Risultati ngspice realmente eseguiti — PR #95 MERGED

La [PR #95](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/95) è stata integrata con commit `bc7eebff2b11103b1daa372780afc8fed3974929`. GitHub Actions [run #43456512235](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43456512235) ha completato **3/3 SUCCESS** (FAST, FULL, required) sul commit `4bcbb33c0437f288c1e246f6b3f23ab731bd407e`; 111 comandi legacy FULL eseguiti. Il log contiene `PASS_NGSPICE_IF455_AM455_GENERIC_DIODE_INPUT_LEVEL_SWEEP_NOT_OEM_NO_FAB_NO_TX`.

| Sorgente AM, V picco | AF pp filtro+diodo (V) | AF pp riferimento diretto (V) | Rapporto dei due modelli |
|---:|---:|---:|---:|
| 0,2 | 0,001312202 | 0,006729355 | 19,50% |
| 0,5 | 0,011504869 | 0,23901695 | 4,81% |
| 1,0 | 0,06547246 | 0,8542723 | 7,66% |
| 2,0 | 0,17444891 | 2,0377306 | 8,56% |

**Interpretazione prudente:** i quattro casi mostrano una risposta non lineare e non proporzionale; il rapporto filtrato/diretto non è monotono (19,50→4,81→7,66→8,56%). Il valore percentuale isolato a 0,2V **non** è una prestazione migliore del ricevitore, ma deriva anche da una risposta di riferimento prossima alla soglia del diodo nel modello. Senza rumore, distorsione, driver IF reale, dati OEM/PVT e prove di banco **non è possibile dedurre sensibilità minima, selettività o progetto definitivo**. Non inserire questa sezione nel master PCB come stage qualificato.
