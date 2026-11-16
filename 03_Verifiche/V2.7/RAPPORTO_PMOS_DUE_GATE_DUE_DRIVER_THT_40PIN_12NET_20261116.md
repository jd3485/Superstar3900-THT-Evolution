# V2.7 — banco nativo THT con due gate PMOS fisicamente separati

16 novembre 2026. Variante **isolata di laboratorio**, non integrata nel master e senza autorizzazione a fabbricazione, TX, batteria o veicolo.

## Modifica elettrica reale
Derivato dal precedente banco `MAIN_SECONDARY_OVP_Q804_Q805_Q806_LOW_CURRENT_ZENER`, preservando i drain separati e i source comuni dei due P-MOS anti-serie Q804/Q805. Il nuovo KiCad9 `MAIN_SECONDARY_OVP_DUAL_INDEPENDENT_GATES_LAB_V2_7_DRAFT.kicad_sch` separa i due terminali gate, prima cortocircuitati nel nodo `COMMON_GATE_LAB`. L'interfaccia di controllo ora ha due rami THT distinti:

- Q804 G1 è sul precedente `COMMON_GATE_LAB`, con R2101 47k pull-up al source, D2101 1N4106-1 clamp candidato e R2102 10k verso sink Q806 KSP42BU, pilotato da R2103 4k7/R2104 100k/J2103.
- Q805 G1 è sul nuovo `GATE_B_LAB`, con R2110 47k pull-up al medesimo source, D2102 1N4106-1 clamp candidato e R2111 10k verso **distinto Q807 KSP42BU**, pilotato da R2112 4k7/R2113 100k/**J2104**. I gate, le basi BJT, le resistenze serie sink, i pullup e gli enable A/B sono reti separate. Nel banco precedente i due 1N4106-1 erano paralleli allo stesso gate: ora uno per ciascun gate; **il margine contro guasto Zener OPEN peggiora** e deve essere riesaminato.
- Source flottante P-MOS, rail input/output e massa di ritorno BJT rimangono **condivisi**: non è un'architettura totalmente indipendente, né un interruttore safety validato. J2103/J2104 richiedono due enable esterni non implementati/qualificati. Un guasto comune di supply, return, source, interferenza o dissipatore rimane bloccante.

## Verifica
`verify_dual_pmos_independent_drivers_native.py` richiede ERC nativo KiCad9 senza errori, esportazione e confronto esatto della netlist di **18 simboli THT, 40 pin e 12 reti**, inclusa separazione dei terminali PMOS G/S/D e dei due collettori KSP42BU. Su modello booleano astratto (16 casi, non vendor SPICE), un singolo Q806 o Q807 C-E SHORT con entrambi gli enable OFF attiva soltanto il gate associato; due C-E SHORT simultanei possono pilotare entrambi, e i guasti D-S dei MOSFET, gate leakage e corrente di carico **non sono modellati**. Nessuna inferenza di sicurezza hardware dalle sole reti.

## Bloccanti di qualificazione
È necessario confrontare lo stato OEM attivo di Q804/Q805 IRF9540NPBF, Q806/Q807 KSP42BU, i due 1N4106-1, temperatura/SOA/I²t, breakdown gate ±20V durante Zener OPEN, assenza driver, picchi Vsource flottante, condizioni brownout, fault corrente e protezioni esatte della rail. **Un solo Zener per gate deve dimostrare PVT full I/V e robustezza singolo guasto**; il nuovo test non lo fa. Le alette TO-220 (DRAIN) devono essere isolate separatamente. Mancano generazione di reference e rail 5V realmente indipendenti e supervisione UVLO/OVP non condivisa; i due enable esterni non dimostrano autonomia. Richieste revisione indipendente e prove fisiche prima di considerare installazione.

**Issue #27 aperta. Nessuna PCB MAIN/FRONT completa, nessun DRC, NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
