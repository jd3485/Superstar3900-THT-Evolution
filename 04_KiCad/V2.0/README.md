# KiCad9 V2.0 — PLL RX a sette fogli + boost MC34063ABN / LM317T VTUNE20 THT

Aprire `PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch`. Il settimo child `POWER20_VTUNE_BOOST_LDO_V2.0.kicad_sch` alimenta concretamente il pad 8 U803 LM358 nel PD filter via `VANA20_FILT` senza modificare alcun collegamento originale V1.9. Include U911 MC34063ABN DIP8, U912 LM317T TO220 (pin2 e TAB = OUTPUT non GND), L920 Bourns RLB0914-681KL **680uH THT ma footprint non selezionato** e reti complete R/C/D + protezioni LM317. `genera_vtune20_v20.js --check` ricostruisce i nove file CAD byte-per-byte.

Ramo **SOLO CAD / NON QUALIFICATO**: non connettere hardware o batteria/veicolo; il MC34063 switching non è stato simulato con modello vendor, no prove rumore/EMI e RF, nessun PCB layout. **NO FAB / NO TX.**
