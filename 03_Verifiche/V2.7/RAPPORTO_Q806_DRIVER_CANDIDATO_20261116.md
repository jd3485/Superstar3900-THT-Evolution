# V2.7 — isolamento THT Q804/Q805 e pilotaggio candidato Q806 2N3904BU

**16 novembre 2026 — laboratorio KiCad9 ISOLATO, NON un supervisore OVP/UVLO né un circuito sicuro da alimentare.**

## Implementazione CAD reale

Schematic: `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_DRIVER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_NPN_LAB_V2_7_DRAFT.kicad_sch`. Preserva l'anti-serie a source comuni Q804/Q805 IRF9540NPBF, R2101 47k source–gate (OFF passivo), D2101 Zener nominale 12V source–gate e R2102 10k tra gate e sink. Nessuna modifica al master MAIN V2.6.

Sostituisce la precedente possibilità di collegare direttamente un sink esterno J2103/1 con una **vera rete THT**:

- **Q806** onsemi `2N3904BU`, NPN TO-92 E/B/C pin **1 EMITTER→LAB_RETURN_ONLY**, **2 BASE→Q806_BASE_LAB**, **3 COLLECTOR→DRIVER_SINK_LAB**. Footprint KiCad generico `Package_TO_SOT_THT:TO-92_Inline` soltanto candidato; quote OEM e campione ancora da controllare.
- **R2103** 4,7 kΩ dal connettore `J2103/1 ENABLE_LOGIC_5V_LAB` alla base Q806; **R2104** 100 kΩ base–return per forzare Q806 spento senza comando. `J2103/2` è return. Tutte le resistenze e il connettore sono candidati THT privi di qualifica di carico/stress/assemblaggio.
- Collettore Q806 porta al gate comune **solo attraverso R2102**. Non esiste più nel disegno un accesso diretto esterno al gate/sink. Il **source comune dei MOSFET resta flottante** e distinto dal return; le alette metalliche TO-220 Q804/Q805 sono DRAIN e non vanno cortocircuitate da un dissipatore comune non isolato.
- La **logica `ENABLE_LOGIC_5V_LAB` è solamente un ingresso, senza sorgente né comparatore**; un eventuale livello alto non equivale a power-good. Non esiste alimentazione 5V indipendente, supervisor OVP/UVLO, controllo fail-safe o valore certo di VGS in transitorio.

## Riferimento OEM (non rilascio BOM)

onsemi `2N3904/D`, datasheet Rev.3 ottobre 2024, [PDF OEM](https://www.onsemi.com/pdf/datasheet/2n3904-d.pdf): pin TO-92 CASE 135AN **E=1, B=2, C=3**; rating massimo **VCEO 40V, VCBO 60V, VEBO 6V, IC continuo 200mA, dissipazione 625mW a 25°C**. La gamma corrente onsemi mostra 2N3904BU THT, ma confermare formalmente stato produttivo OEM corrente, footprint specifico, derating e reperibilità prima di consolidare BOM. Il valore VCE(sat) ≤0,2V è specificato dal produttore a **IC=10mA, IB=1mA**: non estrapolarlo automaticamente a correnti/tensioni/temperature diverse.

## Envelope teorico e guasti che NON devono essere ignorati

`03_Verifiche/V2.7/verify_ovp_q806_gate_driver_native.py` verifica tramite KiCad9 vero (ERC senza waiver + esportazione netlist) **25 estremità elettriche in 8 reti** e corretta continuità di E/B/C. Lo screening aritmetico di **7.290 combinazioni** assume ingressi statici da 0 a 48 V, VBE ipotetica 0,65–0,95V, R2101/R2102/R2103/R2104 a ±5%, caduta diodo ideale 0,2/0,5/0,9V, enable sempre 5V per il budget base. Le formule sono esclusivamente un modello didattico DC, **NON SPICE vendor, NON modello dinamico né prova hardware**.

- A 5V enable con BJT ipoteticamente conduttivo, corrente base teorica `IB ≈ (5−VBE)/R2103 − VBE/R2104`: ~0,81–0,97mA negli angoli adottati; **non certifica saturazione, tenuta a T o comportamento di switch OFF/ON**.
- Se VIN o OUT arriva teoricamente a 48V con Q806 OFF, il **diodo body dei PMOS porta source comune a ~VIN−Vf** se il nodo è senza carico; collettore Q806 può seguire il gate/source fino a ~47,8V oltre il rating **40V VCEO**. L'assenza di ENABLE non garantisce integrità del transistor sotto questo guasto.
- Se lo Zener D2101 è **OPEN**, un Q806 ideale ON potrebbe imporre `|VGS|≈VIN × R2101/(R2101+R2102)`, fino a ~39,58V a VIN48V nominale: supera il massimo MOSFET `|VGS|20V`. Non esiste contenimento doppio guasto né clamp realmente indipendente.
- Con un MOSFET short D-S, l'altro diodo di corpo può condurre in una direzione, e il divieto di collegare insieme tabs Q804/Q805 rimane **bloccante**; lo script verifica anche questi percorsi tramite grafo elettrico ideale.
- Resta da indagare corrente Zener, dissipazione resistenze, safe operating area, off-state leakage a caldo, rimbalzi, cablaggi, transienti e restart.

## Gate prima della qualifica

1. Progettare vero supervisore **indipendente da U801/U802/D806 e dal nodo da proteggere**, con alimentazione controllata fino a guasti, offset e fault dell'intero percorso.
2. Selezionare Q806 o alternativa THT con tensione VCE robusta contro lo scenario di ingresso ammesso e proteggere l'interfaccia anche in guasto Zener aperto; documentare tempi/energia e controllo del gate source-floating. Un 2N3904BU semplice **non è un componente di sicurezza approvato**.
3. ERC/pin↔net di tutta la gerarchia dopo eventuale integrazione, qualifica componenti OEM, modello SPICE vendor dove possibile, prove banco a sorgente limitata autorizzate esplicitamente, review indipendente, PCB reale e DRC prima di fabbricare.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** Questa revisione non autorizza alimentazione di alcun componente.
