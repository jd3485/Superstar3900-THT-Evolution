# V1.2 — Prima integrazione elettrica KiCad reale del PLL RX THT
Data 10 novembre 2026. Repository indipendente `jd3485/Superstar3900-THT-Evolution`.

## Delta fisico CAD
Generato `04_KiCad/V1.2/PLL_RX_MASTER_CAD_V1.2.kicad_sch` **integrando nello stesso foglio KiCad elettrico** il CAD-02 V1.1 (U401/U402/quarzo) e il CAD-01 V1.0 (R901/C901 + LM358N U803). Le librerie THT locali precedenti sono preservate, i componenti del filtro sono traslati dentro un A2, e una sola sorgente di PWR_FLAG GND è mantenuta per evitare driver artificiali duplicati. Si conserva ogni sorgente precedente, senza importare componenti dalla SMD.

**Connessione reale nuova:** `U401 pin4 PDout` e `R901 pin1` condividono l'unico nodo `PLL_PDOUT_3STATE` in un netlist KiCad *integrato*, senza cavi immaginari. Prosegue elettricamente R901 → C901/ingresso `U803 pin3` e driver LM358 di riferimento. Anche `U402 pin5 → U401 pin1` (/2), clock cristallo, bus codici e rail separati sono nello stesso file.

## Precisi limiti del risultato
- È un **pilota master piatto (single-sheet)**. La topologia gerarchica finale, VCO, alimentazione regolata, LO buffer CMOS e MCU N-code non sono ancora integrati; `VTUNE_RAIL` resta un'uscita esterna non terminata su varicap.
- Le due prese originali J401/J901 sono **interfacce di laboratorio temporanee**, non prese obbligatorie della PCB finale.
- `R901=22 kΩ`, `C901=100 nF` provengono dal CAD-01 V1.0; rispetto ai candidati V0.9 (10/47 kΩ e 1µF) **nessuna compensazione fisica è qualificata**. Il driver LM358 può non avere margine di uscita sufficiente a 15 V.
- `+5V_PLL` e `VANA20_FILT` sono **alimentazioni indipendenti esterne**; senza circuito di powergood/mute fisico. Nessun PLL closed-loop, stabilità/phase margin, RF lab, warmup, EMC/EMI o tolleranze vendor testati. **NO FAB / NO TX**.

## Validazione riproducibile
- `genera_master_rx_v12.js` legge i due .kicad_sch reali precedenti e ricostruisce la stessa V1.2 bit-per-bit.
- `.github/workflows/cad_native_v12.yml`: KiCad9 ERC senza waivers, export netlist e SVG, verifica vera U401 pin4 ↔ R901 pin1 ↔ U803 pin3 via due reti reali (il filtro R901 sta fra PDout e ingresso).
- `03_Verifiche/V1.2/verify_integrated_netlist_v12.py` verifica pin-nets di core e driver, tutti i 28 pin U401, i 14 pin U402 e gli 8 pin U803; rifiuta falsi collegamenti all'uscita PLL.
- Il gate nativo è stato verificato con evidenza finale qui sotto; restano NON ESEGUITI i gate della radio completa.

## Prossimo blocco
Passare dal pilota piatto alla gerarchia di schemi con pin e interfacce espliciti, aggiungere il reale VCO candidato e il buffer LO, alimentazione THT e lock/mute fisico, sviluppando contemporaneamente SPICE vendor/di riferimento, BOM e sorgenti MCU. PCB solo quando è tecnicamente il momento, e sempre NO FAB / NO TX prima dei gate.

## Correzione geometrica V1.2

Il primo ERC nativo ha identificato **41 avvisi `endpoint_off_grid`** nel blocco CAD-01 traslato: coordinate originali corrette ma offset arbitrario (300, 10 mm) non multiplo della griglia di connessione. Il generatore ora applica una traslazione **(+304,8 mm, +10,16 mm)**, cioè multipli esatti di 1,27 mm, mantenendo tutte le connessioni originali. **Rieseguire ERC e netlist prima di qualunque dichiarazione PASS.**

## Verifiche V1.2 effettivamente concluse
- Primo workflow fallito: [run 42877986723](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42877986723), **41 warning esclusivamente `endpoint_off_grid`** dovuti al precedente offset non allineato al reticolo.
- Correzione del generatore: offset X+304,8 / Y+10,16 mm, entrambi multipli della griglia KiCad 1,27 mm, senza modificare connessioni o caratteristiche elettriche.
- [Run 42878584174](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42878584174) **SUCCESS**: KiCad9 ERC nativo **0 violazioni**, export netlist **33 reti**, **28 gruppi di pin-net verificati** inclusa U401 pin4 ↔ R901 pin1, rigenerazione deterministica e SVG.
- Sullo stesso commit del branch: 8 workflow principali (KiCad V1.0/V1.1/V1.2, regressioni storiche e 4 ngspice) superati, più seconda run CAD V1.2 riuscita.
- Nessuna verifica `kicad-cli pcb drc`: non esiste `.kicad_pcb` integrata. Hardware, fase/lock reali, EMI, TX, produzione NON ESEGUITI e NON AUTORIZZATI.

**Qualifica:** `ERC_PASS_FLAT_PARTIAL_RX_PLL`, **non** `CAD_INTEGRATED_RADIO`, `PCB_ROUTED` o `LAB_PASS`.
