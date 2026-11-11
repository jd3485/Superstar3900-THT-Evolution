# KiCad V1.9 — alimentazione supervisore OVP sotto inversione, stress R1001

Master `PLL_RX_HIERARCHICAL_MASTER_V1.9.kicad_sch`, sei pagine KiCad9 native. Il foglio ingresso `INPUT_FUSE_REVERSE_TVS_OVP_V1.9.kicad_sch` ora ha **D804 1N5819 in serie sulla supply e sul partitore del controllo**, rete nuova `OVP_CTL_VCC`, **D805 1N5819 clamp inversa GND→control**, **R1001 3k3 1W Vishay PR01000103301JR500** footprint allargato. U801 LM393 e TL431 restano upstream del MOSFET, non garantiti per automotive.

Ricostruzione deterministica `node 04_KiCad/V1.9/genera_supervisore_v19.js --check`. CI native KiCad9 ERC, due netlist reali, confronto completo conservazione pin-net, SVG 6 pagine e stima analitica dissipazione. Sorgenti V1.8 immutati, SMD intatta.

**ATTENZIONE:** non esiste una protezione certificata contro inversione o sovratensione continua oltre i massimi; LM393 max 36V, leakage/temperatura/stabilità/test vendor mancanti, fuse TVS non qualificati, nessun PCB. **NO FAB / NO TX.**

**Risultato CAD:** [KiCad9 native 42971502918](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42971502918): ERC 0, 64 gruppi netlist, 63 gruppi precedenti preservati tranne migrazione tre pin del controllo, generator e SVG sei pagine PASS, test aritmetici 21 scenari PASS non equivalenti ad automotive qualificata. NON usare tensioni di batteria o veicolo. NO FAB / NO TX.
