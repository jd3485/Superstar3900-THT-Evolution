# V2.7 — screening transitorio del diodo AM455 con parametri sintetici Is e Cjo, carico FRONT/LM386

**15 novembre 2026 — simulazioni ngspice, non modelli OEM.** Prosecuzione della PR #235, che dimostra nel modello generico la forte variazione del segnale AF dopo l'aggiunta del potenziometro e del carico all'ingresso LM386. Il nuovo controllo non seleziona un diodo definitivo; confronta modelli plausibili *solo per sondare la sensibilità numerica alle assunzioni*, senza pretendere che siano corner garantiti della Vishay 1N4148.

## Configurazione e gate

Stesso deck `spice/if455_am455_front_lm386_loaded_generic_diode.cir` e verifica con netlist KiCad9 dei valori C1502, RV1301, C1201, R1201 e pin3 LM386. Il test `verify_if455_am455_loaded_generic_diode_parameter_screen.py` conserva `N=1.9, Rs=0.6Ω, Vj=0.75V, Tt=4ns` generici e varia:
- corrente inversa del modello `Is`: **0,25 nA / 2,5 nA / 25 nA**, scenari sintetici, NON intervalli OEM qualificati;
- capacità di giunzione `Cjo`: **2 / 4 / 8 pF**, valori sintetici;
- picco della sorgente a 455 kHz: **0,5 / 2,0 V**, 50Ω ideali;
- posizione potenziometro: **10 / 50 / 90%**.

Totale **3×3×2×3=54 transienti distinti**, finestra di misura 8–11ms dopo transitorio 12ms, passo massimo 0,2µs. Doppia catena indipendente con sorgenti e tank identici: terminazione R1502=100k da sola vs. rivelatore caricato da R1502+RV1301 e C1201/R1201/Rin=50k tipico. Registrati valori pp al pin3 e al riferimento 100k, rapporto di attenuazione, RF positiva e intervalli minimo/massimo per ciascuna combinazione di livello e wiper. Fallimento CI su valori non finiti, nulli, su presunto guadagno della rete passiva rispetto al suo nodo AF e su mancate netlist KiCad.

**Non forzare in questo test** un limite artificiale di THD, sensibilità minima, rumore o intervallo di ricezione. Gli estremi Is/Cjo non sono affermazioni su datasheet né sostituiscono la misura del filtro/sorgente IF, un modello OEM validato o la progettazione delle masse/cavi.

## Evidenze realmente verificate da GitHub Actions

**[PR #236](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/236) MERGED** nel commit `65cbfe021aa8c36a69f6d8aea16612631bbcfca2`, HEAD finale `508a1969f6fafd6f3fac8fa1232d3328cc9067e5`. [Actions #43702519024](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43702519024): FAST/FULL/required **3/3 SUCCESS**, 111 comandi legacy, log `PASS_NGSPICE_54_IF455_AM455_FRONT_LOADED_SYNTHETIC_DIODE_IS_CJO_CORNER_TRANSIENTS_NOT_OEM_NO_FAB_NO_TX`.

Intervalli effettivamente ottenuti sul modello, in Vpp al pin3 LM386 simulato resistivo (Rin=50k tipica), al variare di nove accoppiamenti Is/Cjo sintetici:

| Sorgente 455 kHz, picco | Volume 10% | Volume 50% | Volume 90% |
|---|---|---|---|
| 0,5 V | 0,223–0,743 mVpp (3,33×) | 1,076–3,544 mVpp (3,29×) | 1,934–6,216 mVpp (3,21×) |
| 2,0 V | 3,551–4,454 mVpp (1,25×) | 16,965–21,192 mVpp (1,25×) | 29,915–36,817 mVpp (1,23×) |

**Interpretazione:** nello scenario numerico a minor segnale, l'incertezza sui parametri genericamente ipotizzati del diodo produce un intervallo relativo maggiore che a 2 Vpicco. Non confondere tale rapporto con una tolleranza OEM della 1N4148 o sensibilità del ricevitore. Qualifica datasheet/misure rimane indispensabile.

## Decisione successiva

Se i 54 transienti confermano una dipendenza forte da Is/Cjo, è un ulteriore blocco al congelamento della catena diretta tank→diodo; va valutato stadio IF THT con livello controllato e impedenza d'ingresso appropriata, modello/temperatura del vero 1N4148 e carico audio completo. NON si può estendere il risultato a FM, SSB, AGC o TX. Nessuna modifica di schema MAIN/FRONT o PCB di prodotto. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
