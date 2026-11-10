# Rapporto tecnico V0.3 — primo nucleo circuitale PLL THT

**Data:** 10 novembre 2026. **Repository:** `jd3485/Superstar3900-THT-Evolution`. **Ambito:** primo schema concettuale/pin-to-net con componenti THT reali e modello numerico RX; nessun prototipo fisico. NON è un rilascio di produzione.

## Novità ingegneristiche
- Selezionata **solo per lo sviluppo circuitale** la soluzione A1 `ML145151YP` Lansdale **DIP28** compatibile con vecchio `MC145151P2` Motorola (legacy) + `TC74AC74P(F)` Toshiba **DIP14** che usa un flip-flop come divisore /2; resta valida una seconda topologia con `CD74HC4046AE` e contatori discreti DIP qualora A1 sia impraticabile.
- Realizzata `04_KiCad/V0.3/PLL_U401_U402_PINNET_V0.3.csv` con **28/28 pin** U401 e **14/14 pin** U402, segnale/funzione/rete associati. Verificati i pin rispetto alle figure del datasheet originale Lansdale (pagina 2) e Toshiba. **La matrice non è una netlist completa**, né un vero `.kicad_sch`.
- Riferimento oscillatore candidato `X401 = Citizen HC-49/U-S10240000ABJB` THT, 10.240 MHz, capacità carico 18 pF. Con C403/C404=22 pF e parassiti **assunti** si ottiene CL≈17,727 pF; oscillazione e drive non dimostrati.
- `R=2048` via `RA2 RA1 RA0=1 0 1`; T/R=1 RX; `fPFD=10.240 MHz/2048=5 kHz`; clock VCO 36,310–39,000 MHz; U402 /2; U401 fin 18,155–19,500 MHz, N=3631..3900 per tutte le 270 posizioni. **Il funzionamento del PLL non è provato.**
- CH9 di prova D/9 27,065MHz: LO=37,760MHz, fIN=18,880MHz, N=3776/0xEC0, bit alti N6 N7 N9 N10 N11.
- Documentati R/C decoupling, pull-up T/R, reset provvisorio e connettori candidati; i nodi reset, VCO, carica loop, selezione N, mute e alimentazione restano **interfacce non chiuse**.
- Ordine di grandezza VCO LC puramente ideale L=220nH: Ceff=87,330pF @36,310MHz e 75,699pF @39,000MHz. Non è uno schema di oscillatore funzionante.
- BOM candidato THT di 13 righe, nessun ordine o footprint definitivamente approvato.

## Rischi e limiti individuati
1. **Fornitura U401:** il costruttore Lansdale documenta `ML145151YP` (PDIP28) e offre consultazione/preventivo, ma **stock, minimo d'ordine, prezzo e tempi di consegna non sono verificati**; nessun acquisto consigliato prima di risposta.
2. **Precisione SSB:** il quarzo Citizen selezionato come primo candidato è ±30 ppm iniziali, stabilità ±50 ppm; errore equivalente LO fino a ±1170 Hz iniziale e budget pessimistico fino a ±3120 Hz, **insufficiente come riferimento finale SSB senza correzione o scelta di riferimento più stabile**.
3. **Condizionamento clock RF:** Toshiba specifica frequenze logiche sufficientemente alte per una parte /2 a 39MHz, ma ciò **non dimostra** compatibilità dei livelli, duty, slew e drive RF. Una sinusoide VCO non deve essere collegata direttamente al clock CMOS.
4. **PLL closed-loop:** mancano stadio VCO reale, buffer/limitatore RF, filtro loop dimensionato, guadagno Kvco e fase/margine/tempo di lock, verifica di spur e offset; il modello ideale non ne dimostra alcuno.
5. **Fail-closed RX:** selezione parallela N da 270 posizioni, power-good, reset, mute e lettura lock non sono progettati fisicamente; `LD` da solo non è un interblocco robusto.
6. **PCB e sicurezza:** assenti schematico KiCad, layout, ERC/DRC, simulazioni SPICE, prove di laboratorio e valutazioni normative. Nessun permesso PCBWay o TX.

## Verifiche software predisposte
| Gruppo | Numero test | Stato fino a verifica CI GitHub | Limitazioni |
|---|---:|---|---|
| V0.1 | 12 | Da rieseguire in CI | Solo requisiti/struttura |
| V0.2 | 24 | Da rieseguire in CI dopo correzione del riferimento di configurazione | Solo aritmetica canali e PLL |
| V0.3 | 32 | Da eseguire in CI | Pinout CSV, numeri, BOM, invarianti |
| KiCad ERC / DRC | — | **NON ESEGUITO** | Nessun `.kicad_sch` completo |
| Simulazione elettrica SPICE / RF | — | **NON ESEGUITA** | Modelli IC/VCO non implementati |
| Hardware / laboratorio | — | **NON ESEGUITO** | Zero prototipi |

La CI aggiunta controlla anche che i due pinout DIP abbiano ogni pin dichiarato una sola volta, il cablaggio dei 12 bit N sia coerente, la frequenza divisa sia nel range nominale dei datasheet e TX rimanga falsa nel modello. **Un test PASS non prova il circuito reale**.

## Fonti tecniche
- Lansdale ML145151 famiglia: https://www.lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf — pagine 2–4 e caratteristiche elettriche a fine PDF
- Toshiba TC74AC74P: https://toshiba.semicon-storage.com/info/docget.jsp?did=3156&prodName=TC74AC74P — pinout e timing
- Citizen 10,240MHz: https://www.digikey.com/en/products/detail/citizen-finedevice-co-ltd/HC-49-U-S10240000ABJB/284210 — packaging, tolleranza, stabilità
- NXP MC145151-2: https://www.nxp.com/products/MC145151_2 — storico produzione dismessa

## Risultato e prossima revisione
**V0.3 = primo circuito candidato a livello di pin, con rischi documentati, non PCB funzionante.** **NO FAB / NO TX**.

**V0.4**: confermare presenza e disponibilità di U401, sviluppare VCO THT con transistor/varicap e buffer di clock, calcolare loop filter e stabilità con modelli/parametri verificati, progettare selezione N/lock/mute e alimentazione, quindi creare uno schematico KiCad nativo coerente, senza forzare un ERC PASS quando mancano parti.

## Esito GitHub Actions V0.3 verificato dopo integrazione

- Run: [42807584674](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42807584674)
- Commit verificato: `c73b918acc4d1852b58e590ea84657ab52c0ef89` sul branch `main`.
- Job `static-regression`: **SUCCESS**. Passi `Baseline V0.1 structural tests`, `V0.2 channel plan and candidate PLL arithmetic tests` e `V0.3 PLL pinout and candidate THT core static checks` tutti **SUCCESS**.
- Esito dichiarato delle suite: **12 V0.1 + 24 V0.2 + 32 V0.3 = 68 test software**, tutte le tre suite eseguite senza errori da GitHub Actions.
- **NON ESEGUITI**: validazione circuitale SPICE, KiCad ERC/DRC, EM, laboratorio, qualifica alimentazioni, prototipo, TX. **NO FAB / NO TX**.
