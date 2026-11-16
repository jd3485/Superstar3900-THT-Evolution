# V2.7 — diagnostica di guasti singoli e doppi su due stadi PMOS anti-serie completi

**16 novembre 2026 — banco diagnostico sullo schematico reale KiCad9 della PR #329; solo grafo orientato ideale, NON prova di sicurezza reale.**

## Contratto fisico controllato
Il verificatore `03_Verifiche/V2.7/verify_two_pmos_stages_single_double_fault_native.py` esporta netlist KiCad9 del banco THT `MAIN_SECONDARY_OVP_TWO_COMPLETE_STAGES_LAB_V2_7_DRAFT.kicad_sch` (24 componenti, 54 terminali, 14 reti). Vincola i quattro DRAIN: Q804 su ingresso, Q805/Q814 sul nodo MID, Q815 su uscita finale, le due source distinte `FLOATING_COMMON_SOURCE_LAB` e `FLOATING_SOURCE_B_LAB`, i due gate distinti e i sink Q806/Q816. Non deduce capacità di sicurezza dal solo schema.

## Guasti topologici (ENABLE_A=ENABLE_B=OFF)
Modello di diodo intrinseco P-MOS idealmente orientato DRAIN→SOURCE e canale bidirezionale soltanto con stadio interamente acceso o drain-source del MOSFET in cortocircuito. Nessun carico, tensione, corrente, SOA o caduta diodi modellati.

Sei guasti elementari: Q806 C–E SHORT, Q816 C–E SHORT, Q804/Q805/Q814/Q815 D–S SHORT. Fra i **6 casi con un solo guasto** il grafo non ha percorso attraverso entrambi gli stadi: **0/6**. Fra tutte le **15 combinazioni di due guasti elementari**, **7/15** aprono almeno un percorso:

- **Q806 C–E SHORT + Q816 C–E SHORT:** entrambi gli interruttori ON, passaggio bidirezionale nonostante ENABLE0.
- **Q806 C–E SHORT + Q814 D–S SHORT** consente il percorso inverso; **Q806 C–E SHORT + Q815 D–S SHORT** consente il percorso diretto.
- **Q816 C–E SHORT + Q804 D–S SHORT** consente il percorso inverso; **Q816 C–E SHORT + Q805 D–S SHORT** consente il percorso diretto.
- **Q804 D–S SHORT + Q814 D–S SHORT** consente il percorso inverso; **Q805 D–S SHORT + Q815 D–S SHORT** consente il percorso diretto.

Un guasto simultaneo dei due enable esterni, comune source/return, gate-source clamp OPEN/SHORT, input supply, MOSFET capacitive dv/dt, avalanche, carico o MOSFET in perdita NON è incluso nei sei guasti elementari: non chiamare questa verifica «single-fault safety». Quattro PMOS in cascata **non** garantiscono automaticamente ridondanza protettiva né un singolo guasto sicuro in qualsiasi classe di difetto. 0/6 e 7/15 sono conteggi del grafo definito, non probabilità né tassi di rischio.


## Guasto comune esplicito: consenso esterno incollato HIGH

Le netlist KiCad9 mantengono `ENABLE_LOGIC_5V_LAB` (J2103/1) e `ENABLE_B_5V_LAB` (J2113/1) separati, ma nessuna delle due origini viene implementata o qualificata in questo banco. Se una **sola sorgente comune a monte** alimenta entrambi gli ENABLE e rimane incollata HIGH, il modello `COMMON_ENABLE_STUCK_HIGH` produce percorso in entrambe le direzioni con comandi utente nominali OFF. È un **guasto singolo di causa comune**, non due guasti indipendenti ai transistor. Il test lo vincola in modo esplicito; non è una dimostrazione che la sorgente comune esista sul prodotto finale. Gli originali 0/6 guasti singoli si riferiscono esclusivamente alla lista di sei guasti locali D–S/C–E, **non** a ogni possibile guasto singolo. Per chiudere #27 servono sorgenti, consenso OFF e diagnostiche indipendenti reali, non solo due etichette di rete.

## Azioni obbligatorie prima di impiego
Separare e qualificare l'alimentazione e la supervisione degli stadi; definire il comportamento con un comando di consenso incollato HIGH; verificare pin-pad-tab TO-220, dissipatori isolati, referenze, supply persa, feedback del nodo centrale MID, due Zener per gate in parallelo e fault per singolo diodo, curve OEM I/V e gate ±20V, transitori, termico, SOA e carico reale. Nessuna PCB o test di banco autorizzati dalla sola analisi.

**#27 APERTA. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
