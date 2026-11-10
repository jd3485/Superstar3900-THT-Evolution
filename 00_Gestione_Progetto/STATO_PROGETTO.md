# V1.2 — INTEGRAZIONE CAD-01/CAD-02 NATIVA, VERIFICATA

Primo file unico schematico KiCad U401/U402/LM358, con `PLL_PDOUT_3STATE` in comune (U401/4 → R901/1). GitHub Actions KiCad 9 [run 42878584174](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42878584174): **ERC nativo 0 violazioni**, **33 reti reali esportate**, **28 gruppi pin-net con controlli automatici PASS**, export SVG e rigenerazione deterministica PASS. Verifiche software e ngspice storiche anche PASS su branch; **non** PLL chiuso, master gerarchico, PCB o prova RF. NO FAB / NO TX.

---

# V1.1 CAD-02 su branch, non ancora su main

Disegnato U401/U402 con quarzo e pin reali in nuovo schema KiCad; run GitHub Actions 42870145756 SUCCESS: KiCad9.0.9 ERC 0 violazioni, 22 reti pin-net validate, SVG e generatore PASS. Sottoblocco isolato soltanto. Master/PCB non presenti. NO FAB / NO TX.

---

# Aggiornamento pilot V1.0: schema KiCad filtro/LM358 realmente ERC **PASS 0 violazioni** e **8 reti pin-to-net PASS** sul solo foglio isolato, run 42858721761; 272 regressioni Python PASS sul branch. Nessuna PCB, U401/VCO restano esterni, produzione non autorizzata.

# STATO CAD-FIRST V1.0 (pilot, senza salto di qualifica elettrica V0.9)

Vero file KiCad gerarchico ancora NON COMPLETO. Nuovo foglio THT filtro/LM358 in `04_KiCad/V1.0/PLL_FILTER_DRIVER_CAD_V1.0.kicad_sch`, libreria locale e sorgente riproducibile; **ERC e netlist nativi solo con evidenza CI verde**, non assumere pass. PCB KiCad ancora assente. La **PR #5 CAD preesistente è dirty e non qualificata**; file ripresi in un branch distinto senza modificarla. Stato radio RX attuale rimane ~15% schematico con margine ampio, PCB produzione 0%. Compilare `MATRICE_COPERTURA_CAD_V1.0.csv` ogni incremento.

---

# Stato tecnico attuale V0.9 — 10 novembre 2026

| Sezione | Evidenza |
|---|---|
| Frequenze RX | 270 piano numerico storico, non qualifica radio |
| PLL U401/U402 | ML145151YP PDIP28, U402÷2 DIP14 candidati; sourcing U401 irrisolto |
| Phase detector | **PDout U401 pin4 tri-state ±/Hi-Z da datasheet**, direzione impulsi nota |
| Filtro PLL | **R90110k o47k / C9011µF solo candidati**, test ngspice 6 casi surrogati UP/DOWN/HOLD; non loop stabile |
| VCO | V0.6 candidata Colpitts, 5 punti simulati, vendor/hardware non qualificati |
| Driver VTUNE | LM358N DIP8 x4 V0.8, non agganciato al phase detector, solo opamp ideale |
| Alimentation | MC34063 DIP8 target27V, LM317T TO220 target20V, solo proposte, EMI non misurata |
| Segnali RX sicuri | Modelli fail-closed Python, non circuito interlock fisico |
| KiCad | Soltanto vecchio schemino prescaler; CAD filtro V0.9 è CSV, ERC/DRC NOT_RUN |
| PCB/Hardware | 0 PCB, 0 Gerber, 0 prototipi |
| Fab/TX | **NO FAB / NO TX** |

---

# Stato attuale V0.8 — 10 novembre 2026

| Blocco | Stato |
|---|---|
| RX 270 frequenze | Piano numerico storico verificato, non radio reale |
| PLL tradizionale | U401 ML145151YP DIP28 e U402 TC74AC74P DIP14 candidati; sourcing U401 aperto |
| VCO | Candidata B V0.6 con 5 punti SPICE e modelli non ufficiali; test RF hardware NON RUN |
| Vboost | MC34063ABN DIP8 **27V candidata**, Rsc0,47Ω L470µH Bourns RLB0914-471KL candidata, SB160 DO41 60V; no modello vendor |
| Regolatore | LM317T TO220 **20,022V nominali**, R240/3570 e precarico2,4kΩ/0,5W; no modello vendor |
| Driver VTUNE | LM358N PDIP8 gain4 candidato, `PD_FILTER` esterna, feedback30k/10k e isolatore220Ω/100nF |
| SPICE | 6 transienti **reali del modello IDEALE di opamp**, non reale LM358, PDout o PLL; a headroom peggiorata FAIL VTUNE |
| BOM e reti | 19 pin IC/22 passivi/25 componenti candidate; **NON uno schema KiCad integrato** |
| Sicurezza | Nessun powergood hardware, mute e TX interlock fisico progettati |
| KiCad | V0.4 sottoschema prescaler presente, V0.8 soltanto CSV: ERC/DRC NON RUN |
| Produzione | 0 PCB, 0 Gerber, 0 prototipi, nessun ordine |
| Gate | **NO FAB / NO TX** |

**V0.9:** sostituire modelli ideali, progettare PLL vero, interblocchi e fare avanzare KiCad.

---

# Stato progetto V0.7 — 10 novembre 2026

| Sezione | Stato reale |
|---|---|
| Piano frequenze RX | 270 posizioni con matematica testata, non RF |
| PLL e divisore U401/U402 | Candidati DIP, schema digitale parziale V0.4, sourcing U401 non chiuso |
| VCO | Candidata B V0.6 passa 5 punti ngspice con modelli sintetici; VTUNE8–15V richiesta |
| BOOST VTUNE V0.7 | **MC34063ABN DIP8 candidato**, calcoli e pin-net 8/8, switch NON simulato con vero dispositivo |
| Regolatore V0.7 | **LM317T TO-220 candidato**, 3/3 pin, R=240/3240 ->18,287V nominali |
| SPICE boost | 3 transienti reali **su modello ideale PWM/interruttore**, alimentazioni11/13,8/15,5V, circa24V in uscita: NON test reale MC34063 |
| Criticità Ipk | a Vin11V I_L ON≈0,306A e soglia typ0,33A, margine24mA; possibile limite in CCM |
| Criticità opamp | 18V rail può essere insufficiente per 15V VTUNE a temperature/carico worst case, driver NON definito |
| Isolamento rumore RF | RC solo ideale 10Ω/100µF; compatibilità EMI/phase noise non misurata |
| KiCad booster e PLL | No schematico integrato, ERC/DRC **NON ESEGUITI** |
| PCB / hardware | 0 PCB, 0 prototipi; nessuna fabbricazione |
| TX / FAB | **NO FAB / NO TX** |

**Prossima V0.8:** macro-modelli vendor, sizing di convertitore e rail/driver, prova EMI, netlist/PCB KiCad verificabile. Progetto autonomo, THT, PCBWay solo schede nude.

---

# Stato corrente — V0.6 (10 novembre 2026)

| Blocco | Stato ed evidenza |
|---|---|
| 270 RX / PLL divisione | V0.2 numericamente PASS, non provato in RF |
| PLL classico U401/U402 | Componenti THT candidati, sourcing ML145151 non chiuso |
| VCO V0.5 | **RESPINTO DA ngspice** (varicap avanti, accordo 44kHz) |
| VCO candidata B V0.6 | **MODELLO PASS su 5 punti con avvio VCC da zero**: L166nH, C470pF, R1.2k, VCC5V, VTUNE8-15V, f36,048..39,196MHz |
| Varicap | Nessuna conduzione diretta nei 5 punti del modello, VR inversa max 17,75V; BB204G NOS non qualificato |
| Supply VTUNE | **BLOCCANTE**: 15V non ottenibili direttamente da rail radio nominale 13,8V, circuito driver/boost non progettato |
| Loop PLL, fasi, clock | **NON VALIDATI**: spur, margine fase, lock, buffer prescaler |
| Prova SPICE | **ESEGUITA** con modelli generici; studi multi-run, esiti reali documentati; non vendor models |
| KiCad | Soltanto sottoschema U402 V0.4; ERC/DRC e PCB **NON ESEGUITI** |
| PCBWay / assembly | PCB nude solo dopo validazione; saldatura THT interna; nessun ordine |
| TX / FAB | **NO TX / NO FAB** |

**Prossima V0.7:** risolvere generazione VTUNE, modelli affidabili, tolleranze/temperatura, filtro PLL, buffer RF e KiCad; nessun rilascio producibile.

---

# Stato corrente V0.5 — 10 novembre 2026

| Modulo | Evidenza reale |
|---|---|
| Piano RX | 270 frequenze/ALFA V0.2, controlli aritmetici |
| PLL U401/U402 | ML145151YP PDIP28 e TC74AC74P DIP14 candidati; approvvigionamento U401 non verificato |
| VCO | **Netlist SPICE scritta** Q501/Q502 2N3904-AP TO-92 + BB204G TO-92 con due giunzioni, L150nH, C feedback e bias |
| Accordo ideale | Curva C(V) fitted, 270 parole N, Vtune nominale 3,13–6,95 V **non garantita** |
| Filtro PLL | Rete V0.4 attenuazione 5kHz -1,73dB; rete a due poli studio -41,43dB; **loop NON stabilizzato** |
| Controllo N | Simulatore logico Python di RX mute fail-closed e CH9, non firmware PIC compilato |
| KiCad | Prescaler .kicad_sch V0.4 presente, VCO non integrato; apertura/ ERC/ DRC **NOT_RUN** |
| SPICE RF | Deck completo candidato; esecuzione simulator **NOT_RUN** |
| PCB/prototipo | 0 PCB, 0 Gerber, 0 prototipi |
| Produzione e TX | **NO FAB / NO TX** |

**Bloccanti:** strumenti SPICE e CAD effettivamente eseguibili, modello varicap autentico a 37MHz, sourcing BB204G legacy, margini di loop e riferimento SSB, alimentazioni e protezioni, schema KiCad integrato. **Prossima V0.6:** simulazione circuitale vera, correzioni e CAD.

---

# Stato progetto corrente — V0.4 (10 novembre 2026)

| Modulo | Stato reale |
|---|---|
| Ricezione/piano | 270 posizioni RX matematicamente verificate V0.2; TX OFF |
| PLL core | U401 ML145151YP candidato e U402 TC74AC74P(F) in DIP; fornitura U401 ancora non confermata |
| Primo CAD nativo | `PLL_PRESCALER_RX_V0.4.kicad_sch` = soltanto U402 + 4 connettori, simboli locali, non ancora aperto in KiCad |
| VCO analogico | Tank teorico BB204G TO-92 / L=220nH / Ceq fixed=57.5pF; tensioni nominali interpolate 4.87–15.97V, **NON un oscillatore completo** |
| PLL loop | Tipo B candidato 2.2k + 10k + 100nF, polo 130.5 Hz e zero 159.2 Hz; **stabilità NON convalidata** |
| Clock LO | Buffer/limitatore AC14 DIP solo candidato; PCB non cablata |
| Controllo canali | PIC18F47Q43-I/P PDIP40 candidato; N bus e mute progettati solo come contratto logico, firmware assente |
| Simulazioni circuitali/SPICE | **NON ESEGUITE** |
| KiCad ERC/DRC | **NON ESEGUITI**; esistono solo controlli testuali automatici sul primo .kicad_sch |
| Produzione e collaudi | 0 PCB, 0 prototipi, 0 collaudi; PCBWay fabbrica solo PCB nude quando saranno autorizzate |
| TX / fabbricazione | **NO TX / NO FAB** |

**Bloccanti:** fornitura U401/BB204G, VCO/buffer reali, filtri e margini, precisione riferimento SSB, MCU controllo/fail-closed, KiCad/Erc/DRC nativi e layout PCB. Prossima V0.5: completamento progressivo della catena PLL/VCO e integrazione CAD.

---

# Stato corrente V0.3 — 10/11/2026

| Area | Stato attuale |
|---|---|
| Piano frequenze | 270 posizioni RX, 30 ALFA, 25,615–28,305 MHz (V0.2) |
| Sintesi numerica | 10,240 MHz / 2048 = 5 kHz, /2 VCO, N=3631..3900 |
| U401 PLL | **ML145151YP Lansdale PDIP28**, candidato; pinout documentato, sourcing/quantità non confermati |
| U402 /2 | **TC74AC74P(F) Toshiba DIP14**, pinout documentato e confronto limite clock dati produttore |
| Riferimento X401 | Citizen 10,240 MHz HC-49/US, CL18pF, ±30ppm / stabilità ±50ppm, **solo candidato banco prova** |
| Core analogico | Pierce e primi passivi; **VCO, driver 39MHz, filtro loop, codifica N e powergood ancora aperti** |
| Schema CAD | Matrice pin-net 42/42, **non .kicad_sch nativo**, KiCad ERC/DRC NON ESEGUITI |
| Analisi LC | Tank teorico L=220nH, Ceq 87,33..75,70pF per copertura LO, solo matematica |
| Test | V0.3 32 test software predisposti; V0.2 24 e V0.1 12 regressioni, risultati CI da verificare |
| PCB/prototipi | Nessun PCB, Gerber o hardware; PCBWay solo schede nude |
| Sicurezza | **NO FAB / NO TX** |

**Blocchi principali prima del PCB:** reperibilità U401 in quantità accessibili, eventuale seconda architettura non legacy, specifica riferimento SSB, selettore 270 posizioni, VCO/varicap THT, loop filter, reset/lock RX, alimentazione, schemi nativi e ERC/DRC.

**Prossima V0.4:** sviluppare VCO + buffer/filtro + schema KiCad con verifica datasheet, senza dichiarare il circuito completo finché esistono reti aperte.

---

# Stato corrente — V0.2, 10 novembre 2026

| Area | Stato |
|---|---|
| Piano RX | 270 posizioni con 30 ALFA, 25,615–28,305 MHz, calcolo e test statici PASS |
| CH9 | D/9 = 27,065 MHz AM prioritario |
| IF1 e LO | 10,695 MHz e 36,310–39,000 MHz, **candidati** |
| PLL matematico | REF 10,240 MHz, R=2048, /2, fPFD 5 kHz, N=3631..3900, tutti interi |
| PLL fisico | Due architetture THT in studio, componenti/pin/timing/sourcing non validati |
| Verifiche | V0.2: 24/24 PASS; V0.1: 12/12 PASS, solo software |
| KiCad, SPICE, EM, hardware | **NON ESEGUITI**, nessuna scheda |
| PCBWay | PCB nude e montaggio interno; nessun file di fabbricazione |
| TX e FAB | **INIBITI, NO FAB / NO TX** |

**Criticità:** approvvigionamento sintetizzatore MC145151P2 legacy, livelli al pin fIN, condizioni di clock del prescaler, VCO, rumore, spur e filtro loop, controllo fisico N e assenza di enable TX. **Prossima V0.3:** circuiti veri e verifica dei componenti prima di qualsiasi PCB.

---

# Stato attuale — V0.1 (10 novembre 2026)

**Fase:** definizione progettuale iniziale, non prototipo fabbricabile.

| Area | Stato |
|---|---|
| Requisiti e vincoli | Prima baseline V0.1 documentata |
| Piano dei moduli | Prima roadmap candidata |
| Frequenze 270 posizioni | Solo vincolo quantitativo; CSV dettagliato **da definire V0.2** |
| PLL/VCO tradizionale | Fattibilità e scelta architettura **aperte** |
| Mixer e filtri RF/IF | Architettura candidata, nessuno schema finalizzato |
| Modulazione TX/finale/antenna | Non progettati; TX bloccata |
| Accordatore manuale | Requisito approvato; rete LC e dimensionamento ancora aperti |
| KiCad ERC/DRC | **NON ESEGUITI**: progetto nativo da costruire |
| Simulazioni elettriche/SPICE/EM | **NON ESEGUITE** |
| PCB e Gerber | **NON CREATI** |
| Prototipi fisici e misure | **ZERO** |
| Assemblaggio | Interno; PCBWay solo fabbricazione PCB nude |
| Autorizzazione fabbricazione | **NO FAB** |
| Autorizzazione emissione RF | **NO TX** |

**Decisioni aperte fondamentali:** requisiti di sensibilità/selettività misurabili; gamma e piano RX completo; frequenze IF e oscillatori; topologia PLL THT e disponibilità componenti; potenza TX legale e obiettivi di prova; architettura singola PCB; dimensioni meccaniche; tensioni di alimentazione e dissipazione; accordatore manuale con limiti di impedenza e potenza da definire.

**Prossima revisione:** V0.2 Piano frequenze e studio PLL classico THT. Una simulazione corretta resta una simulazione: la validazione fisica viene dopo la progettazione e le verifiche necessarie.
