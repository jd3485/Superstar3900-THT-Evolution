# V2.7 — sensibilità IF455→AM455 a impedenza sorgente e livello AM (DRAFT)

**13 novembre 2026 — PR in revisione, non integrata al momento della stesura.**

## Perché

Nelle PR #94 e #95 l'uscita della sorgente che alimenta il tank IF455 era **sempre 50 Ω**, scelta illustrativa e non misura del futuro amplificatore IF. Per non trasformare questa ipotesi in un requisito nascosto si verifica con **ngspice nativo** una matrice di sei condizioni:

| Parametro | Condizioni |
|---|---|
| Resistenza serie IF, puramente ipotetica | 50 Ω, 500 Ω, 5 kΩ |
| Ampiezza di picco del generatore AM | 0,5 V e 2,0 V |
| Segnale e circuito fissi | 455 kHz, AM 1 kHz al 50%, 1 mH, 82 pF + trim 30 pF |
| Comparatore | Riferimento diodo diretto con la STESSA resistenza serie |
| Modello | `DGENERIC` comportamentale — **NON** un modello OEM 1N4148 |

Lo script `03_Verifiche/V2.7/verify_if455_source_impedance_matrix_native.py` copia in una cartella temporanea il deck esistente `if455_am455_nonlinear_transient_generic.cir`, modifica soltanto RGEN, RREF e ampiezza della sorgente, ed esegue sei simulazioni transitorie. Per ogni caso acquisisce dai `.meas` nativi ngspice il segnale audio AF picco-picco filtrato e di riferimento, più un picco RF positivo. Richiede risultati finiti/positivi e che gli esiti non siano identici al variare dell'impedenza: **non stabilisce a priori una soglia di prestazione hardware inventata**.

## Limiti e criterio di decisione

La matrice non rappresenta l'impedenza complessa/frequenza-dipendente reale, i bias del driver, rumore, distorsione, guadagno, temperatura o Q dell'induttore; anche l'ipotesi Rcoil=16,5 Ω non è una perdita RF OEM. Il passaggio del test significa **solo** che gli scenari sono stati calcolati e riesaminabili; non seleziona alcun transistor/op-amp THT né rende fabbricabile il banco. Dati OEM, test di rumore e qualifica pinout/footprint rimangono prerequisiti.

**Gate:** FAST+FULL+required su HEAD definitivo, lettura del log con tutte le sei misure; merge tecnico solo con gate verdi. Uso del runner FULL esistente, nessun nuovo workflow Actions. Il master KiCad MAIN V2.6 non è modificato, entrambi i moduli KiCad V2.7 restano separati; nessun layout/DRC reale. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
