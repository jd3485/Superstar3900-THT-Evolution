# V2.7 — definizione verificabile della porta IF455 dal lato mixer (bozza, non mixer reale)

13 novembre 2026. **NON esiste ancora uno stadio mixer/IF completo qualificato nel master MAIN V2.6.** Questo test quantifica come *una sorgente di Thevenin puramente ipotetica* possa caricare il modulo IF455 isolato, senza inventare guadagno, noise figure o impedenza di un mixer non scelto.

## Collegamenti realmente presenti in KiCad9

Nel circuito standalone `04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch`:
- `J1601/1` = `IF455_SOURCE`, ingresso RF 455kHz **da definire rispetto alla vera uscita del mixer/IF**.
- `J1601/2` = `IF_BENCH_GND`, riferimento del banco, **non** progetto di ritorni/massa PCB RF definitivo.
- `J1602/1` = `IF455_FILTER_OUT`, uscita verso il rivelatore/buffer.
- `J1602/2` = `IF_BENCH_GND`.

Il risonatore comprende C1601=10pF ingresso, L1601=1mH, Rcoil=16,5Ω *assunta* come perdita a 455k, C1602=82pF e C1603=30pF trim, R1601=47k e C1604=10pF uscita, R1602=100k. I due connettori e le reti sono **un banco standalone**, non una connessione fisica nel master.

## Nuova prova ngspice nativa e criteri

`03_Verifiche/V2.7/verify_if455_two_port_source_impedance_native.py` svolge **8 vere AC ngspice** 300–650kHz / 1401 punti:
- 6 esperimenti `Rs=50Ω/1kΩ/10kΩ` ipotetici a monte × 2 carichi a valle (`R1602=100kΩ` e il solo surrogato **passivo** gate JFET 10p serie, 1M/7p a massa), riportando trasferimento sorgente→porta filtro e sorgente→uscita filtro, frequenza di picco e banda −3dB;
- 2 esperimenti indipendenti di impedenza complessa `Zin` intrinseca del circuito dalla porta J1601/1, con sorgente esterna disconnessa e sorgente di corrente AC 1A verso ingresso. `Zin` viene misurata con il carico downstream incluso ma **senza** la Rs ipotetica.

Il test verifica le etichette KiCad reali, riproduce le ampiezze a 455k della PR110 al caso Rs=50Ω entro 1%, impone perdita monotona di trasferimento per Rs che aumenta, e conserva il runner completo protetto. L'analisi è lineare a singola portante AC, non riproduce armoniche, spur, LO leakage, PVT, rumore flicker, termica RF attiva o curva d'impedenza del mixer.

## Condizioni da determinare per poter integrare l'interfaccia RX

Prima di disegnare un IF amplifier/buffer sul master, acquisire/definire attraverso modelli OEM e prove reali: **`Vth(f)`, `Zsource(f)` complessa**, impedenza e rumore del mixer e degli eventuali amplificatori IF, conversion loss/gain, controllo AGC ai min/max di segnale, clock/LO spur, return path e alimentazioni, filtro EMI/immagine e maschere AM/FM/SSB, rivelatore con ingresso non lineare e capacità, e budget SNR/SINAD audio. Il test non autorizza l'inserimento del KSP10BU/J113 né l'aggiornamento della BOM o una soglia di sensibilità antenna. Non confondere la resistenza di Thevenin proposta nel modello con `50Ω` di un'antenna o l'impedenza di uscita di uno stadio mixer reale.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** Le due PCB fisiche MAIN/FRONT e il master KiCad V2.6 rimangono invariati; niente DRC PCB.
