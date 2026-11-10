# KiCad — V0.4 primo sottoschema nativo (RX-only)

## Contenuto
- `PLL_PRESCALER_RX_V0.4.kicad_sch`: file **nativo formato S-expression KiCad**, generato per la sezione U402 (Toshiba TC74AC74P(F), DIP14) usata come prescaler /2. Comprende quattro connettori THT per clock CMOS esterno, feedback verso PLL, alimentazione +5V e reset. I due output della sezione di FF non usata hanno marcatori no-connect; gli altri ingressi hanno net definite.
- `THT_V04.kicad_sym`: libreria locale degli UNICI due simboli inseriti (U402 e connettore 1x02). I pin sono numerati e la libreria e' incorporata nel file .kicad_sch.
- `sym-lib-table`: puntatore alla libreria THT accanto allo schema.

## Cosa NON contiene e non bisogna inferire
- **U401 ML145151YP**, quarzo X401 e filtro loop non sono in questo schema. Si trovano ancora in pin-net V0.3.
- **Q501 VCO, D501 BB204G, buffer e limitatore LO** non sono ancora schematizzati né validati. Lo studio analitico e' in `01_Specifiche/V0.4/`.
- Nessuna alimentazione stabilizzata completa: `+5V_PLL` e reset sono ingressi esterni del sottosistema, NON circuiti di protezione.
- **KiCad CLI/GUI e ERC/DRC NON ESEGUITI** nell'ambiente che ha prodotto questo file. I test Python controllano solo struttura S-expression, nomi net, conteggio simboli e footprint, non apertura/validità sintattica del KiCad CAD, non ERC e non produzione.
- Questo sottoschema isolato non è una scheda PCB, un progetto fabbricabile o una radio operativa: **NO FAB / NO TX**.

## Attivita' KiCad della prossima revisione
Verificare apertura in GUI, correggere eventuali problemi di generazione, eseguire ERC nativo, aggiungere U401 e oscillatore/quarzo con impronte THT confermate; progettare VCO fisico e buffer solo dopo aver selezionato transistor/varicap con pinout e disponibilita' verificata. Le quattro connessioni J402..J405 sono **interfacce di banco**, non il connettore finale della scheda principale.
