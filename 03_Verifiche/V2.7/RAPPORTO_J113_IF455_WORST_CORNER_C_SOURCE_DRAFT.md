# V2.7 — J113 onsemi THT, margine ai segnali deboli: C ingresso × R source

**13 novembre 2026, DRAFT di verifica, solo MODELLO GENERICO NJF, NO FAB / NO TX.**

## Punto di partenza

[PR #105](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/105) ha integrato un modulo **KiCad9 standalone** di 9 posizioni THT, netlist 6 reti, ERC **0 errori/0 warning**, con JFET onsemi J113 TO‑92 pin1 D / pin2 S / pin3 G. Il banco usa C1801=10pF C0G, R1801=1MΩ gate a massa, R1802=2,2kΩ source, C1802=10nF, R1803=100kΩ e 6V laboratorio. Nel solo modello generico `JGEN` la risposta AFpp a 0,5V picco era nel caso meno favorevole VTO=−3V/IDSS=2mA **5,823876mV** contro un diretto senza buffer **23,924896mV** (24,34%); risposta insufficiente come base robusta di progetto.

## Modifica progettuale effettivamente esplorata

Nuovo verificatore ngspice `03_Verifiche/V2.7/verify_if455_j113_worst_corner_coupling_source_native.py`: **18 transienti nativi** dell'intera catena filtro IF455→JFET→diodo AM, sempre con identico percorso di riferimento senza follower e rilevazione 455kHz/AM1kHz al 50%, massimo passo 25ns. Si variano direttamente C1801 (10pF / 47pF / 100pF) e R1802 source (680Ω / 1kΩ / 2,2kΩ), a due livelli di sorgente (0,5/2V picco). Si tiene fermo il corner **IDSS=2mA e VTO=−3V**, scelto come caso difficile nel modello della PR #105. Questi sono gli estremi elettrici indicati nei parametri onsemi J113 ma **la correlazione e BETA/CGS/CGD/RS/RD adottati NON sono macromodelli OEM**.

Si misurano AFpp dopo diodo con/senza JFET, rapporto AFpp, picchi RF al tank, swing source e gate-source (via probe `EGS`). La verifica ricalcola la vecchia topologia C=10p/Rs=2k2 e la confronta con PR #105. Il ranking AFpp non deve essere scambiato per qualità di demodulazione; si devono controllare distorsione, risposta a segnali ancora più bassi, impedenza e tolleranze.

**Non è ancora una revisione CAD del modulo**: senza verifiche numeriche e tecniche non si cambia il simbolo J113 né si dichiara la proposta ottimizzata. Nessuna integrazione nel master V2.6, nessuna PCB-MAIN/FRONT instradata, nessun DRC reale. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.
