# V2.7 DRAFT — proposta filtro IF455 con trimmer THT regolabile

**13/11/2026 — revisione NON approvata alla fabbricazione.** Evoluzione reale del circuito KiCad9 IF455 dopo PR #83, che ha dimostrato il rischio di un tank fisso 1mH/110pF con bobina ±5%. Restano 9 posizioni THT e 4 reti elettriche, ma il condensatore C1603 diventa **variabile**.

## Scelta dei componenti

- **L1601**: Delevan **2500-28J**, 1mH ±5%, MPN industriale *candidato* e NON qualificato a 455kHz, Q=60 specificato a 790kHz, SRF=2,8MHz; impronta `TH_TANK:L_1mH_Axial_THT_PROVISIONAL` ancora NON produttiva. Scheda [DigiKey](https://www.digikey.com/en/products/detail/delevan/2500-28J/3479912).
- **C1602**: sostituito **110pF** con **82pF C0G THT**, nominale (ancora da qualificare tolleranze OEM e perdite).
- **C1603**: sostituito condensatore fisso **2,2pF** con **EW Electronics GKG50015**, trimmer **10–50pF**, THT, regolazione dall'alto, ceramica, tensione 100V, temperatura −25..+85°C e Q=200 misurato **a 1MHz, non a 455kHz**. Distributore [DigiKey](https://www.digikey.com/en/products/detail/ew-electronics/GKG50015/11689274) lo indica *Active*. Il simbolo separato `TH_TANK:CT` ha due pin e footprint locale `TH_TANK:Trimmer_GKG50015_2pad_PROVISIONAL`. **Geometria 2 pad e passo 2,50mm del footprint non derivano da un datasheet OEM, quindi DO NOT FABRICATE**: quote, rotore/contatto e accessibilità di regolazione devono essere verificate.
- **Altri componenti**: C1601/C1604 10pF e R1601=47k/R1602=100k invariati, ingresso/uscita su connettori THT generici da banco. Il prototipo resta distinto dal mixer, dall'amplificatore IF e dal rivelatore AM e non è un trasformatore IF completo.

**Topologia:** C1602 e C1603 in parallelo fra nodo `IF455_TANK` e `IF_BENCH_GND`. Capacità ideale shunt variabile da **92 a 132 pF** (82pF +10..50pF), ignorando componenti e carichi parassiti. La posizione nominale puramente illustrativa ~30pF dà 112pF shunt ma non equivale a taratura del filtro intero.

## Nuova simulazione AC ngspice sul modello semplificato

Deck `03_Verifiche/V2.7/spice/if455_trimmer_gkg50015_tuning_envelope.cir` con 8 reti indipendenti per Ctrim **10pF e 50pF**, combinati con:
- bobina L=0,95mH, 1mH, 1,05mH;
- 1mH nominale + 3,23pF paralleli derivati **solo come capacità equivalente ipotetica** dalla SRF 2,8MHz indicata dal fornitore.

Ogni rete contiene sorgente ideale AC 1V con 50Ω, C di coupling 10pF, R bobina 16,5Ω **ipotesi semplificata di perdita AC, NON modello OEM**, 47kΩ parallelo, 100kΩ carico, condensatori ideali. Il test `verify_if455_trimmer_range_ngspice.py` impone che **in tutti e 4 i corner** il picco di rete a Ctrim minimo sia *superiore* a 458kHz e il picco a Ctrim massimo sia *inferiore* a 452kHz; quindi il valore 455kHz sia teoricamente compreso nell'intervallo di regolazione per ciascuna ipotesi. Il test importa **1201 campioni veri da ngspice** per le 8 curve, non usa la sola formula LC. È aggiunto al runner FULL KiCad9/ngspice già esistente senza creare un nuovo job Actions.

**Limitazione essenziale:** il fatto che 455kHz sia incluso nell'intervallo **non** garantisce che il filtro possa essere tarato alla frequenza finale considerando la meccanica reale, né garantisce Q, banda/attenuazione adiacente, perdite inserzione, linearità termica, stabilità in vibrazione e resistenza alle regolazioni. Il trimmer ha Q=200 @1MHz, non convalidato @455kHz; L ha Q=60 @790kHz, non convalidato @455kHz. Anche la capacità del trimmer può essere dipendente dal regolaggio/frequenza e l'accesso dall'alto richiede layout e schermature.

## Release gates ancora bloccati

Il simbolo e la libreria sono CAD reale THT, ma **footprint coil e trimmer PROVISIONAL** con fori e distanze non verificati. Prima di PCB: ottenere e interpretare disegni meccanici OEM, impostare geometrie e BOM corretti, qualificare perdite e SRF, scegliere filtro IF AM/FM idoneo e carico mixer/rivelatore, misurare risposta e taratura su banco, definire regole RF e piano masse. L'ERC KiCad conferma le connessioni, non le prestazioni fisiche. La suite FULL deve risultare **3/3 PASS** sul commit della PR finale prima di qualunque merge.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** MASTER MAIN V2.6 7 fogli/138 refs non modificato, moduli IF455/AM455/audio restano standalone, nessun file PCB, layout e routing 0%, stima progetto ~20%.
