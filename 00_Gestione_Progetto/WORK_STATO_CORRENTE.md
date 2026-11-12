# WORK_STATO_CORRENTE.md — checkpoint canonico Superstar 3900 THT Evolution

**Aggiornato:** 11 novembre 2026. **Repository esclusivo:** `jd3485/Superstar3900-THT-Evolution`.
**Branch autoritativo:** `main`. Questo file documenta l'ultima revisione verificata,
non sostituisce il controllo live di GitHub a ogni nuova sessione. Leggere
[AGENTS.md](../AGENTS.md) **e questo file da main all'inizio**; poi verificare
SHA di main, PR, issue, GitHub Actions e i rapporti CAD.
Non utilizzare la memoria delle chat o lo stato di branch draft come verità di main.

## 12 novembre 2026 — nuovo pilot KiCad9 V2.7 audio RX isolato in revisione

**Ultimo main verificato alla partenza:** commit `06c902240fdd0865a60a942ba551ccf9f1a6ed98` (PR #51 merged, checkpoint ADR-002). Nessuna PR aperta al bootstrap. **CAD integrato ancora MAIN V2.6** e NO PCB-FRONT.

**Lavoro in branch `cad/v27-rx-audio-lm386-tbd` NON integrato:** nuovo schematico nativo KiCad `04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch`, 9 piazzole THT (LM386N-1/NOPB TI PDIP-8 dichiarato ACTIVE ma al momento senza stock TI, 2 R, 6 C). Sottosistema indipendente RX audio, con input/5V/GND/speaker come interfacce da integrare **solo dopo review**; non è un master V2.7 completato. `03_Verifiche/V2.7/verify_audio_draft_native.py` impone ERC e netlist KiCad9 reali, invocati dalla CI FULL. Vedi `03_Verifiche/V2.7/RAPPORTO_AUDIO_RX_THT_LM386_PILOT.md`.

**Attenzione:** alimentare audio dalla 5 V RF/PLL senza verifica può degradare rumore e sovraccaricare il 7805: pilot non collegato al master, nessuna trasmissione. Le caratteristiche di altoparlante, guadagno, dissipazione, temp. 0..70°C, indice di fabbricabilità e frontale non sono approvate. U401/L501 e sicurezza #27 restano bloccanti per i rispettivi circuiti. Gate BOM finale obbligatorio. **NO FAB / NO TX / NO BATTERIA/VEICOLO.** Integrare solo dopo required CI gate verde sullo SHA finale del branch.

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
