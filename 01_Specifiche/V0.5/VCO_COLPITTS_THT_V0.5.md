# V0.5 — Primo VCO Colpitts THT con doppio varicap; correzione architettura PLL

**Candidato per banco di simulazione RX**, non circuito approvato alla costruzione né schematico integrato. Frequenza obiettivo LO1 high-side: 36,310–39,000 MHz. Tutte le grandezze RF devono essere validate con simulatore transistor/varicap e poi strumenti reali; nessun TX.

## 1. Scelta migliorativa rispetto a V0.4

La V0.4 considerava **una giunzione** BB204G, L=220nH e Vtune nominale 4,7–16V. Questo crea un problema concreto: `PDout` del PLL alimentato a **5V** non può generare 16V usando solo un filtro RC passivo. Per V0.5 preferiamo **due giunzioni BB204G in parallelo, entrambe in polarizzazione inversa**, con L=150nH, capacità parassita/fissa complessiva circa 61pF. Il modello con ancore 3V/30V stima Vtune ~3,13–6,95V: un amplificatore di controllo THT su rail analogica 12V rimane necessario.

**BB204G è un componente storico in TO-92**. Pin fisici da datasheet Philips: **1 anodo A1, 2 catodo comune, 3 anodo A2**. In V0.5 **pin1 e pin3 sono entrambi collegati a VAR_A**, pin2 a VTUNE_RAIL: niente terminali flottanti. Il nodo VAR_A ha R505=100k a massa per definire il potenziale DC; **C504=1nF** separa VAR_A dalla tensione continua del collettore. Catodo polarizzato positivamente con Vtune 3–8V previsto; un condensatore THT di disaccoppiamento C505 verso massa stabilizza la tensione RF sulla linea di controllo. Verificare che ampiezza RF non porti alcuna giunzione in conduzione e che le perdite siano ammissibili. Nessun ordine componenti.

## 2. Prima topologia elettrica, parametri di studio

**Q501** `2N3904-AP`, MCC TO-92: pin1 E, pin2 B, pin3 C secondo libreria DigiKey (ricontrollare su datasheet al momento del footprint). **Colpitts a base RF comune** con:
- R501 33kΩ +9V_RF→BASE1 e R502 10kΩ BASE1→GND, C501 1nF BASE1→GND: bias DC ideale circa 2,09V, base a massa RF.
- Q501 emitter **EMIT1**; R503 330Ω EMIT1→GND. Corrente ideale emettitore (senza carico della base) circa 4,22mA.
- L501 **150nH THT** +9V_RF→TANK. C502 **68pF C0G** TANK→EMIT1; C503 **220pF C0G** EMIT1→GND. Capacità di serie del feedback circa 51,94pF; con Cjc, piste, bobina e trimmer il totale **61pF è un'assunzione**, non una distinta fisica. La componente *resonant* del circuito comprende C502/C503 in serie e D501/C504.
- C504 1nF TANK→VAR_A; D501 A1/A2→VAR_A e K comune→VTUNE_RAIL; R505 100k VAR_A→GND; C505 100nF VTUNE_RAIL→GND. Uscita RF tank isolata con C506=2,2pF verso buffer.
- Alimentazione sperimentale +9V_RF esterna da rail protetta/filtrata da definire, C500 100nF THT vicino a Q501 e C500B 10µF verso GND.

**Q502** 2N3904-AP TO-92, stadio emitter follower di isolamento: pin3 COL2→+9V_RF, pin2 BASE2 dopo C506=2,2pF; R506=47k +9V_RF→BASE2, R507=22k BASE2→GND; pin1 EMIT2 con R508 470Ω→GND; C507 100pF EMIT2→LO1_ANALOG_OUT. Nessuna pretesa di ampiezza/impedenza/drive mixer. La variazione di carico dell'emitter follower può perturbare il tank; isolamento e ampiezza devono essere simulati e misurati.

## 3. Modello riproducibile e limiti

`03_Verifiche/V0.5/VCO_COLPITTS_CANDIDATE_V0.5.cir` è un **circuito SPICE candidabile a ngspice**: 2 transistor con un modello BJT *approssimato* e 2 giunzioni diode con fit non certificato; include reti RLC e alimentazioni. Il fit `Cj(V)=Cjo/(1+V/0.8)^M` è vincolato alla metà dell'intervallo C3=34–39pF e al valore tipico C30=14pF: **non è un modello SPICE ufficiale**, né garantisce le caratteristiche della varicap a 37–39MHz. Emettitore e base sono schematizzati; **startup oscillazione, frequenza simulata, VCO swing, rumore, spurious e deriva non sono qualificati finché non gira una simulazione e se ne analizza il log**.

Con L=150nH e `C_fixed_eff=61pF` assunta, includendo C504 in serie alle due giunzioni, la sola formula LC richiede tensione nominale ~3,13–6,95V per 270 posizioni. Il test include la verifica della completa finestra, non la garanzia per estremi di tolleranza. Questo spazio di tuning dipende in modo critico dal valore **effettivo** dell'induttore e dalle capacità parassite; prevedere trimmer THT, punto prova RF ad alta impedenza e budget tolleranze, altrimenti la copertura non è garantita.

## 4. Correzione del filtro loop e della catena di controllo

**Criticità strutturale individuata:** il filtro V0.4 R1=2,2kΩ, R2=10kΩ, C=100nF è un partitore lead-lag ma per il solo modello lineare `H(s)=(1+sR2C)/(1+s(R1+R2)C)`: al riferimento comparatore **5kHz attenua appena ≈−1,73dB**. Non è sufficiente dichiararlo un buon soppressore di spurie. **V0.4 resta storica, non va riutilizzata in produzione come filtro validato.**

Per confrontare la reiezione, modello passivo a due poli `PDout → R601=10k → N1 (C601=10nF a GND) → R602=10k → N2 (C602=100nF a GND)` (ingresso driver ideale): ampiezza a 5kHz **≈−41,43dB** *teorici*. **NON è un filtro di PLL stabilizzato**: due poli aggiungono ritardo di fase e potrebbero impedire l'aggancio. Il valore finale richiede un'analisi del loop chiuso con Kphase, Kvco reale, ripple e tempo di aggancio, con MCU mute su retune.

Per uscire dai 5V del PDout candidato, **U602 LM358N PDIP8** (o equivalente realmente THT con specifiche compatibili) è solo **driver non invertente candidato** con 12V regolati e guadagno ideale circa ×2: input da N2, R603=10k a GND, R604=10k feedback, output→VTUNE_RAIL tramite eventuale resistenza filtro/isolamento da dimensionare. L'amplificatore ha limitazioni di rumore, banda, slew, range di uscita e stabilità su capacità da verificare: non è stato testato a loop chiuso. Un DAC SMD o modulo SMD non è ammesso.

## 5. Selezione dei 270 canali e sicurezza

MCU THT `PIC18F47Q43-I/P` resta candidato, con controllo N e priorità CH9. V0.5 aggiunge un **modello firmware di riferimento (Python, NON compilato XC8)**: quando si cambia canale attiva il mute RX, applica N e richiede stabilità continua di alimentazione/referenza/PLL e contatore di tempo qualificazione (parametro da validare). Qualsiasi cambiamento, perdita lock, reset e scelta invalida mantiene mute. **Non esiste alcun codice che abiliti TX**.

Il controller andrà poi realizzato con pinout PIC, driver/pull-up N[11:0], reset hardware, detector lock e output RX MUTE. I pin MCU e il software XC8 sono lavori successivi.

## 6. Collaudi obbligatori aperti
1. Modello SPICE VCO: ottenere oscillazione 36,31–39MHz con Vtune in range, waveform, ampiezza sufficiente e startup, senza saturazione o varicap in avanti.
2. Vtune e circuito driver: modello PLL completo e phase margin; nessun risultato di ripple conferma aggancio.
3. Verifica pinout fisici con datasheet ufficiali e stock BB204G; scegliere alternativa THT reperibile per evitare scheda non assemblabile.
4. Creare completo KiCad `.kicad_sch` con tutti R/L/C/Q/D, simboli footprint THT e eseguire ERC reale. L'intero LO/TX/RF receiver è ancora incompleto.
5. NO PCB/Gerber/ordine PCBWay e NO TX prima di gates.

## Riferimenti
- Philips BB204G TO-92: https://studfile.net/preview/16503981/
- DigiKey library MCC 2N3904-AP: https://github.com/Digi-Key/digikey-kicad-library/blob/master/digikey-symbols/dk_Transistors-Bipolar-BJT-Single.lib
- TI SN74AC14 PDIP14: https://www.ti.com/product/SN74AC14
- Microchip PIC18F47Q43-I/P: https://www.digikey.it/it/products/detail/microchip-technology/PIC18F47Q43-I-P/11495049
