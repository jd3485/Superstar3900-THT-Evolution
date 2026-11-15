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

## Decisione successiva

Se i 54 transienti confermano una dipendenza forte da Is/Cjo, è un ulteriore blocco al congelamento della catena diretta tank→diodo; va valutato stadio IF THT con livello controllato e impedenza d'ingresso appropriata, modello/temperatura del vero 1N4148 e carico audio completo. NON si può estendere il risultato a FM, SSB, AGC o TX. Nessuna modifica di schema MAIN/FRONT o PCB di prodotto. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
