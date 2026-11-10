# V0.4 — VCO THT candidato, interfaccia LO, filtro PLL e controllo canali

**FASE: progettazione RF analitica preliminare + primo sottoschema KiCad nativo RX.**
I valori non sostituiscono una simulazione con modelli del produttore e NON autorizzano PCB/prototipo.

## 1. VCO THT candidato: capacità/induttanza fisiche

Candidato VCO analogico 36,310–39,000 MHz, stadio oscillatore a transistor **Q501 TO-92 NPN (es. 2N3904-AP MCC, da confermare con datasheet/pinout)**. Il solo valore fT dell'NPN NON dimostra l'avviamento o la stabilità RF, né il livello d'uscita; la topologia esatta (Clapp/Colpitts), i nodi di feedback, polarizzazione e il buffer devono essere chiusi in schema successivo.

Per la regolazione analogica consideriamo **D501 BB204G Philips, varicap doppio a catodo comune in TO-92, pin1=A1 pin2=K comune pin3=A2**. Fonte originale del produttore: https://datasheet4u.com/pdf-down/B/B/2/BB204G_PhilipsSemiconductors.pdf (specifiche 1996). La capacità per **singola giunzione** è **34–39 pF a 3 V**, **14 pF tipici a 30 V** (1 MHz); il rapporto è nominale, NON una garanzia a temperature/frequenze RF. Il secondo diodo va tenuto in configurazione elettrica sicura, non flottante a rischio di carica: soluzione da definire su schematico, eventualmente usando entrambi in configurazione controllata. **BB204G è materiale storico/NOS, reperibilità a lungo termine e autenticità aperte.**

**Studio matematico deliberatamente ideale con un solo diodo equivalente come capacità shunt**:
- L_eff = **220 nH** candidata, includerà tolleranze e parassiti della bobina THT;
- C_eff_fissa = **57,5 pF** (somma teorica di componenti, transistor, piste/parassiti e collegamenti; NON un condensatore fisico da 57,5pF scelto/ordinato);
- C_tot richiesta f=36,310 MHz = **87,330 pF**, cioè varicap equivalente **29,830 pF**;
- C_tot richiesta f=39,000 MHz = **75,699 pF**, cioè varicap equivalente **18,199 pF**.
- Con C(3V) 34–39pF e C(30V) **solo tipica** 14pF, lo spazio di capacità potrebbe coprire la banda in assenza di altri parassiti. **Il riferimento a 30V è un dato di caratterizzazione vicino al limite assoluto, non una tensione di esercizio da impostare**.
- Interpolazione in potenza *puramente assunta* tra punto stimato a 3 V **36,5 pF** (centro intervallo, NON tipico dichiarato) e 14 pF a 30 V: `C(V)=36.5*(V/3)^(-gamma)`, gamma=ln(36.5/14)/ln(10)≈0,416. Con questa sola ipotesi i punti LO di banda si collocherebbero a circa **4,87–15,97 V**; nessun convertitore/offset Vtune è stato selezionato né prova VCO reale effettuata.
- Interpolazione fuori da [3V,30V] vietata dal modello. La fonte non garantisce C(V) a 40 MHz; i valori reali potrebbero invalidare il progetto. Servono misura, tuning range con margine, Q, SRF, rumore di fase, stabilità termica e controllo dei varicap.

**Topologia candidate da chiudere:** Q501 NPN oscillatore con massa RF schermata, L501 e rete C fissa + D501 accoppiata al tank, separazione di DC tra tank e Vtune, bias resistor alto (es. 100k come punto di partenza), filtro noise Vtune e buffer Q502. Connessioni di transistor, bobina, varicap, polarità e bias NON finalizzate: evitare netlist di oscillatore inventata.

## 2. LO e condizionamento 39 MHz

Obiettivo doppio percorso dopo VCO: `LO1_ANALOG` → **buffer RF isolato e filtro LO** → mixer RX; derivazione separata → **limitatore/Schmitt ad alta velocità** → `LO1_CMOS_BUFFERED` → U402 TC74AC74P(F) pin3 clock a 5V. Un **SN74AC14N PDIP14** è disponibile come linea di prodotto TI attiva, ma il listino TI verificato non garantisce stock immediato; è un **candidato da verificare su forma d'onda a 39MHz**, non una conversione analogico-digitale automaticamente valida.

Sia buffer che limitatore devono essere dimensionati per ampiezza, distorsione, isolamento di carico e spur; progetto componente-per-componente (Q502, bias, C accoppiamento, terminazioni, alimentazione, pinout) da completare. **Non connettere direttamente la sinusoidale alla CLK CMOS.**

## 3. Filtro di anello: topologia e valori preliminari

La specifica Lansdale (pagina 28) riporta il filtro passivo **tipo B** per `PDout`: `PDout → R1 → nodo Vtune` con `R2` in serie a `C` fra Vtune e massa, la cui risposta ideale è `F(s)=(1+sR2C)/(1+s(R1+R2)C)`.

Per lo **studio, non per ordine/PCB**, assumiamo `R1=2,2kΩ`, `R2=10kΩ`, `C=100nF` THT. Zero ≈159,15 Hz e polo ≈130,46 Hz, entrambi distanti da fPFD=5000 Hz. Senza **guadagno Kphi corretto, Kvco misurato, rete di carico, fase e dinamica non è possibile certificare margine di fase, tempo di aggancio, spurie o stabilità**. Eventuali buffer/opamp di filtro dovranno essere THT.

**Non dichiarare un filtro compensato:** questa è soltanto una topologia con valori ipotetici e trasferimento analitico. Il Loop chiuso non è stato simulato.

## 4. Controllo 270 posizioni senza PLL moderno né DSP

Candidato **U601 Microchip PIC18F47Q43-I/P PDIP40**, segnalato dal produttore *In Production* e dai distributori come componente THT. Controller digitale semplice per leggere commutatore A-F, selettore canali e ALFA fisico, attribuire priorità CH9 e aggiornare linee parallele `N0..N11`; niente DSP, VOX, CTCSS/DCS o Dual Watch. **Il codice firmware e il pinout controller non sono stati sviluppati** in questa revisione.

Sequenza logica di cambio canale *candidata*: `RX_MUTE=ACTIVE` → validare scelta e tabella → presentare N[11:0] stabile → attendere riferimento e lock PLL continuo per intervallo da definire → `RX_MUTE=INACTIVE`. Alimentazione incoerente, RESET o N illegale → RX silenziata. Interblocco hardwired per TX sempre **OFF**, indipendente dal MCU e non rappresentato come comando software.

Per cambiare davvero 270 frequenze, serve valutare cablaggio interfacce (connettori, ingressi, pullup/pulldown, reset, tempistiche, debounce) e programma di prova; questa revisione definisce soltanto il contratto logico e la selezione del microcontrollore come candidato.

## 5. Prima realizzazione KiCad nativa e sue limitazioni

`04_KiCad/V0.4/PLL_PRESCALER_RX_V0.4.kicad_sch`: scheda **di sottosistema** digitale U402 e quattro connettori THT, tutti i pin del dual FF definiti con un simbolo personalizzato e `Package_DIP:DIP-14_W7.62mm`. `THT_V04.kicad_sym` e `sym-lib-table` forniscono la libreria locale. Pin2=D1 e pin6=/Q1 hanno la stessa net `DIV2_QBAR`; pin5=Q1 va a PLL fIN; quattro header collegano CLK, 5V, GND, RESET e feedback.

Questo **non è lo schematico completo radio e non include U401 o VCO**. I due punti d'uscita FF inutilizzata sono dichiarati NC; reset e CLOCK richiedono segnali esterni condizionati. I simboli sono **generati e controllati staticamente**; KiCad CLI non è installato nell'ambiente di lavoro: **l'apertura e KiCad ERC nativo sono NON ESEGUITI**. Nessun file `.kicad_pcb` o Gerber.

## Rischi ancora aperti
- ML145151YP quota/sourcing non confermati, BB204G NOS, buffer AC14 stock da confermare.
- VCO reale, parametri varactor @ 37MHz, oscillazione e mantenimento lock, drift reference SSB.
- Chiusura schematico U401/loop/VCO/MCU e KiCad ERC/DRC nativi.
- Controlli normativi TX e fabbricazione **NO FAB / NO TX**.

## Fonti
- Lansdale https://www.lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf
- Philips BB204G https://datasheet4u.com/pdf-down/B/B/2/BB204G_PhilipsSemiconductors.pdf
- SN74AC14 https://www.ti.com/product/SN74AC14
- PIC18F47Q43 https://www.microchip.com/en-us/product/pic18f47q43
- KiCad schematic format https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
