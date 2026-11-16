# V2.7 — guasto comune del pilotaggio Q806 per due PMOS anti-serie

16 novembre 2026 — revisione **diagnostica**, non progetto di interruzione certificata.

## Topologia reale del banco nativo KiCad9
Il banco THT candidato `MAIN_SECONDARY_OVP_Q804_Q805_Q806_LOW_CURRENT_ZENER` ha 27 terminali su 8 reti. Q804 e Q805 hanno source comune su `FLOATING_COMMON_SOURCE_LAB`, drain esterni separati, e **gate entrambi sulla stessa** `COMMON_GATE_LAB`. Le resistenze R2101 (47k) source-gate e R2102 (10k) gate-collettore Q806 operano **su entrambi i gate contemporaneamente**. Q806 onsemi KSP42BU è il solo sink, l'ingresso J2103/1 ENABLE è un 5V esterno NON qualificato. Due PMOS anti-serie prevengono il bypass tramite un solo body diode quando entrambi sono OFF, ma **non equivalgono a due comandi fail-OFF indipendenti**.

## Fault screening verificabile
`verify_dual_pmos_common_gate_fault_native.py` in FULL esporta e controlla la netlist KiCad9 esatta, incluso il separato ritorno, entrambi i drain, Q806 pin E/B/C e J2103. Quindi esamina **216** casi matematici con 6 source potenziali ipotetiche, due resistori ±5%, ENABLE0/1 e Q806 C–E OPEN/NORMAL vs **SHORT**. I due gate hanno VGS identico in ogni caso per topologia. Il modello lineare idealizza gli Zener D2101/D2102 OPEN, **non** predice la reale conduzione dei PMOS, la corrente verso il carico o la dissipazione.

Per ENABLE0 con C–E SHORT e Vsource≥13,8V ci sono **36** casi nei quali entrambi i gate risultano polarizzati negativamente simultaneamente, nonostante il comando OFF. Per sink disabilitato e senza C–E SHORT, **54** casi hanno VGS=0 ideali; questo non esclude D–S SHORT, leakage, body diode o impulsi. La configurazione risolve un problema di verso dei diodi, **non** un guasto comune del gate.

## Necessità di una revisione elettrica nuova
Separare **anche** i comandi dei due gate, ciascuno con propria resistenza source-gate e clamp source-gate dimensionato, circuito driver e consenso supervisore autonomi, così da non poter rendere entrambi ON con un singolo C–E SHORT. Verificare che il riferimento source dei PMOS sia fluttuante, isolare le alette dei TO-220 (TAB = DRAIN), trattare VGS≤20V assoluto, rail/power loss, fault singoli e combinati, polarità opposte, transitori e guasti di rete comune. Le due interruzioni devono essere in serie e con feedback power-good indipendente. La sola separazione dei pin in KiCad non costituisce una qualifica safety.

**ISSUE #27 APERTA. NESSUNA PCB, NO FAB, NO TX, NO BATTERIA, NO VEICOLO.**
