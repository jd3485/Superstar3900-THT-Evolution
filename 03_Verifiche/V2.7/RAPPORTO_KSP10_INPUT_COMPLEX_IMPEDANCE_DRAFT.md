# V2.7 — impedenza complessa d'ingresso KSP10 e accoppiamento al tank IF455

**14 novembre 2026 · benchmark KiCad9/ngspice generico, non impedenza OEM verificata.**

## Motivo della verifica

Le [PR #156](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/156), [#158](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/158) e [#160](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/160) dimostrano che condensatore e resistenza serie muovono il compromesso fra livello sul tank e tensione all'uscita KSP10, ma non misurano direttamente **l'impedenza complessa del carico vista dal tank**. Serve separare il comportamento della base BJT dalla reattanza del CIN.

## Esperimento nativo e controllo matematico indipendente

Nuovo `03_Verifiche/V2.7/verify_if455_ksp10_complex_input_port_native.py`, agganciato alla FULL CI, esporta la vera netlist KiCad9 KSP10 (pin1 base, pin2 emettitore, pin3 collettore) e la netlist tank IF455. Si riutilizza il **medesimo BJT generico** 6V, bias22k/10k e emettitore2,2k del benchmark PR156 (non un modello OEM), con carico d'uscita **solo resistivo** 1,5/2kΩ. Per ciascuna combinazione `beta=40/80/160` × carico `1500/2000Ω` × frequenza `445/455/465kHz` × CIN `10/100/1000/10000pF` il test esegue una vera analisi AC ngspice del porto d'ingresso; sono **72 combinazioni**, con **72 ulteriori misure di riferimento direttamente sulla base** (totale **144 risoluzioni native ngspice**).

Le due misure utilizzano la stessa sorgente di corrente/tensione di prova alla porta e mantengono il bias DC originale mediante condensatori di blocco. Il riferimento sulla base impiega una capacità numerica ideale `1 F`, da cui viene **sottratta la reattanza nota**, ottenendo `Z_base(f)`. La porta del tank con CIN trial viene poi verificata tramite un **secondo solver ngspice** e l'identità di rete serie `Z_port=Z_base+1/(j2πfCIN)`, controllata in complesso con errore relativo <0,08%. Si registrano real/imag/magnitudine dell'impedenza d'ingresso e l'errore dell'identità.

Questa verifica non prova che il KSP10 sia un buffer ad alta impedenza: distingue la reattanza della capacità dall'impedenza propria del circuito attivo e consente di quantificare un carico sul tank in modo corretto. **Non equivale a una misura della reale Z(f) del transistor o del mixer SBL-1+**. Il tank risonante è esportato e controllato nei pin, ma la sua interazione completa non è simulata nel deck di impedenza: è una misura di porta isolata; il rapporto di guadagno e il reale bandpass vanno ricontrollati separatamente.

## Qualifiche bloccate

Il produttore [onsemi KSP10](https://www.onsemi.com/pdf/datasheet/ksp10-d.pdf) non fornisce qui un macromodello validato di rumore/IMD o la dipendenza della Zbase reale da Vbe, Ic, temperatura e frequenza. Non inserire CIN/impedenza di test nella radio, non approvare un filtro ceramico sulla sola resistenza nominale e non confondere la cifra `Z_port` con una caratterizzazione OEM. Occorrono rumore d'ingresso, linearità/dinamica con LO, impedenza complessa misurata, eventuale isolatore attivo THT e verifiche reali di filtro IF per AM/FM/USB/LSB/CW (issue [#141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141)).

Master V2.6, standalone KSP10, BOM e PCB invariati. [PR #123 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) e [#143 FB455](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) restano DRAFT per qualifica footprint, MAIN/FRONT non costruite. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
