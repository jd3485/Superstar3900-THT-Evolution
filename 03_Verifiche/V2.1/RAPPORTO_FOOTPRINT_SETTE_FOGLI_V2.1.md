# V2.1 — preflight PCB, F701/D702 su master THT 7 fogli con alimentazione VTUNE20 preservata

## Perché V2.1 invece di V2.0
Durante la progettazione parallela dell'impronta assiale, la PR #17 ha integrato in `main` la versione **V2.0 sette fogli**, con boost MC34063ABN / LM317T e reale alimentazione `VANA20_FILT` a U803. La PR #18 sulle impronte, basata sul master precedente a sei fogli e denominata V2.0, è stata **chiusa senza merge** per evitare la perdita del settimo foglio. Questa V2.1 nasce direttamente da `main` commit `284bd3641d7a0f905d14dc4c9f36ee9da84bbc93` e **preserva il circuito V2.0 integrale**, senza alcuna modifica ai collegamenti.

## Incremento CAD vero
- `F701` Littelfuse PICO II `0251.500MXL` assiale, **L7,11×Ø2,80mm max**, lead Ø0,64mm: footprint `THT_V21:Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm` due fori Ø0,90mm, pad Ø2,10mm, passo assiale proposto **12,70mm**.
- `D702` ST P6KE20CA bidir DO-15, **L6,75×Ø3,53mm max**, lead fino a Ø0,88mm: footprint `THT_V21:TVS_ST_P6KE20CA_DO15_P12.70mm` due fori Ø1,10mm, pad Ø2,30mm, passo assiale proposto **12,70mm**.
- Footprint autorabili `04_KiCad/V2.1/THT_V21.pretty`, tabella locale `fp-lib-table` e riferimenti ai simboli V2.0 via `../V2.0/THT_V20.kicad_sym`; nessun duplicato o override dell'alimentazione 20V.
- Datasheet primaria ST [P6KE DO-15 dimensioni](https://www.st.com/resource/en/datasheet/p6ke12ca.pdf). Littelfuse PICOII 251 [distributore MPN e specifiche meccaniche](https://www.digikey.it/en/products/detail/littelfuse-inc/0251-500MXL/700707), L7,11 mm Ø2,80 mm reoforo 0,64 mm.
- **Non** si dichiara valido un passo meccanico per assemblaggio automatico: ricontrollare piegatura reale, distanza corpo-pad, processo wave e metrologia THT. TVS/fusibile non qualificati per auto o sovratensioni continue.

## Gate robusto
`node 04_KiCad/V2.1/genera_footprint_v21.js --check` rigenera i sette fogli, le due tabelle; il gate CI installa KiCad9, esporta entrambe le impronte e 7 pagine SVG, ERC0, confronta tutte le **72 partizioni native della V2.0 7-sheet** con V2.1 preservando RF, 5V, 20V VTUNE e OVP, svolge audit indipendente 100% componenti del netlist, verifica l'assenza di package SMD espliciti e **segnala L501 VCO e L920 BOOST** ancora senza footprint. Non nasconde questi due release blocker.

## Hardware da completare e rischi
- **L501 VCO RF 166 nH**: solo modello, footprint e qualità RF non definiti; Issue #19.
- **L920 Bourns RLB0914-681KL 680µH BOOST**: MPN dichiarato ma mancano ancora footprint THT verificato, validazione energia/saturazione/termica e ripple 20V.
- **U801 LM393**: sovratensione raw >36V non qualificata; D804/D805 reverse-fault e TVS/F701 source coordination, powergood/mute e temp ignoti.
- Mancano stadi RF input/mixer/IF, demodulatori, audio, PIC e altri I/O, BOM produzione, meccanica e PCB completa. **Nessuna `.kicad_pcb` radio con layout, nessuna DRC PCB, nessun Gerber.** NO FAB / NO TX.

La PR V2.1 non deve essere integrata senza GitHub CI verde sul suo commit finale. Anche se il gate CAD PASS, per PCB finale serve una revisione DFM/DFT indipendente e prototipo testato.
