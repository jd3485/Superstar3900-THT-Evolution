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

## Evidenze effettive su GitHub Actions

[PR #117](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/117) fusa con SHA `403846c498f3ab8db138d9c01e68cab435bef9db`. GitHub [run #43514708784](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43514708784) sul final head `84a45e659e575ea245dfc4bcfae991ecc915cbba`: FAST, FULL KiCad9/ngspice e required **3/3 success**; 111 comandi regressivi storici e 8 analisi AC native nuove.

| Downstream | Rs ipotetica | |V(J1601/1)/Vs| a 455k | |V(J1602/1)/Vs| a 455k | fpeak | banda −3dB |
|---|---:|---:|---:|---:|---:|
| R100k banco | 50Ω | 0,998737253 | 0,835055562 | 454,75kHz | 42,557kHz |
| R100k banco | 1kΩ | 0,975017775 | 0,815223437 | 454,75kHz | 43,597kHz |
| R100k banco | 10kΩ | 0,780455755 | 0,652547922 | 456,25kHz | 53,201kHz |
| Gate JFET solo surrogato passivo | 50Ω | 0,998673780 | 0,665186786 | 450,25kHz | 36,296kHz |
| Gate JFET solo surrogato passivo | 1kΩ | 0,973943467 | 0,648714664 | 450,25kHz | 37,286kHz |
| Gate JFET solo surrogato passivo | 10kΩ | 0,780046990 | 0,519566010 | 451,75kHz | 46,378kHz |

Il rapporto di **modulo** `|Vout|/|Vin al pin|` è costante al variare di Rs nel modello lineare a 455k (~0,83611 con R100k, ~0,66607 con gate passivo), ma non è un guadagno di potenza e non fornisce la fase né l'impedenza di un dispositivo reale. `V(J1601/1)` dipende dal partitore complesso sorgente/rete. Con generatore **scollegato** il filtro ha `Zin(455k)=18530,8105−j19747,3349Ω` (R100k, modulo27080,402Ω) oppure `23604,5788−j18218,5022Ω` (gate surrogato, modulo29817,612Ω). La componente immaginaria risulta capacitiva.

Il primo [workflow #43513982822](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43513982822) è **fallito**, bloccato dal controllo letterale `H455` non presente nel precedente script, **prima** delle nuove simulazioni; non è una discrepanza hardware o elettrica. Contratto del test corretto e nuova FULL PASS #43514708784. Nessuna rinuncia a gate/controlli.

Questa prova **NON giustifica** collegare a J1601/1 un mixer la cui impedenza d'uscita non è caratterizzata; il prossimo passo non è imporre `50Ω` nel CAD ma scegliere un mixer reale, modellarne il carico e confermare conversion gain, stabilità e rumore.
