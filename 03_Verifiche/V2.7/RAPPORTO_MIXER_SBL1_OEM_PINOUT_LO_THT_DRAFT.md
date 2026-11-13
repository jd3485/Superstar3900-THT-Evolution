# V2.7 — candidatura mixer THT Mini-Circuits SBL-1+: simbolo KiCad9 OEM e budget LO

**13 novembre 2026 — solo revisione di fattibilità / simbolo CAD nativo. Nessuna scelta mixer definitiva.**

## Fonti originali e confronto dei candidati

- **NXP SA612AN**: il costruttore indica esplicitamente *No Longer Manufactured* per DIP8. Scheda originale: https://www.nxp.com/products/SA612AN . **Respinto** per requisito di produzione OEM corrente.
- **Mini-Circuits SBL-1+**: scheda OEM https://www.minicircuits.com/pdfs/SBL-1%2B.pdf e pagina prodotto https://www.minicircuits.com/WebStore/dashboard.html?model=SBL-1%2B . Mixer **passivo doppio bilanciamento**, package **A06 plug-in THT**, RF e LO 1–500MHz, IF DC–500MHz, **level 7: +7dBm LO nominale**, conversion loss nominale **5,6dB**, massimo della gamma dichiarata **8dB**, RF max 50mW, corrente IF max40mA, temperatura −55..+100°C. Il dato conversion loss è **potenza trasferita in condizioni di prova**, non guadagno di tensione al nodo IF455 progettato. OEM ancora a catalogo; DigiKey Italia https://www.digikey.it/it/products/detail/mini-circuits/SBL-1/21727788 segnala componente attivo/THT ma stock nullo alla verifica, il rivenditore italiano https://www.rf-microwave.com/it/mini-circuits/sbl-1-/mixer-rf-plug-in/sbl-1/ indica alcuni pezzi a stock: disponibilità e autenticità **da verificare prima di BOM/ordine**.
- **Analog Devices AD831**: OEM https://www.analog.com/en/products/ad831.html segnala **PRODUCTION**, mixer attivo con amplificatore d'uscita e LO nominale −10dBm ma range alimentazione minimo **9V single supply** o **±4,5V** dual. **Non è ancora candidato THT approvato**: occorre confermare MPN package e stock effettivi e verificare se il progetto alimentazioni consente i relativi rail e la dissipazione; non sostituibile pin-to-pin all'SBL-1+.

## Un vero file KiCad, ma non una PCB

Nuova libreria KiCad9 standalone:
`04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/SBL1_MIXER_OEM_PINOUT.kicad_sym` con `sym-lib-table`. Simbolo `MCL_SBL1_CANDIDATE:SBL-1_PLUS`, 8 pin **OEM reali**:

| Pin fisico OEM SBL-1+ | Rete/funzione candidata |
|---:|---|
| 1 | RF ingresso |
| 2 | GROUND |
| 3 | IF_A |
| 4 | IF_B |
| 5 | GROUND |
| 6 | GROUND |
| 7 | GROUND |
| 8 | LO ingresso |

**Obbligatorio** nel futuro schematico vero: pin **3 e 4 IF devono essere connessi esternamente alla stessa rete**, con verifica dei pad fisici; tutti i 4 pin GND devono avere ritorni RF adatti. MCL A06 **non è DIP8 standard**: la scheda OEM mostra quattro colonne di pin con pitch **5,08mm** e due righe di package con quote meccaniche da confrontare con disegno reale. Campo Footprint **intenzionalmente vuoto**, nessun footprint A06 e nessuna pretesa di netlist↔PCB o ERC di ricevitore completo. Prima di assegnare il footprint servono layout 1:1 OEM e revisione indipendente di vista TOP/BOTTOM e pin di riferimento. Le due reti IF3/4 sono ancora distinte *nella sola libreria*, senza netlist di integrato: non definirle già collegate nel master.

Verificatore `03_Verifiche/V2.7/verify_sbl1_mixer_oem_symbol_lo_contract_native.py` nella FULL GitHub Actions:
- esegue davvero `kicad-cli sym export svg --output ...` con KiCad9, controlla SVG;
- verifica indipendentemente gli otto numeri/funzioni (quattro GND, RF1, LO8, IF3+IF4 distinti), campo footprint vuoto, presenza della tabella librerie e dei pin di ingresso della sezione IF455;
- calcola condizionatamente il pilotaggio LO a **+7dBm su 50Ω di terminazione idealizzata**: `P=5,011872mW`; `Vrms≈0,500593V`, `Vpp sin≈1,416V`; `Irms≈10,012mA`. Questo **non** è la tensione che il buffer VCO attuale è in grado di fornire, perché VSWR e rete di adattamento reale sono ignote;
- registra il rapporto di potenza nominale `10^(-5,6/10)≈0,275` e a 8dB `≈0,158`, **da non usare** come trasferimento Vout/Vin del filtro IF455 o conversion gain RF reale garantito.

## Bloccanti per selezionare davvero il mixer

1. **LO drive**: misurare/modelizzare quanto potenza disponibile e spur produce il buffer VCO del master V2.6 alla frequenza locale corretta; +7dBm su 50Ω è il requisito di banco candidato, non abbiamo prova dell'alimentazione e schermatura in ricezione.
2. **IF port matching**: uscita del mixer a doppio bilanciamento non rappresentabile automaticamente con un generatore di tensione ideale 50Ω. Il tank KiCad J1601 ha `Zin(455kHz)≈18,53k−j19,75kΩ` con load100k oppure `23,60k−j18,22kΩ` col surrogato gate JFET: **non esiste ancora una rete di adattamento/diplexer** e nemmeno uno schema IF post-mixer completo.
3. **Gain + rumore**: il mixer passivo presenta perdita di conversione, dunque serve una progettazione della catena RF/IF e rumore fino all'audio con mode AM/FM/SSB, controllo AGC, terminazione e selettività. Il consumo o la cifra di rumore reale a 27MHz e IF455 non derivano dal presente file KiCad.
4. **Footprint e produzione**: disegno A06 THT da verificare, MPN esatto originale in produzione/stock, pin↔pad, valori PVT, giunzioni di massa, calore, EMI, verifica laboratorio e DRC PCB reale.

**Decisione:** SBL-1+ è **CANDIDATO OEM THT PLAUSIBILE** per prototipo di RX, ma **NON QUALIFICATO** per collegamento al master, rilascio BOM o PCB. Non confondere un simbolo KiCad9 nativo con un circuito mixer testato. Nessun cambio al master V2.6, nessuna alimentazione da batteria/veicolo, nessuna fabbricazione/TX. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
