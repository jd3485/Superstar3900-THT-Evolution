# V2.7 — onsemi J113 THT, source follower IF455 ad alta impedenza (DRAFT)

**13 novembre 2026 — prototipo CAD/simulazione INDIPENDENTE, nessuna qualifica radio o fabbricazione.**

## Motivazione

Lo screening integrato con [PR #104](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/104) ha dimostrato nel modello BJT generico che il partitore 22k/10k del KSP10BU precedente assorbe una grande quota del segnale IF455. Partitori da 220k/100k e 470k/220k riducono tale carico, ma restano vulnerabili alla corrente di base e a escursioni estreme del nodo emettitore con ingresso 2V. Proponiamo **una topologia effettivamente diversa**: JFET depletion a gate ad alta impedenza con self-bias di source, sempre 100% THT e sempre SOLO da banco. L'assenza di un partitore gate VCC→GND non implica rumore o qualità superiori senza prove.

## OEM e package — blocco pinout esplicito

- **Produttore/MPN candidato onsemi J113**, N-channel JFET TO-92‑3, elencato *Active / Through Hole* da [DigiKey Italia](https://www.digikey.it/it/products/detail/onsemi/J113/1048989) al controllo del 13 novembre 2026. Datasheet OEM [J111/J112/J113, MMBFJ113/D, rev. 5](https://www.onsemi.com/pdf/datasheet/mmbfj113-d.pdf), pagina 1: per TO-92 straight leads **pin 1 Drain, pin 2 Source, pin 3 Gate**; onsemi specifica che D e S sono intercambiabili dal punto di vista del dispositivo, **NON** la posizione del gate.
- In documenti storici di **altri OEM** per J113 si trova **pin 1 Gate, pin 2 Source, pin 3 Drain**. **Non sono equivalenti senza revisione pinpad**. La libreria locale è intenzionalmente lockata a **onsemi J113** e il gate sul pin 3 (J113 in simbolo `TH_J113:JFET`), con footprint KiCad standard provvisorio `Package_TO_SOT_THT:TO-92_Inline`. Occorre verificare orientamento/case meccanico 135AN sul PCB reale prima di approvare produzione e MPN.
- Datasheet onsemi J113: `IDSS` **min 2mA a VDS=15V VGS=0**, `VGS(off)` **−0.5..−3 V** a ID=1µA VDS=5V, `IGSS` max 1nA @VGS=−15V. Questi sono i **test conditions OEM**, NON garanzie per l'interfaccia 6V e il circuito RF 455kHz; non esiste modello vendor integrato qui.

## CAD KiCad9 reale

Progetto standalone `04_KiCad/V2.7_DRAFT/IF455_J113_SOURCE_FOLLOWER/IF455_J113_SOURCE_FOLLOWER_THT_V2_7_DRAFT.kicad_sch` con libreria locale `TH_J113.kicad_sym`, `sym-lib-table`, `.kicad_pro` e **nove posizioni fisiche THT**, **sei reti**:

- Ingresso IF455 tank `J1801` via `C1801=10pF C0G` verso gate JFET Q1801 (pin 3).
- Gate a massa DC attraverso `R1801=1MΩ` (nessun partitore BJT), drain JFET Q1801 pin1 su `VLAB6_JFET_ONLY` J1803, source pin2 su `R1802=2.2kΩ` a massa.
- Accoppiamento AC source `C1802=10nF` verso uscita `J1802`, `R1803=100kΩ` verso massa.
- Le reti nominate sono `IF455_TANK_OUT`, `JFET_GATE`, `VLAB6_JFET_ONLY`, `JFET_SOURCE`, `JFET_AC_OUT`, `IF_BENCH_GND`. Pin1=D, pin2=S, pin3=G sono accertati anche con export netlist reale KiCad9, non soltanto con una stringa o SVG.

Test `03_Verifiche/V2.7/verify_if455_j113_source_follower_native.py`: KiCad9 CLI ERC con zero errori/avvisi **da raggiungere**, più controllo netlist 9 refs/6 reti; nessun waiver.

## ngspice e limiti del confronto

Deck `03_Verifiche/V2.7/spice/if455_j113_am455_generic_jfet_transient.cir`: sorgente AM 455kHz, Rgen 50Ω e filtro LC identici a PR #101/#102, **due catene indipendenti**: tank→diodo `DGENERIC` e tank→JFET→diodo `DGENERIC`. `JGEN` è modello **ngspice generico NJF**, non macromodello OEM J113. Prova 2 ampiezze (0,5V / 2V picco) × 3 VTO (−0,5/−1,5/−3V) × 2 IDSS **illustrativi** (2/10mA) = **12 transienti non lineari nativi a 25ns**, con BETA calcolato `IDSS / |VTO|²`; parametri parassiti NJF `CGS=5p CGD=2p RD=RS=20Ω` **ipotizzati**. Acquisizione AFpp dopo diodo, rapporto AF, carico del tank, gate–source max/min e source max/min. **Non si impone arbitrariamente che il JFET superi il percorso diretto**: si registrano esiti reali, compresi quelli negativi.

Non è una prova OEM della gamma PVT, non misura rumore/SNR/IMD/THD, niente startup/brownout, stabilità RF, selettività, AGC, effetto impedenza reale del tank o alimentazioni radio. **Nessun collegamento al master V2.6 e nessuna PCB reale. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
