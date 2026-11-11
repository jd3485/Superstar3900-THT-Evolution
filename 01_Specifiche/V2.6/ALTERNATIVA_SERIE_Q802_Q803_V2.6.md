# V2.6 — Analisi di interblocco OVP/UVLO con due 2N3904 in serie (CANDIDATA)

**Precisazione successiva alla PR #31 (audit D803):** D803 onsemi 1N4742A 12 V / 1 W è già collegato al gate/source Q801 in V2.6. L'avvertimento teorico di |VGS| >20 V a VIN 48 V per il solo partitore R1008/R1009 corrisponde al **guasto D803 aperto**. L'audit nativo [43081722718](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43081722718) verifica l'orientamento reale del diodo. Il suo comportamento reale a pochi mA e i transitori restano non qualificati. Consultare `03_Verifiche/V2.6/RAPPORTO_D803_GATE_CLAMP.md`. **Non dedurre un via libera a 48 V.**

La V2.5 collega entrambe le uscite LM393 su CMP_OUT e condivide la retroazione OVP R1005. La prima alternativa V2.6 D807 Schottky rischia di portare il livello LOW troppo in alto per la base Q802: **non adottarla senza verifica.**

## Seconda topologia da valutare nel prossimo schema KiCad
- U801/1 (OVP) rimane CMP_OUT e comanda Q802 attraverso R1007=22k, R1010=100k verso massa.
- U801/7 (UVLO) passa su UVLO_OC con R1014 pull-up 4k7 VREF2V5 e R1015 feedback UVLO 470k verso UVLO_SENSE; Q803 2N3904 THT pilotato tramite R1016 22k e R1017 100k a GND, entrambi **candidati**.
- Q802 collettore resta GATE_SINK; **Q802 emettitore → Q803 collettore, Q803 emettitore → GND**. La conduzione del gate sink richiede il consenso di entrambi i comparatori, indipendenti. Nessun diodo D807 in serie.

## Verifica preliminare eseguita localmente
Script Python `03_Verifiche/V2.6/screen_series_interlock_v26.py` (nessun GitHub Actions necessario per il calcolo). Tabella di verità AND verificata. Con R1008=47k, R1009=10k, VIN=13,8V, due VCEsat ipotizzate in totale 0,2..0,6V, corrente gate-sink circa **0,232..0,239mA**. Ipotizzando Q802 VBE=0,85V e pull-up 2,5V su R1007, corrente base idealizzata 0,0665mA e beta forzato inferiore a 4. **Questo non prova la saturazione**, perché non rappresenta transistor e comparator vendor reali, temperature, startup, leakage e guasti singoli.

**Blocco decisivo:** a 48V, se il percorso gate-sink viene abilitato per guasto, il modello prevede |VGS| del PFET oltre 20V. La topologia non può quindi essere definita fail-closed. Prima di CAD V2.6: modello vendor onsemi 2N3904, TI LM393 e TL431, caratterizzazione VCEsat del BJT superiore con emettitore flottante, pinout/footprint e stress PFET; simulazione transienti, fault-matrix e revisione safety.

Riferimenti: https://www.onsemi.com/download/data-sheet/pdf/2n3904-d.pdf e https://www.ti.com/product/LM393-N .

Questa è una **proposta**, non una revisione KiCad nativa integrata. V2.5 resta ultima CAD della PR, V2.3 ultima su main, PR #28 Draft e issue #27 aperta. Nessuna PCB, DRC o Gerber. **NO FAB / NO TX / NO BATTERIA / VEICOLO.**
