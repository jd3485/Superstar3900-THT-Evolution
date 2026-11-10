# V1.2 — sorgenti KiCad dell'integrazione RX PLL (CAD-01/CAD-02)

`PLL_RX_MASTER_CAD_V1.2.kicad_sch` è uno **schema elettrico reale KiCad 9, piatto e parziale** con U401 ML145151YP, U402 TC74AC74P, R901/C901 e U803 LM358N. **Non è lo schema definitivo gerarchico e non è una PCB.**

Sorgenti deterministici: `../V1.1/PLL_CORE_RX_CAD_V1.1.kicad_sch` e `../V1.0/PLL_FILTER_DRIVER_CAD_V1.0.kicad_sch`. Rigenerare eseguendo `node 04_KiCad/V1.2/genera_master_rx_v12.js` dalla radice. Il generatore allinea la traslazione alla griglia elettrica di 1,27 mm. Le librerie restano in V1.0/V1.1; `sym-lib-table` ha percorsi locali relativi alla directory V1.2.

Test di integrazione su GitHub Actions run 42878584174: ERC nativo 0 violazioni, netlist 33 reti, 28 gruppi controllati, export SVG. Chiuso **solo** il percorso PDout→RC→LM358 a livello pin-net; VTUNE deve ancora essere collegata al VCO, e il PLL chiuso e la stabilità non sono qualificati. **NO FAB / NO TX**.
