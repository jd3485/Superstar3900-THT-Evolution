# KiCad9 V2.0 — PLL RX a sette fogli + boost MC34063ABN / LM317T VTUNE20 THT

Aprire `PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch`. Il settimo child `POWER20_VTUNE_BOOST_LDO_V2.0.kicad_sch` alimenta concretamente il pad 8 U803 LM358 nel PD filter via `VANA20_FILT` senza modificare alcun collegamento originale V1.9. Include U911 MC34063ABN DIP8, U912 LM317T TO220 (pin2 e TAB = OUTPUT non GND), L920 Bourns RLB0914-681KL **680uH THT ma footprint non selezionato** e reti complete R/C/D + protezioni LM317. `genera_vtune20_v20.js --check` ricostruisce i nove file CAD byte-per-byte.

Ramo **SOLO CAD / NON QUALIFICATO**: non connettere hardware o batteria/veicolo; il MC34063 switching non è stato simulato con modello vendor, no prove rumore/EMI e RF, nessun PCB layout. **NO FAB / NO TX.**

**Verifiche native:** [CI 42986863110](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42986863110) ERC0, 72 net groups, 64 vecchie partizioni preservate, simboli e 7 SVG PASS; screen di corrente aggiornato per marcare margini ridotti invece di guasti inventati. BOM THT audit e MPN L920 mancante di footprint bloccano FAB.

**Qualità annotazioni:** il VCO ereditato ha il riferimento legacy C500B rinumerato C509 **solo nelle copie V2.0**; stessi pin e reti. Il test native verifica questa unica mappa e che tutti i componenti abbiano una reference standard.
