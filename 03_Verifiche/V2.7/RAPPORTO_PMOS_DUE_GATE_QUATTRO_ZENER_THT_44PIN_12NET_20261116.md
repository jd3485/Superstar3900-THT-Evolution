# V2.7 — 2 Zener THT per ciascun gate Q804/Q805, driver Q806/Q807 separati

**16 novembre 2026 — schema KiCad9 isolato candidato, NON qualificato per protezione reale.** Questo branch è costruito sopra il precedente banco dual-gate PR #326 (non ancora integrata al momento della creazione); non sostituisce la baseline MAIN V2.6.

## Materiale del circuito
Nuovo CAD `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_DUAL_GATES_TWIN_ZENERS/MAIN_SECONDARY_OVP_DUAL_GATES_TWIN_ZENERS_LAB_V2_7_DRAFT.kicad_sch`: preserva la topologia PMOS anti-serie Q804/Q805 e due driver NPN THT Q806/Q807 su enable esterni separati. I gate G_A e G_B sono elettricamente distinti. Rispetto al predecessore sono stati aggiunti due diodi THT:

- **D2101 + D2110** in parallelo tra source comune e `COMMON_GATE_LAB`: ogni catodo pin1 al source e anodo pin2 a G_A;
- **D2102 + D2111** in parallelo tra source comune e `GATE_B_LAB`, stessa polarità.

Quattro **Microchip 1N4106-1 DO-35**, solo **candidati OEM** 12V/250µA, due per gate, impronte KiCad THT provvisorie. Non sono quattro supervisori: condividono tensione source, ritorno ed energia dei gate; e due diodi in parallelo possono **non** spartire corrente uniformemente. Il corto di un diodo fra gate e source può impedire il comando ON ma non costituisce garanzia in tutti i fault.

## Contratto tecnico e fault
`verify_dual_pmos_twin_clamps_native.py`, registrato in FULL, esporta la netlist reale KiCad9 **20 simboli/44 pin/12 reti**, confronta ogni connessione con il banco split-gate #326 e vincola i quattro terminali K/A. Inoltre valuta **1.944** casi matematici sintetici su source 0–48V ipotetico, tolleranze resistive e quattro stati dei due clamp *di un singolo gate*. Il modello numerico ideale a ginocchio fittizio verifica che un solo diodo OPEN mantiene |VGS| entro 20V in tale dominio, ma non dimostra che il diodo superstite soddisfi la curva OEM I/V in ogni punto (IZT=250µA è un solo punto di prova). Con entrambi OPEN, |VGS| può superare il massimo assoluto PMOS. **VIN48V è scenario teorico, NON autorizzazione hardware.**

L'effettivo modello OEM, comportamento reverse, surge, leakage, temperatura e guasti D–S, driver BJT C–E, sorgenti e comparatori indipendenti, return comune, dissipatori/tab TO-220 drain e soglie power-good restano bloccanti della issue #27. Non dedurre una sicurezza funzionale dal numero di componenti o dal solo ERC. Nessuna PCB progettata.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
