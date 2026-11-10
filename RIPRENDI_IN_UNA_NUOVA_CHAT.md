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
