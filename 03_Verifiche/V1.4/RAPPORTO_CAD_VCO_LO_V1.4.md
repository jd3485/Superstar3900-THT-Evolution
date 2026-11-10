# V1.4 CAD — VCO Colpitts B THT e buffer RX a due stadi
10 novembre 2026, solo `jd3485/Superstar3900-THT-Evolution`.

## Sorgenti CAD reali
Root gerarchico `04_KiCad/V1.4/PLL_RX_HIERARCHICAL_MASTER_V1.4.kicad_sch` più tre figli (PLL U401/U402, filtro R901/C901 U803 LM358, VCO+buffer).
Il nuovo figlio `VCO_RX_AND_LOBUF_V1.4.kicad_sch` contiene **37 istanze** THT/fili/nodi elettrologici: Q501/Q502 2N3904 TO-92; D501 un unico BB204G con due anodi (pin 1/3) e catodo comune (pin2), L501 modello 166nH **footprint ancora VUOTO**, RC del candidato Colpitts B V0.6, U520 SN74AC14N PDIP14 e stadi ausiliari di filtro/accoppiamento. Impiegati due stadi AC14 con polarizzazione ad alta impedenza R510/R511/R512; tutti i quattro input AC14 non utilizzati collegati a GND, quattro output NC.

* `VTUNE_RAIL` ora passa realmente da U803/R805 al **catodo D501/2** per mezzo di sheet-pin/hierarchical-label.
* `LO1_CMOS_BUFFERED` ora passa realmente da U520/4 via R513 100Ω al clock **U402/3**, sheet-pin lungo la gerarchia. Lo stadio Q502 mantiene test analogico LO su J523, senza presupporre carichi di mixer noti.
* `GND` fisica è comune ai tre figli attraverso cavi reali nel root. Le alimentazioni RF `VCC_VCO5` e buffer `VCC_BUF5` sono due ingressi **esterni e distinti** J520/J521 con PWR_FLAG provvisori. La configurazione definitiva con regolatori THT, filtri e mute resta da progettare.

## Source SPICE tracciata ma non simulazione dell'intero nuovo circuito
Transistor e passivi del Colpitts ricostruiscono `03_Verifiche/V0.6/VCO_COLPITTS_CANDIDATE_B_V0.6.cir`, che in screening ngspice 5 punti aveva coperto nominalmente 36,04773–39,19647 MHz a 8–15 V sul controllo. Quello screening **non include il nuovo condizionamento AC14 né l'accoppiamento di carico**, non è una simulazione del PLL chiuso e non prova l'oscillazione di V1.4! Il minimo margine inverso del varicap riportato nel modello era 0,447V, pertanto sono urgenti analisi di ampiezza RF, clipping, sottosoglia, start-up, tolleranze, temperatura e rumore. R509=1Meg al nodo analogico è mantenuta da V0.6, il bias buffer e C510 sono **nuovi circuiti candidati**.

## Datasheet verificati: pinout ma NON compatibilità RF
- Philips BB204B/G 1996: TO-92 variante, pin1 A1, pin2 K comune, pin3 A2; Vr max 30V; C(3V) 34–39pF, C(8V) 22–27pF. [Datasheet BB204G](https://datasheet4u.com/pdf-down/B/B/2/BB204G_PhilipsSemiconductors.pdf).
- TI SN74AC14 (2024): variante N **PDIP14**, pin1 1A, 2 1Y, 3 2A, 4 2Y, 7 GND, 14 VCC; 2–6V, tpd massimo 9.5 ns a 5V. **NON equivale a garantire 36–39MHz dal VCO analogico o la corretta soglia Schmitt.** [Datasheet TI](https://www.ti.com/lit/ds/symlink/sn74ac14.pdf).
- Onsemi 2N3904: TO92 E1/B2/C3 per la variante specifica; confermare la pin assignment del MPN effettivo. [Datasheet 2N3904](https://www.mouser.com/datasheet/2/321/2N3904-33357.pdf).

## Limiti NO FAB / NO TX
L501 ancora SENZA MPN/footprint certificato, BB204G legacy sourcing/lead pitch/stock da verificare, package TO92 generico candidato non qualificato. DRC PCB NOT_RUN, mancano VCO load-pull, simulazione del buffer, validazione oscillazione e fase in PLL, margine di tuning e controllo su temperatura/approvvigionamento. Nessuna produzione, emissione RF o ordine.

## Validazione CAD
`.github/workflows/cad_native_v14.yml` verifica rigenerazione deterministica, export simboli THT, ERC dei quattro fogli, netlist native old/new con conservazione di TUTTI i gruppi pin-net legacy e 15 gruppi candidati nuovi (con distinzione necessaria delle alimentazioni), SVG di 4 pagine e artefatti.
**In attesa del risultato runner prima di dichiarare il PASS.**

## Errore ERC V1.4 intercettato e corretto
Primo run [42891325528](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42891325528) = **FAIL CAD**: due violazioni KiCad9, `pin_not_connected` sul pin GND del foglio filtro e `power_pin_not_driven` U803 pin4. Il problema è la linea GND legacy non divisa nel punto di diramazione x154,94 mm / y87,63 mm. Aggiornati sia il master sia il generatore riproducibile: spezzata fisicamente la linea esistente in due segmenti, tenendo il junction e il nuovo ramo verso VCO. **ERC da rieseguire prima di dichiarare PASS**.

## V1.4 simulazione parallela, NON modello vendor/AC14
`VCO_B_LOBUF_INPUT_LOAD_V1.4.cir` deriva dal deck reale V0.6 candidata B, aggiungendo l'effettiva polarizzazione passiva dell'input buffer R510/511/512 e C510. Per l'**ingresso Schmitt soltanto**, C=5p e i clamp D generici sono **ipotesi di carico e protezione**, non equivalenti al macro-modello TI. Run ngspice automatizzato ai punti VTUNE 8,10,12,15 V con misure di swing e massimo A−K del varicap, pubblicando JSON e log anche in caso di insuccesso; è consentito un risultato di screening elettrico FAIL senza nasconderlo.

Nessun modellamento delle soglie dinamiche Schmitt, jitter, inverter CMOS, separazione alimentazione, phase margin o lock. La CI deve registrare execution PASS distinto da RF validation NOT_RUN. **NO FAB / NO TX.**
