# V2.7 — influenza dell'impedenza sorgente non qualificata sul percorso AM455→FRONT→LM386

**15 novembre 2026 — scenario passivo lineare, non modello OEM del diodo.** Rende più realistica la precedente ipotesi a sorgente di tensione ideale (PR #232) introducendo un resistore serie di Thévenin ipotetico prima del nodo inviluppo AM455. **NON** autorizza a considerare il rivelatore 1N4148 come resistore o a dichiarare queste resistenze come limiti fisici validati.

## Circuito verificato con netlist KiCad9

All'ingresso del modello è un generatore AF ideale in serie a Rsource; sul nodo inviluppo agiscono **R1501=47 kΩ** e **C1501=1 nF** in parallelo a massa, più il ramo **C1502=100 nF** verso R1502=100 kΩ, RV1301=10 kΩ (FRONT) e C1201=100 nF/R1201=10 kΩ/Rin LM386. Le associazioni pin↔net sono controllate sulle netlist KiCad9 esportate (D1501 catodo1, R1501/1, C1501/1, C1502/1 sul nodo `AM_RECTIFIED_ENV`; R1501/2 e C1501/2 a `IF_BENCH_GND`).

Il rapporto di tensione tra ingresso sorgente Thévenin ideale e pin 3 U1201 viene ricavato con riduzione delle impedenze complesse e ricalcolato indipendentemente con sistema **KCL complesso a quattro nodi E/A/wiper/ingresso LM386**. Il test richiede coincidenza assoluta <3e-10, residuo KCL <1e-8, modulo del trasferimento fra 0 e 1, e una diminuzione di modulo all'aumentare della resistenza di sorgente in ciascuna condizione.

**300 punti:** f=100/300/1000/3000/10000 Hz; wiper=1/10/50/90/99%; Rin LM386 25/50/75 kΩ (50k tipico, estremi puramente ipotetici); Rsource 1/10/47/100 kΩ **tutti scenari illustrativi**.

## Esempi calcolati (non simulati OEM, non misurati)

Con Rin=50 kΩ, potenziometro al 99%, Rsource=47 kΩ: |V_pin3 / V_Th| ≈ **0,08938 a 100 Hz**, **0,10296 a 1 kHz**, **0,09678 a 10 kHz**. La perdita aggiuntiva rispetto al precedente caso di inviluppo idealmente pilotato può essere notevole, e la risposta in alta frequenza viene influenzata dalla capacità C1501. Non dedurre da ciò sensibilità minima o potenza acustica: l'impedenza dinamica del diodo dipende fortemente dalla sua conduzione e dal livello RF455, per cui il modello Thévenin lineare non riproduce l'inviluppo reale.

## Decisione ingegneristica

Prima di collegare fisicamente IF455→AM455→FRONT o cristallizzare i valori dei condensatori/trimmer occorrono un modello dinamico OEM diodo, intervalli affidabili di livello, banco per THD e linearità dell'inviluppo, dati della reale porta IF e modello LM386 dipendente da alimentazione/carico. Occorre separare return IF e AF e determinare massa/chassis/cavi reali e EMI/ESD. Il prossimo circuito non deve essere scelto solo perché un KCL lineare è verde.

**Gate:** `03_Verifiche/V2.7/verify_am455_envelope_source_impedance_kcl_native.py` richiamato dal runner FULL `ci/full_regressions.py`. Qualsiasi affermazione di risultato eseguito richiede evidenza della CI sul final HEAD. Nessun master KiCad modificato, nessuna PCB radio, niente DRC di prodotto. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
