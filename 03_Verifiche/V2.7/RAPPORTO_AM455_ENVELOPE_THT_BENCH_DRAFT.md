# V2.7 DRAFT — primo rivelatore AM 455 kHz THT, esclusivamente laboratorio

**13 novembre 2026 — bozza NON integrata nella MAIN V2.6.** Nuova sezione KiCad9 **reale** `04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch`, libreria TH_DEMOD, progetto e sym-lib-table locali. Lo schema serve per provare su banco la demodulazione **AM a inviluppo** di un segnale IF sufficientemente grande applicato da un generatore, **non** è un ricevitore di antenne/27 MHz, non è un demodulatore FM, SSB o CW e non è connesso al master né alla PCB-FRONT.

## Motivazione e architettura radio

Il manuale Superstar 3900 pubblicato su CB Radio NL riporta **AM/FM con 1ª IF 10,695 MHz e 2ª IF 455 kHz**, mentre **SSB lavora a 10,695 MHz**: [manuale famiglia Superstar 3900, sezione receiver](https://www.cbradio.nl/superstar/Downloaded/Manual_Superstar_SS3900_ENG_ESP_FR_PT_DE_PO_FL.pdf). Il manuale tecnico EPT360014B è utile come riferimento storico per componenti IF, demod FM, AGC e S-meter, ma **non autorizza** a copiare la taratura di componenti non qualificati: https://cbradio.nl/superstar/Downloaded/Service_Manual_Superstar_SS3900_EPT360014B_Homer_ENG.pdf . La nostra architettura completa a 2 PCB deve distinguere percorsi AM/FM a 455k e SSB a 10,695M con selezione e rivelazione dedicate, senza promettere prestazioni su tutte le modulazioni.

## Circuito elettrico e sette posizioni 100% THT

| Ref | Componente / funzione | Connessioni nativa previste |
|---|---|---|
| J1501 | connettore 2 pin THT, solo sorgente da banco AM IF 455kHz | pin1 `IF455_BENCH_IN`; pin2 `IF_BENCH_GND` |
| D1501 | diodo di segnale DO-35 THT, **Vishay 1N4148-TAP candidato** | **anodo pin2** ingresso 455k; **catodo pin1** rete `AM_RECTIFIED_ENV` |
| R1501 | 47kΩ 1%, 0,25W assiale, carico di rivelazione | `AM_RECTIFIED_ENV` → `IF_BENCH_GND` |
| C1501 | 1nF 50V C0G THT, filtro RF del rivelatore | `AM_RECTIFIED_ENV` → `IF_BENCH_GND` |
| C1502 | 100nF 50V film THT, accoppiamento AC | `AM_RECTIFIED_ENV` → `AM_DEMOD_AF_BENCH` |
| R1502 | 100kΩ 1%, 0,25W, riferimento AC dopo condensatore | `AM_DEMOD_AF_BENCH` → `IF_BENCH_GND` |
| J1502 | connettore 2 pin THT AF OUT, da banco | pin1 `AM_DEMOD_AF_BENCH`; pin2 `IF_BENCH_GND` |

Riferimento OEM **diodo solo candidato**: [Vishay 1N4148, datasheet DO-35 e codice ordinabile 1N4148-TAP](https://www.vishay.com/docs/81857/1n4148.pdf). **Non dichiarare ancora MPN qualificato per fabbricazione**: stato produzione, temperatura, capacità e comportamento a debole segnale, geometria del footprint e montaggio reale restano da confermare. I riferimenti R/C hanno specifiche standard preliminari coerenti con ADR-002, non BOM finale. La serigrafia della fascetta indica il **catodo**, corrispondente al pad 1 del simbolo D1501; il verso è protetto anche da test netlist.

## Scelta valori e limitazioni fisiche

- `τ = 47kΩ × 1nF ≈ 47µs`: è **molto maggiore** del periodo IF `1/455kHz ≈ 2,20µs` e **minore** del periodo di una voce a 2,8kHz `≈357µs`. È un compromesso di prova, non filtraggio IF calibrato.
- Per il filtro RC lineare equivalente, `fc≈1/(2π×47µs)≈3,39kHz`. **Un vero envelope detector a diodo è non lineare**, la risposta RF ripple e la distorsione da scarica/diagonal clipping variano con profondità modulazione, impedenza del segnale e livello.
- Per l'accoppiamento C1502 in serie a R1502=100kΩ, `fc≈1/(2π×100k×100nF)≈15,9Hz` **soltanto** se il carico del prossimo stadio non altera la resistenza equivalente; il potenziometro FRONT 10k potrebbe abbassare drasticamente l'impedenza vista. Prima di unire il circuito al volume occorre progettare buffer/carico e recupero guadagno.
- **Diodo al silicio senza polarizzazione:** con segnali IF di livello basso potrebbe quasi non rivelare nulla. Questo pilot **richiede segnale AM IF abbastanza ampio da banco** e non è qualificato per sensibilità ricevitore in µV, guadagno IF, AGC, selettività, FM o SSB.
- Il manuale indica per alcune versioni radio **alcuni watt audio su 8Ω**; il nostro pilota LM386 produce centinaia di milliwatt nelle condizioni TI, quindi **non si può affermare equivalenza all'audio originale**. L'obiettivo di potenza e l'amplificatore finale devono essere riesaminati prima del congelamento.

## Verifica tecnica indipendente aggiunta alla FULL CI

Il test `03_Verifiche/V2.7/verify_am455_bench_native.py` esegue **davvero** `kicad-cli sch erc --exit-code-violations`, esporta netlist KiCad9 e controlla **pin↔net** della porta ingresso IF, verso del diodo, R/C, uscita AF e ritorno di massa. Verifica esattamente **7 refs THT e quattro reti**, senza waiver. Il test è agganciato a `ci/full_regressions.py` dopo le verifiche storiche; il job FULL esistente non è duplicato. **Prima di dichiarare PASS è necessario vedere la CI del commit finale della PR.**

**Gate aperti:** amplificatore IF selettivo a 455k, filtri ceramici/trasformatori e MPN attivi, mixer 10,695→455, IF/SSB 10,695, discriminatore FM, detector SSB/BFO, AGC, S-meter analogico, squelch, ANL/NB, protezioni, PCB, ritorni RF, carichi di ingresso e di uscita, prove di sensibilità/SINAD e distorsione. Nessuna emissione o prova su antenna; alimentazione del rivelatore non presente perché passivo.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO**. Master MAIN V2.6 sette fogli/138 riferimenti invariato; questa è una **quarta sezione autonoma V2.7 DRAFT** e non incrementa automaticamente la baseline BOM o la percentuale di routing 0%.
