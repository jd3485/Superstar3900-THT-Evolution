# V2.7 — contratto IF455 → rivelatore AM455 THT (solo banco)

**13/11/2026.** Questo file definisce il primo accoppiamento **logico fra due schemi KiCad9 esistenti**, e impone una verifica nativa delle loro netlist. **Non esiste un cavo reale, una PCB-MAIN integrata, né un amplificatore IF finale.** Il passaggio è solamente di **radiofrequenza 455kHz AM** fra sottocircuiti da laboratorio, senza alimentazione o collegamenti TX.

## Collegamento previsto fra i moduli

| Sorgente: IF455 TANK | Destinazione: AM455 ENVELOPE | Significato |
|---|---|---|
| J1602 pad1 (`IF455_FILTER_OUT`) | J1501 pad1 (`IF455_BENCH_IN`) | 455 kHz AM IF da banco in uscita dal filtro, ingresso all'anodo **D1501 pin2** |
| J1602 pad2 (`IF_BENCH_GND`) | J1501 pad2 (`IF_BENCH_GND`) | massa/ritorno comune da banco |

Sul filtro J1602 pad1 è collegato a **C1604 pin2 e R1602 pin1**; sul rivelatore J1501 pad1 è collegato a **D1501 pin2 anodo**. L'uscita analogica AM demodulata **J1502 pad1** passa da **C1502 pin2**; l'altra estremità J1502 pad2 è massa IF. I pilot sono ancora **indipendenti**, con pin header 2,54 mm generici, privi di una distinta di cavo e di qualifica della meccanica.

## Verifica eseguibile

`03_Verifiche/V2.7/verify_if455_am455_interface_native.py` esporta **due netlist KiCad9 reali con `kicad-cli sch export netlist`**, controlla singoli riferimenti e pad sulle reti e impone corrispondenza biunivoca del segnale/ritorno. Controlla che non compaiano sulle due partizioni rail audio `AUDIO_6V_LAB`, PLL, TX, 13,8V o antenna. È aggiunto alle regressioni **FULL** esistenti, non genera un altro job GitHub Actions. Una CI `PASS` indica esclusivamente consistenza del contratto fra due CAD autonomi, **non continuità fisica o qualità RF**.

## Rischio elettrico sostanziale non risolto

Il detector 1N4148 non polarizzato è **non lineare** e cambia il carico che il tank IF455 vede attraverso C1604 10 pF. La risposta AC a R1602=100kΩ in parallelo nell'attuale studio ngspice **non rappresenta l'ampiezza né l'impedenza del vero diodo in conduzione**. Anche se l'uscita J1602 e l'ingresso J1501 sono collegati correttamente sul piano pin↔net, la prima rilevazione AM potrebbe scendere o distorcere considerevolmente con il carico reale. Serve un vero **studio dinamico con tank + rivelatore + trimmer**, modello diodo OEM o parametrico esplicitamente documentato, e misure a livelli IF diversi. In più vanno progettati guadagno IF, controllo AGC e la catena completa del SuperStar 3900 separata per FM e SSB.

**Limitazioni/meccanica:** C1603 EW GKG50015 ha footprint da disegno OEM 5mm/foro1,2mm (PR #86); L1601 Delevan 2500-28J conserva footprint PROVISIONAL non approvato, e nessuno dei connettori IF ha mating/cavo qualificati. Nessuna PCB 2-board, layout e DRC assenti. MASTER V2.6 7 fogli/138 ref, audio/AM/IF stand-alone invariati. Completamento totale circa 20% stimato, routing 0%. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
