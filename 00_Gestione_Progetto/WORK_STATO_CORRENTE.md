# WORK_STATO_CORRENTE.md — checkpoint canonico Superstar 3900 THT Evolution

**Aggiornato:** 11 novembre 2026. **Repository esclusivo:** `jd3485/Superstar3900-THT-Evolution`.
**Branch autoritativo:** `main`. Questo file documenta l'ultima revisione verificata,
non sostituisce il controllo live di GitHub a ogni nuova sessione. Leggere
[AGENTS.md](../AGENTS.md) **e questo file da main all'inizio**; poi verificare
SHA di main, PR, issue, GitHub Actions e i rapporti CAD.
Non utilizzare la memoria delle chat o lo stato di branch draft come verità di main.


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
