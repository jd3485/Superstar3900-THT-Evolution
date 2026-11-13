# V2.7 DRAFT — stadio IF455 KSP10BU THT a collettore comune

**Data 13 novembre 2026.** Primo schematico KiCad9 nativo isolato di uno stadio adattatore IF455 candidate, **non** progettazione definitiva della catena IF. Nessuna connessione fisica al MAIN V2.6, al tank IF455 o al demodulatore AM455; NO FAB / NO TX.

## Componente OEM e verifica reperibilità

- Transistor Q1701 **onsemi KSP10BU**, NPN RF, montaggio THT TO-92-3. Scheda tecnica OEM https://www.onsemi.com/pdf/datasheet/ksp10-d.pdf (2022 Rev.3), che indica **pin 1=BASE, pin 2=EMETTITORE, pin 3=COLLETTORE**; package 135AN. Contratto inserito nel simbolo KiCad embedded e nel verificatore nativo.
- Limiti OEM: VCEO 25V, VEBO 3V, Pd 350mW a 25°C, fT 650MHz **misurata a VCE=10V, IC=4mA e f=100MHz**: questi valori **non** sono guadagno a 455kHz, prestazione rumore IF o prova di robustezza.
- In data 13/11/2026 [DigiKey Italia](https://www.digikey.it/it/products/detail/onsemi/KSP10BU/1047203) indica `Active` e `Through Hole`. Il datasheet OEM conferma MPN e package, ma il produttore non è stato interrogato direttamente per un certificato di produzione; componente **candidato, NON finale qualificato**.

## Circuito KiCad realizzato

File `04_KiCad/V2.7_DRAFT/IF455_KSP10_FOLLOWER/IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT.kicad_sch`. Componenti fisici THT: 3 connettori da 2 poli (bench ingresso, uscita, 6V lab), 2 condensatori 10nF, 4 resistenze (22k bias alto, 10k bias basso, 2k2 emettitore, 100k carico), 1 Q1701 TO-92: **10 posizioni**.

Schema funzionale **collettore comune** (emitter follower), pilotaggio RF/IF solo in via esplorativa. L'ingresso è AC tramite C1701, il collettore collega il rail *LAB* 6 V, l'emettitore è polarizzato da 2k2 e l'uscita è AC tramite C1702. Il bias 22k/10k produce ~1,875V a vuoto e l'emettitore idealizzato ~1,2V, ma il carico della base, Vbe, β e temperatura possono modificare la polarizzazione. **Questa non è una stima di guadagno o impedenza RF validata** e i 6 V laboratorio **NON** provengono dal master della radio.

Reti previste:
- `IF455_TANK_OUT`: J1701.1, C1701.1
- `IFBUF_BASE_BIAS`: C1701.2, R1701.2, R1702.1, Q1701.1
- `VLAB6_IFBUF_ONLY`: J1703.1, R1701.1, Q1701.3
- `IFBUF_EMITTER`: Q1701.2, R1703.1, C1702.1
- `IFBUF_AC_OUT`: C1702.2, R1704.1, J1702.1
- `IF_BENCH_GND`: J1701.2, J1702.2, J1703.2, R1702.2, R1703.2, R1704.2

## Verifiche e blocchi

Il test `03_Verifiche/V2.7/verify_if455_ksp10_follower_native.py` esegue **KiCad 9 CLI ERC e export netlist** e verifica dieci riferimenti e tutte le pin-net sopra. Aggiunto alla FULL di Actions senza bypassare i controlli preesistenti. **Nessun PASS è dichiarato prima del completamento della CI sul commit finale**.

Il test nativo accerta connessioni CAD, NON MPN OEM attivo certificato, risposta RF o banda. Il footprint standard `Package_TO_SOT_THT:TO-92_Inline` necessita sovrapposizione orientamento numero pin ↔ package 135AN e clearance su PCB reale. Prima di integrarne la catena: simulare transistor con modello rappresentativo e corner, caratterizzare bias minimo/massimo, ampiezza, impedenza d'ingresso vista dal tank, guadagno/stabilità, rumore, alimentazione filtrata, EMI, selettività AM/FM/SSB e prova prototipo fisico. **Nessun progetto PCB o DRC di scheda reale; NO FAB, NO TX, NO BATTERIA/VEICOLO.**

## Esito reale PR #97 e gate CAD (13 novembre 2026)

[PR #97](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/97) **MERGED** `b16778889558d08c4fb8e98c54cd2d41a6238526`. GitHub Actions [#43468430403](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43468430403) sul final HEAD tecnico `1807d9520aab12f9e49154073bf5abbe01e5d964`: **FAST + FULL + required gate 3/3 SUCCESS**; 111 comandi legacy FULL eseguiti e il nuovo test nativo KiCad9 `PASS_NATIVE_KICAD9_IF455_KSP10BU_BENCH_THT10_PINPAD_NET_ERC0_NO_FAB_NO_TX`. Report ERC: **0 errori, 0 warning**. Esportazione e controllo netlist native KiCad9: **10 riferimenti fisici e 6 reti** come nel contratto.

La prima CI segnalava 3 errori reali (ingresso C1701 scollegato + etichette) e 11 warning; la seconda solo 10 warning per la libreria non riconosciuta. Correzione effettiva del filo e registrazione della libreria `TH_IFBUF` tramite `TH_IFBUF.kicad_sym`, `sym-lib-table`, file `.kicad_pro`. **Nessuna deroga ERC.** Non è ancora un amplificatore RF/IF qualificato: manca un modello rappresentativo validato, misura di rumore, gain/stabilità/PVT, impedenze reali e prova hardware. Master V2.6 invariato; nessuna PCB fisica e NO FAB/TX.
