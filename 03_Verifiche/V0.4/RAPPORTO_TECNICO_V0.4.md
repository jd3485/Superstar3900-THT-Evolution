# Rapporto tecnico V0.4 — sottoschema KiCad digitale e studio VCO THT

**Data:** 10 novembre 2026. Repository `jd3485/Superstar3900-THT-Evolution`, evoluzione cumulativa e indipendente. Fase progetto RX. Nessun hardware costruito. **NO FAB / NO TX**.

## Elaborati nuovi e lavoro effettivo
1. **Primo file KiCad nativo generato:** `04_KiCad/V0.4/PLL_PRESCALER_RX_V0.4.kicad_sch` con integrato THT U402 TC74AC74P(F), prima metà usata come /2 e seconda metà con stati definiti, quattro connettori 1x02 THT, simboli incorporati e libreria locale. Si tratta di **sottoschema digitale isolato**, NON della scheda radio, U401 e VCO assenti. I test software non sostituiscono apertura KiCad/ERC.
2. **VCO analitico più concreto:** individuato **BB204G Philips TO-92**, varactor a doppio diodo con pin 1/A1 2/K 3/A2 (materiale storico). Considerata UNA giunzione equivalente nel tank ideale con L=220nH, C_fixed_eff=57,5pF inclusi parassiti da stimare. Il tank necessita di C_var=29,830pF a LO 36,31MHz e 18,199pF a 39MHz. BB204G pubblica C(3V)=34..39pF e C(30V)=14pF **tipica**, misurata a 1MHz: finestra aritmetica potenzialmente compatibile, non qualifica a RF.
3. **Fattibilità di tuning ipotetica:** fit di potenza fra C3 stimata 36,5pF e C30 tipica 14pF dà circa **4,872V** a 36,31MHz e **15,974V** a 39MHz, solo nel modello. Non sono valori di progetto da applicare: i vincoli reali del BB204G e del circuito possono differire.
4. **Filtro loop preliminare dal datasheet Lansdale:** topologia tipo B `PDout → R1 → VTUNE`, `VTUNE → R2 → C → GND`; valori di studio R1=2,2k, R2=10k, C=100nF. Risultano polo ideale circa **130,46 Hz** e zero **159,15 Hz**; chiusura e stabilità del PLL **NON calcolate** senza Kphi/KVCO effettivi e analisi dinamica.
5. **Interfaccia digitale 270 posizioni:** proposto controller semplice **PIC18F47Q43-I/P PDIP40**, attualmente in produzione come famiglia e catalogato come THT: governerà N[11:0], mute RX, selettori e CH9, ma schemi pin/firmware non esistono ancora. Niente DSP, VOX, CTCSS/DCS, Dual Watch.
6. **Buffer**: possibile **SN74AC14N PDIP14** per clock CMOS da progettare; il circuito oscillatore Q501 TO-92, buffer, polarità D501, bias, LO level, alimentazione e circuito limitatore restano da definire.
7. Storico intatto; preparata snapshot della configurazione V0.3 per proteggere la regressione storica.

## Verifiche V0.4: esito da confermare nella CI post-commit
| Livello | Suite | Conteggio / stato iniziale |
|---|---|---|
| V0.1 statici | `03_Verifiche/V0.1/test_v01.py` | 12 test, regressione |
| V0.2 aritmetici | `03_Verifiche/V0.2/test_v02.py` | 24 test, regressione |
| V0.3 pinout/statici | `03_Verifiche/V0.3/test_v03.py` | 32 test, regressione (config snapshot) |
| V0.4 analitici/statici | `03_Verifiche/V0.4/test_v04.py` | **34 nuovi test**, strutture S-expression, VCO matematico, gate |
| **KiCad ERC/DRC reali** | CAD tool | **NON ESEGUITI** (KiCad CLI non disponibile) |
| **SPICE/EM/PCBWay/laboratorio** | Circuiti reali | **NON ESEGUITI** |

**Validazione statica non equivale a schema KiCad aperto e compilato**, né a verifiche RF o layout. Nessun circuito oscillante completo, nessun filtro RF verificato, nessun Gerber e nessuna trasmissione.

## Rischi
- Reperibilità **ML145151YP** Lansdale (quote-only, nessuna conferma ordine piccolo) e **BB204G** storico NOS. Senza componenti autentici non conviene produrre una PCB.
- Capacità varicap a 1MHz diverse da dinamica a 37MHz; Q, perdite, ESR, parassiti THT, tolleranze e deriva; feedback del transistor non dimensionato. Nessuna simulazione SPICE.
- Oscillatore riferimento 10,24MHz V0.3 di precisione ancora insufficiente per SSB definitiva.
- Tuning, bias, loop e stabilità del PLL non verificati; MCU candidato non ha firmware.

## Prossima V0.5
Priorità: consolidare **un VCO fisico con pinout transistor e varicap**, stadio buffer/limitatore e loop compensato con parametri, avviare progetto U401/MCU e verificare i sottoschemi in KiCad nativo (ERC se ambiente disponibile). Fare controlli con sorgenti/datasheet, senza dichiarare fabbricabile ciò che ancora non è stato validato.

**GATE:** NO FAB / NO TX.

## Esecuzione GitHub Actions effettivamente verificata

- **Run [42810567923](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42810567923)**, commit testato `68c8975d44a447f595269bd0eb3718602ffe2f68`, branch `main`.
- Job `static-regression`: **SUCCESS**; le suite V0.1 (12), V0.2 (24), V0.3 (32) e V0.4 (34) sono state eseguite con **successo**, per **102 test software** complessivi.
- Le verifiche riguardano solo dati/funzioni Python e struttura del file S-expression KiCad. **NON ESEGUITI**: apertura in KiCad GUI, ERC/DRC reali, SPICE, hardware, EMI, produzione o TX.
- Nella prima run V0.4 era fallito un test storico per il riferimento alla configurazione corrente anziché allo snapshot storico: ora corretto con `CONFIGURAZIONE_V0.2.json`; la regressione V0.3 è riferita a `CONFIGURAZIONE_V0.3.json`. La run definitiva è interamente verde.
