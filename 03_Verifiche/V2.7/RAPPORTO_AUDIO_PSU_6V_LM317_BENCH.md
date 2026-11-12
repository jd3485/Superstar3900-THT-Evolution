# V2.7 DRAFT — regolazione audio 6 V con LM317 THT, **solo banco isolato**

**13 novembre 2026.** Nuovo sottocircuito elettronico KiCad9 reale ma **isolato** dalla radio. Non è una sorgente 13,8 V veicolare: l'ingresso J1401 richiede un alimentatore di laboratorio regolato, limitato in corrente, **9–10 V**, con polarità corretta. La radio principale non è connessa. Nessun collegamento a batteria/veicolo, alimentatore RF/PLL o antenna/TX.

## Fonti OEM e componenti

- Texas Instruments **LM317T/NOPB** è contrassegnato **ACTIVE** sul sito del produttore, package **NDE, TO‑220 THT, 3 pin**; non dichiarare disponibilità immediata (TI può indicare assenza di stock): https://www.ti.com/product/LM317-N/part-details/LM317T/NOPB . Pinout TI: **1 ADJ, 2 OUTPUT + TAB, 3 INPUT**; la linguetta TO‑220 è a circa +6 V e deve essere isolata da un dissipatore/carter connesso a massa: https://www.ti.com/lit/ds/symlink/lm317-n.pdf .
- Riferimento funzionale TI LM317-N e LM317: https://www.ti.com/lit/ds/symlink/lm317.pdf , applicazione con **R1 OUT→ADJ, R2 ADJ→GND**, condensatore 100 nF d'ingresso, condensatore d'uscita e bypass ADJ, diodi D1 OUT(anodo)→IN(catodo), D2 ADJ(anodo)→OUT(catodo). L'esempio di datasheet non è prova di qualifica della nostra configurazione.
- 1N4002 in D1401/D1402 è **candidato elettrico** non qualificato per ciclo produttivo esatto MPN. Anche i passivi e i connettori hanno MPN finale ancora da scegliere.

## Schema in repository
`04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V/AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch` contiene 10 riferimenti fisici **THT**:

| Riferimento | Funzione | Reti |
|---|---|---|
| J1401 | ingresso LAB 9–10 V + massa con simbolo sorgente di banco | `LAB_VIN_9TO10V`, `AUDIO_GND` |
| U1401 | LM317T/NOPB 3 pin / TO‑220 | IN pin3 LAB VIN, OUT pin2 `AUDIO_6V_LAB`, ADJ pin1 `AUDIO_ADJ` |
| R1401 | **110 Ω 1%** OUT→ADJ | corrente di feedback nominale 1,25/110 ≈ 11,36 mA |
| R1402 | **412 Ω 1% (E96)** ADJ→GND | tensione d'uscita provvisoria ≈ 5,952 V, con Iadj 50 µA tipica |
| C1401 | 100 nF / 25 V ceramico | LAB VIN→GND |
| C1402 | **10 µF / 16 V elettrolitico** | pin1 POS sul 6 V, pin2 NEG a GND |
| C1403 | **10 µF / 16 V elettrolitico** | pin1 POS su ADJ, pin2 NEG a GND |
| D1401 | diodo protezione OUT→IN | pin1 ANODO sul 6 V, pin2 CATODO sull'ingresso |
| D1402 | diodo protezione ADJ→OUT | pin1 ANODO su ADJ, pin2 CATODO sul 6 V |
| J1402 | uscita LAB 6 V e ritorno | `AUDIO_6V_LAB`, `AUDIO_GND` |

Libreria standalone `TH_PSU.kicad_sym`, tabella `sym-lib-table` e progetto `.kicad_pro`. Le dieci impronte dichiarate sono THT, ma le geometrie reali e il connettore di cablaggio restano da qualificare. **Pin-to-pad TO220, dissipatore, drill e clearance del tab** richiedono review anche prima del layout.

### Calcoli espliciti (non misure o garanzie)
La formula di prima approssimazione TI è `Vout = Vref × (1+R1402/R1401) + Iadj × R1402`. Con Vref=1,25 V, Iadj=50 µA, R1=110 Ω e R2=412 Ω si ottiene **5,9524 V nominali**. Non è range PVT: vref TI fino a 1,2–1,3 V, Iadj, tolleranze, deriva e carico modificano la tensione. Il minimo carico del LM317 può arrivare **10 mA**; con R1 max +1% e Vref min 1,2 V, `Idiv≈1,2/111,1=10,80 mA` (margine limitato; da qualificare a caldo).

Bilancio termico illustrativo `P≈(Vin−Vout)×Iload`, `Tj≈Tamb+P×θJA`. Assumendo **solo come stress test** Tamb=60°C, θJA=50°C/W, Iload=0,20 A e Vout=6,0V:
- Vin=9 V: **0,60 W** → Tj stimata **90°C**.
- Vin=10 V: **0,80 W** → Tj stimata **100°C**.
- Vin=13,8 V: **1,56 W** → Tj stimata **138°C**, **oltre la soglia progettuale prudenziale 125°C** anche prima di considerare perdite/limiti reali.

Questo **non** prova che il regolatore sia sicuro o sufficientemente dimensionato per 0,20 A: θJA del PCB/sistema è ignota, Iload del LM386 ha picchi, startup, speaker 4/8Ω e passaggio termico non testati. A Vin=10V, Iload=0,35A e stesse assunzioni: circa **130°C**, anch'esso fuori budget. Non dimensionare un dissipatore usando questo solo calcolo; completare profili SPICE/OEM, protezioni e temperatura reale.

**Non cambiare il LM386 esistente da 5 V a 6 V automaticamente.** La sua nuova sorgente dedicata è un candidato alternativo bench e il collegamento al pin 6 U1201 richiede una decisione circuitale, test di potenza e aggiornamento delle interfacce tramite PR. Non si può inferire potenza reale THD a 5V dalla specifica TI a 6V.

## Gate nuovi e residui
Il test `03_Verifiche/V2.7/verify_audio_psu_lm317_native.py` esegue **KiCad9 ERC --exit-code-violations**, esporta la netlist reale e verifica tutti i 10 componenti, ingresso, uscita, ADJ, protezione diodi e polarità dei due elettrolitici, oltre a controlli aritmetici di P e VIN. Il test è inserito in `ci/full_regressions.py` dopo le suite legacy. **Non dichiarare verde prima di vedere la CI HEAD finale**, nessun waiver.

Rischi aperti: reale LM317 TI package NDE vs footprint THT, SOA, esatta versione del chip, carico minimo a PVT, PSU 9–10 V stessa fonte del ricevitore non definita, reverse/transient input protection mancante, EMC/audio RF return, shutdown e cablaggio. L'ingresso 13,8 V della radio e la sicurezza #27 restano totalmente separati e bloccati. Le due PCB MAIN/FRONT non esistono ancora in layout, e questa bozza non è routing.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** Nessuna modifica al master V2.6, nessun MPN BOM qualificato implicitamente, nessuna misura reale o SPICE vendor dichiarata.
