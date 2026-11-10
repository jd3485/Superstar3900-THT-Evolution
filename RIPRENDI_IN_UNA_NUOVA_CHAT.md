# V0.6 INTEGRATA IN MAIN — CI software 157/157 PASS, run 42823693863; CI ngspice PASS (esecuzione modelli), run 42823693786; PR #2 integrata. RF hardware NON qualificata, NO FAB / NO TX.

# CONTINUITÀ ATTUALE — V0.6 (10/11/2026)

**Repository privata e indipendente:** `jd3485/Superstar3900-THT-Evolution`, fonte di verità `main`. Al riavvio controllare HEAD, PR, tag e CI, poi questo handoff, README, protocollo, stato, decisioni e ultimo rapporto. **NON usare il progetto SMD come dipendenza.**

**Novità V0.6:** veri transienti **ngspice**. VCO V0.5 dichiarato **RF FAIL**: VTUNE 3,2/5/7,5 V dà 38,306/38,319/38,350 MHz e diodi avanti ~0,5V. Un primo esploratore generava falsi positivi usando condizioni iniziali UIC inadatte: rilevato e corretto con prove di alimentazione **0→5V in 100ns senza .ic/uic**.

**Candidata B soltanto per sviluppi successivi:** Q501/Q502 2N3904 THT, D501 doppio BB204G TO-92, L501=166nH candidata da tarare, C504=470pF, R503=1,2kΩ, alimentazione oscillatore5V, VTUNE 8..15V. Modello ngspice con avvio alimentazione: 5 punti monotoni 36,048–39,196MHz, inversa varicap rispettata, VR max17,75V. Non validato con SPICE ufficiale dei produttori né misure; **8–15V VTUNE comporta un nuovo vincolo di generazione tensione maggiore di 13,8V**.

**File indispensabili:** `01_Specifiche/V0.6/VCO_SIMULAZIONE_E_CORREZIONI_V0.6.md`, `03_Verifiche/V0.6/RAPPORTO_TECNICO_V0.6.md`, `03_Verifiche/V0.6/MISURE_SPICE_V0.6.json`, `03_Verifiche/V0.6/VCO_COLPITTS_CANDIDATE_B_V0.6.cir`, `03_Verifiche/V0.6/run_selected_v06.py`, `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`.

**Non fatto:** schematico KiCad VCO completo, KiCad ERC/DRC, simulazione PLL chiuso e rumore di fase, driver VTUNE/circuito di generazione fino a15V, sourcing affidabile BB204G, tutte le misure reali, PCB e TX. **NO FAB / NO TX.**

**Prossima V0.7:** consolidare VCO con modelli vendor e tolleranze/taratura, correggere se necessario la gamma VTUNE, progettare alimentazione/driver THT e circuito controllo PLL, verificare KiCad nativo e preparare RF front-end quando il sintetizzatore è affidabile.

**GitHub:** ogni «continua» modifica solo nuove parti e registri, mantiene vecchie baseline/snapshot, CI e storia. Nessuno ZIP da ricompilare; sull'ultimo main verificare tutti i test, non leggere una vecchia email FAIL come stato corrente.

---

# CI V0.5 verificata: 136/136 controlli Python PASS su main, run 42815442825 (PR #1 integrata). SPICE ed ERC/DRC ancora NON ESEGUITI. NO FAB / NO TX.

# CONTINUITÀ ATTUALE — V0.5 (10 novembre 2026)

**Repository GitHub privata autonoma:** `jd3485/Superstar3900-THT-Evolution`. **Fonte di verità:** HEAD di `main`, non memoria di chat o progetto SMD. All'inizio di ogni chat controllare main, tag, PR, CI; leggere questo handoff, README, protocollo, stato, registro decisioni e ultimo rapporto V0.5.

Requisiti immutati: CB tradizionale 100% THT, 270 posizioni RX su A-F, AM/FM/USB/LSB/CW, accordatore manuale con bypass, PCBWay fabbrica solo PCB nude, saldatura interna; esclusi DSP evoluto, PLL RF moderno, Dual Watch, CTCSS/DCS, VOX, tuner automatico. **NO FAB / NO TX.**

**Progressione:** V0.2 tabella 270 RX e PLL math; V0.3 U401 ML145151YP DIP28 + U402 TC74AC74P DIP14 pin-net e quarzo 10.240MHz; V0.4 primo file KiCad nativo solo prescaler (NON verificato in KiCad), studio un varicap; **V0.5 primo circuito SPICE candidato Colpitts con Q501/Q502 2N3904 TO-92, doppio BB204G TO-92 parallelo e buffer analogico**. L=150nH e Cfixed_eff≈61pF ASSUNTA, tuning nominale ≈3,13–6,95V; modello varicap NON vendor. Correzione filtro V0.4 -1,73dB a 5kHz, confronto passivo due poli -41,43dB che NON è certificato stabile in loop; driver LM358N a 12V candidato ma non progettato.

**File da aprire:** `01_Specifiche/V0.5/VCO_COLPITTS_THT_V0.5.md`, `03_Verifiche/V0.5/VCO_COLPITTS_CANDIDATE_V0.5.cir`, `02_Piano_Frequenze/V0.5/vco_dualvar_model_v05.py`, `08_Firmware_Prototipi/V0.5/rx_controller_reference_v05.py`, `03_Verifiche/V0.5/RAPPORTO_TECNICO_V0.5.md`.

**Prossima V0.6:** eseguire SPICE vero, registrare convergenza/frequenza/swing, correggere startup e componente/fit quando necessario, modellare filtro/phase margin, cercare varicap THT realmente acquistabile, poi KiCad CAD completo. Il PIC PDIP40 resta un candidato; modello Python NON è firmware XC8. NON affermare SPICE o ERC/DRC eseguiti senza report veri.

**Versionamento:** aggiornare solo file nuovi e modificati, non rigenerare ZIP. Mantenere snapshot delle configurazioni V0.1..V0.5, CI regressiva e storia; **non modificare né sincronizzare progetto SMD**.

---

# Esito CI confermato V0.4: 102/102 test software PASS (4 suite), run 42810567923; rimangono NON ESEGUITI KiCad ERC/DRC, SPICE e hardware.

# CONTINUITÀ ATTUALE — V0.4 (10 novembre 2026)

**Repository autonoma privata:** `jd3485/Superstar3900-THT-Evolution`. Verificare **HEAD di main**, PR, tag, CI; leggere README, questo handoff, protocollo continuità, registro decisioni e ultimo rapporto tecnico V0.4. **Mai copiare automaticamente parti dalla repository SMD.**

Stato cumulativo: V0.2 = 270 RX e calcolo PLL integer-N; V0.3 = pin-net U401 Lansdale DIP28 + U402 Toshiba DIP14, quarzo THT 10,24MHz; **V0.4 = modello tank VCO 36,31–39MHz con BB204G TO-92 storico (non validato), filtro anello tipo B analitico, scelta di controller PIC18F47Q43-I/P PDIP40 candidata, e primo sottoschema KiCad nativo GENERATO solo per U402 + 4 connettori** (`04_KiCad/V0.4/`). **Nessun ERC/DRC KiCad nativo, SPICE, PCB, VCO completo, hardware o autorizzazione TX.**

Leggere:
`01_Specifiche/V0.4/VCO_PLL_CONTROLLO_V0.4.md`,
`04_KiCad/V0.4/README.md`,
`03_Verifiche/V0.4/RAPPORTO_TECNICO_V0.4.md`,
`00_Gestione_Progetto/REGISTRO_RISCHI_V0.4.csv`.
CI V0.4 aggiunge 34 test matematici/statici alle suite 12+24+32 precedenti: verificare l'esito della run prima di citare PASS.

**Prossima V0.5:** concretizzare oscillatore Q501/varicap D501 ed eventuale alternativa fornibile, buffer/limitatori, filtro loop con modello dinamico e stabilità, MCU reale e controllo N/powergood/lock. Aprire schematico KiCad in app ed eseguire ERC se disponibile; nessun Gerber prima del rilascio.

Metodo fisso: a ogni «continua» aggiornare solo file nuovi/modificati sul `main`, mantenere cronologia, rapporti, snapshot configurazioni passate e handoff. Progetto 100% THT, analogico, accordatore manuale, PCBWay schede nude, saldatura interna. **NO FAB / NO TX.**

---

# RIPRESA AGGIORNATA — V0.3 (10 novembre 2026)

**Repository privata autonoma:** `jd3485/Superstar3900-THT-Evolution`. **Fonte di verità:** HEAD `main`, non i tag precedenti. Aprire README, protocollo `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, questo file, stato, decisioni e ultimo rapporto tecnico. Controllare commit, PR, tag se presenti e CI.

**V0.3 integra:**
- Piano 270 RX/30 ALFA completo da V0.2, IF1=10,695 MHz candidato, LO=36,310–39,000 MHz, fPFD=5 kHz, prescaler /2 e 14 bit N=3631–3900.
- **Primo nucleo pin-to-net**: U401 ML145151YP DIP28 (alternativa Lansdale al Motorola obsoleto), U402 TC74AC74P(F) DIP14, quarzo Citizen 10,240 MHz THT HC49 18pF candidato, condensatori 22pF e decoupling iniziale, predisposizione N bus e reset; 42 pin documentati.
- **Problema approvvigionamento:** U401 solo da confermare via richiesta al costruttore, nessuna disponibilità in piccole quantità garantita. **Precisione SSB:** quarzo Citizen ±30ppm + stabilità ±50ppm, non approvato per uso SSB definitivo.
- **No schema KiCad nativo/ ERC/DRC/SPICE/hardware**. Codice e tests Python sono solo verifiche aritmetiche/statiche. **NO FAB / NO TX**.

**Leggere prima di continuare:** `01_Specifiche/V0.3/PLL_CORE_CIRCUITO_V0.3.md`, `04_KiCad/V0.3/README.md`, `03_Verifiche/V0.3/RAPPORTO_TECNICO_V0.3.md`, BOM V0.3, registro rischi e decisioni.

**Prossima V0.4:** confermare forniture, specificare VCO analogico, interfaccia LO CMOS e filtro di anello compensato con dati Kvco; progettare selezione parallela N e reset/lock hardware, creare schemi KiCad nativi e svolgere verifiche vere. Solo THT sulle schede, accordatore manuale, PCBWay fabbrica schede nude, saldatura interna. Ogni revisione cambia solo file pertinenti e conserva versioni e storico. Se è presente un workflow CI controllarne l'esito relativo all'ultimo commit.

---

# ISTRUZIONI ATTUALI — V0.2 (10 novembre 2026)

**Repo privata indipendente `jd3485/Superstar3900-THT-Evolution`, branch `main`.** All'inizio di ogni chat verificare HEAD, eventuali tag/PR/CI, poi README, questo file, protocollo, registro decisioni, stato e ultimo rapporto. Non usare la versione SMD come fonte né dipendere da memoria della conversazione.

**Revisione integrata più recente secondo queste note: V0.2.** Piano di 270 posizioni RX, 30 ALFA, CH9 prioritario 27.065 MHz. IF1=10.695 MHz candidata, LO1 36.310–39.000 MHz, riferimento 10.240 MHz /2048 = 5 kHz, prescaler fisso /2, parola N a 14 bit 3631..3900. Due opzioni PLL THT documentate, nessuna approvata; MC145151P2 è legacy, disponibilità da verificare. Test: 24/24 V0.2 e 12/12 regressivi V0.1, solo software.

**Aprire:** `02_Piano_Frequenze/V0.2/PIANO_THT_PLL_V0.2.md`, `03_Verifiche/V0.2/RAPPORTO_TECNICO_V0.2.md`, `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, `00_Gestione_Progetto/STATO_PROGETTO.md`.

**Prossima V0.3:** verificare disponibilità componenti e timing di contatori/PLL, scegliere soluzione elettrica THT e sviluppare schema candidato. Ogni revisione modifica solo i file necessari su GitHub, preserva storico e aggiorna queste istruzioni. **NO FAB / NO TX**, niente DSP evoluto, VOX, CTCSS/DCS, Dual Watch, PLL RF moderno; accordatore manuale con BYPASS e PCBWay solo PCB nude, saldatura interna.

---

# Riprendi Superstar 3900 THT Evolution in una nuova chat

## Regola permanente
La fonte di verità è la repository privata autonoma `jd3485/Superstar3900-THT-Evolution`, branch `main`. **Non utilizzare** come fonte progettuale né aggiornare l'altra repository SMD. Non affidarsi alla memoria della conversazione.

## Procedura obbligatoria
1. Aprire la repository THT corretta; leggere dall'alto `README.md`, questo file e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`.
2. Controllare HEAD `main`, cronologia, tag, eventuali PR non integrate e risultati CI; scegliere la revisione integrata più recente, senza presumere che sia ancora V0.1.
3. Leggere il rapporto tecnico e lo stato corrente, il registro delle decisioni, i rischi e il piano dei moduli.
4. Sviluppare il **prossimo sottosistema reale**, con schemi/circuiti quando maturi, scelte THT documentate, BOM, interfacce e verifiche realmente eseguibili.
5. Dichiarare chiaramente PASS / FAIL / SKIP / NON ESEGUITO. Non attribuire al progetto simulazioni, ERC/DRC, misure o autorizzazioni non documentate.
6. Se la revisione è coerente, documentata e i test dichiarati sono controllati, integrarla in `main` (branch/PR temporanei ammessi). Conservare storia, decisioni e istruzioni di ripresa aggiornate.
7. Non autorizzare ordine PCB, alimentazione del prototipo o emissione TX senza i gate specifici pertinenti; gli interblocchi TX rimangono disabilitati fino a collaudi e verifiche normative.

## Fotografia iniziale del 10/11/2026 — V0.1
Progetto indipendente, 100% THT sulle PCB, montaggio manuale, RF prevalentemente analogica, PLL **tradizionale** candidato, accordatore manuale con BYPASS. Esclusi DSP avanzato, PLL moderno integrato, Dual Watch, CTCSS/DCS, VOX, accordatore automatico. Bande A–F e 270 posizioni RX, AM/FM/USB/LSB/CW; CH9 e ALFA fisici. **Zero componenti scelti definitivamente, zero schematici nativi completi, zero test hardware. NO FAB / NO TX.**

**Prossimo lavoro V0.2:** piano frequenze a 270 posizioni, scelte di IF e fattibilità sintetizzatore tradizionale THT, con calcoli/test riproducibili e valutazione della reperibilità dei componenti.

## Testo minimo da inserire in una nuova chat
> Riprendi il progetto indipendente `Superstar3900-THT-Evolution` dalla sua repository GitHub privata. Leggi `README.md`, `RIPRENDI_IN_UNA_NUOVA_CHAT.md`, `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`, verifica l'ultimo `main`/tag/PR/CI, poi l'ultimo rapporto tecnico. Prosegui dalla revisione successiva con elettronica THT, accordatore manuale, sviluppo modulare e test reali. Mantieni storico, NO FAB / NO TX fino ai gate di rilascio.
