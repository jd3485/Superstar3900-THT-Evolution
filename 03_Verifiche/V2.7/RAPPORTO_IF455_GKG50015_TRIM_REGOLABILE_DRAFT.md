# V2.7 DRAFT — proposta filtro IF455 con trimmer THT regolabile

**13/11/2026 — revisione NON approvata alla fabbricazione.** Evoluzione reale del circuito KiCad9 IF455 dopo PR #83, che ha dimostrato il rischio di un tank fisso 1mH/110pF con bobina ±5%. Restano 9 posizioni THT e 4 reti elettriche, ma il condensatore C1603 diventa **variabile**.

## Scelta dei componenti

- **L1601**: Delevan **2500-28J**, 1mH ±5%, MPN industriale *candidato* e NON qualificato a 455kHz, Q=60 specificato a 790kHz, SRF=2,8MHz; impronta `TH_TANK:L_1mH_Axial_THT_PROVISIONAL` ancora NON produttiva. Scheda [DigiKey](https://www.digikey.com/en/products/detail/delevan/2500-28J/3479912).
- **C1602**: sostituito **110pF** con **82pF C0G THT**, nominale (ancora da qualificare tolleranze OEM e perdite).
- **C1603**: sostituito condensatore fisso **2,2pF** con **EW Electronics GKG50015**, trimmer **10–50pF**, THT, regolazione dall'alto, ceramica, tensione 100V, temperatura −25..+85°C e Q=200 misurato **a 1MHz, non a 455kHz**. Distributore [DigiKey](https://www.digikey.com/en/products/detail/ew-electronics/GKG50015/11689274) lo indica *Active*. Il simbolo separato `TH_TANK:CT` ha due pin e usa ora `TH_TANK:Trimmer_EW_GKG50015_P5.00mm_OEM_DRAFT`. Il disegno OEM di serie GKG…15 indica **2 fori Ø1,2 mm a 5,0 mm** e terminali rotor/stator; nel CAD **pad 2=rotore a massa IF** e **pad 1=statore al nodo IF455_TANK**. Il vecchio placeholder errato a 2,50 mm è stato cancellato. **Non è ancora un'autorizzazione alla fabbricazione**: mantenere verifiche di montaggio reale, margine saldatura/clearance, accesso alla regolazione, orientamento e approvazione della footprint su PCB effettiva.
- **Altri componenti**: C1601/C1604 10pF e R1601=47k/R1602=100k invariati, ingresso/uscita su connettori THT generici da banco. Il prototipo resta distinto dal mixer, dall'amplificatore IF e dal rivelatore AM e non è un trasformatore IF completo.

**Topologia:** C1602 e C1603 in parallelo fra nodo `IF455_TANK` e `IF_BENCH_GND`. Capacità ideale shunt variabile da **92 a 132 pF** (82pF +10..50pF), ignorando componenti e carichi parassiti. La posizione nominale puramente illustrativa ~30pF dà 112pF shunt ma non equivale a taratura del filtro intero.

## Revisione meccanica successiva — GKG50015 footprint su quote OEM

**Fonte primaria del disegno:** [EW Electronics, GKGxx015/016 Ceramic Dielectric Trimmer Capacitors, pagina unica](https://datasheet.ersaelectronics.com/static/datasheets/ew-electronics/ew-electronics-gkg30015.pdf), tabella `GKG50015` e figura inferiore sinistra **GKG___15 TOP ADJUST**. La figura indica diametro corpo 6,0±0,2 mm, dimensione orizzontale fra i due fori `0.20 inch = 5.0 mm`, due fori `Ø0.047 inch = 1.2 mm` e **rotor** e **stator** sul disegno dei terminali. Il catalogo di distributore [DigiKey GKG50015](https://www.digikey.it/it/products/detail/ew-electronics/GKG50015/11689274) riporta MPN attivo, 10–50 pF, altezza massima 5mm. Il vecchio footprint prototipo `Trimmer_GKG50015_2pad_PROVISIONAL` **era sbagliato (2,5 mm anziché 5 mm)** ed è stato cancellato dal repository. Nessuna compatibilità di PCB è attribuita alla vecchia impronta.

**Nuova geometria locale KiCad9:** `TH_TANK:Trimmer_EW_GKG50015_P5.00mm_OEM_DRAFT`, due pad **THT Ø2,2 mm, foro Ø1,2 mm**, passo **5,00 mm**, disegno F.Fab del corpo Ø6mm e contorno F.CrtYd conservativo Ø7,3mm; il diametro pad da 2,2mm e il margine courtyard scelti sono **decisioni CAD**, da validare per processo saldatura e assemblaggio. Nel simbolo KiCad `TH_TANK:CT` C1603 il pin **1=statore** va al tank; il pin **2=rotore** è collegato alla massa IF, riducendo il rischio di accoppiare la regolazione a un elemento flottante. È necessario verificare l'orientamento del disegno OEM in vista di montaggio/rame con un primo prototipo non operativo e un campione del componente prima di congelare il layout.

**Limite critico di stabilità:** EW indica per la variante GKG50015 dielettrico **N2200 ±800 ppm/°C** e Q minimo 200 @1MHz, non NPO e non prestazione RF garantita a 455kHz. Il trimmer serve a riportare il picco sulla frequenza del modello, ma **non certifica stabilità termica, qualità o banda di canale**. L1601 Delevan 2500-28J resta con footprint bobina PROVISIONAL: il [catalogo serie 2500](https://www.mouser.com/catalog/specsheets/del153712.pdf) fornisce corpo A 11,18±0,25 mm, Ø4,83±0,25 mm e reoforo circa Ø0,635mm, **non** determina da solo passo di montaggio e curvatura verificati per il nostro assemblaggio. Non inventare footprint definitivo della bobina; divieto NO FAB per tutto il modulo finché L1601 e le prestazioni RF non sono qualificate.

**Gate di questa revisione:** il test nativo `verify_if455_tank_native.py` verifica in più i due pad KiCad e le loro coordinate/disposizione, cancellazione dell'errata impronta, coerenza libreria embedded/locale e le net KiCad del trimmer (pad1→IF455_TANK, pad2→IF_BENCH_GND). L'ERC nativo e le regressioni ngspice restano invariati. Non affermare PASS fino all'esito CI su final SHA.

---

## Evidenza effettivamente validata sul commit KiCad9

[PR #84](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/84) **MERGED** commit `ce74fb2b929986c587fdec5677f51729ea67d702`, Actions [#43414613097](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43414613097) **3/3 PASS** sul HEAD `9bba90431c3ded21231417e8b72605c0e7d15d95`. KiCad 9 **ERC 0 errori / 0 warnings**, 9 riferimenti THT, 4 reti; ngspice eseguito realmente sui quattro corner L con il trimmer a 10 e 50pF. I picchi simulati sono:

| Corner | Trimmer 10pF, picco Hz | Trimmer 50pF, picco Hz |
|---|---:|---:|
| L=0,95mH | 510533,3 | 432400,0 |
| L=1,00mH | 497466,7 | 421466,7 |
| L=1,05mH | 485466,7 | 411200,0 |
| L=1,00mH con Cpar 3,23pF ipotetica | 489733,3 | 416666,7 |

455kHz cade nell'intervallo di tutte le curve. **Questo è un esito di copertura dell'intervallo e NON una prova di taratura meccanica, Q o selettività effettiva a 455kHz.** Il simbolo e la geometria delle impronte restano PROVISIONAL / NO FAB.

---

## Nuova simulazione AC ngspice sul modello semplificato

Deck `03_Verifiche/V2.7/spice/if455_trimmer_gkg50015_tuning_envelope.cir` con 8 reti indipendenti per Ctrim **10pF e 50pF**, combinati con:
- bobina L=0,95mH, 1mH, 1,05mH;
- 1mH nominale + 3,23pF paralleli derivati **solo come capacità equivalente ipotetica** dalla SRF 2,8MHz indicata dal fornitore.

Ogni rete contiene sorgente ideale AC 1V con 50Ω, C di coupling 10pF, R bobina 16,5Ω **ipotesi semplificata di perdita AC, NON modello OEM**, 47kΩ parallelo, 100kΩ carico, condensatori ideali. Il test `verify_if455_trimmer_range_ngspice.py` impone che **in tutti e 4 i corner** il picco di rete a Ctrim minimo sia *superiore* a 458kHz e il picco a Ctrim massimo sia *inferiore* a 452kHz; quindi il valore 455kHz sia teoricamente compreso nell'intervallo di regolazione per ciascuna ipotesi. Il test importa **1201 campioni veri da ngspice** per le 8 curve, non usa la sola formula LC. È aggiunto al runner FULL KiCad9/ngspice già esistente senza creare un nuovo job Actions.

**Limitazione essenziale:** il fatto che 455kHz sia incluso nell'intervallo **non** garantisce che il filtro possa essere tarato alla frequenza finale considerando la meccanica reale, né garantisce Q, banda/attenuazione adiacente, perdite inserzione, linearità termica, stabilità in vibrazione e resistenza alle regolazioni. Il trimmer ha Q=200 @1MHz, non convalidato @455kHz; L ha Q=60 @790kHz, non convalidato @455kHz. Anche la capacità del trimmer può essere dipendente dal regolaggio/frequenza e l'accesso dall'alto richiede layout e schermature.

## Release gates ancora bloccati

Il simbolo e la libreria sono CAD reale THT, ma **footprint coil e trimmer PROVISIONAL** con fori e distanze non verificati. Prima di PCB: ottenere e interpretare disegni meccanici OEM, impostare geometrie e BOM corretti, qualificare perdite e SRF, scegliere filtro IF AM/FM idoneo e carico mixer/rivelatore, misurare risposta e taratura su banco, definire regole RF e piano masse. L'ERC KiCad conferma le connessioni, non le prestazioni fisiche. La suite FULL deve risultare **3/3 PASS** sul commit della PR finale prima di qualunque merge.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** MASTER MAIN V2.6 7 fogli/138 refs non modificato, moduli IF455/AM455/audio restano standalone, nessun file PCB, layout e routing 0%, stima progetto ~20%.
