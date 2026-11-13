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

## Risultati nativi effettivi — commit 45beaf42, CI #43480011279

Run GitHub Actions [#43480011279](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43480011279): **FAST + FULL + required gate 3/3 SUCCESS**. Verifica `PASS_NATIVE_KICAD9_ONSEMI_J113_TO92_9THT_6NETS_ERC0_PIN1D_2S_3G_NO_FAB_NO_TX`: KiCad9 **ERC 0 errori / 0 warning**, netlist 9 refs/6 nets, pinout OEM specifico. Test `PASS_NGSPICE_IF455_ONSEMI_J113_GENERIC_NJF_12_CORNERS_NOT_OEM_NO_FAB_NO_TX`, runner FULL con 111 comandi storici.

| VTO NJF modellato | IDSS modellato | JFET AFpp 0,5V (mV) | JFET / diretto 0,5V | JFET AFpp 2V (mV) | JFET / diretto 2V |
|---:|---:|---:|---:|---:|---:|
|−0,5V|2mA|25,213|1,0538|441,216|2,0398|
|−0,5V|10mA|41,575|1,7377|510,437|2,3598|
|−1,5V|2mA|11,973|0,5004|383,538|1,7731|
|−1,5V|10mA|31,788|1,3286|532,034|2,4597|
|−3,0V|2mA|5,824|0,2434|294,034|1,3593|
|−3,0V|10mA|23,497|0,9821|488,812|2,2599|

Controllo diretto a 25ns: circa **23,925mVpp** con sorgente da 0,5V picco e **216,30mVpp** con 2V picco; il riferimento numerico è stato verificato con il deck precedente PR #102. Nei dodici casi il valore massimo di `VGS` resta negativo nel modello (**nessuna conduzione gate diretta rilevata** nei parametri scelti). In alcuni casi a 2V il nodo source scende fino a circa **−12mV**: vicino a cutoff / possibile limitazione di escursione del source follower, e AFpp da solo può aumentare anche in presenza di distorsione.

**Conclusione:** lo stadio J113 modella generalmente **meno attenuazione o un segnale maggiore** del percorso diretto per ingressi grandi, ma **non supera il controllo di robustezza ai segnali deboli**: caso VTO=−3V e IDSS=2mA → 24,34% dell'AFpp diretto a 0,5V. La variazione di VTO e IDSS nell'intervallo scelto causa un ampio spread di guadagno del modello. Nessuna strategia di selezione/trim, AGC o schema con bias qualificato è stata dimostrata. Il J113 resta SOLO candidato bench e **non va integrato nel master**.

### Regresso corretto senza bypass

La prima CI della PR ha confermato **KiCad9 ERC0 e netlist corretta**, ma ngspice ha rifiutato la sintassi `.meas MAX v(gate_j,source_j)` perché interpretata come vettore inesistente. Correzione: osservatore a ingresso idealmente infinito `EGS gs_monitor 0 gate_j source_j 1` e misure `.meas` di `v(gs_monitor)`, senza alterare il circuito né rimuovere il controllo gate-source; rinominato l'elemento SPICE `JQ1801` per distinguerlo dal connettore J1801 KiCad. La seconda CI con il controllo effettivo è PASS. Nessuna deroga ERC / no hardware claim.

Il footprint `TO-92_Inline` rimane **provisionale per fabbricazione**: l'orientamento fisico e il package onsemi CASE 135AN richiedono sovrapposizione OEM 1:1 e ispezione DRC su una vera PCB, che ancora non esiste. Anche l'uso di parametri NJF ricavati da IDSS e |VTO| è una approssimazione non OEM e **non caratterizza la noise figure a 455kHz**. NO FAB / NO TX.
