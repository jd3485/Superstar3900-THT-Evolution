# WORK_STATO_CORRENTE.md — checkpoint canonico Superstar 3900 THT Evolution

**Aggiornato:** 14 novembre 2026. **Repository esclusivo:** `jd3485/Superstar3900-THT-Evolution`.
**Branch autoritativo:** `main`. Questo file documenta l'ultima revisione verificata,
non sostituisce il controllo live di GitHub a ogni nuova sessione. Leggere
[AGENTS.md](../AGENTS.md) **e questo file da main all'inizio**; poi verificare
SHA di main, PR, issue, GitHub Actions e i rapporti CAD.
Non utilizzare la memoria delle chat o lo stato di branch draft come verità di main.

## 14 novembre 2026 — PR #148 MERGED: carico ceramico 1500/2000Ω sul J113 THT già esistente

**[PR #148](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/148) MERGED**, commit `main` verificato `c687feff5e6b72a2ce08a82e33724f986e96669b`, HEAD tecnico `588d446605d0472a42d9acf6708f97668f82c5fc`. [Actions #43595989414](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43595989414) **FAST, FULL native KiCad9/ngspice, required gate 3/3 SUCCESS**; FULL logs ispezionati: **18 run ngspice AC con piccolo segnale** + **111 comandi legacy**, marker `PASS_NATIVE_KICAD9_J113_18_NGSPICE_455K_CERAMIC_RESISTIVE_LOAD_CORNERS_GENERIC_NO_OEM_NO_FAB_NO_TX`.

Il verificatore `03_Verifiche/V2.7/verify_if455_j113_ceramic_load_native.py`, rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_J113_CERAMIC_LOAD_DRAFT.md`, invocazione obbligatoria `ci/full_regressions.py` riutilizzano **veramente la netlist KiCad9 J113 THT standalone già progettata** (Q1801: onsemi TO-92 pin1 drain / pin2 source / pin3 gate; alimentazione prova 6V, source R2,2k, gate R1Meg, ingresso C10pF, uscita C10nF) e la netlist tank IF455. Nei deck ngspice temporanei il modello transistor rimane **generico** `NJF` con `VTO=-0,5/-1,5/-3V` × `Idss=2/10mA`, tre carichi resistivi fittizi di ingresso filtro ceramico **100kΩ riferimento/2kΩ/1,5kΩ** (18 sweep 445–465kHz). Questi non rappresentano impedenza complessa/canale del filtro FB455, né un macromodello onsemi, rumore o non linearità grande segnale.

A 455kHz **Vout(2k)/Vout(100k) = 0,6738…0,8907** nei sei corner generici; **Vout(1,5k)/Vout(100k) = 0,6065…0,8588**. Al corner più sfavorevole `VTO=-3V, Idss=2mA, load2kΩ`: `Vout/Vsource=0,261831624`, `Vout/Vtank=0,353135253`, confrontato al corner favorevole `VTO=-0,5V, Idss=10mA, load2kΩ`: `Vout/Vsource=0,574805784`. Il follower riduce considerevolmente il segnale modellato quando pilotato dal filtro ceramico resistivo. **Soprattutto PR #106 J113 aveva già un corner debole AM transitorio pari al 24,34% dell'AF del percorso diretto**: questo problema NON è risolto dal nuovo test AC e l'attuale J113 resta **NON APPROVATO** come buffer dell'interfaccia radio. Non selezionare un candidato realizzato in hardware soltanto perché presente a catalogo.

[onsemi J113 datasheet](https://www.onsemi.com/pdf/datasheet/mmbfj113-d.pdf) e [DigiKey J113](https://www.digikey.com/en/products/detail/onsemi/J113/1048989): dispositivo THT TO-92 attivo a catalogo ma non caratterizzato qui come amplificatore a basso rumore a 455kHz. Serve verifica OEM/acquisizione modelli gm/rumore e campioni, DC bias e variazioni, IMD/overload, adattamento reale filtro 1500/2000Ω e carico uscita, catena demodulazione per modi RX AM/FM/USB/LSB/CW [issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141), caratteristiche LO-driven IF effettive mixer. Master MAIN V2.6 7 fogli/138 refs invariato; nessuna modifica KiCad hardware, BOM non rilasciata; PCB MAIN/FRONT assenti, nessuna DRC PCB. [PR #123 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) e [PR #143 FB455](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) restano DRAFT in attesa di misure OEM/meccanica; niente assegnazione footprint. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #146 MERGED: confronto tre famiglie interfaccia mixer→IF455, 48 simulazioni native

**[PR #146](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/146) MERGED**, commit main `df8ec13306cb26521e3af2873938e7d81cff4dbe`; head tecnico `cf9306efc854c77cd8bbe612a727453a626b36aa`. [Actions #43594909355](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43594909355) **FAST/FULL native KiCad9/ngspice/required 3/3 SUCCESS**; log verificati: **111 comandi legacy**, 48 misure native ngspice contro 48 calcoli analitici complessi, `PASS_NATIVE_KICAD9_IF455_48_NGSPICE_RESISTIVE_LMATCH_BUFFER_IDEAL_COMPARISONS_NO_VENDOR_FAB_NO_TX`.

Verificatore `03_Verifiche/V2.7/verify_if455_three_interface_topologies_native.py`, rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_THREE_INTERFACE_TOPOLOGIES_DRAFT.md`, test obbligatorio in `ci/full_regressions.py`. Esportate le vere netlist KiCad9 standalone del mixer SBL-1+ (IF3+IF4, J1703, GND) e del candidato tank IF455 (J1601→C1601 e GND). **48 soli deck di prova**, Rg Thevenin ipotetica 50/500Ω × carico input ceramico simulato con **semplice resistenza fittizia** 1500/2000Ω × frequenze 445/455/465kHz × quattro varianti: diretto, serie R1 secondo banco OEM, ideale L-match passa-basso, buffer **ideale** controllato in tensione (Zin100kΩ, Zout100Ω, guadagno1). Nessuna frequenza di filtro ceramico, perdita d'inserzione, banda, LO reale, NF/rumore/distorsione buffer o carico all'uscita del filtro sono modellati.

Con Rg50Ω e Rload2000Ω al centro 455kHz: diretto **0,975609756 V/V**; R1 OEM1950Ω **0,5 V/V**; L-match ideale **3,162277661 V/V** (NON guadagno di potenza) con **Lserie≈109,222µH, Cshunt≈1,092222nF**, `Zin(455kHz)=50+j0Ω` *solo modello lossless*; buffer ideale **0,951905 V/V**. L-match ideale attorno al centro dà un rigetto fittizio ±10kHz di appena **0,0773/0,0808 dB**. Nessuna delle reti risolve da sola selettività canale, rumore, terminazione broadband dei prodotti di mixer o compatibilità fisica THT. [Mini-Circuits AN00-009](https://www.minicircuits.com/appdoc/AN00-009.html) usa 50Ω come **condizione di caratterizzazione**, NON stabilisce Zout IF reale SBL-1+ sotto LO e carichi. [NextGen FB datasheet](https://www.nextgencomponent.com/uploads/soft/20241011/1-241011155152A8.pdf) specifica Rg+R1=R2=Znom nel banco OEM, non un'interfaccia universale con mixer. **Non inserire L/C o buffer reale** prima di qualificare componenti, rumore/IMD, THT bias, L/C Q/SRF, alimentazioni, e maschere RX AM/FM/USB/LSB/CW [issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141).

**CAD stato:** master V2.6 7 fogli/138 riferimenti immutato, candidate IF455/mixer isolate, filtro ceramico non assegnato, BOM non rilasciata, PCB MAIN/FRONT ancora assenti e routing 0%, nessuna DRC PCB. [PR #123 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) e [PR #143 NextGen FB455](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) **ancora DRAFT** per qualifica meccanica TOP/fori. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #144 MERGED: filtro ceramico FB455 1500/2000Ω, termine sorgente/carico del banco OEM

**[PR #144](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/144) MERGED**, commit `main` verificato `8a69c22ec028f81fd8126da139367433fef1c2c6`, head tecnico `f52dd80352bea999349b53444927b2966848cb58`. [Actions #43593787466](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43593787466) **FAST/FULL KiCad9-ngspice/required 3/3 SUCCESS**, log FULL ispezionato: **111 comandi storici**, **12 simulazioni native ngspice**, marker `PASS_NATIVE_KICAD9_IF455_12_NGSPICE_FB455_1500_2000_RG_R1_TEST_DUMMY_NO_VENDOR_TRANSFER_NO_FAB_NO_TX`.

Nuovo `03_Verifiche/V2.7/verify_fb455_1500_2000_termination_native.py` e rapporto `03_Verifiche/V2.7/RAPPORTO_FB455_SOURCE_LOAD_1500_2000_DRAFT.md`, regressione obbligatoria `ci/full_regressions.py`. Il test esporta le vere netlist KiCad9 delle porte standalone **SBL-1+ IF3+IF4/J1703** e **filtro LC IF455 J1601/C1601**, conserva gli schemi esistenti, poi verifica la relazione di misura NextGen FB Case11070 [datasheet OEM, p4](https://www.nextgencomponent.com/uploads/soft/20241011/1-241011155152A8.pdf): `Rg+R1=R2=Z nominale`. I 12 deck ngspice temporanei sono **generatori resistivi e carichi resistivi fittizi (NON filtri ceramici)**: Rg ipotetico `50/500/1500Ω`, Znom `1500/2000Ω`, due configurazioni (R1=0 diretto; R1=Znom−Rg da banco OEM). Per ognuna è confrontata la V d'ingresso a 455kHz con algebra di Ohm indipendente, `Vpin/Vsrc=Znom/(Rg+R1+Znom)`. La **resistenza R2 sull'uscita del vero filtro NON è simulata** e resta requisito di interfaccia da progettare.

Esempio Rg50Ω ipotetico e porta nominale FB455 2000Ω: diretto `Vpin/Vsrc=0,975609756`, nella condizione di banco `R1=1950Ω`, `Vpin/Vsrc=0,5` (circa **−5,8dB** rispetto al livello diretto); a Znom1500Ω il banco richiede `R1=1450Ω`, Vpin/Vsrc=0,5. Sono **rapporti di partizione del carico fittizio**, NON conversion loss del SBL-1+, insertion loss ceramica, noise figure, matching broadband IF, passband o selettività reale. Mini-Circuits [AN00-009](https://www.minicircuits.com/appdoc/AN00-009.html) specifica condizioni di misura 50Ω ma il vero `Zout_IF(f,LO,RF)` dello SBL-1+ nella radio è ignoto. **Non aggiungere 1950/1450Ω al circuito reale** senza qualifica OEM/rumore/guadagno e carico selettivo a valle.

[Issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141) mantiene aperte le bande/reiezioni quantitative per modi RX AM/FM/USB/LSB/CW. [PR #143 FB455](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) impronta THT candidata ancora **DRAFT** pur con CI verde per orientamento TOP e fori/assemblaggio OEM; [PR #123 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) resta **DRAFT** per analoghi blocchi. Master V2.6 sette fogli/138 riferimenti immutato, filtro ceramico NON assegnato, PCB MAIN/FRONT assenti, no DRC PCB/nessun BOM release. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #140 MERGED: selettività offset canale IF455, filtro LC singolo insufficiente

**[PR #140](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/140) MERGED**, verificato su main commit `60aea20c847cf216e49b78217f9b08be921f40c2`, ultimo head tecnico `1622b47b3530e2dc1a76ee71891a085c2c123723`. [Actions #43591777373](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43591777373) **FAST, FULL KiCad9/ngspice e required gate 3/3 SUCCESS**; log FULL nativi verificati con **111 comandi storici** e marker `PASS_NATIVE_KICAD9_IF455_FOUR_CHANNEL_OFFSET_NGSPICE_SWEEPS_NO_RECEIVER_MASK_NO_FAB_NO_TX`.

Nuovo verificatore `03_Verifiche/V2.7/verify_if455_channel_selectivity_native.py`, rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_CHANNEL_SELECTIVITY_DRAFT.md`, test obbligatorio in `ci/full_regressions.py`. Dal vero schematico KiCad9 IF455 standalone viene verificato J1601→C1601→L1601 e GND; 4 sweep AC nativi ngspice 300–650kHz, fonte Thevenin ipotetica 50Ω, 2 carichi (100kΩ, gate RC passivo) × 2 perdite bobina ipotetiche (16,5Ω DCR-usata-come-proxy o 82,7286Ω teorici da Q790, **non RF455 misurato**). Il verificatore estrae Vout a esattamente 455kHz e attenuazioni **separate lato basso e lato alto** a ±3/5/10/20/40kHz, normalizzate a Vout(455kHz).

**Evidenza numerica:** sorgente 50Ω, carico 100kΩ, perdita proxy 16,5Ω → picco **454750Hz**, BW −3dB **42556,7Hz**, attenuazione relativa a 455kHz a −10kHz **0,8938dB**, +10kHz **0,8565dB**; a −20kHz **3,0289dB**, +20kHz **2,5440dB**. Variante carico gate RC: picco **450250Hz**, BW **36296,4Hz**, a −5kHz attenuazione **−0,2683dB** (segnale offset maggiore del segnale a 455kHz), +5kHz **0,7577dB**; a ±10kHz peggiore **0,1085dB**. Cambiare perdita a 82,7286Ω allarga il BW di riferimento a **53697,9Hz**, peggiorando il rigetto peggiore a ±10kHz a **0,4554dB**. Tutti i quattro casi hanno almeno un lato di ±10kHz con rigetto **inferiore a 3dB**: questo tank isolato **non** è un filtro di selettività di canale stretto qualificato.

**Requisiti autoritativi** `01_Specifiche/REQUISITI_V0.1.md`: modi RX **AM, FM, USB, LSB, CW già confermati**; target prestazionali e banda per modo ancora `TBD`, IF1 10.695MHz/IF2 455kHz solo candidate, non congelate. [Issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141) aperta per specifiche quantitative per modo e selezione filtro THT dedicato. Non attribuire arbitrariamente 3kHz SSB/6kHz AM/10kHz FM come valori di progetto approvati; occorre definire canali, larghezza occupata, insertion loss, rigetto adiacente, dinamica, demodulazione e MPN OEM. **Nessun filtro scelto né circuito fisico alterato**. Master V2.6 sette fogli/138 refs immutato; PCB MAIN e FRONT assenti, routing 0%, DRC PCB non applicabile; [PR #123 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) resta DRAFT per qualifica meccanica. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #138 MERGED: Q a 790kHz NON è DCR/ESR RF a 455kHz, Delevan 2500-28J

**[PR #138](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/138) MERGED**, verificato su main commit `db4815f187aa0dcc61ff8e2c3b861f799fd288c4`; head tecnico `d811e55831e2028b84d5acc78f857ccb2466938c`. [Actions #43590750543](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43590750543) **FAST/FULL KiCad9-ngspice/required 3/3 SUCCESS**, log FULL verificati con **111 comandi storici** e `PASS_NATIVE_KICAD9_NGSPICE_IF455_8_AC_LOSS_TRIALS_NO_Q455_INFERENCE_NO_FAB_NO_TX`.

File `03_Verifiche/V2.7/verify_if455_2500_28j_q_vs_dcr_native.py`, rapporto `03_Verifiche/V2.7/RAPPORTO_2500_28J_Q_VS_DCR_IF455_DRAFT.md`, suite FULL `ci/full_regressions.py`. Sul vero schematico KiCad9 standalone IF455 L1601 resta `1mH_DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED`. Il distributore OEM elenca **DCR MAX 16,5Ω** e **Q=60 @790kHz**, non una misura ESR/QL a 455kHz. `2π×790000×0,001/60≈82,728607Ω` è solo equivalente ideale **alla frequenza 790kHz** e non un dato RF a 455kHz. Le 8 prove native ngspice in deck temporanei utilizzano 4 resistenze serie ipotetiche (16,5 / 41,3643 / 82,7286 / 165,4572Ω) × 2 carichi output ipotetici (100kΩ, gate RC passivo). Con sorgente 50Ω e carico 100kΩ: R16,5Ω→picco454750Hz, BW42556,7Hz, Vout/Vsrc455=0,835055562; R82,7286Ω→picco455750Hz, BW53697,9Hz, Vout/Vsrc455=0,667749442. Questi sono risultati **del modello**, non prestazioni OEM né canale RX completo. L'impiego fisico della DCR come resistenza di perdita RF è ancora **NON QUALIFICATO**, e non sono stati cambiati schemi/MPN/BOM/PCB.

**Stato invariato:** master V2.6 sette fogli, 138 refs, frontend/mixer/IF V2.7 isolati, PCB MAIN/FRONT non progettate (routing 0%), DRC PCB non applicabile; no release BOM. [PR #123 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) ancora DRAFT bench-only, CI verde ma footprint non assegnato fino a qualifica meccanica reale. Prossima attività sostanziale: definire la banda IF obiettivo per modalità AM/FM/SSB e verificare se un singolo tank da banda 40–60kHz può mai costituire selettività di canale, prima della selezione filtro THT reale. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #136 MERGED: IF455 1mH THT, sensibilità capacità parassita e SRF

**[PR #136](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/136) MERGED**, main commit `1c6b92b32f71b85d0d8cf1dbcc93f28c77d2470c`; HEAD tecnico `63e0fe54d8bacbdb20a0aedc92555281723d487f`. [Actions #43589919230](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43589919230) **FAST, FULL native KiCad9/ngspice e required gate 3/3 SUCCESS**, verificati log: `PASS_NATIVE_KICAD9_IF455_COIL_12_PARASITIC_AC_COMPLEX_Z_CROSSCHECK_SRF_UNQUALIFIED_NO_FAB_NO_TX`; **12 simulazioni ngspice reali** con 12 confronti indipendenti di algebra nodale complessa e 111 comandi legacy FULL.

File: `03_Verifiche/V2.7/verify_if455_coil_parasitic_srf_native.py`; rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_COIL_PARASITIC_SRF_DRAFT.md`; test incluso nella FULL `ci/full_regressions.py`. Dal vero schema KiCad9 IF455 L1601 1mH viene esplorata **solo in netlist SPICE temporanee** Cp ipotetica 0/0,1/1/10pF in parallelo al ramo bobina serie R16,5Ω+L1mH, a 455kHz/1MHz/30MHz. A 455kHz con Cp0 il modello dà `Zin=18530.8105−j19747.3349Ω` (modulo 27080.402Ω); con Cp10pF `30917.3079−j37011.2265Ω` (modulo 48225.624Ω). Il cambiamento è reale **nel modello**, ma Cp non è misurata né inferita dall'OEM; 30MHz non è una predizione RF fisica.

**Evidenza MPN:** L1601 è etichettato `DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED`. [Scheda distributore DigiKey 2500-28J](https://www.digikey.it/it/products/detail/delevan/2500-28J/3479912) e [catalogo Delevan 2025](https://www.delevan.com/-/media/Project/Altramotion/shared/files/Literature/brand/Delevan/pdf/delevan-2025-magnetics-catalog.pdf) riportano **1mH, DCR massima 16,5Ω, Q 60 a 790kHz, SRF MINIMA 2,8MHz e 88mA**. La SRF minima **non** è SRF esatta; 16,5Ω DCR **non** è resistenza RF valida automaticamente. Il test non sostituisce curve OEM Q(f)/Z(f), selezione THT fisica, verifica di tolleranze e montaggio. Master MAIN V2.6 7 fogli/138 refs e V2.7 schematici invariati; PCB MAIN/FRONT ancora assenti; nessuna DRC PCB; nessuna BOM approvata. [PR #123 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) resta **draft**, anche dopo CI verde, per verifica meccanica fori/pin menisco e campione; nessuna assegnazione footprint al mixer. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #134 MERGED: port IF, ammettenza complessa di carichi RC a 3 frequenze

**[PR #134](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/134) MERGED**, commit su main verificato `0f38454bda541e7eb8bf22749c7c03445e1304cc`, HEAD tecnico `9caf5dd6988796254e843b81adbc2d6a4fc0820f`. [Actions #43588038836](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43588038836) **FAST/FULL native KiCad9/ngspice/required gate 3/3 SUCCESS**; log FULL verificato: **111 comandi legacy**, **12 simulazioni ngspice native** con `PASS_NATIVE_KICAD9_IF_PORT_12_NGSPICE_COMPLEX_ADMITTANCE_CASES_NO_REAL_DIPLEXER_NO_FAB_NO_TX`. Nuovo verificatore `03_Verifiche/V2.7/verify_if_port_shunt_frequency_native.py`, rapporto `03_Verifiche/V2.7/RAPPORTO_IF_PORT_SHUNT_FREQUENCY_DRAFT.md`, script obbligatorio in `ci/full_regressions.py`.

Il verificatore esporta le vere netlist KiCad9 di mixer SBL-1+ e filtro IF455, preserva IF3+IF4 e J1601/1→C1601/1, poi prova quattro configurazioni di porta IF **solo modello** (nessuna terminazione; 50Ω a massa; 50Ω+100pF in serie; 50Ω+1nF in serie) × **455kHz, 1MHz, 30MHz**. Per ciascuna misura complessa di impedenza, controlla con algebra indipendente `Y_shunt=1/Z_loaded−1/Z_unloaded` contro ammettenza analitica R/C. Un 50Ω+100pF serie a 30MHz comporta `Zin` dell'intero modello ≈ **41,684−j51,893Ω**, modulo **66,562Ω**, non è garanzia di matching a 50Ω del mixer reale. Le simulazioni fino a 30MHz sono ideali e non modellano SRF bobina 1mH, parassiti THT, layout, leakage e non linearità mixer.

Prima CI [#43587582419](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43587582419) **FAIL** sul parser che richiedeva due righe ngspice anziché un unico campione valido ad una frequenza; corretto il controllo accettando 1–2 righe finite e imponendo prima riga alla frequenza esatta, senza inventare valori. L'unica CI finale accreditata è #43588038836 **3/3 PASS**. Nessun vero diplexer selezionato né alcuna modifica a V2.6 master/PCB/BOM; mixer IF reale e resistenza di terminazione restano **non qualificati**, PR #123 footprint OEM A06 ancora DRAFT. PCB MAIN/FRONT non esistono, DRC PCB non applicabile; routing **0%**. Prossima fase: qualificare risposta OEM SBL-1+ a carichi complessi e LO reale +7dBm, poi topologia biforcata IF/broadband e noise/gain/armoniche senza usare un semplice RC come diplexer verificato. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #132 MERGED: contratto nativo terminazione porta IF SBL-1+ → IF455

**[PR #132](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/132) MERGED**, verificato su main commit `844ecd4caadebd99ceb07bb92487b70cd09e091b`, ultimo head tecnico `e31dcaf3f5de4118f021b5aac9bfa95613adcd83`. [Actions #43586879554](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43586879554) **FAST/FULL KiCad9/ngspice/required 3/3 SUCCESS**; log FULL verificati con 111 comandi storici, 9 sweep ngspice AC nativi e `PASS_NATIVE_KICAD9_MIXER_IF_PORT_AND_9_NGSPICE_TERMINATION_CASES_NO_OEM_LOAD_QUALIFICATION_NO_FAB_NO_TX`.

Nuovo verificatore `03_Verifiche/V2.7/verify_mixer_if_termination_native.py`, rapporto `03_Verifiche/V2.7/RAPPORTO_MIXER_IF_TERMINATION_PORT_DRAFT.md`, registrazione obbligatoria in `ci/full_regressions.py`. Due esportazioni vere KiCad9 controllano connessioni SBL-1+ IF3/IF4 su J1703/1, masse e J1601/1→C1601/1; verificano che **non esiste** alcuna terminazione fisica nella candidata. Nove modelli temporanei per Rs upstream ipotetica 50Ω/1kΩ/10kΩ × shunt IF nessuno/50Ω/100Ω. A 455kHz, con Rs50Ω, `Vout/Vsource` senza shunt=**0,835055562**, shunt50Ω=**0,417791658**, shunt100Ω=**0,556938244**. Con Rs1kΩ senza=0,815223437, shunt50Ω=0,039766943. Numeri del **solo modello passivo** a sorgente Thevenin, NON prova che lo SBL-1+ presenti Zout resistiva 50Ω o che una terminazione 50Ω sia corretta in circuito reale. Nessun diplexer, analisi di prodotti fuori banda, rumore/linearità o conversion loss OEM qualificati.

**Stato CAD:** MAIN V2.6 7 fogli/138 riferimenti invariata; mixer+IF455 V2.7 rimangono schematici standalone; C1601=10pF e nessuna resistenza di terminazione assegnata. PCB MAIN e FRONT reali non esistono, nessuna DRC PCB, routing 0%; BOM non rilasciata. [PR #123](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) ancora DRAFT, footprint A06 non approvata. Prossima attività: ottenere modello o caratterizzazione verificabile della sorgente IF reale sotto LO+7dBm e carichi, valutare diplexer/carico rispetto al rumore e livello IF, solo dopo modificare lo schematico. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #130 MERGED: IF455 C1601 native passband/source sensitivity

**[PR #130](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/130) MERGED**, verified main commit `898d75a453359e2980973082ce2ada97271ae759`, technical head `608f8d1ae8fe0b59f63c2349a9aa47dd0ad68e0d`. [Actions #43586012507](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43586012507) FAST, FULL KiCad9/ngspice, required gate **3/3 SUCCESS**, native FULL logs audited: **111 legacy commands** plus `PASS_NGSPICE_IF455_C1601_15_CASES_BRACKETED_OR_EXPLICITLY_OUT_OF_WINDOW_NO_VENDOR_MIXER_NO_FAB_NO_TX`.

New native test `03_Verifiche/V2.7/verify_if455_c1601_bandwidth_native.py` and report `03_Verifiche/V2.7/RAPPORTO_C1601_BANDWIDTH_SOURCE_DRAFT.md`; test included in `ci/full_regressions.py`. 15 native ngspice linear AC sweeps 300–650kHz (1401 steps), C1601 10/47/100/470/1000 pF × hypothetical Rs 50/1000/10000Ω. **11/15** transfer curves have two bracketed -3dB crossings; **4/15** (470/1000pF × 50/1000Ω) do not have full -3dB bandwidth inside the requested span and are reported with **null boundaries/BW**, not made-up Q. Nominal 10pF / Rs50Ω: peak **454750Hz**, two -3dB boundaries **435080.8Hz** and **477637.5Hz**, modeled bandwidth **42556.7Hz**, Vout/Vsource at 455kHz **0.835055562**. For 47pF/Rs50Ω peak shifts to **398250Hz**; for 100pF/Rs50Ω to **344750Hz**: selection by response *only at 455kHz* is unjustified.

First [Actions #43584881817](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43584881817) **FAIL** on unbracketed response at sweep left edge; corrected classification and preserved all runs without bypassing real failure. The final run #43586012507 3/3 PASS is the **only gate credited**. No real SBL-1+ complex IF source impedance/nonlinear model; source Rs and filter losses are bench assumptions only. **C1601 remains 10pF in unchanged real schematic**, V2.6 master still 7 sheets/138 refs; no PCB MAIN/FRONT, no actual DRC or production BOM. PR #123 A06 footprint remains unqualified DRAFT, not merged. Next technical focus: OEM IF port loading/LO conversion vs source-matched IF455 topology, detector load and noise with vendor/physical qualification. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #128 MERGED: native ngspice sweep accoppiamento C1601 IF455

**[PR #128](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/128) MERGED** e verificata su main commit `d403412915c5abe26bdb36b8e9bce7768e7f3dad`; head tecnico `06585aaa5cb0fd3fc5659ef5c4de652d81d15e27`. [Actions #43583597932](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43583597932) **FAST, FULL native KiCad9/ngspice, required gate 3/3 SUCCESS**; log FULL verificato con 111 comandi storici e `PASS_NGSPICE_IF455_C1601_15_CANDIDATE_SOURCE_CASES_NO_MIXER_MODEL_NO_FAB_NO_TX`.

Nuovo verificatore reale `03_Verifiche/V2.7/verify_if455_c1601_source_sweep_native.py`, rapporto `03_Verifiche/V2.7/RAPPORTO_C1601_SOURCE_SWEEP_DRAFT.md`, test obbligatorio registrato nella FULL CI. **15 sweep ngspice AC nativi**: C1601 10/47/100/470/1000 pF × Rs ipotetiche 50/1000/10000Ω; a 455kHz e Rs50Ω trasferimenti |Vout/Vsource| rispettivamente **0,835055562; 1,123823840; 1,030331830; 0,960992122; 0,951119294**. Reactance ideale nominale C1601 10pF: **34979,108Ω**. Le combinazioni sono **solo temporanee nel modello ngspice**; C1601 fisico resta 10pF nello schematico e non è stata selezionata nessuna sostituzione. Nessun modello impedenza complessa/non lineare reale SBL-1+, nessun adattamento o qualità del ricevitore dimostrati.

**Stato CAD:** MAIN V2.6 a sette fogli/138 refs invariata; standalone mixer/filtro IF V2.7 non integrati; entrambe le vere PCB MAIN e FRONT ancora assenti, routing 0%, DRC PCB non applicabile. [PR #123](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) rimane DRAFT non integrata: footprint A06 THT meccanicamente non qualificata, non assegnare a MX1701 nonostante sua CI verde. Prossima attività: carico/impedenza mixer IF OEM e prova del disegno meccanico TOP/BOTTOM; analizzare banda/rumore e opzioni per interfaccia senza promuovere modelli di banco a hardware. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #126 MERGED: contratto nativo mixer SBL-1+ IF → filtro IF455

**[PR #126](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/126) MERGED**, merge commit `f2b6d60b7d63b0bbe47bbdc16c625f93cbfd6c5e`, head verificato `c9b539f9b8cdd8e7b1e9873de4116c3c20572898`. [Actions #43571786977](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43571786977) **FAST, FULL native KiCad9/ngspice, required gate 3/3 SUCCESS**; 111 regressioni storiche, log `PASS_NATIVE_KICAD9_MIXER_TO_IF455_TWO_PIN_IF3_IF4_TIED_C1601_REACTANCE_NO_MATCH_NO_FAB_NO_TX`. Nuovo verificatore reale `03_Verifiche/V2.7/verify_mixer_if455_interface_native.py` e rapporto `03_Verifiche/V2.7/RAPPORTO_MIXER_TO_IF455_INTERFACE_THT_DRAFT.md`, test aggiunto a `ci/full_regressions.py`.

Il test usa **due esportazioni di netlist KiCad9 effettive**, non string matching, e verifica proposta **solo banco** `MX1701/3,MX1701/4→J1703/1→J1601/1→C1601/1` e `J1703/2→J1601/2` massa, oltre alle reti RF/LO, LC IF455, uscita J1602 e assenza di corti/rail vietati. `C1601=10pF` ha reattanza in serie ideale **34.979,108Ω a 455kHz**, non è prova di adattamento a impedenza RF 50Ω, né misura del mixer. Mancano **Zout complessa/nonlineare del mixer IF, LO reale +7dBm, load/diplexer, amplificazione IF, rumore e selettività**, più qualifica dell'OEM A06; **PR #123** rimane DRAFT aperta NON MERGED con meccanica TOP/BOTTOM e drill ancora da validare. La MAIN V2.6 a 7 fogli /138 refs e le PCB MAIN e FRONT non sono state modificate; routing 0%, nessun DRC PCB o release BOM. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 14 novembre 2026 — PR #124 MERGED: contratto nativo VCO → mixer SBL-1+ LO (nessuna qualifica hardware)

**[PR #124](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/124) MERGED**, commit `93473c2650e410a29e37ff8b581d4b9bb2e93f78`, branch originale `engineering/v27-sbl1-lo-drive-native-contract`, head tecnico `2888cd4deb7e2c69e7b8708fc7452c547abd0e90`. [Actions #43530252508](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43530252508) **FAST/FULL/required 3/3 SUCCESS**, FULL native con 111 comandi originali e risultato `PASS_NATIVE_KICAD9_VCO_TO_MIXER_LO_PORT_SEPARATE_7DBM_THEVENIN_ENVELOPE_NOT_A_VCO_OUTPUT_MEASUREMENT_NO_FAB_NO_TX` verificato nei log. Nuovo test `03_Verifiche/V2.7/verify_sbl1_lo_drive_budget_native.py` e rapporto `RAPPORTO_SBL1_LO_DRIVE_VCO_V26_CONTRACT_DRAFT.md`: obbligo di esportare con KiCad9 le vere netlist VCO V2.6 e SBL-1+ V2.7, controllare connettori `J522` CMOS / `J523` analogico separati, pin LO `MX1701/8` e ritorni a massa; matrice teorica di potenza +7dBm su 50Ω di terminazione **assunta**, due possibili iniezioni 26,545/27,455 MHz per RF27 MHz e IF455 kHz. Il nuovo test è registrato nella FULL CI. Non è una misura di uscita RF del VCO, né un modello del mixer non lineare, né approvazione dell'interconnessione. PR #123 footprint A06 ancora DRAFT indipendente e NON MERGED: [run #43524908848](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43524908848) FAST/FULL/required 3/3 SUCCESS sul suo ultimo HEAD noto `64eb81c7918a47cfcff232a9bb12dc5deff00ba7`, ma gate grafico TOP/BOTTOM e drill/courtyard ancora aperti, quindi non integrare. **Main ora contiene la sola PR #124**, mentre PCB MAIN/FRONT non esistono e routing=0%. Nessuna qualifica LO di potenza, né footprint OEM. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #120 MERGED: schematico THT KiCad9 mixer SBL-1+ OEM 4 reti, ERC0

**[PR #120](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/120) MERGED**, commit `2bfa1a76e4d78f14cfec58151db19dbb6791e093`, final head `39ddef12e9694198118b9147f10c16dbd1be3179`. [GitHub Actions #43519722696](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43519722696): **FAST, FULL KiCad9 ERC/netlist/ngspice e required gate 3/3 SUCCESS**, 111 regressioni storiche e `PASS_NATIVE_KICAD9_SBL1_4REF_4NETS_ERC0_OEM_IF3_IF4_SHORT_A06_FOOTPRINT_NOT_QUALIFIED_NO_FAB_NO_TX`. **Nuovo schematico CAD reale standalone** `04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/MIXER_SBL1_BENCH_THT_V2_7_DRAFT.kicad_sch`, `.kicad_pro`, test nativo `03_Verifiche/V2.7/verify_sbl1_mixer_bench_kicad_native.py`. Comprende mixer passivo `MX1701` Mini-Circuits **SBL-1+** A06 THT e 3 connettori THT J1701 RF, J1702 LO, J1703 IF, **ERC 0 errori / 0 avvisi** su KiCad9 e **netlist reale 4 riferimenti / 4 reti**. Verifica pin↔net nativi: `IF455_MIXER_IF = MX1701/3, MX1701/4, J1703/1` (IF3 e IF4 **uniti esternamente realmente**, obbligo OEM); `RF_27MHZ_INPUT_PENDING = MX1701/1, J1701/1`; `LO_27MHZ_OFFSET_PENDING = MX1701/8, J1702/1`; `IF_BENCH_GND = MX1701/2,/5,/6,/7 e J1701/2,J1702/2,J1703/2`. Il simbolo OEM e il connettore J2 sono presenti nella libreria `SBL1_MIXER_OEM_PINOUT.kicad_sym` e **ambedue esportati nativamente da KiCad9**. Il campo **Footprint MX1701 è volutamente VUOTO**: nessuna PCB/layout e nessun DRC.

**CI corretta onestamente senza waiver:** prima run [#43519032284](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43519032284) FULL FAIL con **3 warning** `lib_symbol_issues` per i connettori J2 incorporati nello schematico ma assenti dalla libreria esterna. Aggiunti i simboli THT J2 alla libreria, aggiornato il test del pinout OEM per isolare i pin dell'SBL-1+ dal J2 e verificare l'esportazione di **due simboli**. Seconda run **#43519722696 3/3 verde** e ERC **0/0**, nessun warning ignorato.

**Bloccanti reali prima di master/PCB:** (1) footprint OEM A06 da disegnare e confrontare con **viste TOP/BOTTOM reali** e dimensioni/raster fori, non usare un DIP8 generico; (2) verificare che il VCO master V2.6, con `Q501/Q502` 2N3904, `U520` SN74AC14N e uscite `LO1_ANALOG_OUT` e `LO1_CMOS_BUFFERED`, possa fornire in modo lineare e filtrato **+7dBm LO** al carico reale (su 50Ω teorici equivale a 5,011872mW / 0,500593Vrms / 1,415892Vpp; **NON misurati** sul VCO); (3) adattamento RF/IF del mixer passivo verso la porta IF455 misurata nella PR #117, guadagno e rumore mixer, oscillatore LO, AGC, selettività e rumore AM/FM/SSB. La perdita di conversione OEM 5,6dB tipica non garantisce il livello ai pin del rivelatore. **Nessuna integrazione nel master gerarchico MAIN V2.6** (7 fogli/138 ref) né nelle PCB MAIN+FRONT (routing **0%**). Progresso generale ~20% stima, release BOM ancora bloccata; **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**. GitHub protetto, solo branch→PR→CI→merge.

---

## 13 novembre 2026 — PR #119 MERGED: simbolo KiCad9 OEM Mini-Circuits SBL-1+ A06 passivo

**[PR #119](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/119) MERGED**, commit `b4408d2d372ee5dd90e2700b6bd0c4ba214e6f57`, final head `44d67e0b2a3667b2dc4a883a1b3b8519b6295ee0`. [GitHub Actions #43517848737](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43517848737): **FAST/FULL KiCad9/ngspice/required 3/3 PASS**, 111 comandi storici e `PASS_KICAD9_SBL1_OEM_8_PIN_A06_SYMBOL_LO_POWER_CONTRACT_NO_FOOTPRINT_NO_FAB_NO_TX`. **Nuova vera libreria KiCad9** `04_KiCad/V2.7_DRAFT/MIXER_SBL1_CANDIDATE/SBL1_MIXER_OEM_PINOUT.kicad_sym` e `sym-lib-table`: simbolo passivo `SBL-1_PLUS`, pin numerati OEM 1=RF, 8=LO, 3+4=IF da **collegare esternamente**, 2/5/6/7=GND. KiCad9 `sym export svg` **nativo PASS**, esportato SVG 32717 bytes. Campo Footprint volutamente **VUOTO**: Mini-Circuits A06 THT **non** è un DIP8 standard; quote meccaniche, pitch, verifica vista TOP/BOTTOM e pad↔pin per futuro PCB ancora assenti. Report `03_Verifiche/V2.7/RAPPORTO_MIXER_SBL1_OEM_PINOUT_LO_THT_DRAFT.md` e test `03_Verifiche/V2.7/verify_sbl1_mixer_oem_symbol_lo_contract_native.py`.

**Scelta OEM in corso:** NXP SA612AN DIP8 è **No Longer Manufactured** (fonte NXP originale); Mini-Circuits SBL-1+ è a catalogo THT passivo level-7 1–500MHz LO/RF, IF DC–500MHz, perdita conversione **5,6dB tipica**; non ha guadagno attivo. LO **+7dBm** su 50Ω ipotizzati equivale a **5,011872mW / 0,500593Vrms / 1,415892Vpp**, non è una misura dell'uscita del buffer VCO V2.6. La perdita di conversione OEM **non** è l'attenuazione in tensione con il filtro IF455 reale. Distribuzione: produttore attivo, disponibilità negozi variabile/stock a confermare. AD831 production ma *non dimostrato THT* e richiede rail 9V single/±4,5V dual: non automaticamente alternativo pin-compatibile.

**Prossimo passo concreto:** realizzare schematico KiCad9 **standalone** con MX1701 OEM, 3 connettori RF/LO/IF, **pin IF 3 e 4 uniti in netlist reale**, tutti GND e test nativi KiCad9 ERC/netlist; sempre **senza footprint mixer** e senza integrazione master. Poi qualificare LO drive VCO reale, matching IF455 a 455kHz, rumore mixer/LNA/AGC/AM/FM/SSB, MPN produzione/footprint A06 e prove hardware. Master MAIN V2.6 sette fogli/138 refs resta intatto; PCB MAIN/FRONT non esistono/routing **0%**, progresso completo ~20% stima, nessun DRC PCB. Repo main protetto, nessuna deroga CI. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #117 MERGED: modello impedenza d'ingresso IF455 verso futuro mixer

**[PR #117](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/117) MERGED** su `main` commit `403846c498f3ab8db138d9c01e68cab435bef9db`, codice tecnico final head `84a45e659e575ea245dfc4bcfae991ecc915cbba`. [Actions #43514708784](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43514708784): **FAST + FULL KiCad9/ngspice + required 3/3 SUCCESS**, 111 regressioni storiche ed esito `PASS_NGSPICE_IF455_6_SOURCE_PORT_AC_PLUS_2_COMPLEX_ZIN_NO_MIXER_NO_FAB_NO_TX`. Nuovo test `03_Verifiche/V2.7/verify_if455_two_port_source_impedance_native.py` e rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_CONTRATTO_PORTA_MIXER_SOURCE_Z_DRAFT.md`.

**Contratto KiCad standalone verificato:** `J1601/1 = IF455_SOURCE`, `J1601/2 = IF_BENCH_GND`; `J1602/1 = IF455_FILTER_OUT`, `J1602/2 = IF_BENCH_GND`. Non esiste mixer/IF reale integrato nel master V2.6. Le 8 AC native sono **6 combinazioni** sorgente di Thevenin puramente ipotetica `Rs=50Ω, 1kΩ, 10kΩ` × downstream `R100k` o surrogato JFET **passivo** `C10p/R1M/C7p`, più **2 sonde** di `Zin` complessa del filtro disconnesso dalla sorgente esterna. Sweep 300–650kHz, 1401 punti, 455kHz esatto, 16,5Ω perdita RF bobina **assunta**, trimmer 30p, R damping47k, uscita100k.

**Risultati del SOLO modello a 455kHz**, `Rs→|Vout/Vsource|`: con `R100k` **50Ω→0,835055562; 1kΩ→0,815223437; 10kΩ→0,652547922**; con gate JFET passivo **50Ω→0,665186786; 1kΩ→0,648714664; 10kΩ→0,519566010**. `Zin` del modulo J1601/1 rispetto alla massa **senza Rs esterna, downstream incluso**: con R100k `18530,81 − j19747,33 Ω` (modulo 27080,40Ω); con gate passivo `23604,58 − j18218,50 Ω` (modulo 29817,61Ω). Ingresso presenta una componente capacitiva e impedenza non definibile come puro resistor; `Rs=50Ω` NON è valore reale OEM del mixer. Il test mostra perdita del trasferimento al crescere di Rs e riproduce PR #110 a 50Ω.

**Errore CI rimosso con verifica completa:** prima run [#43513982822](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43513982822) FULL FAIL su guard testuale per identificatore `H455` assente nel sorgente di test precedente, prima degli 8 ngspice. Corretto il riferimento al contratto `CONTRACT=(...` e `RGEN src gen 50`, senza bypass, eseguita nuovamente intera FULL #43514708784 PASS 3/3. Il master originale MAIN V2.6 7 fogli/138 refs è intatto; PCB MAIN/FRONT non progettate (routing **0%**, ~20% completamento complessivo stimato), DRC fisico non applicabile.

**Prossima progettazione vincolata:** identificare e qualificare reale mixer THT e stadi IF (impedenza complessa fonte `Zsource(f)`, conversion gain/loss, rumore, uscita al livello AGC, alimentazione e LO leakage/spur) e rivelatore AM con carico reale e PVT. Solo dopo ha senso interconnettere i due blocchi nativi KiCad e scegliere R1601/R1602/C1603 e buffer. Non usare i numeri del solo generatore da banco per sensibilità d'antenna, SNR/SINAD, banda AM/FM/SSB. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**; repository pubblico protetto, nessun merge non verde.

---

## 13 novembre 2026 — PR #115 MERGED: incrocio nativo banda RF e rumore di 6 valori IF455

**[PR #115](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/115) MERGED**, commit `9e677634f9facde583cab8a48c9b190d4337b5af`, final head `3b08819af20a444c874c0afe6dafeef5cd645fd2`. [Actions #43508971077](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43508971077) **FAST/FULL KiCad9/ngspice/required 3/3 PASS**, 111 comandi storici e `PASS_NGSPICE_IF455_6_NOISE_TRADEOFF_AC_BANDWIDTH_NATIVE_NOT_RECEIVER_NO_FAB_NO_TX`. Nuovo script `03_Verifiche/V2.7/verify_if455_resistor_noise_bandwidth_crosscheck_native.py`, report `03_Verifiche/V2.7/RAPPORTO_IF455_NOISE_VS_BANDA_R_LOAD_DRAFT.md`: sei sweep AC nativi 300–650kHz/1401 punti che convalidano i 6 H455 della PR #114 e calcolano banda−3dB, fpeak e rapporto H455/Hpeak.

**Dati modello R1601 smorzamento/R1602 uscita → H455 (V/V); fpeak (kHz); BW−3dB (kHz); rumore PR114 riferito a generatore (nV/√Hz):** 47k/100k → **0,835056; 454,75; 42,557; 27,755**; 47k/220k → **1,016659; 456,00; 36,521; 24,486**; 100k/100k → **1,280374; 454,00; 27,482; 21,300**; 100k/220k → **1,711592; 455,50; 21,576; 18,306**; 220k/100k → **1,723341; 454,00; 20,289; 17,955**; 220k/220k → **2,556853; 455,25; 14,419; 14,736**. L'ultima combinazione è la migliore nel SOLO confronto di singolo risonatore passivo e noise termico a 455kHz; **NON** equivale a una banda utile/interferenza di un ricevitore AM/FM/SSB completo, né a guadagno RF attivo o sensibilità d'antenna. Rcoil 16,5Ω è ipotesi AC non OEM, sorgente50Ω ideale, nessun rumore J113/KSP10, mixer o diodo reale.

**BLOCKER obbligatorio:** specificare architettura mixer e stadio IF con livelli, impedenza complessa, reiezione canale adiacente, guadagno RF/IF, SNR/SINAD/THD e AGC reali, selezionare OEM THT in produzione e PVT/rumore, poi variare R1601/R1602 e capacità di accordo in schemi KiCad validati. Nessuna autorizzazione a promuovere l'assetto 220k/220k; master MAIN V2.6 sette fogli/138 refs, due PCB MAIN/FRONT non progettate **0% routing**, progresso complessivo ~20% stima. Nessun DRC fisico. Repository main protetto, merge via PR con required CI senza waiver. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #114 MERGED: 30 trasferimenti rumore/attenuazione RF su 6 R IF455

**[PR #114](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/114) MERGED**, commit `88ccfbd1cf9ce856078922e48a1ae08bca4f1682`, final head `2ee10222ca02b5600f58c6ca1fa23263a37bd4e8`. [GitHub Actions #43507681428](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43507681428) **FAST+FULL KiCad9/ngspice+required 3/3 SUCCESS**, 111 comandi storici, test `PASS_NGSPICE_IF455_R_DAMP_R_LOAD_30_NATIVE_NOISE_AND_TRANSFER_PROBES_NOT_RECEIVER_NO_FAB_NO_TX`. Script nuovo `03_Verifiche/V2.7/verify_if455_passive_resistor_noise_load_tradeoff_native.py`; rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_PASSIVE_NOISE_DAMP_LOAD_TRADEOFF_DRAFT.md`. **30 ngspice AC reali**: 3 valori R1601 damping 47/100/220k × 2 valori R1602 output 100/220k × 5 trasferimenti (segnale più rumore indipendente di RGEN/RCOIL/RDAMP/RLOAD), temperatura290K, integrazione RF 451–459kHz, no transistor/modello OEM.

**Misure a 455k nel modello (R1601/R1602 → |H|; output nV/√Hz; rumore equivalente al GENERATORE nV/√Hz):** 47k/100k → **0,835056; 23,17706; 27,75511**; 47k/220k → **1,016659; 24,8944; 24,48648**; 100k/100k → **1,280374; 27,27151; 21,29965**; 100k/220k → **1,711592; 31,33268; 18,30617**; 220k/100k → **1,723341; 30,9425; 17,95495**; 220k/220k → **2,556853; 37,67653; 14,73551**. Valori transfer >1 da risonanza passiva in tensione NON significano guadagno di potenza né sensibilità antenna. La variante che ha il **rumore input-referred minore a 455k** presenta **rumore d'uscita maggiore** e guadagno di tensione maggiore; occorre controllare BW/accordo/selettività e noise mixer/active prima di scegliere un prodotto.

La prima [run #43506659503](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43506659503) è FALLITA per mancata creazione directory temporanee del test, **non** per un limite RF; corretta la gestione directory, ripetuta **intera FULL** #43507681428 e tutti e tre i gate verdi, nessun bypass. **Priorità successiva:** verificare banda a −3dB e spostamenti di accordo per i medesimi sei corner di rumore; scegliere il carico soltanto insieme a una reale maschera selettività e un modello IF mixer+amplificazione e budget rumore completo. Master MAIN V2.6 7 fogli/138 refs e due PCB THT MAIN/FRONT non modificati, **PCB routing 0%** e ~20% di progetto stima; no OEM RF/Q/ESR PVT, AM/FM/SSB SNR/THD/SINAD, NO FAB/TX/BATTERIA/VEICOLO. Protezioni GitHub PR+CI mantenute.

---

## 13 novembre 2026 — PR #113 MERGED: primo budget di rumore termico RF passivo IF455

**[PR #113](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/113) MERGED**, commit `276918b93ae6a26540abee83f22711a10ae4e88d`, final head `2667024532c6d0955c4e646a9bacb953d1043a64`. [GitHub Actions #43505458793](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43505458793): **FAST+FULL KiCad9/ngspice+required gate 3/3 SUCCESS**, 111 storici, `PASS_NGSPICE_IF455_PASSIVE_THERMAL_RF_RESISTORS_2_LOADS_NOT_NF_NO_FAB_NO_TX`. Nuovo script `03_Verifiche/V2.7/verify_if455_passive_resistor_noise_budget_native.py`, rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_BUDGET_RUMORE_TERMICO_PASSIVO_DRAFT.md`: 11 AC ngspice reali, 2 carichi passivi × sorgente e rumore indipendente Johnson di RGEN50Ω/RCOIL16,5Ω/RDAMP47kΩ/RLOAD100kΩ/più R_GATE1MΩ su surrogato JFET. PSD sommerse come `4kTR×|H|²`, temperatura nominale assunta **290K**, solo RF 451–459kHz (8kHz RF), nessuna uscita audio/SNR.

**Risultati modello passivo:** riferimento R100k `|H455|=0,835055562`, densità RF output **23,17706nV/√Hz**, RF 8kHz **2,063867µV RMS**, rumore input-referred **27,75511nV/√Hz** alla **sorgente ideale del banco**, NON all'antenna. Surrogato passivo gate JFET 10p/1M/7p `|H455|=0,665186786`, rumore output **18,59163nV/√Hz**, integrato **1,654389µV RMS**, input-referred **27,94949nV/√Hz**. Contributi dominanti al riferimento: R1601 damping47k ~**17,051nV/√Hz**, R1602 load100k ~**14,775nV/√Hz**, bobina perdita assunta16,5Ω ~**5,252nV/√Hz**, Rgen50Ω ~**0,747nV/√Hz** (sommati quadraticamente); il rumore d'uscita minore dopo il carico JFET passivo **NON prova miglior SNR**, perché decade anche il trasferimento utile.

**Errore tecnico CI corretto senza bypass:** la prima [run #43504675995](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43504675995) è FALLITA per una verifica testuale che richiedeva la stringa `Zport` in un rapporto che la chiamava diversamente, prima di eseguire ngspice. Corretto il contratto documentale senza rimuovere verifiche elettriche, poi seconda run completa 3/3 PASS. Nessuna deroga ERC/DRC.

**Prossimo blocco tecnico:** quantificare il trade-off R1601/R1602 (rumore Johnson vs trasferimento vs larghezza di banda e centro), stimare input budget **soltanto dopo** identificazione vero mixer/IF, e ottenere dati OEM Rcoil/Q reale, J113/KSP10BU, demodulatore e alimentazione. Niente noise figure OEM, niente SNR/SINAD AM, niente front end completo; **nessuna sensibilità antenna deducibile**. Master MAIN V2.6 7 fogli/138 refs invariato; PCB-MAIN/PCB-FRONT fisiche e routing **0%**, progresso totale **~20% stima**. I moduli attivi standalone sono solo candidati e **NON** approvati. GitHub Actions consentite per gate tecnici, PR branch protetto. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #111 MERGED: 36 sweep IF455 trimmer sotto carico, no falsa compensazione di perdite RF

**[PR #111](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/111) MERGED**, commit `0ed6b1c2fe7c3a41c96b826568eef6a34bf5ac05`, head tecnico/documentale `cb897fe2430569f586c4098d3bc4f98f1f905799`. [Actions #43497158192](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43497158192) **FAST + FULL KiCad9/ngspice + required gate 3/3 SUCCESS**, 111 comandi legacy e `PASS_NGSPICE_IF455_36_REAL_TRIM_LOAD_AC_CASES_UNQUALIFIED_NO_FAB_NO_TX`. Script nativo `03_Verifiche/V2.7/verify_if455_loaded_trimmer_retune_native.py`, rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_TRIMMER_CARICO_RITARATURA_AC_DRAFT.md`. 36 AC ngspice nativi su filtro passivo IF455 1mH/82pF/16,5Ω ESR solo **ipotizzata**: 4 carichi × 9 Ctrim 10–50pF a passi 5pF, sweep 350–550kHz/1001 punti, 455kHz esatto, controllo valori 30pF PR #110 e direzione dell'accordo.

**Risultati a 455kHz del solo modello:** con riferimento R100k il massimo fra i nove trim è **30pF, |H|=0,835055562, fpeak≈454,8kHz**; +10k shunt **20pF, |H|=0,236347233 (+30,74% rispetto a 30pF, fpeak458,2kHz)**; +1k shunt **20pF, |H|=0,033471412 (+51,635% vs 30pF, fpeak456,8kHz)**; surrogato passivo JFET gate 10pF/1M/7pF **25pF, |H|=0,681552505 (+2,46% vs30pF, fpeak459,6kHz)**. Il carico1k perfino dopo accordo dà solo **4,01%** del trasferimento del port R100k, e il 10k **28,30%**: l'accordo **non corregge un errato carico resistivo**. La ricerca discreta non assicura un optimum continuo, reale Q/ESR, tolleranze OEM, impedenza d'ingresso J113 reale, rumore, SINAD e selettività AM/FM/SSB.

**Decisione e next engineering blocker:** fissare il **contratto IF reale** prima di integrare RX; livelli *effettivamente al pin* post mixer/IF, banda necessaria, noise budget/cascata, maschera selettività, AGC/AM/FM/SSB, impedenza complessa e buffer a carico noto. Non attribuire sensibilità antenna a modelli con generatore50Ω e diodo generic. Il master MAIN V2.6 7 fogli/138 refs rimane intatto e non è stato creato PCB-MAIN/FRONT: routing **0%**, avanzamento complessivo **~20% stima**. Componenti finali esclusivamente THT OEM attivamente prodotti, moduli KSP10BU e J113 autonomi NON QUALIFICATI, no DRC fisico. Repository pubblico protetto, modifiche con branch PR e Actions gate reali, nessuna forzatura. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #110 MERGED: Z complessa e BW passiva al port IF455, quattro carichi

**[PR #110](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/110) MERGED**, commit `4700929d0d0948b02cee5fbbdeddf2a44f21cfe7`, su codice finale `417537c431ebc333df5dabb05a94bbacf870366c`. [GitHub Actions #43495492840](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43495492840) **FAST / FULL KiCad9+ngspice / required gate 3/3 SUCCESS**, 111 comandi legacy. Nuovo script `03_Verifiche/V2.7/verify_if455_passive_port_impedance_selectivity_native.py`: **8 analisi AC ngspice native** (4 carichi × transfer/porta Zout), 300–650kHz/1401 punti, vettori complessi Re/Im, fpeak e BW−3dB. Report `03_Verifiche/V2.7/RAPPORTO_IF455_PORT_Z_COMPLESSA_BANDA_AC_DRAFT.md`. Modello passivo: L=1mH, 16,5Ω Rcoil RF **assunta da DCR non certificata RF**, C=82p + trimmer 30p, C ingresso/uscita 10p, R damping47k e R uscita100k, sorgente50Ω.

**Dati modellati al port `out` verso 455kHz:** R100k isolata `|H455|=0,835056`, `fpeak=454,75kHz`, BW−3dB **42,557kHz**, `Zport≈33541−j15429 Ω` (con R100k inclusa); shunt10k: `|H455|=0,180772`, `fpeak=440,25kHz`, BW37,418kHz, `Zport≈7959,5−j723,1Ω`; shunt1k: `|H455|=0,022074`, `fpeak=439,0kHz`, BW29,765kHz, `Zport≈975,9−j10,8Ω`; gate JFET **SURROGATO PASSIVO** 10p/1M/7p: `|H455|=0,665187`, `fpeak=450,25kHz`, BW36,296kHz, `Zport≈21582−j19978Ω`. Attenzione: `Zport` è impedenza **complessa con carico già incluso**, la sorgente è spenta in AC e si inietta 1A di prova nel simulatore. Non è impedenza intrinseca senza carico, noise figure, selettività CB completa, frequenza/rumore OEM garantiti o impedenza effettiva del J113 fisico. Il `fpeak/BW` cresce per alcuni carichi shunt nonostante l'ampiezza crolli: **non è prova di Q RF migliore**.

**Conclusione progettuale:** serve riaccordare IF455 **con il carico finale effettivamente collegato** e conoscere reale ESR/Q e impedenza; la tensione a 455kHz può perdere 78% (10k) o 97% (1k) rispetto al riferimento. Il J113 e KSP10BU standalone rimangono **non qualificati**; il modulo master MAIN V2.6 7 fogli/138 refs è intatto, PCB MAIN/FRONT **0%**. Prossima revisione studio di ritaratura 10–50pF carico-dipendente senza alterare master. Progetto completo ~20% stima, OEM/rumore/PVT/THD/AGC/FM/SSB ancora aperti. GitHub branch protetto, PR+required CI e nessun waiver, Actions usate in base alla necessità. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #108 MERGED: 10 casi IF455 a livello basso; nessuna sensibilità antenna deducibile

**[PR #108](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/108) MERGED**, commit `a7e67b5c001cbb809b3876d0907aaddf07e6a691`. [GitHub Actions #43484801445](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43484801445) sul HEAD `c98af789d7e528eaea280754d6b437ef87acd25d`: **FAST + FULL native KiCad9/ngspice + required gate 3/3 SUCCESS** con 111 comandi storici e `PASS_NGSPICE_IF455_10_LOWLEVEL_GENERIC_DIODE_J113_CASES_NO_SENSITIVITY_CLAIM_NO_FAB_NO_TX`. Nuovo script `03_Verifiche/V2.7/verify_if455_lowlevel_envelope_native.py` e rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_LIVELLI_BASSI_SOGLIA_DEMOD_DRAFT.md`.

**Esperimento:** generatore di prova ideale prima del filtro IF455, AM portante 455kHz/mod. 1kHz al 50%, `Rgen=50Ω` *assunta*, 5 ampiezze carrier picco **100µV/1mV/10mV/100mV/500mV** × due corner J113 `NJF GENERICO` IDSS2mA/VTO−0,5 o −3V; riferimento senza buffer e ramo con J113 e diodo `DGENERIC`, a 25ns. A 100µV fonte l'AFpp nel modello **senza JFET** ≈**0,804167µV**, con J113 worst −3V ≈**0,463908µV**. A 1mV: **8,041947µV** diretto contro **4,639164µV** worst; a 10mV **80,44396µV** vs **46,39673µV**; a 100mV **0,8103563mV** vs **0,4654612mV**. A 500mV: **23,925459mV** diretto vs **5,823876mV** worst. Segnale estremamente piccolo e risposta non lineare in alcune condizioni **MA** ngspice è privo di rumore e modelli OEM, perciò AFpp>0 **NON dimostra audio ascoltabile, SNR, SINAD o sensibilità antenna in µV**.

**Nuovo blocker vincolante:** definire il piano di interfaccia dal mixer al rivelatore IF455 con livello **misurato al nodo IF**, guadagno reale precedente, impedenza complessa del filtro e carico, Q/banda, margine AM, AGC, modalità FM/SSB, rumore e THD prima di selezionare/adattare un amplificatore THT. Evitare nuovi sweep del solo generatore ideale spacciati per miglioramenti di sensibilità. Gli schematici standalone KSP10BU e onsemi J113 restano candidati NON QUALIFICATI e non collegati al master. Master V2.6 7 fogli/138 refs intatto, due PCB MAIN+FRONT non disegnate/routing **0%**, avanzamento complessivo conservativo **~20%**; MPN vendor attivi finali e PVT/OEM ancora aperti. Repository PR protetto e required CI obbligatori, Actions usabili per verifiche necessarie senza limite di minuti imposto. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #106 MERGED: 18 corner IF455 J113 con C ingresso/R source, tentativo NON QUALIFICATO

**[PR #106](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/106) MERGED**, commit `b2f0d12adb33d8ab2aa67f200e939bef43adff7a`. Esecuzione ngspice sul commit tecnico `54560c8b9861b9a6136b624424fd22e8e09648f3`: [Actions #43481864363](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43481864363) **FAST+FULL+required 3/3 SUCCESS**, 111 comandi storici e `PASS_NGSPICE_IF455_J113_GENERIC_18_WORSTCORNER_CAP_SOURCE_NO_OEM_NO_FAB_NO_TX`. Esecuzione sul commit finale `2f466cf3b2f1dbec95f8827b2cda0dafb0a42477`, [#43482723008](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43482723008): **FAST/FULL/required 3/3 SUCCESS**. Nuovo script `03_Verifiche/V2.7/verify_if455_j113_worst_corner_coupling_source_native.py`, report `03_Verifiche/V2.7/RAPPORTO_J113_IF455_WORST_CORNER_C_SOURCE_DRAFT.md`. 18 transienti ngspice nativi: C1801 10/47/100pF × R1802 source 680/1k/2k2 × sorgente AM0,5/2V picco; corner **NJF GENERICO VTO=−3V IDSS=2mA**, non garanzia OEM.

**Esiti fondamentali del SOLO modello:** con ingresso sorgente 0,5V picco, AFpp riferimento diretto ~**23,925mV**; J113 baseline **C1801=10p/Rs2k2: 5,824mV (24,34%)**, modifica 47p/2k2 **9,326mV (38,98%)**, 100p/2k2 **10,058mV (42,04%)**. Con ingresso 2V il riferimento è ~**216,306mV** e J113 100p/2k2 produce **366,805mV (169,58%)**. Diminuire Rs a 680Ω/1kΩ **peggiora** il caso 0,5V nel modello; a 2V si rileva `VGSmax>0` per vari casi Rs680 e per 100p/1k, con **conduzione gate nel modello**. AFpp maggiore non è prova di qualità radio. L'opzione 100p/2k2 resta **INSUFFICIENTE ai segnali deboli** e non diviene approvata. Il KiCad J113 PR105 da banco resta invariato; il master MAIN V2.6 è intatto.

**Priorità corretta:** non fare tuning infinito con modelli generic e generatori da 0,5/2V (non livelli realistici di sensibilità RX): definire con criteri verificabili una **specifica di interfaccia IF455** (ampiezze e impedenze realistiche, noise figure/SNR/SINAD, selettività, banda passante, linearità di diodo e stadio attivo, AGC/AM/FM/SSB, PVT), reperire modelli e parametri OEM onsemi J113 e diodo, validare pinout/footprint e il circuito nel master KiCad gerarchico prima delle PCB. La sola geometria KiCad9 J113 standalone ha ERC0/netlist9refs/6nets, **non** DRC PCB. Due PCB MAIN + FRONT 100% THT, nessun layout/routing (**0%**), avanzamento complessivo conservativo **~20%**, master sette fogli/138 refs. Repository pubblico protetto, tutte le modifiche via PR e gate required; GitHub Actions autorizzate secondo qualità tecnica senza restrizioni volontarie sui minuti. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #105 MERGED: nuovo onsemi J113 THT source follower, KiCad9 ERC0 e 12 corner NJF

**[PR #105](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/105) MERGED**, commit `6d25c020b7d61263fb1b990ff922b290c4ba8b70`. GitHub Actions [#43480011279](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43480011279) sul commit `45beaf42a4dc67cfd0f351c519196fe37509a8bb` e run finale [#43480919521](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43480919521) sul commit `c3a7adeea56e2b1501473b07a21dec060b549c18`: **FAST+FULL+required gate 3/3 SUCCESS** e 111 comandi legacy FULL. Nuovo schema nativo `04_KiCad/V2.7_DRAFT/IF455_J113_SOURCE_FOLLOWER/IF455_J113_SOURCE_FOLLOWER_THT_V2_7_DRAFT.kicad_sch` + symbol-lib-table, `TH_J113.kicad_sym`, `.kicad_pro`: **9 refs THT / 6 nets, ERC0 errori/0 warning**, pin1 D / pin2 S / pin3 G onsemi J113 TO‑92 dichiarati esplicitamente e verificati con export netlist KiCad9. Attenzione: altri produttori J113 possono usare pinout diverso, perciò il componente è **OEM lockato e non automaticamente sostituibile**. Prova `PASS_NATIVE_KICAD9_ONSEMI_J113_TO92_9THT_6NETS_ERC0_PIN1D_2S_3G_NO_FAB_NO_TX`.

Nuovo deck `03_Verifiche/V2.7/spice/if455_j113_am455_generic_jfet_transient.cir` e 12 transienti ngspice (2 ampiezze AM sorgente 0,5/2V × VTO−0,5/−1,5/−3V × IDSS modellati 2/10mA), confrontando filtro LC + diodo diretto e filtro LC + JFET + diodo; `PASS_NGSPICE_IF455_ONSEMI_J113_GENERIC_NJF_12_CORNERS_NOT_OEM_NO_FAB_NO_TX`. **MODELLO NJF GENERICO, non onsemi SPICE OEM**: a 0,5V AFpp con JFET varia **5,823876–41,574927mV** (diretto ~23,925mV); a 2V varia **294,03445–532,03390mV** (diretto ~216,30mV). Corner peggiore VTO=−3/IDSS=2mA dà a 0,5V **5,823876mV**, solo **24,34%** del diretto: lo schema J113 **non è approvato** per integrazione, benché l'interfaccia ad alta Z sia più promettente del BJT precedente. Alcuni corner 2V portano source vicino/sotto 0V; AFpp non misura distorsione/SNR. La prima FULL ha fallito per comando ngspice incapace di risolvere `v(gate,source)` in `.meas`; corretto con sonda di tensione differenziale VCVS ad ingresso idealmente infinito `EGS`, non rimosso il controllo. Report `03_Verifiche/V2.7/RAPPORTO_IF455_ONSEMI_J113_SOURCE_FOLLOWER_DRAFT.md`.

**Passaggio successivo già definito:** esplorare C1801 accoppiamento e R1802 source con scenario VTO=−3/IDSS=2mA per migliorare segnale debole senza peggiorare swing, poi verificare bias PVT OEM, linearità THD/IMD, rumore, impedenza vera, decoupling alimentazioni e gate-source alla presenza di RF. Master MAIN V2.6 7 fogli/138 refs intatto; moduli V2.7 autonomi, due PCB non avviate, routing 0%, avanzamento ~20% stima. Repository pubblico con protezioni branch PR+required CI, user non impone limiti minuti Actions. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #104 MERGED: 16 casi ngspice del BJT IF455 ad alta impedenza (NON APPROVATO)

**[PR #104](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/104) MERGED**, commit `d1fda6af10a5534d335ab647268a4d1c7d887f44`. Esecuzione nativa [GitHub Actions #43477471030](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43477471030) (modifica tecnica, 111 comandi storici) **FAST+FULL+required SUCCESS 3/3**; run finale dopo aggiornamento del report [#43478153999](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43478153999) anch'esso **3/3 SUCCESS**. Nuovo verificatore `03_Verifiche/V2.7/verify_if455_highz_bias_coupling_screen_native.py`, integrato nel runner FULL preesistente: 8 configurazioni reali di C1701/partitore KSP10 con sorgente AM 0,5V e 2V picco (16 transienti ngspice), modello BJT e diodo generic, passo 25ns, confronto tank e AFpp non lineare. Report `03_Verifiche/V2.7/RAPPORTO_IF455_HIGHZ_BIAS_COUPLING_SCREEN_DRAFT.md`.

**Numeri importanti del SOLO modello:** baseline C1701=10n/partitore22k–10k → AFpp con buffer **0,752869mV** a 0,5V e **15,565562mV** a 2V; con partitore 220k–100k e C1701=47p → **10,80998mV / 372,99562mV**; con 470k–220k e C1701=10n → **23,966195mV / 468,95129mV**; percorso diretto senza buffer ≈**23,925mV / 216,298mV**. A ingresso 2V i casi con alto bias presentano source/emitter in alcuni istanti circa **0V o lievemente negativo**, sicché AFpp più grande non dimostra buona linearità o qualificazione RF. La sola diminuzione di C1701 a 2,2p **non risolve** i segnali deboli. **Topologia KSP10 non ancora approvata**: servono controllo PVT, noise, distorsione, ingresso tank e modelli OEM. Lo screening ha motivato la separata proposta di source follower JFET onsemi J113 THT (da validare autonomamente con PR, non automaticamente promuovere).

Master MAIN KiCad V2.6 7 fogli/138 refs intatto; due PCB fisiche ancora non disegnate, **0% layout/routing**, progresso complessivo **~20% stima**. Nessuna deroga di ERC/DRC o promessa di produzione. Repository protetto: commit tecnici via PR e required Actions; nessun limite di minuti imposto per risparmio, ma controlli basati sul rischio. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #102 MERGED: convergenza numerica della cascata IF455–KSP10–AM455

**[PR #102](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/102) MERGED**, commit `1582ca3e905a10e4c299f8617616dddb0121aa29`. GitHub Actions [#43474856530](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43474856530) sul commit finale `10e3e1447d624716b71fbf57159f1b0e07a8fa26`: **FAST / FULL native KiCad9+ngspice / required gate 3/3 SUCCESS**; 111 comandi regressivi storici eseguiti, nuovo gate `PASS_NGSPICE_IF455_KSP10_AM455_6_TIMESTEP_AUDITS_NOT_OEM_NO_FAB_NO_TX`. Lo script nativo `03_Verifiche/V2.7/verify_if455_ksp10_cascade_timestep_convergence_native.py` impone ora **variazione inferiore al 2% fra 25 e 12,5 ns per tutte le otto metriche RF/AF** (due livelli × quattro misure): tutte superate realmente, massimo rilevato **1,4955%** (AF buffer, ingresso 2V). Report completo `03_Verifiche/V2.7/RAPPORTO_CASCATA_IF455_KSP10_CONVERGENZA_TIMESTEP.md`.

**Esito quantitativo MODELLO GENERICO a timestep 12,5ns:** sorgente AM 0,5V picco → audio senza buffer **0,024045417 Vpp**, con buffer Q1701 **0,000755608 Vpp** (**3,1424% del diretto**). Sorgente AM 2V picco → audio senza buffer **0,216750780 Vpp**, con buffer **0,015801883 Vpp** (**7,2903% del diretto**). La riduzione del segnale nel filtro caricato dal follower rimane forte. L'architettura Q1701 KSP10BU con polarizzazione 22k/10k e accoppiamento 10nF è **NON APPROVATA** per integrazione nel master. Non significa che il transistor fisico KSP10BU sia intrinsecamente inadatto: l'insieme polarizzazione/adattamento/diodo e i modelli devono essere revisionati.

**Nota storica critica:** i valori 200ns delle PR #94/#95/#96 erano sensibili al timestep, come già precisato nella #101. Il test #102 dimostra convergenza *pratica limitata alle misure e al modello* fra 25→12,5ns, NON modello OEM o prestazioni hardware. Mancano dati vendor e qualifica produzione RF attiva, input Z complessa, rumore/AGC/FM/SSB, alimentazioni sicure, PCB-MAIN e FRONT, BOM e footprint. Master MAIN V2.6 sette fogli/138 refs intatto; V2.7 moduli standalone; PCB routing/DRC reale **0%**, progetto completo **~20% stima**. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

**Prossima priorità ingegneristica:** confrontare alternative THT di adattamento IF a elevata impedenza d'ingresso, prima su modelli espliciti con carico filtro e diodo, quindi su KiCad 9 nativo/ERC/netlist con componenti OEM attivamente prodotti; valutare bias PVT, rumore, selettività e alimentazioni prima di qualunque integrazione nel master. Actions usabili senza limite di minuti come scelta dell'utente, ma PR protette e required gate rimangono obbligatori. `main` protetto: checkpoint aggiornato tramite PR, non push diretto.

---

## 13 novembre 2026 — PR #101 MERGED: filtro IF455→KSP10→AM455, buffer candidato respinto dal modello

**[PR #101](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/101) MERGED**, commit `cf1078c3ed557ec728c32113b179435675eb2b15`. L'esecuzione finale [GitHub Actions #43473518325](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43473518325) sul final commit tecnico/documentale `b0bf220e7f644d06b0536f4083eab947a7ab0269` è **FAST+FULL+required gate 3/3 SUCCESS**. Run precedente [#43473046507](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43473046507) ha eseguito il calcolo nativo a 50ns: `PASS_NGSPICE_IF455_KSP10_AM455_GENERIC_NONLINEAR_CASCADE_NOT_OEM_NO_FAB_NO_TX`, 111 comandi storici FULL, ripetibilità del riferimento a 50ns < **0,061%**.

**Misure ngspice MODELLO GENERICO**: a 0,5V picco AFpp filtro diretto+diodo **23,326606mV**, con Q1701 buffer+diodo **0,741563mV** (3,179% del diretto), picco RF tank **0,3938995V → 0,09449585V**. A 2,0V picco AFpp diretto **214,324050mV**, con Q1701 **14,614407mV** (6,8188% del diretto), RF tank **0,7549801V → 0,3779901V**. Nel modello, **la polarizzazione e il collegamento tramite C1701 da 10nF caricano il filtro invece di adattarlo: l'attuale follower KSP10BU NON va integrato nella radio**. KiCad Q1701 PR #97 rimane *schematico da banco*, non un modulo RF approvato.

**Anomalia numerica importante:** il modello legacy a 200ns (PR #94/#95) aveva `0,17444891Vpp` a 2V picco, ma lo stesso deck ricalcolato a 50ns fornisce `0,21445359Vpp` (+22,9%). La referenza diretta PR #101 a 50ns dà `0,21432405Vpp` (-0,0604% dal deck legacy ricalcolato allo stesso passo). I dati storici sono **sensibili al timestep**, non dimensionamenti convergenti. Il primo run PR #101 è fallito correttamente per discrepanza fra passi 200ns e 50ns; la correzione ha aumentato la risoluzione e introdotto controllo indipendente a parità di passo, **nessun bypass**. Per qualifica serve sweep 50/25/12,5ns, in questa revisione successiva in corso. Report `03_Verifiche/V2.7/RAPPORTO_CASCATA_IF455_KSP10_AM455_TRANSIENT_GENERIC_DRAFT.md` e deck/script reali.

**Stato fisico:** master MAIN V2.6 7 fogli/138 refs intatto, Q1701 standalone non interconnesso, PCB-MAIN e PCB-FRONT non progettate fisicamente, layout 0%; progresso complessivo ancora **~20% stima**. Mancano modello OEM, impedenza, rumore, selettività, FM/SSB, AGC, alimentazioni sicure, BOM THT attiva e footprint finali. L'uso GitHub Actions rimane orientato alla qualità, protezioni PR+CI sempre attive. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #99 MERGED: KSP10BU THT bench 9 corner DC + AC ngspice GENERICO

**[PR #99](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/99) MERGED** commit `30dca9bc5187b40a9a54a6fbb2af079ea5d59ec5`, GitHub Actions [#43469630157](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43469630157) sul final commit tecnico `e12c2e681f498e89bdd97ecdd65dea61782c96c8`: **FAST + FULL + required gate 3/3 SUCCESS** con 111 comandi storici FULL e `PASS_NGSPICE_IF455_KSP10_GENERIC_BJT_9_BIAS_AC_CORNERS_NOT_OEM_NO_FAB_NO_TX`.

Nuovo deck nativo `03_Verifiche/V2.7/spice/if455_ksp10_generic_bjt_bias_ac.cir`, script `verify_if455_ksp10_generic_bjt_bias_ac.py`, gate nel runner FULL esistente. Nove transienti+AC a **455 kHz** di un circuito che riprende lo schematico KiCad9 della PR #97: alimentazione banco 5,5/6/6,5 V × beta generic40/80/160. Nel **solo modello** emettitore **1,011065–1,364428 V**, corrente emettitore **0,459575–0,620195 mA**, rapporto AC ampiezza `Vout/Vsource` **0,966637–0,973451**; per rail 6V β80: base **1,830799V**, emettitore **1,192877V**, corrente **0,542217mA**, ampiezza AC **0,970670**. Report con tutti e 9 i casi `03_Verifiche/V2.7/RAPPORTO_KSP10_IF455_GENERIC_BJT_DC_AC_CORNERS_DRAFT.md`.

**Non equivocare:** BJT `QGEN` non è un modello OEM di KSP10BU, beta e capacità non sono tolleranze certificate, il test non include filtro tank/demod AM, rumore, PVT, selettività, guadagno IF o instabilità hardware. Il Q1701 KSP10BU resta CANDIDATO THT con pinout OEM verificato, non parte BOM finale qualificata. La policy Actions è lasciata abilitata per ogni controllo necessario, senza trattare il costo dei minuti come vincolo progettuale secondo la decisione dell'utente; rami protetti e PR/CI obbligatorie restano. Master MAIN V2.6 7 fogli/138 refs intatto; nuovo follower V2.7 isolato, nessuna PCB reale, layout/routing **0%**, avanzamento complessivo **~20% stima**. Prossimo gate: prova di interfaccia filtro IF455→follower→rivelatore AM con carico non lineare, datasheet OEM e caratterizzazione del rumore/stabilità prima di revisione RF. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #97 MERGED: primo stadio IF455 THT KSP10BU, KiCad9 nativo ERC0

**[PR #97](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/97) MERGED**, commit `b16778889558d08c4fb8e98c54cd2d41a6238526`. GitHub Actions [#43468430403](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43468430403) sul final HEAD tecnico `1807d9520aab12f9e49154073bf5abbe01e5d964`: **FAST + FULL + required gate 3/3 SUCCESS**; 111 comandi legacy eseguiti. Nuovo test `PASS_NATIVE_KICAD9_IF455_KSP10BU_BENCH_THT10_PINPAD_NET_ERC0_NO_FAB_NO_TX`: **KiCad9 ERC 0 errori / 0 warning**, netlist esportata e controllata: 10 componenti THT, 6 reti, tutte pin↔net verificate.

**Revisione CAD reale**: standalone `04_KiCad/V2.7_DRAFT/IF455_KSP10_FOLLOWER/IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT.kicad_sch` + progetto `.kicad_pro`, symbol library `TH_IFBUF.kicad_sym` + `sym-lib-table`. Circuito banco a collettore comune Q1701 onsemi **KSP10BU RF TO-92 candidato**: pin1 BASE/pin2 EMETTITORE/pin3 COLLETTORE secondo datasheet OEM, rail laboratorio 6V separato, 22k/10k bias, 2k2 emettitore, due 10nF AC e carico 100k. DigiKey Italia elenca KSP10BU come ACTIVE; qualifica OEM di produzione, guadagno/noise/PVT/impedenza a 455k, layout e stabilità **ancora aperti**. Prime due esecuzioni FULL avevano correttamente bloccato errori filo e warning libreria; risolti con correzioni CAD reali, **nessun waiver**. Rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_KSP10BU_FOLLOWER_CAD_DRAFT.md`.

**Protezione repository:** il tentativo di aggiornare direttamente `main` dopo merge è stato respinto da GitHub (`Changes must be made through a pull request`), quindi questo checkpoint è inviato via branch e PR dedicata, rispettando la protezione. L'utente ha comunicato che i repository ora sono pubblici e non desidera vincolare l'uso di Actions ai costi: la priorità resta controlli tecnici necessari, non risparmio runner; mantenere gate verdi per ogni merge.

Il master V2.6 sette fogli/138 refs non è stato modificato; i moduli V2.7 restano isolati, PCB-MAIN e PCB-FRONT non disegnate, layout/routing **0%**, avanzamento complessivo ancora **~20% stima**, non aumentare per un test KiCad bench. Prossimo blocco tecnico: simulazione di polarizzazione e piccoli segnali dello stadio KSP10 con modelli non OEM chiaramente etichettati, poi modello/dati OEM, impedenza d'ingresso effettiva sul tank, rumore e selettività. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #96 MERGED: matrice impedenza sorgente IF455 e livelli AM, simulazione nativa

**[PR #96](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/96) MERGED**, commit `4c5b5293fb1d1f6fc9d667fa6add008c7fc24f98`. Workflow [#43460892882](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43460892882) sul commit tecnico `40ca3846c2db35a7267750e34d79c01712ae88d2`: **FAST + FULL native KiCad9/ngspice + required gate 3/3 SUCCESS**, con **111 comandi legacy** eseguiti e `PASS_NGSPICE_IF455_SOURCE_IMPEDANCE_LEVEL_MATRIX_GENERIC_ONLY_NO_FAB_NO_TX`. Nuovo verificatore `03_Verifiche/V2.7/verify_if455_source_impedance_matrix_native.py`: sei transienti **ngspice reali**, incrocio Rs 50/500/5000Ω con AM 0,5/2,0 V picco. Uscite AFpp filtro+diodo `DGENERIC` ai tre Rs: per 0,5V **0,011504869 / 0,011262692 / 0,009101405 V**; per 2V **0,17444891 / 0,18185761 / 0,1527582 V**. Riduzione (50→5000Ω) di ~**20,89%** e **12,43%** nel modello rispettivamente. Risposte **non monotone** a tutti gli Rs: a 2V il risultato con 500Ω supera quello con 50Ω, quindi nessuna conclusione puramente lineare. Riferimenti diretti e picchi RF documentati in `03_Verifiche/V2.7/RAPPORTO_IF455_ZSOURCE_LIVELLO_MATRIX_DRAFT.md` aggiornato dopo merge. Gancio nel runner FULL esistente senza job Actions addizionali.

**Limiti irrisolti:** modello diodo non OEM, Rs puramente resistivo, Rcoil 16,5Ω ipotetica non perdita RF misurata; assenti guadagno/impedenza complessa del driver, rumore, SNR/SINAD, bande FM/SSB, PVT, filtri selettivi, prova banco e buffer THT qualificato. Il master MAIN V2.6 resta **7 fogli / 138 posizioni**; draft V2.7 separati, nessuna PCB-MAIN o PCB-FRONT instradata, **layout 0%, stima progetto ~20%**. Prossimo intervento prioritario: definire specifiche e candidati reali attivi OEM THT per interfaccia IF, validare circuiti con KiCad nativo e prove di carico/rumore prima di integrazione. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #95 MERGED: risposta transitoria AM455 ai livelli IF, modello generico

**PR [#95](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/95) MERGED**, SHA `bc7eebff2b11103b1daa372780afc8fed3974929`. CI [#43456512235](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43456512235) sul HEAD tecnico `4bcbb33c0437f288c1e246f6b3f23ab731bd407e`: **FAST + FULL + required gate 3/3 SUCCESS**, 111 comandi legacy eseguiti; `PASS_NGSPICE_IF455_AM455_GENERIC_DIODE_INPUT_LEVEL_SWEEP_NOT_OEM_NO_FAB_NO_TX`. Verificatore reale `03_Verifiche/V2.7/verify_if455_am455_input_level_sweep_native.py` usa ngspice quattro volte sul deck combinato PR #94, con sorgente AM 455kHz modulata 1kHz 50% e Vpicco `0,2/0,5/1/2`. Risultati modello AFpp *filtrato* **0,001312202/0,011504869/0,06547246/0,17444891 V**; AFpp *diretto di riferimento* **0,006729355/0,23901695/0,8542723/2,0377306 V**; rapporti **19,50/4,81/7,66/8,56%**, NON monotoni. Sono risultati di diodo generico e sorgente ideale, **non** sensibilità del ricevitore, rumore, SINAD o comportamento OEM 1N4148; il riferimento diretto non è candidato di filtro. Runner FULL preesistente, nessun nuovo job GitHub Actions. Report `03_Verifiche/V2.7/RAPPORTO_IF455_AM455_SWEEP_LIVELLO_GENERIC_DRAFT.md` aggiornato con le misure dopo il merge.

**Prossimo blocco concreto:** definire il livello/impedenza del driver IF reale e un modello OEM con variazioni PVT; valutare stadio THT di adattamento/buffer con misure RF e analisi del rumore prima di abilitare l'integrazione del rivelatore. Master MAIN V2.6 a 7 fogli / 138 refs invariato; entrambi i pilot IF455 e AM455 standalone, PCB-MAIN e PCB-FRONT non instradate, layout 0%, complessivo **~20% stima**. L1601 footprint coil ancora provvisorio, C1603 trimmer non ancora validato su PCB, sicurezza alimentazioni/FМ/SSB/AGC/S-meter e BOM finale aperte. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #94 MERGED: transitorio non lineare IF455→AM455 con diodo GENERICO

**PR [#94](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/94) MERGED** con SHA `9f218cbcc888b03247a03399bca41ea3b57c5bd9`. La CI del commit tecnico `75b6271b59d6ab16dddddf1d3ce2732041bb2f46`, [run #43455702580](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43455702580), ha **FAST + FULL + required gate 3/3 SUCCESS**, con **111 comandi storici FULL** eseguiti. Il log nativo ngspice riporta `PASS_NGSPICE_GENERIC_DIODE_TRANSIENT_NOT_OEM_NOT_HARDWARE_NO_FAB_NO_TX` e misure sul modello: AF picco-picco filtro+diodo **0,17444891 V**, AF del rivelatore alimentato direttamente **2,0377306 V**, rapporto **8,56094%**, massimo RF positivo al nodo uscita filtro **0,6972108 V**. Il deck assume sorgente AM 455kHz picco 2V, modulazione 1kHz 50%, 50Ω, L1mH, 82pF+30pF trimmer, Rcoil16,5Ω ipotetica; diodo `DGENERIC` già usato nel banco. **NON è macromodello OEM della 1N4148** e il confronto diretto non è un'architettura RF approvata: non esprime sensibilità reale della radio né giustifica ancora un buffer scelto.

**Modifiche reali integrate**: deck `03_Verifiche/V2.7/spice/if455_am455_nonlinear_transient_generic.cir`, verificatore `verify_if455_am455_nonlinear_transient_native.py`, gancio nel runner `ci/full_regressions.py` **senza nuovo job GitHub Actions**, rapporto `RAPPORTO_IF455_AM455_TRANSITORIO_NONLINEARE_GENERIC_DRAFT.md` aggiornato successivamente con risultati CI. **Master MAIN V2.6 ancora invariato**, sette fogli/138 posizioni; moduli KiCad9 V2.7 standalone, non interconnessi su scheda fisica. Prossimo blocco: sweep transitorio di ampiezza e modelli/corner diodi, caratterizzazione IF source/input, scelta IF/buffer THT e selettività, poi FM/SSB/AGC/S-meter e alimentazioni. Induttanza L1601 footprint non qualificato, disegno PCB-MAIN e PCB-FRONT **0%**, complessivo **~20% stima**. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 13 novembre 2026 — PR #92 MERGED: sensibilità al carico d'uscita IF455 verificata in ngspice

**PR [#92](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/92) MERGED** su `main` SHA `a965d3bc585e4a0cfe9ded4edea59086c6bcf7cf`. GitHub Actions [#43442916740](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43442916740) **3/3 PASS** sul HEAD `ede2503195a25abd15ec77f0f64a1b4302c8f44f`: FAST PASS, FULL KiCad9/ngspice con **111 comandi storici** PASS, required gate PASS. Log nativo ngspice `PASS_NGSPICE_IF455_DETECTOR_LOAD_SENSITIVITY_SURROGATES_NOT_DIODE_NO_FAB`: rapporto trasferimento |Vout/Vin| a 455 kHz del **modello** con tank L1mH, C82pF, Ctrim30pF, Ccoupling10pF, Rcoil16,5Ω **assunta**:
- Solo R1602 uscita 100kΩ: `0.835056`.
- In parallelo ulteriore resistenza 10kΩ: `0.180772` (circa **−78,35%** rispetto al riferimento).
- In parallelo ulteriore resistenza 1kΩ: `0.022074` (circa **−97,36%**).

**Interpretazione vincolante:** i due carichi aggiunti sono **surrogati resistivi**, NON l'impedenza reale non lineare della 1N4148. I risultati dimostrano la vulnerabilità del circuito al carico, **non** provano che il diodo reale abbia quegli effetti o che un buffer specifico sia obbligatorio. Serve la simulazione transitoria dello stadio combinato e qualifica del livello/impedenza dell'amplificatore IF. Report `03_Verifiche/V2.7/RAPPORTO_IF455_AM455_CARICO_USCITA_NGSPICE.md`; deck/script nelle verifiche V2.7. Riutilizzato runner FULL senza job Actions aggiuntivo.

**Gestione corretta delle PR concorrenti:** il contratto KiCad9 a due fogli J1602→J1501 era già MERGED con PR #89 e relativo checkpoint PR #90; le PR #88 e #91, duplicate o in conflitto documentale, sono state CLOSED senza merge, evitando di sovrascrivere `main` o duplicare test. Solo il nuovo studio di carico della #92 è integrato.

**Rilascio NON autorizzato:** master MAIN V2.6 7 fogli/138 posizioni intatto; IF455 e AM455 sono moduli KiCad9 standalone senza cablaggio fisico; mancano IF/mixer, FM/SSB, AGC, S-meter, alimentazioni sicure, selettività e BOM/footprint finali, PCB layout 0%, complessivo circa **20% stima**. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #89 MERGED: contratto pin IF455 TANK→AM455 ENVELOPE

**PR [#89](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/89) MERGED** su main `214e063a7c016613ae4c28f77f79ff01f3a4d2b3`; run [#43441748177](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43441748177) **3/3 PASS** su final HEAD `d47b7baaff79d0ebcc9a829dd74447e92b6bc9e6`, FAST/FULL KiCad9/ngspice/required gate tutti verdi e 111 comandi legacy conclusi. La nuova verifica `PASS_KICAD9_NATIVE_IF455_AM455_2WIRE_IF_CONTRACT_NO_FAB_NO_TX` ha esportato e confrontato **realmente le due netlist autonome KiCad9**, stabilendo J1602.1→J1501.1 (RF IF 455kHz e anodo D1501.2), J1602.2→J1501.2 (massa/ritorno), assenza di commistione 6V AUDIO, PLL, TX e 13,8V. La mappa cavi è **logica da banco**, non un PCB o un cablaggio reale costruito o qualificato. Nuovi file `03_Verifiche/V2.7/verify_if455_am455_interface_native.py` e `RAPPORTO_CONTRATTO_IF455_AM455_THT.md`, nuovo gate nel runner FULL esistente.

**Prossima priorità concreta:** simulare l'effetto del **diodo AM non lineare** sull'impedenza e sull'accordo del filtro IF455 con C1603 trimmer regolabile; precedenti sweep hanno Rload100k ma non carico reale D1501. Mancano OEM RF model, guadagno IF, SSB/FM/AGC, filtro reale, layout e DRC. L1601 bobina footprint PROVISIONAL, C1603 EW GKG50015 ora P5mm da disegno OEM ma clearance PCB non provata; master V2.6 7 fogli/138 refs e tutte le partizioni THT invariati. Completamento complessivo **~20% stima**, PCB fisiche e routing **0%**. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — nuovo contratto pin↔net IF455 Tank→AM455 Envelope, in revisione

**Base main verificata:** commit `54dc37e09368073e2c3cd58f416fd08464dfe061` (PR #86/#87 MERGED, nessuna PR aperta). Nuovo branch tecnico `engineering/if455-am455-native-interface-20261113`, ancora **NON INTEGRATO**: verifica `03_Verifiche/V2.7/verify_if455_am455_interface_native.py` con **due netlist esportate da KiCad9 reale** per assicurare collegamento logico fra J1602 del tank IF455 e J1501 del rivelatore AM455 (pad1 segnale 455k AM IF, pad2 massa), anodo D1501 pin2 in ingresso, resto rivelatore J1502 AF out, nessuna commistione con rail 6V audio/PLL/TX/13,8V. Aggiunto al runner FULL preesistente `ci/full_regressions.py` senza job extra Actions. Rapporto `03_Verifiche/V2.7/RAPPORTO_CONTRATTO_IF455_AM455_THT.md`. **CI ancora da verificare; non merge fino al gate verde**.

**Limite cruciale:** **NON** è un collegamento di PCB o un harness fisico, e la simulazione AC del tank con Rload100k **NON** garantisce risposta quando caricato dal diodo 1N4148 **non lineare**; serve simulazione transitoria dell'assieme e un IF driver/buffer qualificato. Filtro e detector restano 2 pilot THT separati, master MAIN V2.6 7 fogli/138 refs non modificato, bobina L1601 con footprint PROVISIONAL, C1603 GKG50015 quote OEM ma clearance PCB ancora non validata, 2 PCB fisiche non disegnate, layout0%, complessivo ~20% stima. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #86 MERGED: correzione meccanica C1603 GKG50015

**PR [#86](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/86) MERGED** su main, SHA `20e417126d89af9aa66be5ff78d4be636d0c19ae`. Run [#43440490803](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43440490803) **3/3 PASS** sul final HEAD `91c062c6005a345129bd98e840580701b87421a5`: FAST success, FULL KiCad9/ngspice + 111 comandi storici success, required gate success. Log: ERC **0 errori/0 warning**, `PASS_KICAD9_IF455_THT9_ERC0_VARIABLE_10TO50PF_PROVISIONAL_NO_FAB`, `PASS_NGSPICE_IF455_VARIABLE_10TO50P_TUNING_RANGE_ONLY_NOT_RF_QUALIFIED_NO_FAB`.

**Correzione CAD concreta**: il trimmer C1603 EW GKG50015 precedente aveva footprint provvisorio *sbagliato* a 2,50mm. Dal disegno EW serie GKGxx015 top-adjust risultano **2 fori da Ø1,2mm distanti 5,0mm** e terminali rotor/stator. Rimossa l'impronta sbagliata `Trimmer_GKG50015_2pad_PROVISIONAL`; aggiunta vera impronta KiCad9 `TH_TANK:Trimmer_EW_GKG50015_P5.00mm_OEM_DRAFT` (pad2 rotor collegato GND a x0, pad1 stator nodo IF455_TANK a x5; rame Ø2,2mm, footprint F.Fab Ø6mm e F.CrtYd conservative). Aggiornati schema nativo, simbolo locale e test che controlla pad/drill/passo e rifiuta footprint vecchio. Il datasheet indica TCC del GKG50015 **N2200±800ppm/°C**, non NPO; Q @1MHz non equivale a garanzia @455kHz. La bobina L1601 Delevan conserva footprint coil 15,24mm **PROVISIONAL** non verificato come passo di montaggio; progetto **NO FAB**. Rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_GKG50015_TRIM_REGOLABILE_DRAFT.md` aggiornato.

**Non confondere ERC con DRC:** manca un file PCB reale, quindi DRC fisico e clearance reali non ancora eseguiti. Master MAIN V2.6 7 fogli/138 refs non modificato; moduli V2.7 IF455, AM455, audio ancora separati. Layout/routing delle due PCB **0%**, avanzamento complessivo ~20% stima. Prossimo gate di progetto: continuità pin↔net IF455 filter→AM455 demod da verificare e poi effetto del carico del rivelatore su accordo/AF. **NO FAB/TX/BATTERIA/VEICOLO**.

---

## 13 novembre 2026 — nuovo footprint C1603 GKG50015 corretto da disegno OEM, PR in review

**Bootstrap verificato live su main:** commit `03ea2ec6bf33afd1a6095097246723ec1394d792`, nessuna PR aperta, AGENTS e checkpoint riletti. Branch `cad/if455-gkg50015-oem-footprint-20261113` NON ancora integrato. La fonte **OEM EW Electronics GKGxx015** [disegno meccanico](https://datasheet.ersaelectronics.com/static/datasheets/ew-electronics/ew-electronics-gkg30015.pdf) mostra per C1603 **GKG50015 top-adjust** due fori THT **Ø1,2mm con interasse 5,0mm**, diametro corpo Ø6,0±0,2mm e terminali rotor/stator. **Scoperto e corretto errore nella precedente footprint**: `TH_TANK:Trimmer_GKG50015_2pad_PROVISIONAL` simulava erroneamente 2,50mm ed è stata rimossa. Nuovo file reale `04_KiCad/V2.7_DRAFT/IF455_TANK/TH_TANK.pretty/Trimmer_EW_GKG50015_P5.00mm_OEM_DRAFT.kicad_mod`, pad2 x0=rotore a `IF_BENCH_GND`, pad1 x5=statore al `IF455_TANK`, foro1,2mm, rame Ø2,2mm deciso CAD, corpo F.Fab Ø6mm, courtyard tentativo. Simbolo `TH_TANK:CT`, schema embedded e libreria locale aggiornati. `verify_if455_tank_native.py` ora **rifiuta la vecchia impronta** e verifica coordinate 5,00mm, ordine pad/ruolo, drill e netlist nativa. Nuovo rapporto nel `RAPPORTO_IF455_GKG50015_TRIM_REGOLABILE_DRAFT.md`. La CI finale della PR deve ancora confermare gate nativi.

**Qualifica ancora aperta:** installazione e rotore/statore da confrontare su campione con orientamento reale OEM; pad Ø2,2mm/clearance e processo saldatura non validati su PCB. EW GKG50015 è **N2200±800ppm/°C** (non NPO), Q dato @1MHz e non @455kHz. **L1601 Delevan 2500-28J conserva footprint 15,24mm PROVISIONAL** non qualificato per piegatura/assemblaggio; datasheet di serie fornisce corpo Ø4,83mm×11,18mm e reofori Ø0,635mm ma non validazione foro/passoreale. Continuità e ERC non garantiscono stabilità/riduzione spur/canale. Il master V2.6 7 fogli/138 refs e architettura 2 PCB rimangono invariati; schematico tank separato; layout/routing0%, avanzamento ~20% stima. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #84 MERGED: accordo IF455 regolabile su schema THT e simulazione ai corner

**PR [#84](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/84) MERGED** su main `ce74fb2b929986c587fdec5677f51729ea67d702`; GitHub Actions [#43414613097](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43414613097) **3/3 PASS** sul final HEAD `9bba90431c3ded21231417e8b72605c0e7d15d95`: FAST, FULL KiCad9/ngspice e required gate success. Log FULL reali: `PASS_KICAD9_IF455_THT9_ERC0_VARIABLE_10TO50PF_PROVISIONAL_NO_FAB` con `0 Errors 0 Warnings`; `PASS_NGSPICE_IF455_VARIABLE_10TO50P_TUNING_RANGE_ONLY_NOT_RF_QUALIFIED_NO_FAB`, 1201 righe AC per 8 reti, con picchi **estremi** misurati: L−5% `510533.333/432400Hz`, Lnom `497466.667/421466.667Hz`, L+5% `485466.667/411200Hz`, Lnom+Cpar3.23pF `489733.333/416666.667Hz` (Ctrim=10pF/50pF). Il valore 455kHz si trova all'interno dei quattro intervalli del modello; 111 comandi legacy PASS. Non equivale a precisione di taratura, Q, banda selettiva o prestazione hardware.

**Nuovo schema KiCad9 reale:** nel tank IF455 C1602 da 110pF a **82pF C0G THT** e C1603 da 2,2pF a **EW Electronics GKG50015 THT trimmer 10–50pF CANDIDATO**; nuovo simbolo `TH_TANK:CT`, footprint locale `TH_TANK:Trimmer_GKG50015_2pad_PROVISIONAL` con **geometria non verificata da disegno OEM, NO FAB**. L1601 resta Delevan 2500-28J 1mH candidato con footprint coil PROVISIONAL. Tutti gli ingressi/uscite e i nove riferimenti, quattro reti restano invariati. Vecchie simulazioni del circuito 110pF fisso ancora eseguite come regressioni storiche, con documentazione del loro perimetro.

**Blocchi attivi:** MPN e impronte coil/trimmer industrialmente confermate e misure RF (Q a 455k, SRF reale, ESR, perdite, risposta IF con ingressi e carichi reali, accessibilità trim), filtro selettivo e amplificatore IF, mixer 10,695→455, demod FM e SSB, AGC, S-meter, audio adeguato e alimentazione sicura. MASTER MAIN V2.6 7 fogli/138 refs invariato; tutti i pilot V2.7 separati, nessuna PCB né DRC fisico; layout/routing **0%**, avanzamento progetto **~20% stima**. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #83 MERGED; IF455 regolabile C1602+C1603 trimmer, nuova revisione in review

**PR [#83](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/83) MERGED** sul main `c9f1a473bf00080bf961693bd397eb9982df4667`; Actions [#43413234046](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43413234046) **3/3 SUCCESS** sul final HEAD `d99880b7c13a02005f3c7308c72f6cac89752bf9`: FAST, FULL native KiCad9/ngspice, required gate PASS, 111 comandi legacy. Nuovo ngspice AC 2001 punti ha misurato, nel SOLO modello RLC semplificato con Delevan 1mH ±5% e 16,5Ω di perdita assunta: picco `466220Hz` con L−5%, `454395Hz` nominale, `443395Hz` con L+5%, `448510Hz` con Cpar 3,23pF equivalente SRF. Rilevato esplicitamente `REJECT_FIXED_110PF_IF455_TANK_WITH_5PCT_COIL_UNTIL_TRIM_AND_RF_MEASUREMENTS`. **Test PASS significa che il rischio è stato individuato**, non che la bobina è qualificata. L1601 sullo schema è ora `1mH_DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED`, footprint locale ANCORA PROVISIONAL. Candidato Delevan 2500-28J active 1mH±5%, Q@790k e SRF2,8MHz catalogo; Xicon IF storico obsoleto, escluso.

**Nuovo ramo `cad/if455-variable-trimmer-gkg50015-v27-20261113` (NON ancora merged):** modifica nativa KiCad9 sul tank IF455, sempre 9 refs THT/4 nets, **C1602 110pF→82pF C0G** e **C1603 2,2pF fisso→EW Electronics GKG50015 trimmer 10–50pF THT** (DigiKey ACTIVE, Q200 @1MHz non @455kHz) con simbolo separato `TH_TANK:CT` e footprint THT locale **PROVISIONAL** 2 pad (geometria OEM ancora da confermare, NO FAB). Capacità di shunt nel banco 92–132pF per coprire in teoria i corner ±5% e capacità parassita del modello, rispetto a 110pF non regolabile. Nuova simulazione ngspice 8 reti/1201 punti `verify_if455_trimmer_range_ngspice.py` impone peak min-cap>458k e peak max-cap<452k per ogni corner; test aggiunto al runner FULL esistente senza Actions aggiuntive. Rapporti in `03_Verifiche/V2.7/RAPPORTO_IF455_GKG50015_TRIM_REGOLABILE_DRAFT.md` e `RAPPORTO_L1601_DELEVAN_2500_28J_TOLLERANZE_IF455.md`.

**Non dichiarare validata la seconda revisione prima del gate 3/3 CI sul final HEAD.** V2.6 MAIN 7 fogli/138 componenti invariata, quattro draft audio/AM455, tank IF455 ancora separati, nessun layout fisico/DRC, progetto circa 20% stima e routing0%. Apertura RF/IF + AGC/S-meter/SSB/FM, sicurezza e MPN restano. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — L1601 candidato OEM attivo + sweep IF455 tolleranze, lavoro in revisione

**Bootstrap live:** MAIN HEAD `909396c0e8530fe296f8345c46c8b6af882eeef5`, nessuna PR aperta; AGENTS e checkpoint riletti da main. L1601 sul pilot IF455 rimane **1mH THT con footprint provvisorio**, non ancora fabbricabile. La ricerca corrente ha individuato un MPN industriale concreto: **Delevan `2500-28J`** (distributore DigiKey indica `Active`), induttore assiale 1mH ±5%, DCR max16,5Ω, Q60 @790kHz, SRF2,8MHz, Ø4,83×11,18mm, −55…105°C. `Q@790kHz` **NON** è Q@455kHz, DCR **NON** è perdita RF AC e SRF non fissa il comportamento del filtro. Alcuni Xicon `42IF102-RC` oggi sono dichiarati **Obsolete** e NON candidati per la distinta finale.

**Nuovo branch `engineering/if455-delevan-tolerance-review-20261113` NON ancora integrato:** nello schematico KiCad9 il valore di L1601 è identificato `1mH_DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED` ma **non cambia** pin↔net, valore nominale, né footprint THT **PROVISIONAL**. Nuovo deck ngspice `spice/if455_delevan_2500_28j_tolerance_ac.cir` con quattro casi: L=0,95/1,00/1,05mH e nominale con Cpar3,23pF derivata da SRF 2,8MHz **come ipotesi**, Rserie16,5Ω scenariale e sorgente/carichi precedenti. Nuovo test nativo `verify_if455_delevan_tolerance_ngspice.py` fa scansione AC 2001 punti e impone di rilevare spostamento di frequenza che **blocca la release del filtro a capacità fissa 110pF senza taratura**. Nuovo controllo nel runner FULL esistente, nessun nuovo workflow GitHub Actions e nessuna modifica alla policy economica. Rapporto `03_Verifiche/V2.7/RAPPORTO_L1601_DELEVAN_2500_28J_TOLLERANZE_IF455.md`. **Non dichiarare PASS prima della CI finale della PR.**

**Continuano i blocchi:** serve sorgente a impedenza reale, filtro IF adatto AM/FM, mixer, AGC, S-meter, selezione bobina/tuning, modello OEM e layout fisico; Xicon obsoleti esclusi; nessun DRC PCB o fabbricazione, master MAIN V2.6 7 fogli/138 refs intatto, pilot standalone, layout/routing 0%, complessivo ~20% stima. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #81 MERGED: tank IF455 THT ricalibrato sotto carico e verificato ngspice

**PR [#81](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/81) MERGED**, SHA `3a217a5135696355309fd89e482c84e3aa02c54e`. GitHub Actions [#43411046493](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43411046493) **3/3 PASS** sul commit HEAD `d8a7929c50fa32f263233163829e36a826f09f4c`: FAST, FULL nativo KiCad9+ngspice, required gate tutti SUCCESS. Log tecnici: `PASS_KICAD9_IF455_THT9_ERC0_1MH_112P2_UNLOADED_PROVISIONAL_NO_FAB` con ERC **0 errori/0 avvisi**, 9 refs/4 reti pin↔net verificati; `PASS_NGSPICE_IF455_LOADED_RESONANCE_RETUNE_GENERIC_RLC_NOT_OEM_NO_FAB`, scansione AC nativa **1001 punti** con `old=437000.0Hz`, `updated=454500.0Hz`, LC ideale scarico `475142.31Hz`, modulo gain picco nuovo `0.79366` **soltanto nel modello**; legacy `executed_commands=111` PASS.

**Modifica CAD reale:** il risonatore IF455 standalone di PR #80 conserva J1601/J1602, C1601/C1604 10pF, L1601 1mH footprint THT **provisorio e vietato alla fabbricazione**, R1601=47kΩ, R1602=100kΩ, C1603=2,2pF; C1602 è stato corretto **da 120pF a 110pF**. Motivo: la rete accoppiata, con generatore 50Ω, capacità di ingresso/uscita 10pF e resistenza della bobina **30Ω ipotetica**, ha picco simulato 437kHz nel precedente schema, non 455kHz; nuovo valore sposta il picco simulato a **454,5kHz**. Il valore LC scarico nuovo è 475,14kHz e non deve essere confuso con la risposta della rete completa.

**Limitazioni inderogabili:** Q, SRF, perdita, variazioni con temperatura e capacità parassita della bobina OEM **ignota**, C0G e geometria di PCB da verificare; la simulazione si basa su perdite di bobina assunte e sorgente/carico di prova, non rappresenta il vero IF e non determina selettività di canale, SINAD, sensibilità o BER. Occorrono filtro e trasformatore IF regolabili/qualificati, mixer 10,695→455, guadagno AGC e percorso FM/SSB separato, collegamento elettrico fra moduli, prove di banco. Master MAIN V2.6 7 fogli/138 refs invariato, pilot AM455 7 refs e draft audio separati, layout fisico delle PCB 0% e avanzamento complessivo ~20% **stima**, non aumentare sulla base di questa verifica. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #80 MERGED, correzione accordo IF455 sotto carico in revisione

**PR [#80](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/80) MERGED**, commit main `63343cc924ae86e50ae682ca17ad3176839f802f`; Actions [#43410035549](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43410035549) 3/3 PASS sul final head `029667747cf2f1e43eec362b17f93f17dbf43d19`, `PASS_KICAD9_IF455_THT9_ERC0_1MH_122P2_NOMINAL_PROVISIONAL_NO_FAB`, ERC0/0 warning, 9 refs THT/4 reti, 111 comandi legacy PASS. Scheda IF455 risonante DRAFT autonoma; footprint L1601 15,24mm **provvisorio non produttivo**.

**Correzione tecnica successiva in branch `cad/if455-loaded-resonance-ngspice-v27-20261113` NON ancora merged:** il picco della rete **caricata** da C coupling 10pF input/output, sorgente50Ω e coil loss assunta30Ω non coincide con 455,29kHz della LC isolata 1mH+122,2pF; nel modello semplice il picco era circa 437kHz. Modificato lo schema nativo per C1602 **110pF** (in precedenza 120pF), C1603 2,2pF; `f_LC_scarica≈475,14kHz` ora volutamente diverso dal picco di rete accoppiata atteso ~454,5kHz. Aggiunto vero AC sweep ngspice 350–600kHz vecchio/nuovo con analisi di 1001 punti, script `verify_if455_loaded_ac_ngspice.py` che estrae `wrdata` e impone miglioramento frequenza; test inserito in FULL già esistente. ERC/netlist aggiornati sulla nuova capacità, rapporto `RAPPORTO_IF455_TANK_THT_BENCH_DRAFT.md`. **CI finale ancora da verificare**; nessuna dichiarazione di selettività garantita. Perdita coil30Ω non OEM, carico del diodo non qualificato, bobina attualmente prodotta da selezionare; NO FAB.

**Stato globale:** MAIN V2.6 7 fogli/138 refs immutata, quattro draft audio+AM455 e nuovo tank IF455 standalone, non una PCB completa; layout 0%, percentuale di progetto circa 20% stima. Non alimentare radio da veicolo/batteria, NO TX.

---

## 13 novembre 2026 — IF455 tank passivo THT KiCad9, PR tecnica in revisione

**Bootstrap live main:** SHA `11f055fd2a2ff9380696178c0e09bd0811bc7c1d`, PR #77/#78/#79 integrate e nessuna PR aperta. Nuova branch `cad/if455-passive-tank-bench-v27-20261113` **non ancora integrata**: creato il vero schema KiCad9 `04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch`, 9 refs THT, 4 reti, con C1601=10pF, L1601=1mH THT **induttore RF OEM non identificato, footprint 2 pad THT PROVVISORIO e NO FAB**, C1602=120pF + C1603=2,2pF C0G, R1601=47kΩ carico Q, C1604=10pF e R1602=100kΩ, ingressi J1601 e uscita J1602. `f≈455,29kHz` **solo formula LC ideale**, senza dati SRF/Q/ESR, accoppiamento, filtri o carico reale del diodo AM. Nessuna selettività garantita e nessun collegamento alla MAIN.

**Gate nativo proposto** `03_Verifiche/V2.7/verify_if455_tank_native.py` esegue KiCad9 ERC --exit-code-violations, netlist e controllo pin↔net 9 refs/4 reti e footprint induttore THT 15,24mm nominalmente provvisorio; chiamato da `ci/full_regressions.py` senza nuovo job. Rapporto `03_Verifiche/V2.7/RAPPORTO_IF455_TANK_THT_BENCH_DRAFT.md`. **Nessun PASS dichiarato finché la CI finale non conclude su SHA HEAD.** AM/FM IF455 non include SSB IF10,695. Bloccano il circuito finito: MPN e Q/SRF bobina attiva OEM, carico/filtri RF, simulazione selettività/tolleranze, stadi attivi IF e mixer, AGC, S-meter, input safety.

**Stato generale:** master MAIN V2.6 7 fogli/138 refs invariato, pilot AM455 7 refs e tre pilot audio separati, PCB-MAIN/FRONT non sbrogliate, DRC fisico assente, percentuale complessiva ~20% stima e layout 0%. **NO FAB/NO TX/NO BATTERIA/VEICOLO**.

---

## 13 novembre 2026 — PR #78 MERGED: simulazione 455kHz AM con ngspice reale, diodo generico

**PR [#78](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/78) MERGED** su main, SHA `caa5288fbb5ea6d6c26c8099ef62fb2f51b800fd`. Workflow [#43407974037](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43407974037) **3/3 PASS** sul final HEAD `5968ee408df3904c243c11faa3ccbeec2a1f6157`: FAST, FULL KiCad9 + ngspice e GATE obbligatorio tutti success. Log veri: AM455 KiCad9 ERC `0 Errors 0 Warnings`, `PASS_KICAD9_AM455_THT7_ERC0_DIODE_CATHODE_NETS_BENCH_ONLY_NO_FAB`, ngspice `PASS_NGSPICE_AM455_GENERIC_DIODE_AM_VS_UNMOD_BENCH_NO_FAB_NO_SSB_FM`, tutte le 111 regressioni storiche eseguite.

**Risultato simulato:** portante bench 455kHz, ampiezza 2,0Vpk, modulazione AM 1kHz indice 0,5, diodo **generic model non OEM**; test in finestra 30–40ms ha misurato AF picco-picco circa **1,9125V** (portante modulata) contro **0,1255V** (portante non modulata). Il residuo secondo caso contiene transitorio del condensatore di accoppiamento AC e ripple del modello; non interpretarlo come dato di reiezione RF o prestazione audio dell'hardware. Il test certifica soltanto differenza funzionale dentro la simulazione ed è integrato nel runner FULL esistente **senza job Actions aggiuntivo**. Rapporto `03_Verifiche/V2.7/RAPPORTO_AM455_NGSPICE_GENERIC_DIODE_BENCH.md`, deck ngspice e validatore in V2.7.

**Confini non modificati:** PR #77 ha integrato solo un DRAFT AM455 con 7 refs THT/4 reti KiCad9; il master MAIN V2.6 7 fogli/138 riferimenti, i 3 pilot audio e la PCB-FRONT restano **non integrati**. Il 3900 storico usa IF 10,695MHz + 455kHz per AM/FM e IF 10,695MHz per SSB; il rivelatore AM non è FM o SSB, non ha amplificazione/AGC, né funziona direttamente con segnali d'antenna microvolt. Manca PCB layout/routing (0%), DRC PCB e approvvigionamento OEM finale; avanzamento complessivo circa **20% solo stima**. Prossima priorità: catena IF/mixer e stadi di selezione/AGC, distinguendo rivelatori AM, FM e SSB, oltre a specifica potenza audio. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #77 MERGED; simulazione AM455 ngspice generica in revisione

**PR [#77](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/77) MERGED** su `main`, commit `0a56a9bf2e1b99506e706fdc1ad708062ae1b35c`, Actions [#43407170875](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43407170875) **3/3 SUCCESS** sul final HEAD `9ddefff104aa5f94e830d461fcbfeef928d46701`. Esempio nativo nuovo `PASS_KICAD9_AM455_THT7_ERC0_DIODE_CATHODE_NETS_BENCH_ONLY_NO_FAB`: KiCad9 ERC **0 errori, 0 warning**, 7 refs/4 reti/pin direzione D1501 verificati con export netlist, e 111 comandi storici FULL superati. **È il primo pilot di demodulazione AM IF455 THT reale in KiCad9**, standalone **solo laboratorio**, non circuito finale della radio.

**Nuovo lavoro sulla branch `simulation/am455-am-demod-ngspice-bench-20261113` (non ancora integrato):** `03_Verifiche/V2.7/spice/am455_envelope_1khz_generic_diode_bench.cir` implementa una vera simulazione transitoria ngspice per AM 455kHz/tono 1kHz/indice0,5 su generatore 2Vpk, confrontata con portante NON modulata, due rivelatori D `DGENERIC`+47kΩ/1nF+100nF/100kΩ come nel CAD; `verify_am455_generic_diode_spice.py` legge max/min in banda audio dal simulatore e verifica una differenza misurabile. Inserito nella FULL `ci/full_regressions.py`; **modello diodo genericamente stimato, NON datasheet Vishay né simulazione vendor**. Rapporto `03_Verifiche/V2.7/RAPPORTO_AM455_NGSPICE_GENERIC_DIODE_BENCH.md`; CI ngspice finale non ancora verificata.

**Nessun master integrato:** V2.6 MAIN 7 fogli/138 refs invariato, tre pilot audio e ora quarto pilot AM455 7 refs separati. IF AM/FM 10.695→455 e IF SSB 10.695, mixer/filtri/AGC/S-meter e alimentazione veicolare ancora incompleti; layout e routing PCB-MAIN/FRONT 0%, avanzamento complessivo circa 20% stima. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — nuovo CAD AM IF 455kHz rivelatore d'inviluppo THT, in revisione

**main verificato a inizio lavoro:** SHA `8c9ffefc334d56521aac5928a977b3ffe5ea57a2` (PR #75 e #76 MERGED; zero PR aperte); `AGENTS.md`, checkpoint, stato progetto e handoff letti live. Ripresa priorità radio dopo ottimizzazione GitHub Actions.

**Nuovo ramo `cad/am455-envelope-detector-bench-v27-20261113` (NON ancora merged):** realizzato `04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch` con **7 riferimenti fisici tutti THT**, libreria locale `TH_DEMOD.kicad_sym`, progetto e tabella. Ingresso AM 455kHz **da banco** J1501, D1501 Vishay **1N4148-TAP candidato DO-35** (anodo pin2 IF, catodo pin1 envelope), RC R1501 47kΩ/C1501 1nF (tau ~47µs, fc equivalente ~3,39kHz), C1502 100nF AC coupling, R1502 100kΩ riferimento AF e J1502 uscita AM audio bench. **Nessun collegamento** al master MAIN V2.6, all'amplificatore LM386 o alla FRONT, nessuna alimentazione, nessuna RF da antenna.

**Vincolo architettura:** documenti storici Superstar 3900 riportano AM/FM prima IF 10,695MHz/seconda IF 455kHz, SSB su 10,695MHz; un semplice rivelatore d'inviluppo **non è FM/SSB**, e senza IF amplificata non soddisfa la sensibilità RX. Il pilot serve soltanto a provare il principio a livello segnale IF grande. Diodo MPN OEM e carico RC da qualificare; uscita caricata dal volume FRONT 10k potrebbe alterare drasticamente la risposta. Inoltre pilot LM386 6V/8ohm non fornisce i watt dell'audio radio di alcune versioni originali: specifica audio ancora da decidere. Fonti e blocchi dettagliati `03_Verifiche/V2.7/RAPPORTO_AM455_ENVELOPE_THT_BENCH_DRAFT.md`.

**Nuovo controllo nativo** `03_Verifiche/V2.7/verify_am455_bench_native.py` nella FULL verifica ERC KiCad9, netlist e 7 refs/pin del diodo e quattro reti; **CI finale ancora da verificare e merge NON autorizzato prima del PASS**. Master MAIN V2.6 7 fogli/138 posizioni invariato, due PCB reali/routing ancora assenti, complessivo circa 20% stima e layout 0%. Gate #27/#42/IF critica intatti, **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #75 MERGED: Actions FAST-only selettivo per 4 file analitici

**Main verificato:** commit merge `eb9518662caa6c4d55d5ff55f85552a02579eaf1`, PR [#75](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/75) **MERGED**. GitHub Actions [run #43404924743](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43404924743) **3/3 SUCCESS** sul final HEAD `d14c4470b2cdfb8e02cf5840b5ab52b19e6067b4`: FAST, KiCad9/ngspice FULL e required gate PASS. **La PR di modifica della policy ha superato la FULL**; nessun ERC/netlist, SPICE o controllo storico eliminato.

**Ottimizzazione reale:** `ci/ci_scope.py` ha una allowlist esatta `FAST_ONLY_ANALYTICAL` con **due script Python di sola aritmetica** `verify_audio_load_envelope.py` e `verify_audio_rail_current_graph_v27.py`, più i due CSV associati. Gli script sono eseguiti in `ci/fast_regressions.py` **ad ogni PR**. Se il diff contiene soltanto documentazione o i quattro file ammessi, la FULL viene SKIPPED dopo successo FAST; se contiene anche un solo file KiCad, SPICE, test nativo, workflow, policy, BOM o file ignoto, è obbligatorio il FULL KiCad9/ngspice e il required gate impone PASS. `ci/ci_scope.py --selftest` include casi di file nuovi e diff misti che non possono saltare FULL. Manual `workflow_dispatch` rimane FULL. AGENTS e `ci/CI_COST_OPTIMIZATION.md` allineati.

**Nessun risparmio in euro quantificato:** la regola riduce i job KiCad9 solo in futuri casi circoscritti di cambi puramente numerici, che in precedenza triggeravano FULL. Nessuna modifica al progetto elettrico o ai tre draft; il master radio MAIN V2.6 rimane 7 fogli/138 refs; PCB-MAIN/PCB-FRONT fisiche e piste ancora assenti; complessivo ~20% stimato, routing 0%. Priority next: sviluppare RF/IF e demod RX in KiCad nativo, non moltiplicare report. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #73 MERGED: connettori THT JST XH 2,50mm audio LAB

**PR [#73](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/73) integrata** su `main`, merge SHA `c17f5843c8cb694e3fb225198dbc1569f495aa72`. GitHub Actions [#43403815473](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43403815473) **3/3 PASS** sul final HEAD `534867ed039ffa532fa975e97be07df6efc57b9f`: FAST success, FULL native KiCad9/ngspice/111 regressioni storiche success, required gate success. Log: `PASS_KICAD9_JST_XH_2P50_TH_HEADER_PAD1_PAD2_PITCH_BOTH_MODULES` e `PASS_NATIVE_6V_PSU_LM386_PIN_CONTRACT_NO_FAB_NO_BATTERY`.

**CAD realmente modificato:** nei due schematici standalone V2.7, con librerie embedded/locali concordanti, i connettori **J1402 PSU 6V** e **J1201 LM386** hanno l'impronta THT `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` anziché header generico 2,54mm. Pad1 +6V lab e pad2 ritorno audio verificati via export netlist native; il test ora legge l'effettivo footprint installato in KiCad9 con 2 pad THT a pitch 2,50mm. **Solo test CAD, non un DRC su PCB.** Primo run CI [#43403435479](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43403435479) era fallito per regex errata nel nuovo test: parser corretto senza diminuire i gate, run finale sopra SUCCESS.

**Candidati cablaggio OEM JST presenti nel catalogo corrente:** B2B-XH-A (2 header PCB), XHP-2 (2 housing femmina), SXH-001T-P0.6 (4 crimp), cavo AWG26 candidato entro range di contatto; non sono ancora una BOM/fornitura qualificata né un cavetto montato. Da qualificare *lifecycle OEM esatto*, crimpatura, pin1 orientamento, anti-inversione anche dei fili crimpati, ritenzione, vibrazione, schermatura/routing RF, lunghezza, caduta su entrambi i conduttori, strain relief, isolamento da tab +6V LM317 e sicurezza. Dati e fonte nel `03_Verifiche/V2.7/RAPPORTO_HARNESS_JST_XH_AUDIO_6V_LAB_DRAFT.md`.

**Stato generale:** master MAIN V2.6 7 fogli/138 componenti invariato; LM386 MAIN, LM317 LAB, controllo volume FRONT sono tre schemi DRAFT autonomi, nessuna PCB fisica, nessuna fabbricazione o DRC, layout 0%; progressione complessiva circa 20% **stima senza incremento artificiale**. Alimentatore LM317 bench richiede 10–10,5V al pin IN, NON ingresso veicolo 13,8V; simulazioni ngspice sono comportamentali, non modello OEM. Prossima priorità sostanziale: chiudere architettura ricevitore RF/IF e valutare schematici MAIN mancanti, non restare indefinitamente su verifiche software del pilot audio. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — connettori di alimentazione LAB PSU↔LM386 JST XH 2,50mm, in revisione

**Bootstrap:** HEAD `ab2e9ad89b200375fd0929158fd8e6a34ed130f4`, PR #70/#71/#72 MERGED e nessuna PR aperta. Branch tecnica `cad/audio-jst-xh-two-pin-lab-harness-20261113`, **non ancora integrata**. Per collegamento lab 6V PSU→LM386, modifica KiCad **reale**: i footprint a due pad di **J1402 PSU** e **J1201 LM386**, embedded e librerie locali, sono ora `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` (sostituisce header generico 2,54mm). Pad 1 alimentazione `AUDIO_6V_LAB`, pad 2 massa locale/ritorno. Per un cavo fisico con due header da PCB sono previste **due housing femmina JST XHP-2** e quattro terminali a crimpare **SXH-001T-P0.6**, AWG 22–28 come documentato dal catalogo ufficiale JST. Codici *candidati OEM documentati*, stato manufacturing dei singoli MPN, crimpatura, sicurezza/anti-inversione e resistenza alle vibrazioni **non ancora qualificati**.

**Gate tecnico esteso:** `03_Verifiche/V2.7/verify_audio_6v_supply_contract_native.py` richiede due istanze CAD, due simboli embedded e due librerie con footprint esatto; confronta il **file footprint originale installato in KiCad9** e impone 2 pad through-hole, passo 2,50mm, pin1/pin2; continua export netlist nativa e prova separazione RF/PLL. Report `03_Verifiche/V2.7/RAPPORTO_HARNESS_JST_XH_AUDIO_6V_LAB_DRAFT.md`. **CI FINAL HEAD da verificare prima di merge**, non dichiarare preventivamente ERC o footprint validati.

**Perimetro:** il resto dei connettori e PCB-MAIN V2.6 138 posizioni non cambia; PSU LM317 e audio LM386 restano schemi standalone non cablati. Un housing polarizzato NON protegge da crimp invertiti, +6V vs massa, corti o vibrazioni; no fabbricazione. Alimentatore 10–10,5V solo LAB, nessuna idoneità 13,8V, NO FAB / NO TX / NO BATTERIA / NO VEICOLO. Layout fisico due PCB ~0%, complessivo ~20% stima.

---

## 13 novembre 2026 — PR #71 MERGED: transitorio ngspice differenziale 2 fili e ground bounce

**PR [#71](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/71) MERGED** su `main`, SHA `48bbe6d02c8dcfcf17a5ea62fe9e456c54e14434`. Workflow [#43400933150](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43400933150) **3/3 PASS** su final HEAD `28d4701f200a5a115193c2fcc4cf8d37cccb8e2d`: FAST PASS, FULL native KiCad9/ngspice e 111 regressioni legacy PASS, required gate PASS. Evidenza log `PASS_NGSPICE_BEHAVIORAL_AUDIO_6V_RAIL_STEP_NO_VENDOR_OR_FAB` con **droop_good=0,078 V**, **droop_bad=0,390 V**, ground bounce **0,028 V** e **0,210 V**. Nessun waiver.

**Correzione tecnica essenziale:** i risultati 54/210mV della prima PR #70 valevano soltanto per il **ritorno di massa idealmente perfetto**. La nuova versione della stessa netlist comportamentale modella anche il **filo di ritorno**, usa un voltmetro ideale non caricante `EAMPDIFF` per acquisire `V(amp+,amp_gnd)` (la sintassi diretta `.meas FIND v(a,b)` aveva fallito un primo tentativo CI), e verifica anche `vgndload`. Resistenze scenario andata e ritorno rispettivamente 0,20Ω/0,20Ω o 1,50Ω/1,50Ω, più R PSU **assunta** 0,25Ω; gradino 20→140mA, C1402 10µF e C1206 100µF ideali. Prima CI del branch annullata da commit successivo, seconda con measure differenziale non supportata, **solo l'ultima è valida**.

**Maturità NON acquisita:** questo è ngspice realmente eseguito su una rete passiva **senza macromodelli OEM LM317/LM386**, ESL/ESR, risposta del chip al clipping, cavo o hardware fisici. Non prova prestazioni, EMC, THD, dissipazione, SOA o sicurezza automotive. LM317 PSU richiede 10–10,5V **solo laboratorio**; NON collegare a 13,8V batteria/veicolo. Schemi KiCad MAIN V2.6 (7 fogli/138 refs) e DRAFT LM386, LM317, FRONT non modificati; PCB-MAIN/FRONT layout ancora 0%, complessivo ~20% **stima**. #27 sicurezza, #42 BOM fabbricazione e RF U401/L501 ancora aperti. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #70 MERGED, correzione ritorno massa nella simulazione in review

**PR [#70](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/70) MERGED** su `main` SHA `da9dec49ffbe4bb337cd57d7f33f45a1d7f3d723`; Actions [#43399709031](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43399709031) **3/3 PASS** sul final HEAD `e34955a487400cd0e6198ad092c8bac00f381fc2`. Questo integra **ngspice realmente eseguito** per il modello comportamentale passivo rail 6V: `PASS_NGSPICE_BEHAVIORAL_AUDIO_6V_RAIL_STEP_NO_VENDOR_OR_FAB` con droop 54mV e 210mV **solo sotto l'ipotesi precedente di massa/ritorno ideale**. Full KiCad9/ngspice legacy PASS con 111 comandi storici; niente waiver.

**Difetto di approssimazione individuato dopo merge:** il primo circuito modellava solo la resistenza di andata. La nuova branch `simulation/audio-6v-rail-return-path-20261113` (NON ancora merged) aggiunge **il conduttore di ritorno** da LM386 a PSU, misura il rail differenziale `V(AMP+, AMP_GND_LOCALE)` e il ground bounce, con test ngspice che impone misure reali di entrambi. Le resistenze **ipotetiche** sono ora 0,20Ω andata + 0,20Ω ritorno, oppure 1,50Ω + 1,50Ω. Caduta attesa col gradino 20→140mA: **78mV e 390mV**; ground bounce di 28mV/210mV al carico. Non sono misure fino alla CI final HEAD. Aggiornato `RAPPORTO_TRANSITORIO_RAIL_AUDIO_6V_NGSPICE.md` e test `verify_audio_rail_step_ngspice.py`; la fonte 5,952V e R interna 0,25Ω sono sempre **comportamentali e NON vendor**.

**Stato fisico invariato:** LM317 bench 10–10,5V ingresso, LM386 PSU→AMP è solo un contratto fra due draft THT, non esiste cablaggio, DRC PCB o Gerber. MAIN V2.6 7 fogli/138 refs, FRONT draft, layout 0%, stima complessiva ~20%. Alimentazione veicolare, termica, rumore e sicurezza #27/MPN #42 sono aperti. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** Integrazione della seconda PR solo dopo gate nativi HEAD verde.

---

## 13 novembre 2026 — circuito ngspice reale per transitorio del rail 6V audio, in review

**Baseline main letta all'avvio:** SHA `b9f96bdec552620e8230d83861dbb045a69710fb` (PR #68/#69 MERGED, nessuna PR aperta); `AGENTS.md` e questo checkpoint letti da main. Branch `simulation/audio-6v-rail-step-spice-20261113`, **NON ancora integrato**. Nuova simulazione ngspice **reale** `03_Verifiche/V2.7/spice/audio_6v_lab_rail_step_behavioral.cir` e validatore `03_Verifiche/V2.7/verify_audio_rail_step_ngspice.py` agganciato a `ci/full_regressions.py` (riutilizza ngspice già installato e runner FULL, senza ulteriore job). La rete passiva corrisponde ai condensatori di PSU C1402=10µF e LM386 C1206=100µF, con **sorgente IDEALE** 5,952V, resistenza interna ipotetica 0,25Ω e resistenze cavo ipotetiche 0,20/1,50Ω; gradino carico forzato 20→140mA di 5ms, misure native `.meas` di droop/ripristino a 4/8/15ms. Attese analitiche: **54mV** con R totale 0,45Ω e **210mV** con R totale 1,75Ω; questi non sono risultati misurati prima dell'esito CI. Rapporto `03_Verifiche/V2.7/RAPPORTO_TRANSITORIO_RAIL_AUDIO_6V_NGSPICE.md`.

**Limitazioni obbligatorie:** modello comportamentale idealizzato, **NON macromodello TI LM317/LM386**, niente impedenze reali di cavi, condensatori con ESR/ESL, USB/veicolo, né simulazione THD, startup o transitori di batteria. Il test PASS indica coerenza della simulazione ngspice con un modello passivo, non idoneità alla fabbricazione o alla trasmissione. L'LM317 rimane solo LAB 10–10,5V e l'LM386 solo DRAFT. **CI e merge sul final SHA ancora da verificare**. Master V2.6 7 fogli/138 refs invariato, PCB-MAIN/FRONT non sbrogliate, layout/routing 0%, percentuale complessiva ~20% stima. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — PR #68 MERGED: corrente media tipica LM386 stimata da Fig. 6-7 TI

**PR [#68](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/68) MERGED** sul ramo `main`, SHA `83b9c820a5d4c96b37c931e5aa87f52e87ca3b92`; Actions [#43397404736](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43397404736) **3/3 PASS** sul final HEAD `f1a39edbe004f4e49040d6512937c2873b723384`: FAST, FULL KiCad9/ngspice/legacy e required gate SUCCESS. Log FAST `PASS_LM386_TYPICAL_CURRENT_GRAPH_ENVELOPE_NOT_VENDOR_SPICE_OR_FAB` con scenari `(0.125, 0.071, 0.091, 0.082, 0.103, 85.2)` e `(0.25, 0.105, 0.133, 0.116, 0.145, 95.6)`; le ultime temperature sono **solo** per θJA=50°C/W assunto e Tamb=60°C.

**Nuova evidenza e regola:** dalla curva **tipica, non garantita** del grafico OEM TI LM386 SNAS545D Fig.6-7, con ampi intervalli visivi, sono state stimate correnti medie 6V/8Ω LM386 ~71–91mA a 125mW, ~105–133mA a 250mW; aggiungendo il feedback R1401 LM317 ~10,8–11,94mA -> ~82–103mA e ~116–145mA illustrative sul regolatore. Registrati file `03_Verifiche/V2.7/verify_audio_rail_current_graph_v27.py`, `LM386_GRAPH_6V_RAIL_CURRENT_BRACKETS.csv`, `RAPPORTO_CORRENTE_REALE_STIMATA_LM386_FIG6_7.md`, e test FAST in `ci/fast_regressions.py`; nessun runner EDA aggiuntivo per sola aritmetica. **Non** è misura, worst-case TI, qualifica PVT, SPICE vendor o certezza della corrente reale.

**Decisione ancora aperta:** analizzare riserva PSU startup/clip/temperatura e rumore, LM386 THD e temperature reali, dissipation package e dissipatore, protezioni, speaker 8Ω fisico/cavo meccanico. L'LM317 bench rimane con VIN **10–10,5V da LAB**, non 13,8V veicolare, senza protezione automotive. Nessun cambiamento alle net KiCad, master MAIN V2.6 7 fogli/138 refs e 3 moduli standalone invariati, nessuna PCB o DRC, progettazione complessiva ~20% stima e layout/routing 0%. **NO FAB / NO TX / NO BATTERIA/VEICOLO.**

---

## 13 novembre 2026 — stima corrente di rail LM386 da figura OEM, revisione in PR

**Stato main verificato all'apertura:** SHA `e502141b49bc7fb01ceb42e24ede539bb05dbb28`, PR #66/#67 MERGED, nessuna PR aperta. Branch nuova `engineering/audio-6v-supply-current-typical-20261113` non ancora fusa. Dai grafici **tipici** TI LM386 SNAS545D §6.6 Figura 6-7 (dissipazione chip vs potenza di uscita a 6V/8Ω), calcolati intervalli **approssimativi, NON min/max garantiti** di corrente media di rail: 125mW speaker → ~71–91mA LM386, 250mW → ~105–133mA LM386; aggiungere ~10,8–11,94mA di feedback R1401 LM317 → intervalli di corrente **illustrativi** ~82–103mA e ~116–145mA al pin OUT LM317. I 125mA speaker RMS non sono 125mA supply DC. La dissipazione LM317 per un carico tipico non equivale alla capacità continua garantita; 0,35A teorici continuano a violare il caso termico ipotetico.

**Nuova verifica economica:** `03_Verifiche/V2.7/verify_audio_rail_current_graph_v27.py` + CSV di intervalli di lettura grafico + `RAPPORTO_CORRENTE_REALE_STIMATA_LM386_FIG6_7.md`, invocati da `ci/fast_regressions.py`. Nessun nuovo test nativo KiCad per sola aritmetica e nessun wafer/hardware/SPICE TI testato. **CI della nuova PR da verificare prima di merge**. La baseline MAIN V2.6 7 fogli/138 THT, DRAFT audio MAIN/FRONT/PSU rimangono immutati. Il 6V è **solo laboratorio**, input PSU 10–10,5V da banco; nessuna protezione veicolare. Layout 0%, stima progetto ~20%; NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

---

## 13 novembre 2026 — PR #66 MERGED: gate numerico corrente speaker e termica LM317

**PR [#66](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/66) integrata** su `main`, SHA `f1a6d570a095141b91f06c053310372e168937f6`. CI [#43395884826](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43395884826): **3/3 SUCCESS** sul final HEAD `dea1540a8d7512aaf3374178f6f16b16d054d874` (fast unit PASS, full native KiCad9/ngspice/legacy PASS, gate obbligatorio PASS). Nei log veloci `PASS_LM386_LM317_ANALYTICAL_LOAD_ENVELOPE_NO_POWER_CERTIFICATION`, LM317 termica simulata solo per ipotesi `tj_at_0p2A_C=108.94`, `max_theta_at_0p35A_C_per_W=37.94`. Nessuna nuova suite nativa: riusate le regressioni FULL, calcolo numerico collocato nelle FAST.

**File integrati:** `03_Verifiche/V2.7/verify_audio_load_envelope.py`, `AUDIO_LOAD_ENVELOPE_LM386_6V.csv`, `RAPPORTO_LM386_LM317_ENVELOPE_CARICO_AUDIO.md` e aggiornamento `ci/fast_regressions.py`. Scenari 4/8Ω e 100/125/250mW distinguono V/I RMS/picco nel carico dalla corrente **non nota** del rail. TI LM386: 250mW MIN a 6V/8Ω ma **THD 10%**; 0,2% THD è dato TYP a 125mW/1kHz. Con PSU laboratorio VIN10,5V, VOUT parametrico minimo 5,6055V, Tamb60°C, θJA assunto 50°C/W, **0,35A supply DC ipotetici** darebbero ~145,7°C, sopra il budget prudenziale Tj≤125°C. Queste sono formule illustrative, NON una prova SPICE vendor o verifica hardware. La PSU e la linea RF restano scollegate.

**Prossima attività critica:** scegliere target audio e altoparlante 8Ω, ricavare profilo realistico di corrente e THD a 6V con modello/misure, definire dissipatore/PCB termico e soluzione audio PSU da 13,8V con protezioni prima di freeze dell'alimentazione. Non dedurre che 8Ω 125mW corrisponda a I_regolatore=125mA. Master MAIN V2.6 7 fogli/138 refs invariato, 3 schemi audio standalone, PCB fisiche/layout e DRC assenti, progresso globale circa 20% stimato e layout **0%**. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — gate numerico potenza LM386 / termica LM317 in revisione

**Bootstrap verificato:** SHA main `c9e95217372bb15d013b615e51902f90cfd49944` (PR #65 MERGED, nessuna PR aperta). Nuova branch `engineering/audio-6v-load-envelope-20261113` in review, **nessuna modifica ai simboli/footprint o alle reti KiCad**. Implementato `03_Verifiche/V2.7/verify_audio_load_envelope.py` con tabella `AUDIO_LOAD_ENVELOPE_LM386_6V.csv` e relazione `RAPPORTO_LM386_LM317_ENVELOPE_CARICO_AUDIO.md`; integrato nella **CI FAST** per evitare un nuovo job nativo solo per aritmetica.

**Evidenza OEM:** TI LM386N-1 a 6V/8Ω: potenza 250mW minima / 325mW tipica **a 10% THD**, valore 0,2% THD **tipico a 125mW /1kHz**; non confondere le condizioni, né potenza altoparlante con potenza dal rail. I nuovi calcoli a 8Ω e 4Ω per 100/125/250mW ricavano corrente speaker RMS/picco e taglio RC ideale del C1202 220µF. La PSU LM317 resta **10–10,5V da banco**: modello termico illustrativo con VIN10,5V, VOUT statico min ~5,6055V, Tamb60°C, θJA assunto 50°C/W -> ~109°C a 0,2 A **ipotetici DC supply**, ~146°C a 0,35 A, oltre soglia prudenziale 125°C; non sono misure/limiti garantiti. Definire consumo DC e pulsato reale LM386, carico/speaker, THD/ripple, SOA e dissipatore prima di fissare circuiti.

**Ancora NON convalidato su CI HEAD della branch** al momento della stesura; nessun nuovo prodotto hardware testato, nessun rilascio. Master MAIN V2.6 7 fogli/138 refs e moduli standalone invariati, nessuna PCB fisica o DRC PCB, stima complessiva ~20%, routing 0%. Resta NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

---

## 13 novembre 2026 — PR #64 MERGED: rete 6V LM386 e contratto PSU pin↔net integrati

**PR [#64](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/64) MERGED su `main`** SHA `0098877dc5bd195cc774be7c6b91e183e48a501a`. Actions [#43392859696](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43392859696) **3/3 PASS** su HEAD `a010b707be652431e4c6429e46e9621b254bf0ac`, incluso ERC0 reale KiCad9 su LM386 e PSU, test interfaccia FRONT invariato, test `PASS_NATIVE_6V_PSU_LM386_PIN_CONTRACT_NO_FAB_NO_BATTERY`, 111 comandi nativi storici eseguiti. Il gate obbligatorio ha autorizzato il merge, senza waiver.

**CAD aggiornato realmente:** nel foglio DRAFT audio RX LM386 e libreria `TH_AUDIO.kicad_sym`, la rete di alimentazione da laboratorio **`AUDIO_5V` è diventata `AUDIO_6V_LAB`**; sono invariati gli altri collegamenti fisici, i 12 refs THT e la scheda MAIN V2.6. I due fogli PSU/LM386 continuano standalone ma ora sono verificati tramite 2 netlist KiCad9: J1402 PSU pin1→J1201 LM386 pin1 rail `AUDIO_6V_LAB`, pin2→pin2 ritorno, con `U1401.2` e `U1201.6` entrambi sul corretto rail locale dei rispettivi fogli. Aggiunti `verify_audio_6v_supply_contract_native.py` e test nel gate FULL; aggiornata la specifica LM386 e il contratto FRONT per la rete +6V. Rapporto `03_Verifiche/V2.7/CONTRATTO_6V_PSU_LM386_BENCH_DRAFT.md`.

**Limiti immutati:** la connessione tra schemi è una **mappa logica**, non è ancora un cablaggio fisico né due PCB integrate. J1402/J1201 sono pin-header entrambi maschi; crimp, antinversione, carico potenza e ritorni da qualificare. PSU richiede 10–10,5V al suo ingresso da banco, non compatibile con alimentazione veicolare 13,8V. LM386 audio output, THD/potenza, corrente/surriscaldamento e layout RF non sono qualificati. Il master MAIN V2.6 mantiene 7 fogli/138 refs e nessun PCB layout/routing; tre draft standalone con 12/3/10 refs. Stima complessiva ~20%, routing 0%. Issue #27/#42 e RF U401/L501 bloccanti. **NO FAB/NO TX/NO BATTERIA/VEICOLO**.

---

## 13 novembre 2026 — collegamento logico LAB 6V LM317 → LM386, KiCad9 in review

**Ultimo main verificato:** SHA `c4baf599e6aa956b3893fea12e577ee0710d27d1` (PR #62, #63 MERGED), nessuna PR aperta. **Branch `cad/audio-lm386-6v-lab-interface-20261113` NON ancora integrato:** nel vero schematico DRAFT LM386, rail del connettore bench +5V `AUDIO_5V` rinominato `AUDIO_6V_LAB`, mantenendo identici i pad e i nodi circuitali: U1201.6, C1205.1, C1206.1, J1201.1. Lato PSU già esiste `AUDIO_6V_LAB` da U1401.2 a J1402.1. In libreria `TH_AUDIO.kicad_sym` e simbolo embedded il connettore adesso è `BENCH_6V_CONN` (soltanto dichiarazione di alimentazione laboratorio).

**Test nativo aggiunto in `ci/full_regressions.py`:** `verify_audio_6v_supply_contract_native.py` riesporta netlist PSU e LM386 e controlla mappa **J1402→J1201 pin1 6V/pin2 ritorno**, nessuna commistione di rail PLL RF e intervallo statico di riferimento LM317 compatibile col range LM386N-1. Aggiornati i test ERC/netlist dei due moduli e del contratto audio FRONT. Report `03_Verifiche/V2.7/CONTRATTO_6V_PSU_LM386_BENCH_DRAFT.md`. Tutte le prove native sul nuovo SHA devono terminare **PASS** prima di merge.

**Vincoli fermi:** ancora **nessuna connessione fisica fra due schede, nessun ingresso 13,8V automotive**, connettori maschi richiedono cavo/distanziamento/anti-inversione; test corrente, THD/EMI, termica, protezioni e alimentatore definitivo non completati. MASTER MAIN V2.6 7 fogli/138 refs invariato, FRONT volume draft 3 refs, PSU 10 refs e LM386 12 refs separati, PCB/routing **0%**, stima complessiva **~20%**. NO FAB/NO TX/NO BATTERIA/VEICOLO.

---

## 13 novembre 2026 — PR #62 integrata: headroom LM317 audio corretto e verificato

**PR [#62](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/62) MERGED** su `main`, SHA `ce4ccf33272d2e76ffb2524a4627b47f307baa8a`. GitHub Actions [#43391899904](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43391899904) **3/3 PASS** sul commit finale `0aa80817558863644751443ea8576361d0d050d9`: veloce PASS, FULL nativo KiCad9/legacy PASS, required gate PASS. Il test PSU nativo ha riportato `ERC messages: 0 Errors 0 Warnings`, `PASS_KICAD9_AUDIO_6V_LM317_PSU_ERC0_THT10_PINNET_NO_FAB` e output statico `LM317_REFERENCE_ENDPOINTS_NOT_FULL_PVT 5.6055 6.3091`. Nessun waiver; 111 comandi storici FULL.

**Modifica tecnica CAD reale:** il draft `AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch` e la libreria `TH_PSU.kicad_sym` ora riportano ingresso lab `LAB_VIN_10TO10P5V` e 10–10,5V **al pin IN** del regolatore, correggendo vecchio 9–10V che non soddisfaceva il VIN−VOUT≥3V nelle condizioni parametrizzate alte. Test KiCad9 e PVT di riferimento ±1% ripetibili, rapporto `RAPPORTO_AUDIO_PSU_6V_LM317_BENCH.md` aggiornato. Non altera gli altri draft (LM386/FRONT) né il master V2.6.

**Restano bloccanti:** la connettività PSU→LM386 non è stata realizzata, la sorgente 10–10,5V è esterna da laboratorio e NON è alimentazione della radio 13,8V, nessuna qualifica SOA/dissipazione reale, ripple, load transients, protezione inversione, protezione ingresso o chassis/tab attivo; MPN OEM finali non completi, RF/PLL e Issue #27 aperte. MAIN V2.6 7 fogli/138 refs, PCB-MAIN e PCB-FRONT layout/routing **0%**; percentuale complessiva approssimativa **20%** senza crescita artificiale. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — correzione input headroom LM317 6V LAB, CAD in review

**Baseline verificata su main:** merge PR #61 `e0d1be6230ca04833a872a98d7d5e542d48f6d44`, nessuna PR aperta. I tre draft KiCad9 audio (LM386 MAIN, volume FRONT, PSU LM317) rimangono **standalone**; 7 fogli MAIN V2.6 e 138 refs invariati, layout PCB 0%.

**Lavoro in branch `cad/audio-lm317-input-headroom-pvt-20261113`, NON ancora integrato:** il regolatore audio PSU 6V precedente definiva erroneamente **9–10V ingresso LAB** mentre TI LM317-N garantisce le caratteristiche sul range con **VIN−VOUT≥3V**. All'estremo alto VREF/IADJ e resistenze ±1% si ricava VOUT≈6,31V: a 9V resterebbero solo ≈2,69V. Modificati **file KiCad9 reale e libreria locale**, J1401 e net name in `LAB_VIN_10TO10P5V`, intervallo vincolato **10–10,5V misurati al pin IN del regolatore**, bench a corrente limitata senza batteria/veicolo. Calcolo 6V nominale ~5,952V, estremi statici ~5,61–6,31V non equivalenti a qualifica PVT completa. Aggiornati test di copertura netlist e vincoli di headroom (9V volutamente FAIL come condizione), con nuovi stress termici 10 e 10,5V. Rapporto aggiornato `03_Verifiche/V2.7/RAPPORTO_AUDIO_PSU_6V_LM317_BENCH.md`.

**Manca gate CI completo su HEAD**, nessuna integrazione PSU→LM386 autorizzata. Un alimentatore a 10–10,5V NON è un rail finale radio: terminazione audio, protezioni transitori/inversione, SOA/sink del TO220 tab LIVE e potenza speaker da verificare. Distinta OEM per fabbricazione ancora BLOCCATA e NO FAB / NO TX / NO BATTERIA / NO VEICOLO. Stima gestione circa 20%, routing 0%.

---

## 13 novembre 2026 — PR #60 MERGED: alimentazione THT audio 6V da banco validata con KiCad9

**PR #60 MERGED** su `main`, commit `aa3118a8f89ea37253e3482ef898d3744fcc2c42`. Azioni [#43330851162](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43330851162): **3/3 SUCCESS** sul final head `188065066667d1f8b8383901f0e04071ddce4e9f` — test rapido PASS, suite full KiCad9 native/legacy PASS, required gate PASS. Il nuovo `verify_audio_psu_lm317_native.py` ha esportato la netlist reale, confermato **10 refs THT**, pinout LM317 ADJ/OUT/IN, diodi e polarità C1402/C1403, **ERC nativo 0 errori e 0 warning**. Anche il controllo aritmetico vincola il derivatore R=110Ω/412Ω, Vout nominale 5.952V e l'esclusione del caso termico 13.8V/0.2A. **NON è SPICE vendor, né qualifica termica o prova hardware**.

**Artefatto nuovo `04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V/AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch`**, con libreria `TH_PSU.kicad_sym`, progetto, `sym-lib-table`, e 10 posizioni THT: U1401 TI LM317T/NOPB dichiarato ACTIVE OEM TO220 pin1 ADJ pin2 OUT+TAB pin3 IN, R1401/1402, C1401/1402/1403, D1401/1402 e J1401/1402. Alimentazione isolata **esclusivamente 9–10V da banco limitata in corrente**, uscita 6V verso test. **Non collegata all'LM386** né al master radio. Rischi: protezione inversione e transitori ingresso assente, OEM diodi/passivi da qualificare, SOA, dissipatore con TAB LIVE e 6V+ termica, speaker load e budget corrente. Anche a 10V/0.35A, modello termico illustrativo supera la soglia progettuale.

**Stato radio corretto:** la V2.6 MAIN resta 7 fogli/138 posizioni, non esiste alcun PCB-MAIN/FRONT fisico completo o routing; il pilot MAIN LM386 12 ref, FRONT volume 3 ref e PSU audio 10 ref sono DRAFT separati, senza conteggio BOM integrato. Il criterio passivi standard ADR-002 consente proseguimento degli schemi, ma la fabbricazione è bloccata da BOM #42, protezioni #27 e RF U401/L501. Completamento progetto circa **20% stima**, routing **0%**. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 13 novembre 2026 — nuovo schema nativo 6 V audio indipendente solo laboratorio (PR tecnica in revisione)

**Main iniziale:** SHA `72a0dbd175d1e6033061d4a06fcb82b2441fed12`, PR #58/#59 integrate e nessuna PR aperta. Master MAIN V2.6 invariato, due draft KiCad9 MAIN audio LM386 e FRONT volume già integrati, nessuna PCB/Routing.

**Nuovo lavoro nella branch `cad/audio-dedicated-6v-lm317-bench-20261113` (non ancora MERGED):** standalone `04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V/AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch` con **10 componenti THT**: U1401 TI LM317T/NOPB ACTIVE **TO‑220 3 pin NDE**, R1401 110Ω/1%, R1402 412Ω/1%, C1401 ingresso 100nF, C1402 uscita 10µF polarizzato, C1403 ADJ 10µF polarizzato, D1401 diodo OUT→IN, D1402 diodo ADJ→OUT, J1401 ingresso lab **9–10V soltanto**, J1402 uscita 6V. Regolatore live pin1 ADJ, pin2 OUT + linguetta, pin3 INPUT. Impostato valore nominale circa **5,952 V**, divider worst-case minimo >10mA; **NESSUN collegamento all'LM386** né ai rail radio o veicolo. `03_Verifiche/V2.7/verify_audio_psu_lm317_native.py` aggiunto a CI FULL, deve verificare ERC, netlist 10 THT, protezioni e polarità. Rapporto: `03_Verifiche/V2.7/RAPPORTO_AUDIO_PSU_6V_LM317_BENCH.md`.

**Termica ancora da qualificare**: budget illustrativo a 60°C e θJA=50°C/W, 0.2A: Vin9→90°C stimati, Vin10→100°C, Vin13.8→138°C (NON ammissibile nell'esempio). 13.8V **vietati per questo pilot**; ingresso non reverse-protected, corrente reale LM386 e SOA ignoti. Non proclamare qualifica su semplice calcolo o ERC; test nativo da controllare prima del merge. Master radio V2.6 138 refs intatto; tre draft THT separati non sono la PCB. Stima progetto circa 20% e layout 0%, NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

---

## 13 novembre 2026 — PR #58 integrata, polarità elettrolitici audio verificata

**PR #58 MERGED su main** SHA `9230f55c1b500b736f95c332ffe6f1e7a8b35e8c` e [GitHub Actions #43328377827](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43328377827) **3/3 PASS** su head `d47e793f18d4602c31eb863184e2a5e6218171e3`: native KiCad9 audio ERC **0 errori / 0 warning**, `PASS_POLARITY_C1202_C1204_C1206_3_THT_ELECTROLYTICS`, `PASS_KICAD9_AUDIO_DRAFT_ERC0_NETLIST_12_THT`, FRONT-volume e MAIN/FRONT native pin contract PASS, regressioni storiche complete. Nessun waiver.

**Modifiche integrate:** simbolo `TH_AUDIO:CP` embedded e libreria locale con pin1 `POS_+` e pin2 `NEG_-`; test pin↔net nativi C1202 positivo `AMP_OUT` negativo `SPK_HOT`, C1204 positivo `BYPASS` negativo `GND`, C1206 positivo `AUDIO_5V` negativo `GND`; rapporto `03_Verifiche/V2.7/RAPPORTO_AUDIO_POLARITA_E_POWER_BUDGET.md`. È una modifica reale KiCad9 a **schema DRAFT isolato**, non al master V2.6.

**Blocco aperto:** LM386N-1 produce la potenza 250–325mW (a 8ohm, THD10%) dichiarata OEM **a 6V**, non garantita a 5V; da verificare rail audio dedicato, corrente speaker, termica, controllo volume effettivo e polarità fisica MPN dei capacitori. MASTER V2.6 7 fogli/138 refs invariato; PCB-MAIN/FRONT layout **0%**; avanzamento globale stimato circa **20%** invariato. **NO FAB / NO GERBER DI PRODUZIONE / NO TX / NO BATTERIA-VEICOLO**.

---

## 13 novembre 2026 — revisione CAD polarità elettrolitici audio e gate alimentazione

**Main verificato alla partenza:** `7d0395316729134429172fe5225affdec69a30e4`; PR #56/#57 MERGED, nessuna PR aperta; master MAIN V2.6 e FRONT senza layout, NO FAB. **Branch `cad/audio-lm386-electrolytic-polarity-20261113` (NON ancora fuso):** `TH_AUDIO:CP` nel pilot audio LM386 e nella libreria locale ora esplicita **pin1 POS+**, **pin2 NEG-** per C1202/C1204/C1206, senza alterare reti o numerazione dei pad. Il controllo nativo `verify_audio_draft_native.py` è stato rafforzato per confrontare simbolo embedded/libreria e le membership pin-net dai file **KiCad9 netlist**: C1202 positivo AMP_OUT negativo SPK_HOT, C1204 positivo BYPASS negativo GND, C1206 positivo AUDIO_5V negativo GND. Rapporto OEM e calcoli illustrativi in `03_Verifiche/V2.7/RAPPORTO_AUDIO_POLARITA_E_POWER_BUDGET.md`.

**Problema potenza ancora aperto:** TI specifica LM386N-1 output nominale 250–325mW su 8ohm e **6V**, THD10%; non è garanzia della potenza a **5V** del pilot. La corrente di riposo 4mA tip/8mA max a 6V non è corrente di picco richiesta dal carico speaker. Non collegare LM386 a 7805 PLL senza analisi corrente, termica, rumore e compatibilità RF; temperatura OEM 0..70°C. Le polarità ora sono dichiarate ma la forma fisica/MPN dei condensatori non è qualificata. Gate native CI su HEAD definitivo da verificare prima di merge; ERC0 da solo non prova sicurezza o fabbricabilità. Stima progetto circa **20%**, layout **0%**, nessun numero aumentato grazie alla sola nuova audit. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---

## 12 novembre 2026 — PR #56 MERGED: contratto audio MAIN ↔ FRONT validato su netlist native

**PR #56 MERGED** su `main`: SHA `e9ea0c20e4ba0404b286eab637d4ab3c992c2230`. CI [run #43274571617](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43274571617) **3/3 PASS**, su HEAD `1acf42bc431b8ae1c5a575de5a3292e67b5afd2c`. Il nuovo controllo native KiCad9 `verify_interboard_audio_contract_native.py` ha esportato entrambe le netlist reali dei pilot MAIN-audio e FRONT-volume e verificato: FRONT J1301-1→RV1301-1 `DEMOD_AUDIO`, RV1301-2→J1302-1 `VOL_WIPER_TO_AMP`, J1301-2/RV1301-3/J1302-2 `AF_GND`; lato MAIN J1202-1/C1201-1 `AUDIO_IN`, J1202-2/U1201-4 `GND` e J1201-1/U1201-6 `AUDIO_5V`. La connessione **logica** del cablaggio previsto è J1302 FRONT pin1→J1202 MAIN pin1, pin2→pin2. Tutte le suite storiche eseguite e PASS.

**Non è ancora un collegamento PCB fisico:** nessun cablaggio/PCB assemblato, nessun PCB-MAIN/FRONT layout, nessun DRC PCB. Le due estremità sono pin-header maschi, quindi un cavo idoneo è ancora da progettare e scegliere; pot 10k/footprint provvisorio e demod RX non ancora qualificati. Il rail audio +5V del banco NON è connesso al +5V PLL/RF; alimentazione dedicata da progettare. Master MAIN V2.6 invariato; 138 refs di baseline non includono i 15 componenti dei due DRAFT.

**Stima progetto documentata:** circa **20%** ingegnerizzazione complessiva delle due PCB (incertezza alta), **0%** layout/routing, non equiparare a 6/138 OEM attivi (gate BOM). **NO FAB / NO TX / NO BATTERIA/VEICOLO**. Prossime priorità: scelta concreta di cablaggio/mating headers, qualifica di pot THT e interfaccia demod, budget corrente e isolamento audio prima di disegnare PCB.

---

## 12 novembre 2026 — bozza contratto elettrico MAIN ↔ FRONT audio con pin-net verificabili

**Main verificato prima del lavoro:** SHA `c9362037015fbad2792af3c67fca821e60a6677c`, PR #54 e #55 integrate, nessuna PR aperta. Schemi principali V2.6 invariati. Due moduli standalone V2.7 DRAFT già integrati nella repository: LM386 RX MAIN (12 ref THT, ERC0) e volume FRONT (3 ref THT, ERC0). **Nessuna PCB**.

**Nuova branch in revisione:** `verification/interboard-audio-pin-contract-20261112`. Aggiunto `03_Verifiche/V2.7/CONTRATTO_AUDIO_INTERBOARD_MAIN_FRONT_DRAFT.md` con schema cavo **a 2 conduttori**: J1302 FRONT pin1 segnale wiper RV1301 → J1202 MAIN pin1 AUDIO_IN; J1302 pin2 AF_GND → J1202 pin2 GND. Le schede restano isolate: contratto è **logico, NON una connessione fisica**. Il demod RX, il potenziometro/shaft definitivo e il 5V audio dedicato restano da qualificare. Entrambe le estremità utilizzano header maschi da PCB: **non accoppiabili direttamente**, serve cavo con contatti femmina o soluzione interboard diversa con MPN verificati.

**Controllo reale previsto nella CI FULL:** `03_Verifiche/V2.7/verify_interboard_audio_contract_native.py` esporta entrambe le netlist usando KiCad9 e verifica membership pin→net per 2 connessioni e potenziometro; aggiunto al `ci/full_regressions.py`, nessuna deroga ERC. **Non dichiarare PASS finché non siano verificati i log del commit finale**.

**Stima gestionale al 12/11:** ~**20%** progettazione globale delle due PCB, **0% layout e routing fisico**; stima non metrica formale. 6/138 MPN confermati per MAIN V2.6 è solo progresso BOM di fabbricazione, **non** percentuale progetto. Gate sicurezza #27 e approvvigionamento #42 aperti; NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

---

## 12 novembre 2026 — PR #54 MERGED: primo schema KiCad9 FRONT_VOLUME THT validato

**Stato LIVE dopo il merge:** PR [#54](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/54) MERGED su `main`, SHA `31e84a6c91fc47c810e1090f13759af94519540b`, CI FULL [run #43257852754](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43257852754) **3/3 SUCCESS** sul final HEAD `4f167d5a61164a1f6bc84eec0cd7b1456f83a117`. Nativa KiCad9: **ERC 0 errori, 0 warning**; tre componenti THT `RV1301`, `J1301`, `J1302`; export netlist ufficiale conferma `/AF_GND`, `/DEMOD_AUDIO`, `/VOL_WIPER_TO_AMP`. Tutte regressioni storiche della MAIN eseguite e superate, nessun waiver.

**Artefatti nuovi reali:** `04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch`, simboli custom `TH_FRONT.kicad_sym`, tabelle librerie, progetto KiCad, footprint a tre pad `TH_FRONT.pretty/Potentiometer_THT_3Pin_PROVISIONAL.kicad_mod` e verificatore `03_Verifiche/V2.7/verify_front_volume_native.py` agganciato al gate FULL. L'utente ha approvato la separazione delle PCB (ADR-001). Il pot 10 kΩ lineare è solo una **scelta elettronica preliminare**: impronta e posizione dell'albero non sono qualificate, e devono essere sostituite da un vero MPN OEM THT ancora prodotto PRIMA del layout/frontale definitivo.

**Non affermare:** non esiste ancora un'interconnessione reale master MAIN / FRONT, un demod RX, una PCB-FRONT tracciata, una prova audio o un DRC su PCB. Il master radio **MAIN V2.6 rimane 7 fogli, 138 refs, 76 reti**; il pilot MAIN RX audio da 12 ref e questo FRONT_VOLUME da 3 ref sono schematici DRAFT **separati**, non entrano nel denominatore della BOM V2.6. Da progettare: alimentazione audio senza disturbi RF, segnale dal demodulatore, impedenze/livello e volume audio ergonomico, connettore fisico interboard e massa. Issue #27 sicurezza, #19 Coilcraft, #42 MPN finali ancora aperte. **NO FAB / NO GERBER DI PRODUZIONE / NO TX / NO BATTERIA-VEICOLO.**

---

## 12 novembre 2026 — Primo schema nativo PCB-FRONT volume THT in revisione

**Main live al bootstrap:** `564f2084f8ddbc4488b4a85562acf6806a493780`, PR #53 MERGED, nessuna PR aperta; master V2.6 ancora **7 fogli/138 THT/76 reti**. Precedente audio RX LM386 V2.7 DRAFT isolato 12 THT, ERC0 con [CI #43254795252](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43254795252), nessuna PCB reale.

**Lavoro nuovo in branch `cad/front-volume-audio-v27-draft-20261112`, NON ancora integrato:** schema KiCad9 `04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch`, 3 ref THT: J1301 segnale/audio GND da demod RX, RV1301 pot 10k lineare THT (pin1 ingresso, pin2 cursore, pin3 massa), J1302 ingresso del modulo LM386. `TH_FRONT.kicad_sym`, `sym-lib-table`, `fp-lib-table` e file progetto, footprint locale **PROVVISORIO tre pad**, NON associato a un OEM pot di produzione, assolutamente **NO PCB FAB**. Il test `03_Verifiche/V2.7/verify_front_volume_native.py` è incluso nella CI FULL per imporre ERC KiCad9 e netlist; report `03_Verifiche/V2.7/RAPPORTO_FRONT_VOLUME_THT_DRAFT.md`.

**Limiti:** nessuna continuità pin↔net fra due PCB ancora dimostrata, nessun demod reale, ergonomia/audio pot 10k da validare, alimentazione audio MAIN indipendente ancora da progettare, componenti DRAFT aggiuntivi NON inclusi nei 138 MAIN. Nessun PCB routing, DRC o misure elettroniche. Merge soltanto dopo gate CI sul final HEAD, NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

---

## 12 novembre 2026 — PR #52 integrata: primo schema audio RX THT nativo V2.7 DRAFT

**PR #52 MERGED** nel `main` vero: SHA `78f077a9132a2067d50330d8a5bcbdc62ba4b3f3`. CI FULL [run #43254795252](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43254795252): **3/3 SUCCESS** su HEAD `7e07cc47b7421048ccaa1670e75daebe088f6c5a`. Il controllo effettivo `kicad-cli sch erc --exit-code-violations` sul nuovo foglio audio riporta **0 errori / 0 warning**, netlist KiCad9 esportata e verificati **12 ref THT**; tutte le 22 suite storiche CI FULL hanno completato (111 comandi reali). Nessun waiver ERC.

**Artefatti reali nuovi, senza alterare la baseline:** `04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch` con U1201 TI LM386N-1/NOPB PDIP-8 (MPN OEM dichiarato ACTIVE, ma temporaneamente non disponibile sul sito TI), R1201–R1202, C1201–C1206, J1201 (+5 V da laboratorio), J1202 ingresso audio RX, J1203 uscita speaker, 12 componenti fisici THT; simboli progetto `TH_AUDIO.kicad_sym`, `sym-lib-table`, `.kicad_pro`. Validatore nativo `03_Verifiche/V2.7/verify_audio_draft_native.py` aggiunto alla CI FULL. Il primo ERC era 8 errori + 40 warning, il secondo 2 + 10, il finale 0 + 0 dopo correzioni **vere** di griglia, connettori e libreria.

**Distinzione fondamentale:** questo è **uno schematico nativo DRAFT isolato e verificato**, non un master radio V2.7, non una PCB. La sezione non è connessa al V2.6 MAIN: gli attuali **7 fogli, 138 refs, 76 reti** restano immutati. I 12 ref audio NON si aggiungono ancora al denominatore dei 138 dell'inventario master, ma richiederanno verifica MPN finale. Il 5V viene solo dal connettore **da banco** J1201: non alimentare dal 7805 RF/PLL senza budget corrente, separazione masse/rumore e qualifica termica. Mancano demodulatore AM/FM, controllo volume su PCB-FRONT, integrazione alimentazione, speaker load/THD e test PVT. **ERC0 non significa qualifica funzionale o sicurezza.**

**Prossimo sviluppo:** revisionare e integrare un sottosistema RF/IF/audio coerente con ADR-001, verificare lo stadio audio con sorgente/corrente e prestazioni realistiche; U401/L501 e sicurezza #27 rimangono bloccanti per le proprie parti. Gate BOM finale #42 resta attivo (6/138 confermati). **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 12 novembre 2026 — nuovo pilot KiCad9 V2.7 audio RX isolato in revisione

**Ultimo main verificato alla partenza:** commit `06c902240fdd0865a60a942ba551ccf9f1a6ed98` (PR #51 merged, checkpoint ADR-002). Nessuna PR aperta al bootstrap. **CAD integrato ancora MAIN V2.6** e NO PCB-FRONT.

**Lavoro in branch `cad/v27-rx-audio-lm386-tbd` NON integrato:** nuovo schematico nativo KiCad `04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch`, 12 piazzole THT (LM386N-1/NOPB TI PDIP-8 dichiarato ACTIVE ma al momento senza stock TI, 2 R, 6 C, 1 connettore d'alimentazione banco, 2 connettori AF in / speaker out). Sottosistema indipendente RX audio con alimentazione +5V esclusiva da laboratorio simulata da J1201, con input/5V/GND/speaker come interfacce da integrare **solo dopo review**; non è un master V2.7 completato. `03_Verifiche/V2.7/verify_audio_draft_native.py` impone ERC e netlist KiCad9 reali, invocati dalla CI FULL. Vedi `03_Verifiche/V2.7/RAPPORTO_AUDIO_RX_THT_LM386_PILOT.md`.

**Diagnosi ERC native preliminari**: run #43252593439 e #43253022016 FALLITI per il nuovo pilot (8 errori e 40 warning all'inizio): label gerarchiche sul root, due pin di alimentazione non pilotati, 31 coordinate off-grid e 9 simboli senza libreria. Schematic e libreria aggiornati nel branch per risolvere le cause, senza waiver; Secondo run #43254009373 ha ridotto le segnalazioni a 2 errori e 10 warning; aggiunti J1202/J1203 e progetto locale KiCad per affrontare i due errori e i warning. CI finale da verificare prima del merge.\n\n**Attenzione:** alimentare audio dalla 5 V RF/PLL senza verifica può degradare rumore e sovraccaricare il 7805: pilot non collegato al master, nessuna trasmissione. Le caratteristiche di altoparlante, guadagno, dissipazione, temp. 0..70°C, indice di fabbricabilità e frontale non sono approvate. U401/L501 e sicurezza #27 restano bloccanti per i rispettivi circuiti. Gate BOM finale obbligatorio. **NO FAB / NO TX / NO BATTERIA/VEICOLO.** Integrare solo dopo required CI gate verde sullo SHA finale del branch.

---

## 12 novembre 2026 — ADR-002 ratificato e nuovo gate progettazione/fabbricazione

**PR #50 MERGED** su `main`: SHA reale `bca0c76bf1f8b6fcfc08d645b759ba7c820efaed`. CI [run #43250659897](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43250659897) **3/3 SUCCESS**, inclusi test Python veloci, regressioni KiCad9 native e required gate sullo SHA head `757db03812e007b12ac4569b88cf9d990cebee73`. Aggiunta [ADR-002](ADR-002_GATE_DESIGN_PASSIVI_STANDARD_THT.md), aggiornato `AGENTS.md`, introdotto `classify_design_risk_v26.py` e esteso `verify_mpn_inventory_v26.py` con asserzioni su tutte le 138 posizioni.

**VINCOLO REVISIONATO SU RICHIESTA UTENTE:** componenti R/C standard selezionabili a specifica per sviluppare il circuito, senza MPN OEM esatto subito; 37 posizioni classificate `STANDARD_PASSIVE` in prima analisi cautelativa, altre reti RF/PLL/sicurezza sono a gate dedicato. Per FAB/BOM finale resta l'obbligo di MPN OEM attivo THT su ciascun componente **montato**, con DNI C805 risolto. L'issue #42 è stata aggiornata e resta aperta come gate di fabbricazione. Conteggio OEM confermati **6/138**, non indice completamento radio.

**PROSSIMA REVISIONE TECNICA:** ricominciare V2.7 nelle porzioni **indipendenti** dai blocchi U401/L501/#27 (solo con CAD vero e test), mentre verificare produzione attuale della PLL Lansdale, disponibilità Coilcraft RF e rischi di sicurezza; documentare pin↔pad↔net e PVT. Elettronica integrata **V2.6** con 7 fogli; nessuna PCB MAIN/FRONT completa né DRC hardware. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 12 novembre 2026 — decisione committente ADR-002: passivi standard non bloccano più gli schemi

**PR #49 integrata** su `main`, commit `e1596756a6086151c9c140df831a14c934f9abf6`; CI [#43249465480](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43249465480) 3/3 PASS. L'audit di 8 condensatori da cross-reference storica Vishay è documentazione, non approvazione OEM.

**Nuovo lavoro in branch (NON su main finché non merge)**: [ADR-002](ADR-002_GATE_DESIGN_PASSIVI_STANDARD_THT.md) recepisce il cambio esplicito deciso dall'utente: resistenze/condensatori comuni possono essere specificati per requisiti, senza MPN produttivo esatto per continuare le sezioni V2.7 indipendenti; componente RF/sicurezza/PLL/boost richiede gate di settore prima del design freeze. `classify_design_risk_v26.py` classifica tutte le 138 refs e l'inventory verifier ne controlla la copertura. **Il gate BOM finale `--release` rimane obbligatoriamente bloccante** finché mancano MPN attivamente fabbricati e DNI risolti. 6/138 certificati OEM, 132 da verificare; numeri di **fabbricazione**, NON percentuale di completamento del progetto.

**Prossima attività tecnica:** riprendere schemi reali delle sezioni indipendenti e accertare fattibilità PLL U401 e RF L501 prima di congelare tali reti; la sicurezza input #27 rimane aperta e la protezione non è dichiarata pronta. MAIN KiCad V2.6 invariata, PCB-FRONT non iniziata. NO FAB/NO TX/NO batteria/veicolo. Gate CI della policy in attesa.

---

## 12 novembre 2026 — PR #48 integrata e otto ulteriori posizioni THT sotto audit

**PR #48 MERGED** sul ramo `main`, SHA `9d714b41e223eb7e940b0d533ec7dc401acb6ed1`, Actions [#43248555956](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43248555956) **3/3 PASS**. Sei posizioni passive (tre resistori 10k, tre ceramici 100nF) con MPN candidati Yageo/Vishay, **non ancora qualificati**.

**Lotto successivo in branch, NON integrato**: `03_Verifiche/V2.6/RAPPORTO_PASSIVI_LOTTO2_C0G_X7R.md` e 8 posizioni in inventario: C403/C404 (22pF C0G PLL), C507/C510 (100pF C0G VCO), C602/C614/C615/C616 (100nF X7R bypass 5V). I candidati sono ricavati da cross-reference Vishay rev. **23/08/2012**, che NON dimostra fabbricazione corrente. Pitch documentato **2.54mm**, KiCad **2.50mm**: non qualificare come drop-in fino a confronto meccanico. Nessuna modifica CAD, nessuna simulazione vendor dichiarata.

**Resta** 6/138 `ATTIVO_CONFERMATO`, 132/138 `DA_VERIFICARE`, release BOM BLOCCATA. Issue #42 OEM U401/L501 e Issue #27 sicurezza ancora bloccanti. STOP V2.7, NO FAB / NO TX / NO batteria/veicolo.

---

## 12 novembre 2026 — PR #47 integrata; audit passivi lotto 1 in corso

**PR #47 MERGED** su `main`, commit `e210a17642c89c8825694b6a1cfbdfc66cc2189c`, CI [#43245509954](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43245509954) **3/3 PASS** incluse native KiCad9/regressioni e required gate. Aggiunto lo strumento di raggruppamento acquisti e verifica copertura di **138 refs / 114 gruppi (Value, footprint)**, senza allentare il gate BOM.

**Lotto passivi in revisione, NON integrato:** R403/R502/R804 (Yageo CFR-25JB-52-10K candidato 10k THT, stato OEM MPN da certificare), C401/C405/C406 (Vishay K104K15X7RF53L2 candidato X7R 100nF, passo OEM 2.54mm vs CAD 2.50mm da verificare); `03_Verifiche/V2.6/RAPPORTO_PASSIVI_LOTTO1_CANDIDATI.md`. Nessun valore o footprint CAD modificato, nessun lifecycle promosso, **6/138 ACTIVE e 132/138 DA_VERIFICARE**. Conferma produttiva corrente e fit/performance mancanti. STOP V2.7, NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

---

## 12 novembre 2026 — PR #46 integrata e nuovo gate di copertura audit approvvigionamento

**PR #46 MERGED** su `main`: SHA `696e6d19dc04d96f07517c46b441db223885fca9`, CI [#43218640115](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43218640115) fast PASS, required gate PASS, KiCad native SKIPPED per solo checkpoint documentale. Confermata la necessità di evidenza OEM sui nuovi lotti per U401 ML145151YP e L501 Coilcraft 150-05J08L.

**Lavoro nuovo in PR #47 (NON ancora integrato):** strumento `03_Verifiche/V2.6/group_procurement_v26.py`, relativo rapporto e rafforzamento del verificatore inventario per garantire esattamente **114 gruppi valore/impronta e 138 riferimenti fisici non duplicati**. Il raggruppamento **non** certifica equivalenza elettrica, disponibilità né ciclo produttivo. La CI deve verificare la modifica allo script prima dell'integrazione. Stato BOM **6/138 ACTIVE, 132/138 DA_VERIFICARE**, ultima V2.6 CAD, nessuna PCB. STOP V2.7, NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

---

## 12 novembre 2026 — PR #45 MERGED e conferma blocchi produttivi principali

**PR #45 integrata** su `main`: commit `3f2c34b004081de964c70229651793d34a8b3531`. GitHub Actions [run #43217910409](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43217910409) **3/3 SUCCESS** sullo SHA head `72ad054f482344570b6ab1838140522ada9bf3cf`, incluse suite fast, KiCad9 nativa/regressioni e required gate. Inventario V2.6 arricchito con prove OEM relative a D701/D804/D805/D920, L920, F701 e rapporto `03_Verifiche/V2.6/RAPPORTO_AUDIT_OEM_LOTTO3_DIODES_FUSE_L920.md`. **Nessun cambiamento circuitale.**

**Nuovo controllo diretto documentazione OEM (registrato in Issue #42 e #19):** Lansdale pubblica il cross-reference `MC145151P2 -> ML145151YP` PDIP28 e modulo «Request a Quote», **non prova nuova fabbricazione corrente**. Coilcraft Uni7 `150-05J08L`: L regolabile **137–193 nH** (nom. 165 nH), Q min **114 a 50 MHz**, SRF min **650 MHz**, DCR **13,2 mΩ** nella pagina OEM; pagina segnala anche configurazione non acquistabile online, condizione **non sinonimo EOL**. Produttori devono confermare nuovi lotti fabbricati, continuità produttiva, conformità e modalità ordini. I due MPN **non sono promossi a ACTIVE**. Links: https://www.lansdale.com/datasheets.php ; https://www.lansdale.com/parts_reference.php?manufacturer=Motorola%2FFreescale&series=Wireless ; https://www.coilcraft.com/en-us/products/rf/tunable-rf-inductors/vertical-mount/uni7/?skuId=27487 .

**STATO reale**: MAIN KiCad V2.6, 7 fogli, 138 THT e 76 reti; FRONT ancora da progettare. **6/138 MPN posizionali produttivi confermati, 132 DA_VERIFICARE**, gate `--release` bloccato. Non è stata inviata una richiesta commerciale ai fabbricanti e nessuna risposta scritta OEM acquisita. Prossimo passo: ottenere riscontri esatti su U401/L501/L920, selezionare MPN dei passivi e identificare fattibilità del criterio B, poi qualifica sicurezza #27. **STOP V2.7, NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

---

## 12 novembre 2026 — PR #44 integrata; lotto 3 audit Schottky/boost/fusibile in revisione

**PR #44 MERGED** su `main`, commit `a600627c3933ad12c331eb49bd8e309fd1837d97`. CI [#43216359795](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43216359795): fast PASS, required gate PASS, suite native **SKIPPED correttamente** per diff esclusivamente documentale. Documento pinout preliminare TI U801/U803/U912 integrato; nessuna modifica CAD.

**Lotto 3 in branch (non ancora integrato):** `03_Verifiche/V2.6/RAPPORTO_AUDIT_OEM_LOTTO3_DIODES_FUSE_L920.md`, 6 righe di inventario arricchite di fonti senza promozione lifecycle: D701/D804/D805/D920 Vishay 1N5819 (SKU precisi da scegliere, 40 V nominali impongono test fault/transient), L920 Bourns RLB0914-681KL PCN e parametri, F701 Littelfuse 0251.500MXL dichiarazione REACH con Pb. I documenti di qualità/PCN/conformità non provano produzione OEM attuale. Conteggio **6/138 ACTIVE** e **132/138 DA_VERIFICARE** invariato. Nessuna simulazione vendor, ERC nuova, BOM-release o progetto PCB dichiarati.

**Priorità:** verifica MPN SKU OEM scritta e prodotto ancora fabbricato; selezione MPN esatti, controllo VRRM/guasti, L920 corrente/saturazione, U401 PLL e L501 Coilcraft; poi qualifica CAD. Resta STOP V2.7 e BOM-release, Issue #27 sicurezza. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

---

## 12 novembre 2026 — PR #43 integrata, audit di pin candidati successivo in corso

**PR #43 MERGED** su `main`: merge SHA `5a43da52e5eb73188832f050c7786c01ec24d0a1`. CI definitiva [run #43215777733](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43215777733) **3/3 PASS** sul commit head `55a90ddfa7e21bc9a030b8736f48b089f62c966b`: fast, suite native KiCad9/ngspice e gate. File aggiunti/aggiornati: inventario OEM V2.6 e `03_Verifiche/V2.6/RAPPORTO_AUDIT_OEM_LOTTO2_2026-11-12.md`. Le prove produttive di tre **candidati** TI (LM393N/NOPB, LM358N/NOPB, LM317T/NOPB) NON costituiscono promozione dei MPN CAD; F701 ha evidenza RoHS ma non lifecycle. **6/138 confermati; 132/138 da verificare.**

**Lavoro successivo non ancora integrato:** [`RAPPORTO_PINOUT_CANDIDATI_TI_LOTTO2.md`](../../03_Verifiche/V2.6/RAPPORTO_PINOUT_CANDIDATI_TI_LOTTO2.md), audit documentale della corrispondenza pin numerici simbolo KiCad/OEM e intervalli termici 0..70°C U801/U803. Nessuna modifica ai file KiCad o al gate BOM; nessuna nuova KiCad ERC/netlist/CI dichiarata per questo branch. Prossimi blocker: qualifica sotto guasto #27, specifica MPN di tutti i passivi, U401 ML145151YP, L501, L920, verifica effettiva pin-pad-net e package meccanici. **V2.7 circuitale sospesa, NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

---



## STOP V2.7 — Audit produttivo obbligatorio di TUTTI i 138 THT (12 novembre 2026)

**Richiesta vincolante dell'utente:** prima di ulteriori revisioni elettroniche, essere certi che TUTTI i componenti siano **effettivamente fabbricati attualmente**, con **MPN/footprint 100% THT** e fonti **ufficiali dei produttori**, non scorte NOS o semplice presenza di un datasheet. Questo requisito prevale sulle precedenti priorita di progettare subito la doppia protezione.

**PR #41 MERGED:** merge `8c45a1f1e9c3deb0dbf665bc90895d0bb3eee4a2` e [Actions #43119368514](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43119368514) **3/3 PASS** sul head tecnico `694924f02b3971894507290786009472857d7f50`. Inventario aggiornato `03_Verifiche/V2.6/INVENTARIO_MPN_V26.csv`; [rapporto gate produttivo](../../03_Verifiche/V2.6/RAPPORTO_GATE_PRODUZIONE_138_THT.md). **6/138 MPN esatti attivi confermati** con pagine OEM: Q801 IRF9540NPBF, U802 TL431BCLP, U520 SN74AC14N, U601 L7805CV, U911 MC34063ABN, D806 Diotec 1N5352B (lead-free No/esenzione RoHS 7(a)-I). **132/138 NON VERIFICATI**, non significa EOL. Stato produttivo non è qualifica elettrica/termica. Vecchio conflitto U911 ST tra categoria e tabella prodotto: riga esatta MC34063ABN indicata active in volume production sul sito ST.

**Nuovo gate di rilascio:** `python3 03_Verifiche/V2.6/verify_mpn_inventory_v26.py --release` DEVE RIFIUTARE BOM mentre anche una sola posizione non è OEM ACTIVE; la CI ordinaria verifica solo integrita CAD e NON approva produzione. [Issue #42 — BLOCCANTE BOM](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/42) creato per tracciare la certificazione. Priorita assolute: ML145151YP Lansdale produzione esatta, L501 Coilcraft 150-05J08L produzione, L920 Bourns, 45 resistori/42 condensatori/22 connettori/1 quarzo con MPN non generici, associare pinout e suffix per U801/U803/U912, risolvere C805 DNI. Su Coilcraft 150-05J08L sito OEM riporta configurazione non acquistabile online: non scambiare per EOL senza conferma. Lansdale afferma fabbricazione aftermarket come attivita generale ma non garantisce specifico ML145151YP senza risposta puntuale.

**STOP nuova V2.7 circuitale, RF/IF/audio e PCB** finche il vincolo produttivo non è risolto. La PCB-FRONT futura richiedera audit separato. Ultimo KiCad MAIN reale V2.6, 7 fogli, 138 componenti THT, 76 reti; ADR-001 due PCB / frontalino Evolution / S-meter analogico confermati. Issue #27 sicurezza OVP/UVLO resta aperta. **NO FAB / NO TX / NO BATTERIA/VEICOLO.**

---

## PR #39 MERGED — RETTIFICA BOM FISICA E PRIMA QUALIFICA LIFECYCLE (12 novembre 2026)

**Merge commit:** `70857c04468930a6cc53accad9c225b1728be45c`. [PR #39](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/39) MERGED. [GitHub Actions #43118083104](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43118083104): **3/3 PASS** sul commit tecnico `ac0a8b6e1eef5bb1d4b848f222248222201d8e30`, incluso test rapido e KiCad9/regressioni legacy reali.

**Correzione sostanziale:** precedente `INVENTARIO_MPN_V26.csv` aveva 138 righe ma non rappresentava tutti i 138 componenti fisici: includeva erroneamente PWR701/PWR801/PWR802, marcatori ERC senza componente, e ometteva **Q801, D804, R1011**. Nuovo parser controlla **singoli blocchi di simbolo** e verifica esattamente i 138 componenti della gerarchia V2.6; nessun elemento ERC-only inventariato. Nuovo rapporto [RAPPORTO_MPN_PRIORITARI_PRODUTTORI_2026.md](../../03_Verifiche/V2.6/RAPPORTO_MPN_PRIORITARI_PRODUTTORI_2026.md) con fonti originali e data.

**Stato produttivo verificato per 6 posizioni critiche:** **Q801 Infineon IRF9540NPBF TO220** e **U802 TI TL431BCLP TO92** attivi sul codice d'ordine esatto; **U911 ST MC34063ABN DIP8 CONFLITTO_FONTI** (pagine ST Active vs NRND), sospendere approvazione; **U401 ML145151YP** presente nel datasheet del costruttore Lansdale (PDIP28), ma **produzione corrente dell'esatto codice non ancora dimostrata**, non sostituire preventivamente; **U402 Toshiba TC74AC74P(F)** part number rappresentativo ancora da confermare; **U801 TI LM393N/NOPB** attivo come candidato, ma CAD ha descrizione LM393N_DIP8_DUAL da associare al codice esatto. Conteggio del CSV: 2 `ATTIVO_CONFERMATO`, 1 `CONFLITTO_FONTI`, 135 `DA_VERIFICARE`. Nessuna prova di fabbricazione corrente degli altri 135 componenti, nessuna BOM qualificata.

**Prossimo blocker:** conferma scritta Lansdale per ML145151YP (non solo fondi di magazzino/die banking) e ST per stato ABN; qualificare temperature e pinout dei componenti di sicurezza, poi progettare **vera V2.7 circuitale KiCad** con secondo power-good indipendente (contratto PR #35), test guasti/corner e riferimento separato. L'Issue #27 resta OPEN. **CAD MAIN ancora V2.6, 7 fogli, 138 THT, 76 reti; PCB-FRONT approvata ma non disegnata. ADR-001 confermata. NO FAB / NO TX / NO BATTERIA/VEICOLO.**

---

## PR #37 MERGED — inventario di tutti i 138 riferimenti THT (11 novembre 2026)

**PR #37 MERGED**: commit `ace025d02f42c0ec55b5252ab28755b8ba14d0b5`, head tecnico `0ff34d307f0cd3fa7d656ce534f3afa5769b741b`. [CI finale 43113341328](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43113341328) **3/3 PASS** (fast, KiCad9 nativo, gate). Prima esecuzione 43113260951 fallita per classificazione test troppo restrittiva del footprint quarzo `Crystal:Crystal_HC49-U_Vertical`; corretta e riverificata, senza nascondere l'esito fallito originario.

Nuovi file: `03_Verifiche/V2.6/INVENTARIO_MPN_V26.csv` (138 riferimenti unici da sette fogli nativi), `verify_mpn_inventory_v26.py` e `RAPPORTO_AUDIT_LIFECYCLE_THT_V26.md`; check incluso nei test rapidi a ogni PR. **Tutti i lifecycle risultano DA_VERIFICARE, non dichiarati attivi**; campi `Value` non garantiscono MPN esatto. Priorità verifica produttore U401 ML145151YP PLL legacy, U402 TC74AC74P(F), protezione LM393/TL431, Q801, U911 e induttori RF. **Nessun componente sostituito**, BOM non approvata.

**CAD elettrico MAIN ancora V2.6**, sette fogli e 76 reti; seconda catena PG prevista dalla PR #35 ma non realizzata. Vincolo **due PCB THT FRONT/MAIN con S-meter analogico** e criterio **componenti ancora in produzione** permanenti. Issue #27 bloccante; #19, #21, #29 non risolte. **NO FAB / NO TX / NO BATTERIA/VEICOLO**.

---

## Regola permanente di approvvigionamento — componenti THT attualmente in produzione (criterio B, 11 novembre 2026)

**Requisito vincolante approvato dall'utente e valido per entrambe le PCB, ogni nuova chat e ogni revisione:** tutti i componenti da approvare per la distinta definitiva devono essere **ancora attivamente prodotti dal rispettivo fabbricante** (codice produttore/MPN esatto), con contenitore e montaggio **100% THT**. Sono ammesse sostituzioni con equivalenti **attualmente prodotti**, anche di altra marca, ma solo dopo qualificazione documentata di pinout, tensioni/correnti, tolleranze, stabilità, dissipazione, caratteristiche RF, dimensioni e footprint, prestazioni e interazione con il circuito. La reperibilità di scorte presso un distributore **non** prova che un codice sia ancora in produzione; non considerare fondi di magazzino, NOS, componenti EOL/NRND/obsoleti come scelte finali senza autorizzazione esplicita dell'utente. Favorire canali autorizzati e pluralità di fornitori, distinguendoli dalla conferma di stato produttivo del fabbricante.

**Procedura obbligatoria prima di consolidare la BOM e prima di ogni sostituzione:** audit di tutti gli MPN distinti già presenti nella V2.6 (138 riferimenti fisici, non necessariamente 138 MPN distinti), poi verifica dei nuovi MPN con fonti ufficiali aggiornate e data della verifica; classificare «attivo confermato», «da verificare», «obsoleto/NRND da sostituire». Ogni componente non confermato rimane **candidato non qualificato**, non automaticamente approvato. Riesaminare periodicamente lo stato in vista della produzione. Se un equivalente altera il circuito, applicare il normale ciclo branch → CAD → controlli → PR → CI → merge. **Nessun componente, schema o BOM viene modificato per effetto della sola adozione di questa regola:** prima svolgere l'audit, poi proporre le sostituzioni e discuterle con l'utente.

## PR #35 MERGED — CONTRATTO PRE-CAD PER SECONDO POWER-GOOD INDIPENDENTE (11 novembre 2026)

**main merge:** `ca244f885811c0065751128d4bd2ad231ad7fcc9`. [PR #35](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/35) integrata. [Actions run #43110429072](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43110429072) **3/3 PASS** sul commit finale `996e3437f4292b27cd0b524342f15ee001ab822b`. ERC0, 76 reti KiCad9 native, 111 comandi regressione storica. Script `03_Verifiche/V2.6/screen_independent_pg_contract_v26.py` esegue **48 stati logici di guasto singolo**: 10 stati pericolosi nel solo percorso primario attuale, 0 nella **sola ipotesi matematica** di due interruttori e due canali OVP/UVLO indipendenti, più 3 stati pericolosi di guasto comune entrambi bloccati su consenso. **Q804 e secondo supervisore NON ESISTONO ancora nel CAD**, quindi zero sicurezza fisica dimostrata; nessuna "V2.7 KiCad", MPN, simulazione vendor o PCB creata. Rapporto: [contratto PG indipendente](../../03_Verifiche/V2.6/RAPPORTO_CONTRATTO_POWERGOOD_INDIPENDENTE.md).

**Prossimo lavoro prioritario:** realizzare **una vera revisione KiCad con secondo interruttore e supervisore indipendenti**, selezionare MPN/footprint THT, evitare deadlock di accensione e reference/supply comuni, controllare ULVO/OVP, gate IRF9540N VGS ed eventuale transistor short, monitor PG e audio/TX mute di default. Validare schema con export KiCad9 e SPICE vendor/test banco, quindi non chiudere Issue #27 prematuramente. L501 Coilcraft 150-05J08L e L920 Bourns RLB0914-681KL hanno già candidati THT e footprint locale: #19/#21 restano aperte per qualifica RF, saturazione, termica e layout (non riaprire vecchio lavoro di sola selezione). **CAD MAIN ultima V2.6, 7 fogli, nessuna PCB**, ADR-001 due PCB THT e frontalino Evolution con S-meter analogico confermata, **NO FAB/NO TX/NO BATTERIA/VEICOLO**.

---

## PR #34 MERGED — Q802/Q803 UN SOLO CORTO ELUDE OVP O UVLO (11 novembre 2026)

**main merge:** `3fea7099edd996a2e03e4c79c17092522ff003d9`. [PR #34](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/34) integrata, [CI 43107738831](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43107738831) **3/3 PASS** sul commit finale `df89d21bc13db9aab2738ac7c266c9ade0d578f0`. KiCad9 ERC0 e netlist nativa V2.6 **76 reti**, 111 comandi di regressione storica, nuovo script indipendente `03_Verifiche/V2.6/audit_q802_q803_single_fault_v26.py`: **20 combinazioni binarie** con transistor sano, C-E corto e C-E aperto; verifica pin↔net Q802/Q803/R1009/R1007/R1016/Q801/D803.

**Risultato BLOCCANTE:** con Q802 C-E corto e UVLO che consente, GATE_SINK può attivarsi **anche se OVP nega**. Con Q803 C-E corto e OVP che consente, può attivarsi **anche se UVLO nega**. I due NPN in serie sono AND solo *nominale*, NON un sistema fail-closed a guasto singolo. Questo è un modello logico, non simulazione transistor/PVT/bench. [Rapporto](../../03_Verifiche/V2.6/RAPPORTO_Q802_Q803_GUASTO_SINGOLO.md). Il log conserva anche test RF esplorativi storici con `FAIL_VARACTOR_FORWARD_IN_MODEL` per alcuni corner non qualificati: i gate software sono verdi, la RF NON è qualificata.

**Ultima revisione CAD MAIN: V2.6**, nessuna variazione elettrica o PCB. **ADR-001 due PCB FRONT/MAIN + S-meter analogico** rimane approvata e integrata. Prossima revisione sostanziale: progettare con true KiCad9 THT una catena di **power-good + mute indipendente** dal sink Q802/Q803 e validare guasti singoli LM393/TL431/Q802/Q803, transitori, reverse, VGS. Issue #27 resta OPEN; #19 VCO e #21 boost ancora aperte. **NO FAB/NO TX/NO BATTERIA/VEICOLO**.

---

## PR #32 INTEGRATA — AUDIT R1011/D806 E BIAS LM393/TL431 (11 novembre 2026)

**Main merge SHA:** `a602c4698c902dcbbaaed620cf8b552382b349b6`. [PR #32](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/32) MERGED. **CI finale** [run 43106337951](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43106337951) **3/3 PASS**, native KiCad9 ERC0, 76 netlist reali, regressioni storiche complete 111 comandi; test `03_Verifiche/V2.6/audit_r1011_d806_thermal_fault.py` 675 combinazioni e `03_Verifiche/V2.6/screen_ctl_rail_bias_v26.py` 2268 combinazioni (entrambe analisi **idealizzate**, NON qualifica hardware). Prima CI run 43106061528 FAILURE per un bug Python nel nuovo test, corretto su HEAD e poi CI finale tutta verde: **non occultare la failure storica**.

**Risultati indicativi:** a VIN=13,8V, `OVP_CTL_VCC` 7,815..10,099 V nel modello caricato R1011/R1001/U801; D806 15V idealizzato spento; a VIN=11,5V rail 6,286..8,470V. La tensione di clamp D806 NON è garantita alle correnti inferiori ai 75mA di specifica. A 48V / 140°C alcuni corner superano il limite termico teorico PR03; D806 corto può sovraccaricare R1011. Con D806 aperto e TL431 sano, 48V → 30,562..34,317V nel modello, **ma con guasto congiunto del riferimento si può superare 36V**: nessun fail-safe dimostrato. <https://github.com/jd3485/Superstar3900-THT-Evolution/blob/main/03_Verifiche/V2.6/RAPPORTO_BIAS_LM393_TL431_V26.md>.

**CAD MAIN ancora V2.6**, nessuna modifica KiCad/PCB; futura architettura due PCB **ADR-001 è integrata** e resta vincolante. **Priorità #27 aperta:** scelta topologia a guasto sicuro rail LM393/TL431, controllo reference-open e latch/power-good fail-closed; prove PVT/vendor, poi gestione RF #19/#21. Nessun layout, DRC scheda, prototipo, fab o TX. **NO FAB / NO TX / NO BATTERIA/VEICOLO.**

---

## ADR-001 INTEGRATA SU MAIN — PR #33 (11 novembre 2026)

**Decisioni confermate e persistenti tra chat:** due PCB THT (PCB-MAIN radio + PCB-FRONT comandi/display), stile Superstar 3900 **Evolution**, manopole e comandi tradizionali, **S-meter analogico a lancetta**. Documento decisionale [ADR-001](ADR-001_DUE_PCB_FRONTALE_EVOLUTION.md), istruzione permanente aggiornata in [AGENTS.md](../AGENTS.md). **PR #33 MERGED**, merge commit `6fac6ed458c02778197d179aa1d088e8baa75f7c`, [Actions 43103277921](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43103277921) PASS (fast e gate; native saltato correttamente per soli documenti). La scelta sostituisce il precedente obiettivo di PCB unica senza toccare i sette fogli della V2.6; nessuna PCB FRONT è ancora disegnata.

**Priorità ingegneristica invariata:** riprendere la [PR #32](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/32) audit R1011/D806, [run 43096018510](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43096018510) in coda all'ultima verifica, poi protezione LM393 e blocchi RF. Issue #27 resta aperta; NO FAB / NO TX / NO BATTERIA/VEICOLO.

---

## ADR-001 — nuova architettura approvata: due PCB e frontalino Evolution

L'utente approva **PCB-MAIN radio + PCB-FRONT** con manopole fisiche e **S-meter analogico a lancetta**, display moderno discreto, look Superstar 3900 Evolution. Decisione completa: [ADR-001](ADR-001_DUE_PCB_FRONTALE_EVOLUTION.md). Il mandato storico «PCB unica» è sostituito **solo come architettura futura**, non significa che la frontale esista già. V2.6 rimane ultima CAD MAIN integrata; PCB-FRONT senza schemi/layout/footprint qualificati. PR #32 resta bozza di audit termico e CI #43096018510 in coda all'ultimo controllo. Tutti i rischi #27 e NO FAB/NO TX restano.

---

## CHECKPOINT SUCCESSIVO: PR #31 AUDIT D803 INTEGRATA SU MAIN (11 novembre 2026)

**Ultima revisione CAD integrata: V2.6**, invariata elettricamente. [PR #31](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/31) MERGED, merge commit `0d28a2c38c785d92421c7b99aec4a039a3962c12`. Test ufficiale sull'ultimo HEAD tecnico `0f97a724bd283baf47dc877aa8e71071560a3946`: [CI 43081722718](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43081722718) **3/3 PASS**. ERC0, 76 netlist reali, D803 1N4742A catodo verso source Q801/FUSED_RAW e anodo verso gate/PFET_GATE; 486 corner Python ideali; tutte le regressioni KiCad/ngspice consolidate PASS. **Nessuna componente o netlist modificata** rispetto a V2.6. Il report `03_Verifiche/V2.6/RAPPORTO_D803_GATE_CLAMP.md` sostituisce l'inferenza senza Zener del precedente test R1008/R1009: l'allarme |VGS| >20V a 48V è riferibile a **D803 aperto**, mentre la Vz reale è non qualificata alle correnti ~3mA, inferiori ai 21mA di specifica.

**Blocchi ancora aperti:** issue #27 sicurezza a guasto, LM393 max 36V, Q802/Q803, VGS transitoria, onsemi D803 open/short, coordinamento TVS/fusibile e PG/mute indipendenti; #19 VCO e #21 boost; nessuna PCB, DRC o Gerber. **NO FAB / NO TX / NO BATTERIA/VEICOLO**. Questo checkpoint è superiore temporalmente alle sezioni storiche successive.

---

## STATO CORRENTE — MERGE V2.6 VERIFICATO IL 11/11/2026

**main integrato:** PR #28 [MERGED](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/28), merge SHA `998e619ed35af13a51b03ff58cd570e22cc877c5`. L'ultima revisione CAD effettivamente presente su main è **V2.6**. Master `04_KiCad/V2.6/PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch` (sette fogli THT). V2.4/V2.5 conservate.

**CI obbligatoria sul PR final HEAD `3e3f904358f7a0e4b384a2ecf9964076a1d8a896`:** [run 43076650377](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43076650377) PASS tutti e tre i job; KiCad9 ERC0, sette SVG reali, generatore riproducibile 10 file, V2.5→V2.6 73→76 netlist reali con sole migrazioni U801/7 e Q802/1, 138/138 campi footprint THT; regressioni precedenti KiCad/ngspice e Python PASS.

**Sicurezza e completezza:** baseline CAD *candidata e NON qualificata*: Q803 2N3904 e R1014–R1017 aggiungono percorso di consenso UVLO separato dalla retroazione OVP; nessuna prova di fail-closed a guasto singolo, alimentazione a 48V, TL431, diodi/fusibile, VGS PFET, startup, termica o power-good/mute. Issue #27 aperta, più #19 e #21 componenti RF/boost e #29 infra storico. **La radio RX e PCB completa non esistono ancora; nessuna DRC, nessuna fabbricazione/TX autorizzati, niente batteria/veicolo.**

Prossimo lavoro: validazione indipendente dei guasti della protezione, scelta di un clamp VGS e del mute/power-good, modelli vendor e qualifica magnetici, poi circuiti RF/IF/audio/controlli THT. Questo paragrafo è il checkpoint attuale; le sezioni seguenti descrivono **stati storici anteriori al merge e non devono sostituirlo**.

---

## ARCHIVIO: checkpoint PR #28 prima del merge — NON PIÙ STATO ATTUALE

Al commit `4b957715ff28d149b322f6af8c5d378ccff8e2dd` la run ottimizzata [43075944405](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43075944405) ha superato realmente 3/3 job. **KiCad9 ERC0**, generatore V2.6 riproducibile (7 schemi + 3 librerie), netlist **73→76** gruppi e **138/138** impronte THT, sette SVG, tutte le regressioni native KiCad/ngspice e test Python precedenti. La V2.6 implementa Q803 + R1014..R1017, U801/7 su UVLO_OC e Q802/1 su SERIES_MID. V2.4/V2.5 preservate. Prove hardware, fault-tolerance, 48V, reverse, termica e power-good/mute restano OPEN: issue #27, #19, #21; nessuna PCB/DRC/Gerber.

**Main osservato in questo checkpoint:** `b9dcca23725166573144079924e18f2852fafc58` / CAD V2.3. PR #28 ancora DRAFT, non fusa. La presente piccola revisione del checkpoint e dei soli flag diagnostici deve superare una nuova CI sul commit HEAD prima di qualsiasi integrazione. No hardware/fab qualification, NO FAB / NO TX / NO BATTERIA/VEICOLO.

## Checkpoint supplementare PR #28 (SOLO BRANCH DRAFT, NON ANCORA SU MAIN)

Verifica live 11 novembre 2026: main HEAD b9dcca23725166573144079924e18f2852fafc58, PR30 ottimizzazione CI merged; revisione CAD ufficiale V2.3. PR28 V2.4 resta draft e NON merged.
La precedente CI #43057845067 PASS (ERC0, 72->73 netlist, 131 footprint fields) appartiene esclusivamente al precedente SHA 715c41c3ebcdef9c851f9434be3420132aac92a5.
Questa revisione del branch modifica davvero master e generatore: R1011 ora Vishay PR03 820R/3W e D806 Diotec 1N5352B 15V/5W DO-201; aggiornati BOM, simbolo, impronte, test PVT con derating e rapporto. Prima di qualsiasi merge richiede nuova CI su HEAD finale; non attribuire al nuovo SHA il vecchio PASS. Qualifica elettrica, UVLO, fail-closed, reverse, F701/D702, thermals e 48V restano BLOCCATI. Il checkpoint su main rimane V2.3 finché PR28 non è merged. NO FAB / NO TX / NO BATTERIA/VEICOLO.

## V2.5 candidate in PR #28 DRAFT — 11 novembre 2026 (NON MERGED)

Sul branch `feature/v2.4-ovp-lm393-guard-15v-tht`, dopo la V2.4 candidata verificata da run #43060668801 sul commit 9d0b7d77, è stata preparata **una nuova revisione V2.5 con sette nuovi schemi KiCad9 nativi**, mantenendo V2.4 e tutta la storia. Le modifiche V2.5 sono limitate al circuito di supervisione:
- U801 LM393B comparatore B: **pin5 da GND a UVLO_SENSE; pin7 da NC a CMP_OUT** insieme a pin1 del comparatore A (open-collector wired-AND); pin6 resta VREF2V5.
- R1012 Yageo 36k/1% e R1013 Yageo 10k/1% THT per soglia UVLO nominale 11,5V; **R1001 Vishay PR01 da 3k3 a 1k8** per migliorare corrente TL431 alla soglia minima in modello ideale.
- Nuovi generatore, audit netto dei pin-nets reali, PVT screening, delta BOM, rapporto e workflow v25 manuale, con tutti i gate nel job unico ottimizzato. Il benchmark precedente della V2.4 NON convalida la V2.5: serve CI sul HEAD finale nuovo.
- Non è una soluzione fail-closed garantita sotto guasto singolo: TL431 open, clamp open/short, commutazioni a soglia senza isteresi, gate, F701/D702, prova di corrente reale, 48V e thermal rimangono APERTI. Non esiste PCB/DRC. **NO FAB / NO TX / NO BATTERIA/VEICOLO**.

Main rimane V2.3 (ultimo HEAD osservato `b9dcca23725166573144079924e18f2852fafc58`) finché la PR #28 non è realmente fusa. Non dichiarare merge, ERC0 V2.5 o CI verde se non risultano da log SHA finale.

## Ottimizzazione dei controlli GitHub Actions, distinta dallo stato elettrico

La revisione CAD realmente integrata resta **V2.3** (PR #26,
commit tecnico `faa146e2bdd12b13df1cbb4d20e67196ad5098b9`).
Nell'intervento infrastrutturale successivo sono stati identificati
**20 workflow legacy** auto-attivati su ogni PR e su push main, di cui
**14 native KiCad9** con download indipendente via PPA Launchpad,
**5 simulazione ngspice**, **1 regressioni Python V0.1–V1.0**.
Questo moltiplicava consumi e fallimenti di rete (issue #29).

Policy disponibile nel nuovo `.github/workflows/ci_optimized.yml` e
[ci/CI_COST_OPTIMIZATION.md](../ci/CI_COST_OPTIMIZATION.md):
- nessun push main automatico o invocazione di venti suite distinte;
- regressioni Python sulla PR, anche se solo documentale;
- per qualunque modifica non documentale, **tutte** le 19 suite storiche
  KiCad/ngspice eseguite in un solo job dentro il container KiCad 9.0.9
  ufficiale, digest pinned e pilota ERC0 [43054348749](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43054348749);
- 20 workflow originali restano invocabili manualmente e i loro singoli
  step di verifica sono eseguiti fedelmente dal runner aggregato;
- gate unico MUST PASS su SHA finale prima di ogni integrazione tecnica;
  nessuna inferenza di DRC PCB senza PCB.
**Avvertenza:** i file documentano la policy ma la piena migrazione si considera
realizzata solo dopo esito CI e merge confermato della relativa PR su main.

**Lavoro tecnico ancora OPEN**: [PR #28 V2.4](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/28)
(candidato guardia LM393/R1011/D806 non integrato, ERC e netlist native
V2.4 da ripetere con runner funzionante), [issue #27](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/27)
(guasti, UVLO, power-good/mute fail-closed non qualificati), [issue #29](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/29)
(storico PPA Launchpad); issue #19 e #21 RF/termica.
Non cambiare il conto/budget Github. **NO FAB / NO TX**.

## Ultima revisione realmente integrata — V2.3

| Campo | Ultimo stato accertato |
|---|---|
| **Ultima revisione ELETTRICA/CAD MERGED** | **V2.3 — sette fogli KiCad9 RX PLL/VCO/5V/13,8V OVP/VTUNE20, footprint L501 Coilcraft candidato** |
| **HEAD main all'ultimo controllo tecnico** | `faa146e2bdd12b13df1cbb4d20e67196ad5098b9` (merge PR #26; un successivo commit solo-documentale cambierà naturalmente HEAD: RIVERIFICARLO live) |
| PR #20 **V2.1 MERGED** | [#20](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/20) — merge `b7b475e05b7279f2944fbfa6ea50d38680f874c4`, footprint assiali F701 e D702 THT candidati |
| CI V2.1 sul final HEAD | **18/18 workflow PASS** (17 regressioni storiche + gate V2.1); [native KiCad run 42991959540, tentativo 3](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42991959540): ERC 0, 72 partizioni pin-net, 7 SVG, 2 footprint SVG |
| PR #24 **V2.2 MERGED** | [#24](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/24) — merge `30328084e72339f3909e618ff37162e8f31827d4`, footprint THT candidato L920 Bourns 680µH |
| CI V2.2 sul final HEAD | **19/19 workflow PASS** su `574abd13c5591a1cbb3ccc0c8cd2289a2df05339`; [native run 43011468320](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43011468320): ERC0, 72 partizioni intatte, 128/129 campi footprint |
| PR #26 **V2.3 MERGED** | [#26](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/26) — merge `faa146e2bdd12b13df1cbb4d20e67196ad5098b9`, candidato Coilcraft 150-05J08L L501 e nuova impronta THT |
| CI V2.3 sul final HEAD | **20/20 workflow PASS** su `d0b31d413a044e0c8035c0460086b5193e52197f`; [native run 43012377058](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43012377058): KiCad9 ERC0, sette fogli SVG, **72 gruppi netlist e tutte le partizioni pin→net invariate** |
| Master KiCad autorevole | [04_KiCad/V2.3/PLL_RX_HIERARCHICAL_MASTER_V2.3.kicad_sch](../04_KiCad/V2.3/PLL_RX_HIERARCHICAL_MASTER_V2.3.kicad_sch) |
| Copertura CAD nel master RX **parziale** | **129 riferimenti fisici, 129/129 campi Footprint valorizzati**; passaggio di audit **non** equivale a qualifica componenti/package né al completamento radio |
| PCB unica, routing, DRC PCB | **NON ESISTONO / NON ESEGUITI**. Nessun `.kicad_pcb` completo. Nessun Gerber produttivo, nessun prototipo o test hardware |
| Autorizzazioni | **NO FAB / NO GERBER PRODUZIONE / NO TX**; vietata connessione a batteria, veicolo o catena TX senza autorizzazione |

### File reali della revisione V2.3

Sette schemi nativi nuovi `04_KiCad/V2.3/*.kicad_sch`, generatore
`04_KiCad/V2.3/genera_L501_v23.js`, tabelle librerie e
`THT_V23.pretty/Inductor_Coilcraft_150-05J08L_Uni7_Tunable_THT.kicad_mod`,
audit `03_Verifiche/V2.3/verify_kicad_v23.py`, gate aritmetico
`screen_vco_l501_v23.py`, rapporto `RAPPORTO_L501_VCO_V2.3.md`, workflow
`.github/workflows/cad_native_v23.yml` e delta BOM. Solo proprietà
**Value** e **Footprint** di L501 variate intenzionalmente da V2.2; tutte
le 72 partizioni elettriche native invariate.
La V2.2 conserva F701, D702, L920 e la gerarchia BOOST/VTUNE20; V2.1
conserva l'intero master V2.0 a sette fogli.

## Qualifiche ancora NON superate — blocchi reali

1. **[Issue #19, L501 VCO](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/19)**: Coilcraft **150-05J08L THT regolabile** candidato 165nH, range 137–193nH, Q min 114 a 50 MHz, SRF min 650 MHz **senza nucleo**, impronta diagonale con foro 0,8/pad 1,8mm proposta. Non è una qualifica RF. Mancano campione/fit, disponibilità MPN, tuning con BB204G, **KVCO, lock 270 canali, phase noise, deriva termica, Q caricato, EMI** e schermatura del boost. [Datasheet Coilcraft](https://www.coilcraft.com/getmedia/aaa9fcd2-5ef1-4ee2-b9b8-0ec1aa8c8db0/uni7.pdf). Lasciare issue aperta.
2. **[Issue #21, L920 boost](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/21)**: candidato Bourns **RLB0914-681KL** 680µH THT, footprint Ø2mm/drill1mm/pitch5mm. Irms tipica 0,49A, Isat tipica 0,9A, DCR max1,6Ω. Da validare stress, ripple, Ipk MC34063, saturazione termica, ingresso, EMC e spur sul VCO/IF; hardware e dimensioni pezzo. [Datasheet Bourns](https://www.bourns.com/docs/product-datasheets/rlb.pdf).
3. **Ingresso 13,8 V / protezione**: LM393 upstream ha **36V massimo** non protetto per sovratensioni sopra limite; reverse battery, transitori, load dump e rete Q802/gate-source non qualificati. **F701** Littelfuse 0251.500MXL e **D702** ST P6KE20CA hanno impronte THT candidate ma **senza** coordinamento sorgente/fusibile I²t/TVS energy e senza prova meccanica del pitch assiale 12,70 mm.
4. **Regolatori e sicurezza funzionale**: 7805/boost 20V LM317 non qualificati per correnti, termica, startup, brownout, PSRR/ripple e comportamento da guasto; **power-good/mute fail-closed non integrati**. Non attribuire sicurezza ai soli ERC0 o test ideali.
5. **Ricevitore completo assente**: preselector/front-end RF, mixer, IF, demodulazione AM/FM/USB/LSB, audio, squelch, controllo canali e front-panel completamente da progettare THT. Nessuna PCB completa, nessuna DRC, layout RF/IF o netlist↔PCB qualificata.
6. **Sola evidenza da software**: ngspice storico è modello surrogato/comportamentale; non sono eseguiti macro-modelli vendor completi o misure elettriche/RF su prototipi. Nessuna trasmissione ammessa.

## Issue, PR e GitHub Actions al checkpoint

- **Issue #22 (quota Actions)**: [CLOSED](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/22), 2.000/2.000 minuti consumati in precedenza; titolare ha sbloccato Actions. Runner ripartiti: gate V2.1/V2.2/V2.3 **eseguiti davvero** e passati. Diversi tentativi hanno incontrato **HTTP 500/504 Launchpad PPA** durante installazione KiCad; quelli falliti sono stati ritentati, non reinterpretati come test CAD. Non cambiare budget senza consenso.
- Nessuna **PR tecnica** rimasta aperta al merge della V2.3. La sola PR documentale [#25](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/25) era OPEN/DRAFT ed è stata **aggiornata con questo checkpoint**. Verificare live prima di usarla come fonte.
- Project SMD **mai modificato** in questa sessione. Non trasferire specifiche SMD.

## Prossima sequenza tecnica autonoma

Partire da `main` V2.3 e dagli issue aperti: prima progettare e verificare **protezione OVP del comparatore LM393 e network gate su fault, startup/brownout, power-good/mute fail-closed**, con datasheet originali e analisi fault; evitare falsi PWR_FLAG. Poi validare componenti magnetici/TVS con dimensionamento PVT, modelli vendor e criteri meccanici; proseguire verso front-end RF e mixer/IF THT, demodulazione/audio/controlli.
Ogni revisione reale: branch → nuovo file KiCad nativo → ERC e netlist pin-net in KiCad9 + test appropriati → PR/CI su **HEAD finale** → merge solo dopo gate verdi. Dopo merge aggiornare questo checkpoint.
Non creare una PCB dimostrativa o Gerber fintanto che l'intera radio RX/THT e safety non sono completati e riesaminati.

**VINCOLI ASSOLUTI: NO FAB / NO TX, NO BATTERIA / VEICOLO.**

## Ripresa in una nuova sessione

«Leggi `AGENTS.md` e `00_Gestione_Progetto/WORK_STATO_CORRENTE.md` da `main` del repo `jd3485/Superstar3900-THT-Evolution`. Verifica in tempo reale SHA main, PR, Actions e issue. Riparti dall'ultima revisione effettivamente MERGED, prosegui autonomamente con più revisioni KiCad THT, CI e merge solo dopo tutti i test; aggiorna checkpoint. NO FAB / NO TX; non toccare SMD.»
