# Rapporto tecnico V0.9 — PDout three-state e filtro PLL passivo

**Stato:** revisione RX-only THT cumulativa, nuovo sottoblocco PDout V0.9 su branch; **NO FAB / NO TX**.

## Risultato centrale

La vecchia interpretazione di `PDout` come sorgente analogica già filtrata era incompleta. U401 ML145151YP **pin 4** emette impulsi positivi o negativi ed è ad **alta impedenza** quando la fase e la frequenza coincidono, secondo datasheet Lansdale/Motorola. `PD_FILTER` V0.8 non viene creato dal MCU: serve un filtro analogico vero che accumuli il segnale di errore prima del driver LM358.

## Numeri: veri transitori ngspice su SURROGATO (non vendor)

Workflow [42851241908](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42851241908) **SUCCESS**. `PDOUT_TRISTATE_SURROGATE_V0.9.cir`: due switch ideali +5/0V e Hi-Z, R filtro10k o47k, C1µF, R leakage100M esclusivamente numerico, partenza forzata a2,5V, impulsi1ms ogni10ms (NON5kHz).

| Stato di prova | R901 | PD_FILTER prima impulso | PD_FILTER dopo 1° | finale 29ms |
|---|---:|---:|---:|---:|
| UP | 10k | 2,499963 | 2,736908 | 3,145000 |
| DOWN | 10k | 2,499963 | 2,262904 | 1,853720 |
| HOLD/Hi-Z | 10k | 2,499963 | 2,499900 | 2,499275 |
| UP | 47k | 2,499963 | 2,552527 | 2,653848 |
| DOWN | 47k | 2,499963 | 2,447276 | 2,344741 |
| HOLD/Hi-Z | 47k | 2,499963 | 2,499900 | 2,499275 |

**PASS:** la sorgente di prova fa salire la tensione con impulsi UP, scendere con DOWN, mantiene quasi costante in Hi-Z. **NOT QUALIFIED:** non dice se il PLL realmente aggancia, se fase corretta, ripple/spurie, mantenimento nel tempo e sotto input bias reali, oppure se passivi scelti sono stabili in anello.

## Analisi complementare
- R10k/C1µF: taglio15,915Hz, tau10ms, attenuazione ideale primo polo5kHz≈−49,94dB;
- R47k/C1µF: taglio3,386Hz, tau47ms, attenuazione ideale5kHz≈−63,39dB.
- `100MΩ` di perdita è un valore **artificiale e NON una referenza fisica**; simulazione C/R non include correnti di bias LM358 né leakage PCB.
- La pendenza media VCO dai cinque punti non dà K_vco locale né coefficiente di fase/charge; phase margin PLL **NOT_RUN**.

## Documenti e gate

`01_Specifiche/V0.9/PDOUT_TRISTATE_FILTRO_V0.9.md`, `02_Piano_Frequenze/V0.9/pll_tristate_budget_v09.py`, `04_KiCad/V0.9/PLL_PDOUT_FILTRI_CANDIDATI_V0.9.csv`, `07_Componenti/BOM_FILTRO_PLL_V0.9.csv`, deck e runner SPICE.

**Non eseguiti:** modelli vendor ML145151/LM358, PLL closed loop, KiCad ERC/DRC nativi, Bode e KiCad PCB, prove di laboratorio EMC e hardware. Non fabbricare PCBWay e non abilitare TX. Prossimo rilascio: compensazione reale e CAD.

Fonte primaria: https://lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf
