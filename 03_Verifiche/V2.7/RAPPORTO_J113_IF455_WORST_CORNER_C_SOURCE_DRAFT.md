# V2.7 — J113 onsemi THT, margine ai segnali deboli: C ingresso × R source

**13 novembre 2026, DRAFT di verifica, solo MODELLO GENERICO NJF, NO FAB / NO TX.**

## Punto di partenza

[PR #105](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/105) ha integrato un modulo **KiCad9 standalone** di 9 posizioni THT, netlist 6 reti, ERC **0 errori/0 warning**, con JFET onsemi J113 TO‑92 pin1 D / pin2 S / pin3 G. Il banco usa C1801=10pF C0G, R1801=1MΩ gate a massa, R1802=2,2kΩ source, C1802=10nF, R1803=100kΩ e 6V laboratorio. Nel solo modello generico `JGEN` la risposta AFpp a 0,5V picco era nel caso meno favorevole VTO=−3V/IDSS=2mA **5,823876mV** contro un diretto senza buffer **23,924896mV** (24,34%); risposta insufficiente come base robusta di progetto.

## Modifica progettuale effettivamente esplorata

Nuovo verificatore ngspice `03_Verifiche/V2.7/verify_if455_j113_worst_corner_coupling_source_native.py`: **18 transienti nativi** dell'intera catena filtro IF455→JFET→diodo AM, sempre con identico percorso di riferimento senza follower e rilevazione 455kHz/AM1kHz al 50%, massimo passo 25ns. Si variano direttamente C1801 (10pF / 47pF / 100pF) e R1802 source (680Ω / 1kΩ / 2,2kΩ), a due livelli di sorgente (0,5/2V picco). Si tiene fermo il corner **IDSS=2mA e VTO=−3V**, scelto come caso difficile nel modello della PR #105. Questi sono gli estremi elettrici indicati nei parametri onsemi J113 ma **la correlazione e BETA/CGS/CGD/RS/RD adottati NON sono macromodelli OEM**.

Si misurano AFpp dopo diodo con/senza JFET, rapporto AFpp, picchi RF al tank, swing source e gate-source (via probe `EGS`). La verifica ricalcola la vecchia topologia C=10p/Rs=2k2 e la confronta con PR #105. Il ranking AFpp non deve essere scambiato per qualità di demodulazione; si devono controllare distorsione, risposta a segnali ancora più bassi, impedenza e tolleranze.

**Non è ancora una revisione CAD del modulo**: senza verifiche numeriche e tecniche non si cambia il simbolo J113 né si dichiara la proposta ottimizzata. Nessuna integrazione nel master V2.6, nessuna PCB-MAIN/FRONT instradata, nessun DRC reale. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

## Risultati 18 transienti nativi — run #43481864363, 3/3 PASS

GitHub Actions [#43481864363](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43481864363), commit tecnico/documentale `54560c8b9861b9a6136b624424fd22e8e09648f3`: **FAST + FULL KiCad9/ngspice + required gate 3/3 SUCCESS**, 111 comandi legacy, `PASS_NGSPICE_IF455_J113_GENERIC_18_WORSTCORNER_CAP_SOURCE_NO_OEM_NO_FAB_NO_TX`. Circuito di riferimento AFpp ≈**23,925mV** a sorgente 0,5V picco e **216,306mV** a sorgente 2V picco. Lo screening riproduce il caso originale 10p/2,2k con accuratezza entro 3% rispetto a PR #105.

| C gate | R source | AFpp JFET a 0,5V (mV) | /diretto 0,5V | AFpp JFET a 2V (mV) | /diretto 2V | Gate forward a 2V nel modello |
|---|---:|---:|---:|---:|---:|---|
|10p|680Ω|1,600|6,69%|125,547|58,04%|**SÌ**, Vgs max +0,128V|
|10p|1kΩ|2,357|9,85%|183,305|84,74%|no|
|10p|2,2kΩ|5,824|24,34%|294,034|135,93%|no|
|47p|680Ω|2,191|9,16%|177,705|82,15%|**SÌ**, +0,284V|
|47p|1kΩ|3,468|14,50%|241,194|111,51%|no (Vgs max ≈−0,002V)|
|47p|2,2kΩ|9,326|38,98%|356,418|164,77%|no|
|100p|680Ω|2,318|9,69%|186,934|86,42%|**SÌ**, +0,310V|
|100p|1kΩ|3,716|15,53%|251,211|116,14%|**SÌ**, +0,020V|
|100p|2,2kΩ|10,058|42,04%|366,805|169,58%|no|

**Decisione:** con VTO=-3V/IDSS=2mA nel modello, **ridurre R source a 680Ω o 1kΩ peggiora il segnale debole**; in alcune configurazioni a 2V compare Vgs positivo (conduzione giunzione gate-source: rischio di distorsione e di loading non lineare). Portare C1801 a 100p lasciando Rsource=2,2k migliora AFpp debole da **5,824mV** a **10,058mV**, ma rimane solo **42,04% del percorso diretto**. Nessuna configurazione testata dimostra sufficientemente un adattatore RF robusto con segnale debole e distorsione non verificata; **non cambiare il CAD J113 né congelare questo MPN come stadio IF del prodotto**.

I valori input source 0,5/2V sono ampiezze di un generatore ideale, **NON** livelli tipici µV di sensibilità radio. La differenza di AFpp dopo un rivelatore a diodo non è misura di audio SINAD, selettività AM, noise figure o linearità. Il gate J113 è pin3 esclusivamente per OEM onsemi nella libreria; nessuna prova su PCB, no DRC fisico. Passi successivi più importanti: specificare il vero livello IF ricevuto e l'impedenza complessa del filtro, simulare rumore/THD, carico di piccole ampiezze e valutare topologie di buffering/trasformatore alternative con modelli OEM.
