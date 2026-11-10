# V1.1 — CAD-02: vero nucleo PLL THT RX in KiCad 9
Data 10 novembre 2026. Si applica il metodo CAD-first del progetto THT, indipendentemente dal progetto SMD. **NO FAB / NO TX**.

## Artefatti reali del branch
- `04_KiCad/V1.1/PLL_CORE_RX_CAD_V1.1.kicad_sch`: schematico nativo, con 28 pin U401 **ML145151YP PDIP28** e 14 pin U402 **TC74AC74P DIP14**.
- `genera_pll_core_v11.js`, libreria locale `THT_V11.kicad_sym`, `sym-lib-table`, workflow con ERC, netlist pin-per-pin ed export SVG di KiCad 9.
- I segnali fisici `PLL_FB_18M` (U402 pin5 → U401 pin1), `DIV2_QBAR` (U402 pin6 → pin2), `PLL_PDOUT_3STATE` (U401 pin4 → J401 pin1), `N_CODE_0..11` (U401 ↔ J405), `LO1_CMOS_BUFFERED` (ingresso esterno) sono collegati con etichette elettriche KiCad, non tabelle.
- X401 HC-49/U 10,240MHz, C403/C404=22pF, C401/C405=100nF, C402=10uF, RC reset R403=10k/C406=100nF **solo candidati**, da qualificare; niente supervisore reale.
- RA2/RA1/RA0 = HIGH/LOW/HIGH per R2048; T/R=HIGH per ricezione senza offset; N12/N13=GND. Flip flop U402 secondario ingressi definiti, uscite NC.

## Correzioni da CI
Eseguita correzione allineamento grid nativo KiCad 1,27 mm (pin, fili, labels, NC) e aggiunti J407–J409 come interfacce di osservazione per phiR, phiV, fV; resta da verificare il nuovo ERC e la netlist.

## Limiti e gates
Gli alimentatori, il clock LO CMOS, la codifica N, i driver/buffer RF e il filtro analogico V1.0 sono **interfacce esterne**: non è ancora uno schema master gerarchico collegato, né un PLL chiuso. Il filtro R901=22k/C901=100n della V1.0 resta variante non qualificata rispetto V0.9 10k/47k e 1uF.

**Stato iniziale:** il file CAD è una nuova candidata; ERC, netlist ed export KiCad non devono essere dichiarati PASS prima della CI specifica. PCB non esiste; DRC, prove RF reali, rumore, accuratezza SSB, condizioni termiche e lock PLL restano NON ESEGUITI. Non autorizzare fabbricazione né trasmissione.

## Datasheet
- Lansdale ML145151 issue A, pagina 2 (pinout): https://www.lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf
- Toshiba TC74AC74P pinout: https://toshiba.semicon-storage.com/info/docget.jsp?did=3156&prodName=TC74AC74P

**Prossimo CAD-03:** prima integrare CAD-01 e CAD-02 in un master collegato, poi VCO e alimentatore, mantenendo simulazioni, firmware, BOM e test in parallelo.
