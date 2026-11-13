# Handoff operativo aggiornato — Superstar 3900 THT Evolution; baseline storica V0.9 preservata, 13 novembre 2026

> **STATO ATTUALE:** non usare le sezioni storiche sottostanti come ultima revisione; iniziare da [AGENTS.md](AGENTS.md) e dal [checkpoint main](00_Gestione_Progetto/WORK_STATO_CORRENTE.md), poi verificare HEAD e CI live.
>
> **Ultima revisione tecnica verificata:** [PR #102](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/102) MERGED `1582ca3e905a10e4c299f8617616dddb0121aa29`, CI [#43474856530](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43474856530) FAST/FULL/required **3/3 green** sul final head `10e3e1447d624716b71fbf57159f1b0e07a8fa26`, 111 comandi legacy. Il test nativo a 50/25/12,5ns sulla catena IF455 tank→KSP10 candidate→AM455 generic diode passa il criterio **<2%** sulle otto misure nel dimezzamento finale.
>
> **Decisione tecnica aperta:** l'attuale follower Q1701 da banco su KiCad 9 standalone è **respinto** come adattatore da integrare perché nel modello generico riduce AFpp a circa **3,14% e 7,29%** del percorso diretto (input 0,5/2 V). Servono studio di bias/input loading, OEM model e rumore, non semplice modifica di schema per fabbricazione.
>
> **Architettura vincolante:** due PCB 100% THT MAIN + FRONT con S-meter analogico, ADR-001/002; master MAIN V2.6 sette fogli/138 riferimenti intatto, **PCB fisiche/routing 0%**, circa 20% stima progetto. Componenti finali OEM attivamente prodotti, **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**. Rami protetti e PR + required CI obbligatorie; l'utente non vuole limitare verifiche per il costo Actions.
>
> **Priorità successiva:** progettare e confrontare interfacce IF455 THT ad alta impedenza di ingresso e non lineari con filtro/diodo; qualifica OEM/PVT/noise e solo poi KiCad gerarchico della radio.

---

# Handoff THT — aggiornamento verificato 11 novembre 2026

**Baseline storica V0.9 preservata** senza modifiche a modelli, test e revisioni precedenti; le versioni KiCad successive aggiungono solo modifiche verificate. NO FAB / NO TX.

**Fonte canonica al prossimo avvio:** [WORK_STATO_CORRENTE.md](00_Gestione_Progetto/WORK_STATO_CORRENTE.md) su `main` + [AGENTS.md](AGENTS.md). Confermare sempre le evidenze live.

**Ultima revisione CAD EFFETTIVAMENTE MERGED:** **V2.3, PR #26**, main commit tecnico `faa146e2bdd12b13df1cbb4d20e67196ad5098b9`. Nella stessa sessione integrate V2.1 PR20 `b7b475e05b7279f2944fbfa6ea50d38680f874c4` e V2.2 PR24 `30328084e72339f3909e618ff37162e8f31827d4`. KiCad9 V2.3 native [run 43012377058](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43012377058) PASS ERC0/72 partizioni/7 SVG/129 riferimenti con footprint campo compilato. **20/20 workflow PR final head V2.3 PASS.**

**NON È UNA PCB COMPLETA**: resta un sottosistema RX PLL; l'induttore L501 Coilcraft 150-05J08L è candidato THT NON qualificato RF, come L920 Bourns (termica e EMI non verificate), F701/D702 e catena OVP oltre 36V LM393. Sono assenti powergood/mute fail-closed, RF/IF/audio/controller, PCB, DRC, Gerber, hardware. Issue #19/#21 restano aperte; #22 quota Actions risolto/chiuso, CI ora utilizzabile. NO FAB / NO TX, non collegare batteria/veicolo.

**Prossimo intervento tecnico:** stress e protezione upstream LM393 e gate durante transitori/reverse/overvoltage, power-good/mute fail-closed, poi sicurezza alimentazioni/valori MPN e RF front end; modifiche native KiCad + verifiche gate reali PR prima di merge.

---

# V2.0 — sette fogli KiCad9: alimentazione VTUNE20 THT fisicamente integrata (baseline V0.9 preservata)
- **Novità CAD reale:** master `04_KiCad/V2.0/PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch`, settimo child `POWER20_VTUNE_BOOST_LDO_V2.0.kicad_sch`. U911 **ST MC34063ABN PDIP8** con boost candidata ~27,95V, **L920 Bourns RLB0914-681KL 680µH THT**, U912 **onsemi LM317T TO220** regola ~20,02V ideali, C/R filtro dopo LM317, `VANA20_FILT` collegata *tramite gerarchia reale* al pad **U803 pin8** del filtro PLL. D921/D922 scarica condensatori LDO, tab U912 è VOUT e non GND; tutte le reti V1.9 RX/5V/PLL/VCO restano inalterate.
- **Evidenza KiCad9 concreta:** [run 42986863110](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42986863110) ha completato **ERC0**, **72 gruppi netlist V2.0 rispetto a 64 V1.9**, tutte le precedenti partizioni-pin identiche, 7 pagine SVG e generatore 9 file PASS. Lo script DC ha inizialmente fermato l'esecuzione per una classificazione del margine corrente troppo rigida; la correzione distingue condizioni **vicine** al limite teorico da vere violazioni. I CI del commit finale restano da concludere.
- **Nessuna PCB:** il progetto reale della scheda THT, il routing, DRC e prototipo sono **NON INIZIATI**. [Piano PCB RF THT V2.0](00_Gestione_Progetto/PIANO_PCB_RF_THT_V2.0.md) rende obbligatori MPN/footprint/ritorni RF, verifica boost EMI e revisione indipendente prima di qualsiasi Gerber.
- **Limitazioni / NO FAB / NO TX:** nessun modello vendor MC34063/LM317, nessuna misura hardware di 20V, footprint **L920 non selezionato**, condensatori senza MPN/esr, boost spur e accoppiamento PLL/IF ignoti, 13V8 protetto non qualificato su batteria/veicolo, F701/D702 e L501 footprint mancanti, powergood/mute, RF/IF/audio/controller/PCB non completati. Non alimentare da veicolo/batteria.
- **Rischio EDA risolto nella V2.0 solo:** riferimento legacy VCO `C500B` (non standard) normalizzato in `C509` tramite generatore riproducibile. Nessuna modifica a piedini, connessioni o files storici; il confronto netlist V1.9→V2.0 applica esplicitamente questa sola rinumerazione. 

---

# V1.9 — supervisore OVP THT con Schottky D804/D805 e R1001 1 W (baseline elettrica V0.9 preservata)
- **CAD KiCad9 reale**: `04_KiCad/V1.9/PLL_RX_HIERARCHICAL_MASTER_V1.9.kicad_sch` contiene sei fogli nativi. D804 1N5819 **A2 da FUSED_RAW / K1 a OVP_CTL_VCC** alimenta U801 LM393 pin8, R1001 pin1 e R1002 pin1. D805 1N5819 **A2 GND / K1 OVP_CTL_VCC** è un clamp candidato. R1001 sostituita con Vishay PR01000103301JR500 3,3 kΩ/1 W assiale, footprint 9x3,2mm pitch 12,7mm.
- [**KiCad9 CI run 42971502918**](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42971502918): **ERC 0**, **64 gruppi elettrici**, conservate TUTTE le partizioni pin V1.8 63 gruppi ad eccezione dei tre pin U801/8 R1001/1 R1002/1 spostati intenzionalmente sul nuovo rail, SVG sei pagine, generazione bit-per-bit e screening DC 21 casi PASS. Nessun vendor SPICE e nessun test fisico; 36 V ingresso e Vf 0,25–0,60 V ipotizzata portano R1001 a ~0,328–0,335 W.
- **LIMITI CRITICI**: l'alimentazione del controllo è ora bloccata da un diodo contro inversione diretta ma la polarità inversa di veicolo NON è qualificata (leakage Schottky, Q802/gate, massimi dei pin); LM393 max 36 V a monte di Q801 ancora esposto alle sovratensioni; fusibile/TVS/termica non validati, 20V VTUNE e powergood non integrati, nessuna PCB o hardware RF. Sorgenti V1.8 e progetto SMD invariati. **NON collegare a batteria/veicolo; NO FAB / NO TX.**

---

# V1.8 — OVP high-side THT IRF9540N/LM393/TL431B nel master KiCad (baseline elettrica V0.9 preservata)
- **Circuito nativo realmente modificato:** `04_KiCad/V1.8/PLL_RX_HIERARCHICAL_MASTER_V1.8.kicad_sch` (6 pagine): Q801 P-MOSFET TO-220 inserito **in serie tra F701 e D701**; U801 LM393N PDIP8 + U802 TL431BCLP TO-92 + Q802 2N3904, D803 zener gate e R1001–R1010 gestiscono soglia e isteresi. Schemi V1.7 e SMD invariati.
- [**KiCad9 + ngspice CI 42966236280**](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42966236280) **PASS**: ERC nativo **0 violazioni**, **63 gruppi netlist** (62 reti collegate e 1 U801 pin7 NC), **54 reti V1.7 mantenute** eccetto spostamento voluto D701 pin2, libreria THT e 6 pagine SVG, generator bit-per-bit, analisi 128 combinazioni di tolleranze e **ngspice comportamentale**.
- Nel solo modello **ideale** ngspice: ingresso 13,8V → uscita switch 13,78V; sovratensione 19V → circa 0V; riduzione a 15,5V → resta OFF, 14V → ritorna ON. Soglia indicativa da calcoli ~16,42V trip e ~15,14V reclose; **NON sono modelli vendor** né test hardware.
- **NESSUNA QUALIFICA DI SICUREZZA/RF**: LM393 alimentato sul bus FUSED_RAW a monte del MOSFET con **massimo VCC 36V**, non protegge da qualsiasi sovratensione continua/automotive; fuse F701 e TVS D702 non coordinati, footprint non scelti, termica/inrush/EMI, rail 20V VTUNE, powergood/mute e PCB ancora mancanti. **NON collegare a batteria/veicolo. NO FAB / NO TX.**

---

# V1.7 — ingresso THT con fusibile, Schottky e TVS nel master a 6 fogli (baseline elettrica V0.9 preservata)
- **KiCad9 CAD nativo:** `04_KiCad/V1.7/PLL_RX_HIERARCHICAL_MASTER_V1.7.kicad_sch` include nuovo child J701 `+13V8_RAW` → F701 Littelfuse 0251.500MXL 500mA → D701 Vishay 1N5819 A2/K1 → `+13V8_PROTECTED` al regolatore U601; D702 ST P6KE20CA bidirezionale tra FUSED_RAW e GND. Rimossi vecchi J601 bypass e PWR601 ERC-only dal solo child V1.7, fonti V1.6 intatte.
- [**KiCad native CI 42921509495**](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42921509495): **ERC 0**, **54 reti** in V1.7 vs **52** di V1.6, tutte le partizioni-pin conservate eccetto J601 rimosso, esportazione SVG 6 pagine e libreria simboli PASS. `genera_gerarchia_input_v17.js --check` verifica la migrazione bit-per-bit dei cinque file CAD derivati da V1.6; i due originali nuovi (foglio protezione e libreria) restano editabili.
- **Non qualificato per sicurezza:** il TVS limita solo i transitori specificati, **non** scollega una sovratensione prolungata; fusibile 500mA e I²t non coordinati, fault-current e vehicle/load-dump ignoti, footprint F701/D702 mancanti, J701 solo laboratorio. V1.5 aveva 4/12 scenari termici analitici a rischio. Senza 20V VTUNE, power-good/mute, prove hardware o PCB.
- **NO FAB / NO TX**. Non collegare a veicolo o batteria; progetto esclusivamente THT, SMD invariata.

---

# V1.6 — alimentazione THT 5V connessa nel master KiCad a cinque fogli (baseline elettrica V0.9 preservata)
- `04_KiCad/V1.6/PLL_RX_HIERARCHICAL_MASTER_V1.6.kicad_sch`: root KiCad9 + 4 child reali; U601 L7805CV alimenta elettricamente tre rami isolati R611/R612/R613 per PLL U401/U402, VCO Colpitts e buffer LO U520. `GND` unita via wire root.
- [KiCad9 run 42918087055](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42918087055): **ERC nativo 0 violazioni**, netlist **52 reti** = 50 originali V1.4 + 6 V1.5 − 4 unioni intenzionali; tutte le partizioni dei pin conservate, SVG 5 pagine, rigenerazione bit-per-bit PASS. Corretto un `PWR_FLAG` GND solo-ERC ridondante senza waivers.
- **NON QUALIFICATA** la regolazione 5V in carico, correnti, termica (4/12 scenari analitici a rischio nella V1.5), protezione input 13.8V, boost 20V, powergood/mute e PLL/VCO RF. Questa è una gerarchia **parziale RX**, non una PCB né una radio completa. **NO FAB / NO TX**.

---

# V1.5 CAD 5V THT (baseline elettrica V0.9 preservata) — nuovo sottoblocco AUTONOMO verificato con KiCad 9, NON integrato nel master V1.4
- `04_KiCad/V1.5/THT_5V_POWER_DISTRIBUTION_V1.5.kicad_sch` con U601 L7805CV TO-220, D601 anti-scarica, condensatori e tre rami RC per PLL/VCO/buffer.
- [GitHub KiCad run 42909924401](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42909924401): **ERC 0 violazioni**, netlist **6/6 reti PASS**, rigenerazione deterministic, export simboli/SVG e screening termico.
- Budget puramente analitico: 12 scenari VIN/carico, **4 segnalati termicamente a rischio** con ipotesi 50°C ambiente e RθJA 50°C/W. Né assorbimenti reali né dissipatore sono definiti. NON è una qualifica termica o RF.
- La protezione 13,8 V a monte NON è progettata e la sezione 20 V VTUNE NON è integrata. File V1.4 preservati. **NO FAB / NO TX**.

# V1.4 PASS CAD (baseline elettrica V0.9 invariata) — master RX PLL GERARCHICO A 4 FOGLI: 04_KiCad/V1.4/PLL_RX_HIERARCHICAL_MASTER_V1.4.kicad_sch, foglio VCO Colpitts B e condizionatore LO SN74AC14N THT integrati. KiCad9 run 42892782874 ERC0, 50 reti, 33 legacy preservate, VTUNE→D501/2 e U520→U402/3 PASS. ngspice input analogico buffer run42892783098 4 punti 8–15V, min reverse 0.376V. VCO/AC14 non RF qualificati, L501 166nH MPN/footprint irrisolto, supply esterne, nessun PCB. NO FAB / NO TX.

# V1.3 PASS — baseline V0.9 preservata; master gerarchico RX PLL in 04_KiCad/V1.3/ con root e due child THT. KiCad9 run 42884939754: ERC 0 violazioni, 3 pagine SVG, equivalenza integrale pin-net 33/33 rispetto a V1.2. U401 PDout pin4 ↔ R901 pin1; GND tra child. È solo RX PLL parziale, VCO/PCB assenti. NO FAB / NO TX.

# V0.9 baseline elettrica / V1.1 CAD-02 branch feature/v1.1-cad02-pll-core: schematico KiCad nucleo PLL U401/U402, quarzo, netlist gate, CON VALIDAZIONE CAD-02 NATIVA: KiCad9 ERC 0 violazioni, netlist 22 reti PASS (run 42870145756), ma non PLL completo né PCB. Leggere rapporto 03_Verifiche/V1.1/RAPPORTO_CAD02_V1.1.md. Non merge senza verifica CI, NO FAB / NO TX.

# CAD-FIRST V1.0 — confermata KiCad 9 native ERC PASS 0 violazioni e 8 reti validate da netlist, run 42858721761; 272 controlli statici PASS run 42858721619; stato elettrico V0.9, schema PCB master ancora NON ESEGUITO. **NO FAB / NO TX**.

# DAL 10 NOV 2026: CAD-FIRST V1.0 PILOT — priorità a schemi elettrici `.kicad_sch` / PCB `.kicad_pcb` veri, senza rinunciare a test, simulazioni, firmware e BOM. **Fonte elettrica V0.9**, corrente sviluppo CAD V1.0. Leggere `00_Gestione_Progetto/METODO_CAD_FIRST_V1.0.md`; primo studio in `04_KiCad/V1.0/`, con R90122k C901100n ancora NON QUALIFICATI e non coincidenti con filtro V0.9. Verificare GitHub Actions CAD native per ERC prima di dichiarare successo. PR #5 CAD storico separato **non integrare se ERC FAIL/merge conflict**. Nessuna fabbricazione: NO FAB / NO TX.

---

# V0.9 INTEGRATA IN MAIN — PR #6, 254/254 Python PASS e 4 workflow ngspice SUCCESS; ultimi run 42852994951, 42852997335, 42852994921, 42852994798, 42852995032. Modelli surrogati, NO FAB / NO TX. Una PR CAD #5 separata non è approvata.

# CONTINUITÀ ATTUALE — V0.9 (10 novembre 2026)

**Repository autonoma THT:** `jd3485/Superstar3900-THT-Evolution`; fonte di verità HEAD `main`, controllare PR e Actions e rileggere protocollo/README/Stato/Decisioni/rapporto V0.9. Non toccare il repository SMD. Ogni versione aggiunge solo file nuovi o modificati, nessuna rigenerazione ZIP o azzeramento storico.

**Radio progettata:** CB stile Superstar 3900 interamente THT; 270 posizioni RX (A-F, CH ALFA), AM/FM/USB/LSB/CW, PLL tradizionale ML145151YP candidato, accordatore manuale/bypass, PCBWay solo scheda nuda, montaggio interno; esclusi DSP evoluto, PLL moderno, VOX, CTCSS/DCS, Dual Watch. **NO FAB / NO TX**.

**V0.6:** VCO candidata B Q501/Q502 2N3904 TO92, BB204G TO92 legacy, L166nH, C470pF, VCC5V, richiede VTUNE8–15V per LO36,310–39MHz nel modello; non vendor/hardware qualificato.

**V0.7/V0.8:** sorgente candidato MC34063ABN DIP8 boost27V, LM317T TO220 regolato20V e LM358N PDIP8 x4 su `PD_FILTER` verso VTUNE. Modelli switching e opamp IDEALI, non real vendor/PLL; nessun powergood fisico, KiCad o noise phase margin.

**V0.9:** `ML145151YP` **pin4 PDout con tre stati logici distinti**, ovvero tre stati: positivo, negativo, alta impedenza a coincidenza. `PD_FILTER` V0.8 necessita filtro THT di accumulo per queste transizioni. **R90110k o47k / C9011µF** come sola prova iniziale; 6 ngspice realmente eseguiti su surrogate ± digitali, non ML145151; passi da2,5V in UP/DOWN/HOLD. R902100Meg **solo leakage fittizio**, non BOM d'acquisto. Non c'è loop in retroazione, non sono note stabilità, fase e tempi di aggancio. Dati nel rapporto `03_Verifiche/V0.9/RAPPORTO_TECNICO_V0.9.md` e `MISURE_TRISTATE_V0.9.json`; pin-net `04_KiCad/V0.9/PLL_PDOUT_FILTRI_CANDIDATI_V0.9.csv`. Controllare CI nuova V0.9 prima di affermare PASS.

**Prossima V1.0:** filtro PLL stabilizzato realmente con Kphi/Kvco/PLL completo, test continuità lock e powergood-mute HW, progetto KiCad verificabile; modulo analogico RF e architettura alta tensione restano in sviluppo. **Niente PCB fabbricabile, ERC DRC NOT_RUN, nessuna TX.**

---

# V0.8 INTEGRATA IN MAIN — 226/226 test software PASS; 3 simulazioni ngspice workflow PASS (solo modelli non vendor). PR #4 MERGED. CI su main 42843501500, 42843501265, 42843501213, 42843501144. **NO FAB / NO TX**.

# CONTINUITÀ ATTUALE — V0.8 (10 novembre 2026)

**Fonte di verità:** repository privata indipendente `jd3485/Superstar3900-THT-Evolution`, HEAD branch `main`, GitHub Actions, PR e README. Rileggere `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md` e rapporto tecnico **V0.8**. Non copiare automaticamente file della versione SMD, non rigenerare ZIP e non cancellare revisioni.

**Missione:** reinterpretazione radio Superstar3900 analogica 100% THT, 270 posizioni RX, AM/FM/USB/LSB/CW, PLL tradizionale, accordatore antenna manuale, PCBWay solo PCB nude, montaggio interno; escluse le funzioni avanzate precedentemente rimosse. **NO FAB / NO TX**.

**V0.6:** VCO Colpitts candidata B, Q501/Q502 2N3904 TO92 e D501 BB204G TO92 legacy, L166nH C470pF VCC5V. In *modello ngspice non vendor* VTUNE8–15V -> LO 36,048–39,196MHz in cinque punti e varicap inversi. Non misura RF o circuito qualificato.

**V0.7:** booster solo comportamento ideale target24V + LM317~18,3V; dimostrazione che Rsc1Ω e carico LM317 non garantiscono margini. Schemi non completi.

**V0.8:** corregge studio alimentazione: MC34063ABN DIP8 target **27V**, Rsc0,47Ω, L470µH Bourns RLB0914-471KL THT (Irms0,56A typ, Isat1A typ, NON schermata), diodo **Vishay SB160-E3/54** Schottky DO41 60V; LM317T TO220 target **20,022V** con R240Ω/3,57kΩ e **precarico2,4kΩ/0,5W**; LM358N PDIP8 non invertente gain4 da PD_FILTER a VTUNE. `PD_FILTER` non ancora derivato da reale phase detector U401, filtro PLL e powergood/mute fisici non progettati. 19 pin su 3 IC, 22 passivi e BOM25 componenti candidati.

**Simulazione V0.8:** ngspice sul solo modello **comportamentale ideale** del driver, con R/C reali ed uscita clip artificiale. 6 transienti: input PD_FILTER2,2,5,3,75V -> VTUNE ~8/10/15V con rail19,05V e headroom stimata3V; caso headroom4,3V **FAIL** con output14,75V. Il reale LM358, il vero circuito MC34063 e LM317 NON sono stati simulati e nessun PLL lock è verificato.

Aprire: `01_Specifiche/V0.8/VTUNE_POWER_DRIVER_THT_V0.8.md`, `03_Verifiche/V0.8/RAPPORTO_TECNICO_V0.8.md`, `03_Verifiche/V0.8/MISURE_DRIVER_V0.8.json`, `04_KiCad/V0.8/VTUNE_PINNET_V0.8.csv`, `07_Componenti/BOM_VTUNE_V0.8.csv`. Controllare CI V0.8 prima di citare PASS.

**Bloccanti:** VCO vendor model/varicap BB204G legacy; frequenza MC34063/Ct corrente/ESR/EMI, minimo carico LM317 worst-case termico, swing reale LM358, progetto circuito completo del PD U401 + phase margin/mute, schematici KiCad/ ERC/DRC e PCB. Né fabbricazione né TX autorizzate.

**Prossima V0.9:** modellazione componenti reali e regolatore, hardwired powergood/mute, circuito U401 e filtro compensato, avvio CAD nativo di driver/supply con ERC, senza forzare approvazione PCB.

**Metodo di continuità:** aggiornare in modo cumulativo main via branch e PR, eseguire verifiche tutte le revisioni, congelare snapshot V0.1..V0.8, registrare PASS / FAIL / NOT_RUN, mai promettere un PCB pronta senza ERC/DRC e prove RF.

---

# V0.7 INTEGRATA SU MAIN — GitHub Actions 190/190 Python PASS (run 42829647107); VCO V0.6 ngspice run 42829647299 PASS (solo modello); VTUNE boost V0.7 ngspice run 42829647279 PASS (solo switch ideali). PR #3 integrata. NO FAB / NO TX.

# CONTINUITÀ ATTUALE — V0.7 (10 novembre 2026)

**Repository privata autonoma:** `jd3485/Superstar3900-THT-Evolution`. Prima di fare qualsiasi lavoro rileggere HEAD `main`, PR, Actions, README, questo file, protocollo, registro decisioni e ultimo rapporto V0.7. Non usare né modificare `Superstar3900-SMD-Evolution`.

**Scopo invariato:** Superstar 3900 ricreata con tecnologia **esclusivamente THT**, RX A–F (270 posizioni), AM/FM/USB/LSB/CW, PLL tradizionale, tuner manuale con bypass, CH9; nessun DSP avanzato, VOX, Dual Watch, CTCSS/DCS o PLL moderno; PCBWay solo PCB nude, saldatura nostra. **NO FAB / NO TX.**

V0.6 aveva trovato la **candidata B VCO** con vero ngspice: Q501/Q502 2N3904 TO-92, BB204G storico TO-92, L166nH effettiva, C470pF, R1,2kΩ, VCC5V, VTUNE8–15V e modello di frequenza in 5 punti 36,04773–39,19647MHz, diodi inversi. NON vendor models né hardware; V0.5 precedente rimane respinta e archiviata.

**V0.7 risolve solo a livello di TOPologia il problema 15V >13,8V**: elevatore THT ST MC34063ABN DIP8 da Vin11–15,5V ipotizzati a24V, poi TI LM317T TO-220 18,287V, RC 10Ω/100µF. Pin-net di tutti gli 11 pin, passivi e BOM. L701 470µH, sense R7011Ω con margine picco bassissimo24mA a11V; switching40kHz è ASSUNTO, non misurato sul vero U701. **NON sono ancora progettati driver PLL→VTUNE, isolamento EMI RF certificato, protezione e powergood hardwired, né schemi KiCad nativi del booster.**

**Evidenza V0.7:** 3 transitori ngspice con ideale switch e comparator danno Vboost circa24V per ingresso11/13,8/15,5V; run 42827358481. La reale dinamica MC34063 e LM317 non è stata simulata, nessuna misura reale effettuata. La linea +18V non garantisce ancora 15V in uscita all'opamp, specie alle tolleranze worst case.

**Leggere:** `01_Specifiche/V0.7/ALIMENTAZIONE_VTUNE_THT_V0.7.md`, `03_Verifiche/V0.7/RAPPORTO_TECNICO_V0.7.md`, `03_Verifiche/V0.7/MISURE_BOOST_V0.7.json`, `04_KiCad/V0.7/`, `02_Piano_Frequenze/V0.7/vtune_power_design_v07.py`. Verificare CI prima di affermare PASS delle nuove regressioni. Ultimo V0.6 main già aveva157/157 software PASS, ngspice VCO solo modello.

**Prossima V0.8:** compensare la criticità L/Ipk con un vero modello di switching, modellare tensione/PSRR/rumore, definire driver analogico THT per phase detector e VTUNE con headroom, protezioni e mute fail-closed, e trasferire schematici completi in KiCad; niente PCB prima di ERC/DRC, BOM autentica e RF/EMC.

**Storicizzazione:** ogni `continua` aggiunge soltanto modifiche cumulative in GitHub, configura snapshot revisioni V0.1–V0.7 e CI regressiva. Niente ricreazione ZIP, nessuna dipendenza da chat precedente. **NO FAB / NO TX.**

---

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
