# V2.0 — PCB preflight: footprint fisici THT F701/D702, non ancora layout radio

Questa revisione aggiunge **due footprint locali editabili e collegati realmente ai simboli di schematico**. Non costruisce una PCB fittizia e non dichiara completata la radio: un file `.kicad_pcb` finale e uno sbroglio produttivo sono ancora inesistenti.

## Rilievi dimensionali / fonti
- **F701 Littelfuse PICO II 251, esatto candidato 0251.500MXL**, assiale 500mA fast, corpo **L7,11mm** per **Ø2,80mm max**, reofori **Ø0,64mm**, nominal I²t **0,0598 A²s**, tensione nominale 125V DC, capacità interruzione riportata 300A DC a tensione nominale per questo MPN. [Datasheet PICO II](https://www.littelfuse.com/media?resourcetype=datasheets&itemid=089101e2-902c-48bc-9a90-3959fdfc31e1) e [catalogo dimensioni](https://www.digikey.it/en/products/detail/littelfuse-inc/0251-500MXL/700707). I²t non prova il coordinamento con **l'effettiva sorgente**, né che 500mA sia il corretto valore per la radio.
- **D702 ST P6KE20CA bidirezionale**, package DO-15, corpo **L6,05–6,75mm**, **Ø2,95–3,53mm**, reofori **Ø0,71–0,88mm**. [ST P6KE datasheet, tabella 3](https://www.st.com/resource/en/datasheet/p6ke12ca.pdf). Standoff 17,1V; break 19–21V; clamp 27,7V solo alla corrente di impulso specificata, non protezione dalla sovratensione continua. [ST datasheet](https://www.st.com/resource/en/datasheet/p6ke12ca.pdf).

## Footprint consegnati
- `04_KiCad/V2.0/THT_V20.pretty/Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm.kicad_mod`: 2 pad THT 12,70mm interasse, Ø foro **0,90mm**, Ø pad **2,10mm**, anello nominale **0,60mm** e sovrametallo minimo sul conduttore **0,26mm** diametrali, corpo rappresentato a max 7,11 × 2,80mm.
- `04_KiCad/V2.0/THT_V20.pretty/TVS_ST_P6KE20CA_DO15_P12.70mm.kicad_mod`: 2 pad THT 12,70mm interasse, Ø foro **1,10mm**, Ø pad **2,30mm**, anello nominale **0,60mm** e gioco tra foro e reoforo massimo **0,22mm** sul diametro, corpo max 6,75 × 3,53mm.
- `fp-lib-table` locale registra la libreria. Il foglio `INPUT_FUSE_REVERSE_TVS_OVP_V2.0.kicad_sch` assegna concretamente i due footprint; l'intero master a sei fogli è aggiornato senza alcuna nuova connessione elettrica.

## Avvertenza sul package reale
Il passo orizzontale **12,70mm** è una scelta preliminare per la piegatura dei reofori: **non** è un passo raccomandato verificato dai costruttori. Le dimensioni di foro/pad sono stime CAD per geometria e montaggio assiale, non hanno verifica IPC su processo saldatura e stress reofori. Evitare di imprimere sforzi meccanici sull'epossidico, verificare reofori preformati, isolamento, tolleranze PCB, processi solder wave e disponibilità con il fornitore PCB/assemblaggio. Il fusibile e TVS restano incompatibili con una dichiarazione di sicurezza finché corrente di guasto e I²t sono ignote.

## Gate e prerequisiti della PCB finale
1. **CAD nativo:** generazione deterministica dei sette file schematici + 2 footprint + tabelle; esportazione native di 2 footprint e 6 fogli; ERC0; netlist V1.9 64 → V2.0 64 con ogni partizione legacy identica.
2. **Alimentazione e protezioni:** documentare specifiche sorgente, inversione batteria, massimo 36V LM393, energia TVS/fusibile, dissipazione 5V, test rail powergood/mute.
3. **Ricevitore completo:** realizzare e verificare veramente RF front end, mixer IF, AM/FM/SSB, audio, PIC, connettori e rail VTUNE 20V.
4. **PCB:** solo dopo progettare contorno meccanico, stackup e piani massa, budget di impedenza/corrente, layout per domini analogici/RF/digitali, verifica footprint dal vero, DRC e netlist↔PCB, regole fab, BOM e test points.
5. **Pre-release:** schemi/ERC0, PCB/DRC0 e parità elettrica 100%, test di banco, derating BOM, design review indipendente, stress EMI/termici, controlli meccanici e checklist assembly. Tutti gli oggetti non verificati bloccheranno il release.

**NO FAB / NO TX**, non collegare a batteria/veicolo; la sola copertura di impronte non cambia il fatto che la **PCB radio completa è ancora 0% layout/autorouting**.

## Audit indipendente del CAD totale
Lo script `03_Verifiche/V2.0/audit_all_components_v20.py` analizza il `.net` esportato nativamente da KiCad9, costruisce l'inventario di tutti i reference designator, verifica i due footprint nuovi nell'archivio reale, blocca assegnazioni esplicitamente SMD, elenca i componenti con footprint ancora vuoto e produce `native_results/v20_component_footprint_coverage.json`. Il test **passa solamente se il rapporto è veritiero**, senza fingere che il resto della radio sia completo. I componenti privi di footprint restano blocchi per la fabbricazione.
