# V2.7 — laboratorio THT KiCad9: Q804/Q805 P-MOSFET a source comuni (anti-serie)

**16 novembre 2026 — bozza isolata NON fabbricabile.** Lo schematico è `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_ANTISERIES/MAIN_SECONDARY_OVP_Q804_Q805_B2B_LAB_V2_7_DRAFT.kicad_sch`. Non modifica il master V2.6 né il progetto FRONT. Sono due candidati MOSFET Infineon IRF9540NPBF TO-220AB identici (Q804/Q805), R2101 47k, R2102 10k, D2101 1N4742A nominale 12V, J2101–J2103 laboratorio. Impronte THT **candidate, non misurate**; gli MPN esatti di passivi/connessioni restano non qualificati.

## Topologia fisica e verifiche vincolanti

- **Q804 pin2 D** = `PRIMARY_IN_DRAIN_LAB` (J2101/1); **Q805 pin2 D** = `SECONDARY_OUT_DRAIN_LAB` (J2102/1). **Q804/3 e Q805/3 source uniti** in `FLOATING_COMMON_SOURCE_LAB`; entrambi i gate pin1 in `COMMON_GATE_LAB`.
- **R2101** 47k source↔gate per default OFF passivo; **D2101** con catodo al source e anodo al gate, clamp candidato; **R2102** 10k tra J2103/1 `DRIVER_SINK_LAB` e `COMMON_GATE_LAB`, limita la corrente statica in caso di sink rigido **solo con Zener integro**.
- **LAB_RETURN_ONLY** J2101/2, J2102/2 e J2103/2, non cortocircuitata al nodo source fluttuante. Questo progetto necessita un vero driver *riferito al nodo source* e di un supervisore di alimentazione indipendente, **non presenti**. Non ponticellare J2103 con massa su hardware.
- La verifica obbligatoria `verify_ovp_dual_pmos_backtoback_lab_native.py` usa KiCad9 **ERC con zero violazioni, senza waiver**, netlist reale con **18 pin su 6 reti** e confronto bidirezionale dei body diode teorici. Con i MOSFET idealmente OFF, diodi drain→source dei due FET puntano entrambi al source comune: niente percorso diretto input→output o output→input attraverso soli diodi. Non è una qualifica del guasto di uno dei FET.
- **L'aletta del TO-220AB è DRAIN**: un dissipatore comune non isolato collega input e output, creando bypass diretto anche con gate OFF. Necessari dissipatori separati o isolamento con parametri elettrici/meccanici verificati, non scelti in questo lab.

## Analisi matematica limite — NON vendor/NO PVT

Assumendo source idealmente imposto, J2103/1 a return tramite sink ideale, R2101=47k, R2102=10k, Zener ideale a 12V (nessuna curva I/V reale):

| Scenario teorico | Risultato | Conseguenza |
|---|---:|---|
| 13,8V, sink rigido, Zener non in conduzione | |VGS| = 13,8×47k/57k = **11,38V** | Perdita/termica MOSFET a corrente di carico ancora non qualificate |
| 48V, Zener integro ideale | |VGS| = **12V**, R2102 dissipazione **0,1296W** | Non prova che D2101, R2102 e driver sopravvivano a transitori, reverse, stress termico o VIN48 |
| **48V, D2101 OPEN**, sink rigido | |VGS| = 48×47k/57k = **39,58V** | **Viola VGS assoluto ±20V** di IRF9540N, fail-safe assente |
| Tabs Q804/Q805 cortocircuitate | Drain input connesso a drain output | Bypass totale della disconnessione, indipendentemente dall'ERC |

L'analisi copre soltanto condizioni statiche teoriche. **Non** è un modello vendor, non include dinamica delle capacità gate, avalanche, SOA, guasti simultanei o bias del futuro supervisore. Anche con ERC0 la protezione OVP/UVLO non è stata dimostrata; i guasti D-S short dei MOSFET e le perdite common-mode rimangono aperti.

## Gate successivi

1. Progettare una **sorgente di supervisione indipendente**, con limiti 36V dei comparatori candidate, startup/brownout/reverse, guasti del clamp e driver riferito al source fluttuante.
2. Selezionare e qualificare realmente componenti attivi THT OEM e valori/derating R2102/D2101 con modelli vendor, stress VGS, corrente, energia e transitori.
3. Audit meccanico pin↔pad/tab/heatsink e isolamento reale; banco, prove di carico, EMC, RF/IF e review safety indipendenti sono indispensabili **prima** di parlare di circuito qualificato.
4. Nessuna modifica al master MAIN V2.6 finché i gate di sicurezza e netlist master non saranno chiusi.

Fonte OEM pin e limiti: [Infineon IRF9540N datasheet](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irf9540n-datasheet-en.pdf). **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
