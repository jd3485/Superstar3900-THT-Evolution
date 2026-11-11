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

# V1.5 CAD 5V THT — nuovo sottoblocco AUTONOMO verificato con KiCad 9, NON integrato nel master V1.4
- `04_KiCad/V1.5/THT_5V_POWER_DISTRIBUTION_V1.5.kicad_sch` con U601 L7805CV TO-220, D601 anti-scarica, condensatori e tre rami RC per PLL/VCO/buffer.
- [GitHub KiCad run 42909924401](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42909924401): **ERC 0 violazioni**, netlist **6/6 reti PASS**, rigenerazione deterministic, export simboli/SVG e screening termico.
- Budget puramente analitico: 12 scenari VIN/carico, **4 segnalati termicamente a rischio** con ipotesi 50°C ambiente e RθJA 50°C/W. Né assorbimenti reali né dissipatore sono definiti. NON è una qualifica termica o RF.
- La protezione 13,8 V a monte NON è progettata e la sezione 20 V VTUNE NON è integrata. File V1.4 preservati. **NO FAB / NO TX**.

---

# V1.4 — primo foglio VCO e buffer LO THT REALMENTE inseriti nella gerarchia, 10 novembre 2026
- Quattro schemi KiCad9 editabili; nuovo sottosistema con Q501/Q502 TO-92, BB204G catodo comune pin2, L501 166nH modello con footprint volutamente vuoto e U520 SN74AC14N DIP14 con due inverter, bias R510/R511/R512 e ingresso AC-coupled C510. 37 nuove istanze; rail VCO5/BUF5 esterne distinte.
- [KiCad9 CI 42892782874](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42892782874): ERC **0 violazioni**, **50 reti**, tutte le **33 reti legacy conservate senza spezzature/corti**, connessi R805→D501 pin2 VTUNE e U520→U402 pin3 LO; simboli esportati e pagine SVG native. Corrette la giunzione GND e la falsa aspettativa di PWR_FLAG in netlist senza sconti ERC.
- [ngspice CI 42892783098](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42892783098): 4 transienti candidato VCO B con ingresso analogico stimato del buffer (NON modello vendor/digitale AC14). Diodi in inversa ai quattro punti, minimo A−K = **−0,376121 V** a VTUNE 8V, segnale modellato al buffer ~1,39–3,99V. **Non test di oscillazione con CMOS attivo, lock, phase noise o maturità RF.**
- Storico V0.9 e CAD V1.0–V1.3 invariati, repository SMD indipendente intatta; nessuna PCB, nessun DRC, BOM/coil MPN incompleti, nessun ordine, NO FAB / NO TX.

---

# V1.3 — gerarchia KiCad RX PLL a 3 pagine nativa, 10 novembre 2026
- Root + child PLL digitale + child filtro/LM358 THT. PDout e GND ora passano su sheet pins e HLabels reali, senza scorciatoie global-label; sorgenti precedenti V1.0/V1.1/V1.2 inalterate.
- [KiCad9 native CI run 42884939754](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42884939754): ERC **0 violazioni**, export SVG **3 fogli**, **33/33 reti**, **tutta la partizione dei pin identica al master piatto V1.2**, verificati due sheetpath diversi; generazione bit-for-bit riproducibile.
- Non completo master radio, nessun VCO/buffer/supply/MCU collegato, nessun PCB, lock RF e fisico NON RUN. NO FAB / NO TX.

---

# V1.2 — integrazione elettrica reale del PLL, 10 novembre 2026
- Nuovo master **parziale piatto** KiCad A2 che riunisce CAD-01/02: U401, U402, R901/C901, LM358N U803, quarzo e connettori; nodi PDout e GND condivisi. **33 componenti/simboli THT** nel nuovo foglio (inclusi connettori/flag provvisori).
- Native KiCad9 ERC **0 violazioni**, 33 reti e 28 gruppi pin-net verificati; U401 pin4 e R901 pin1 effettivamente nella stessa rete KiCad (run 42878584174). Generatore deterministico e librerie locali senza cambi ai precedenti file.
- Risolti 41 avvisi di griglia ERC iniziali: posizionamento corretto su griglia 1,27mm. Simulazioni e regressioni storiche preservate.
- **Non** master gerarchico, PLL chiuso o PCB fabbricabile, VCO/supply/controllo ancora esterni. NO FAB / NO TX.

---

# V1.1 CAD-02 — 10 novembre 2026
- Sottoblocco KiCad 9 del PLL U401 ML145151YP/U402 TC74AC74P, quarzo, filtro di reset solo candidato, connettori e decoupling THT.
- Generatore Node deterministico, libreria locale, ERC e netlist native KiCad, 22 reti pin-per-pin PASS e zero violazioni ERC (run 42870145756). Nessuna deroga THT.
- Tutti i regressivi storici e quattro simulatori ngspice verdi sul commit branch. Nessuno schema master o PCB, nessun loop PLL chiuso qualificato. NO FAB / NO TX.
- Mandato operativo per sviluppare autonomamente anche schema/PCB senza sacrificare simulazioni, firmware, BOM, datasheet e verifiche.

---

# CAD-FIRST V1.0 pilot — 2026-11-10

- Adottata la filosofia **CAD-first rigorosa**, senza smettere di simulare, modellare, sviluppare firmware, selezionare componenti e documentare.
- Recuperato schematico nativo THT parziale della PR #5 su nuovo percorso V1.0, con libreria versionata, generatore deterministico e GitHub Actions `kicad-cli` per verifica reale di simboli/ ERC / netlist / export SVG.
- Mantenuta PR #5 separata non approvata; nessun file V0.1–V0.9 eliminato. Completa matrice 14 blocchi fino al PCB master.
- **NO FAB / NO TX**, elettronica V0.9 e suoi test preservati.

---

# V0.9 — 10 novembre 2026 — filtro phase detector tri-state e primo simulatore vero

- Dimostrato da datasheet che `PDout` ML145151YP pin4 emette impulsi positivi/negativi ed è high-Z in lock, richiede filtro RC di mantenimento verso ingresso LM358 V0.8.
- Creato primo sottoblocco passivo THT candidato R90110k/47k + C9011µF film e netlist SPICE con uscita surrogate ±/Hi-Z.
- Eseguiti 6 transitori ngspice veri con artificiale condizioni iniziali2,5V (non modello PFD reale), misurato incremento/decremento/mantenimento: nessuna stabilità PLL garantita.
- Aggiunti studio frequenza RC/ripple5kHz, matrice reti/BOM, rapporto rischi, test regressivi e snapshot di configurazione V0.8, documenti handoff.
- Integrato solo dopo CI V0.1–V0.9 e regressioni SPICE. **NO FAB / NO TX**, nessun ERC/DRC KiCad nativo.

---

# V0.8 — 10 novembre 2026 — correzione margini alimentazione e driver THT

- V0.7 boost24/rail18.3/Rsc1ohm superata come idea ma non dimensionata: nuova proposta boost27V, Rsc0,47Ω e L470µH con soglia minima ST250mV, rettificatore SB160 DO41 60V.
- LM317T impostato a20,022V nominali, aggiunto R7132,4kΩ0,5W di precarico per minimo carico; calcoli su tensioni e watt.
- LM358N PDIP8 driver a guadagno4 da input filtrato PD_FILTER a VTUNE; 19 pin IC, 22 passivi, BOM25 componenti THT candidate.
- **6 simulazioni ngspice** del modello opamp ideale clamp: output8/10/15V nominali nel modello, ma caso rail headroom peggiore raggiunge solo14,75V (**non qualificato**). Nessuna vera simulazione MC34063/LM317/LM358.
- Snapshot storico V0.7, test regressivi, rapporto, rischi, documenti di ripresa e CI aggiornati. Nessuno schematico KiCad integrato/ERC/DRC o PCB; **NO FAB / NO TX**.

---

# V0.7 — 10 novembre 2026 — Sorgente VTUNE THT 24V + 18V candidata

- MC34063ABN DIP8 boost e LM317 TO-220 lineare, pin-net11/11, 16 passivi candidati, BOM THT, scheda tecnica e rischi.
- Calcoli ripple e tolleranze, Ipk e duty, source Vin11–15,5V, target Vboost~24V, Vreg nominale18,287V, filtro RC10Ω/100µF. **Valori non certificati**.
- Prima simulazione ngspice comportamentale con ideal switch/comparator a tre tensioni, uscite circa24V. Modelli IC reali non eseguiti, rumore RF ignoto.
- Nuovo rischio bloccante: Rsc1Ω+L470µH lascia appena24mA di margine nel calcolo tipico; uscita opamp potenzialmente insufficiente per VTUNE15V. V0.8 dedicata a modelli reali, driver PLL e filtri.
- Snapshot configurazione V0.6, nuova suite statica, rapporto e handoff cumulativi; KiCad/ERC/DRC e PCB non eseguiti. **NO FAB / NO TX.**

---

# V0.6 — 10 novembre 2026 — Prima simulazione elettrica VCO e variante correttiva THT

- Eseguito il VCO V0.5 in vero ngspice 45.2; scoperto **RF FAIL**: frequenza quasi bloccata 38,306..38,350MHz e forward bias BB204G +0,5V.
- Eseguiti sweep C/L/emitter/VCC con ngspice: 36 varianti iniziali/108 transitori, 6 valori L/18, 8 punti nuovo Colpitts, 14 prove seed/ramp, 16 varianti power-ramp/80, più verifica selezionata/5 e originale/3. Le prove servono al modello, non alla qualificazione fisica.
- Catturata dipendenza da condizioni iniziali artificiali UIC; introdotto startup VCC0→5V, analisi di tensioni diodo e misura frequenza da 200 fronti.
- Variante **B** L166nH, C470pF, R1,2kΩ, VCC5V, VTUNE8–15V: 5 punti modello monotoni e inversi, f36,048..39,196MHz. **NON certificata per produzione**.
- Aprono nuovi rischi: VTUNE 15V > 13,8V, approvvigionamento varicap, rumore fase, effettivo tank, modello vendor/temperatura, KiCad ERC/DRC.
- Aggiornati rapporti, script, misure, BOM delta e istruzioni ripresa; aggiunta suite statica V0.6 alle regressioni precedenti.
- **NO FAB / NO TX**.

---

# V0.5 — 10 novembre 2026 — VCO circuitale THT e controllo RX

- Progettato circuito candidato Colpitts con Q501/Q502 TO-92, D501 doppio varicap BB204G, induttore, rete di bias, capacitori RF e buffer.
- Aggiunta netlist ngspice **non ancora eseguita** con transistor e varicap approssimati, e matrice CSV pin/connessioni.
- Modello numerico del tuning nominale e risultati di reiezione del filtro: evidenziata carenza -1,73dB dello stadio PLL V0.4 e tradeoff stabilità del filtro a due poli -41,43dB.
- Introdotto controller RX di riferimento fail-closed con CH9, 270 N, tempo di qualificazione lock, nessuna TX, ma non compilabile su PIC.
- BOM e rischi, report V0.5 e 34 test software aggiuntivi; mantenuti integralmente file e test delle V0.1–0.4.
- Nessun ERC/DRC, SPICE eseguito, hardware, PCB o ordine PCBWay; **NO FAB / NO TX**.

---

# V0.4 — 10 novembre 2026 — VCO analitico e primo CAD digitale THT

- Primo **sottoschema KiCad S-expression `.kicad_sch`** di U402 prescaler con simboli locali e quattro header THT. File generato e controllato staticamente; **non aperto in KiCad e non validato con ERC**.
- BB204G Philips TO-92 trovato in documentazione originale, circuito VCO studiato con modello LC e varactor equivalente: C_var teoriche 29.83..18.20 pF, tensioni interpolate 4.87..15.97 V. Non simulazione RF.
- Filtro di anello passivo tipo B candidato 2.2kΩ / 10kΩ / 100nF; polo e zero calcolati, nessun margine fase certificato.
- Controller `PIC18F47Q43-I/P` PDIP40 candidato per 270 posizioni, CH9/ALFA/mute, senza DSP o funzioni escluse.
- Aggiunti test software V0.4, modello Python, rapporto, BOM e rischi. Le versioni storiche continuano a leggere snapshot di configurazione coerenti.
- VCO reale, filtri/buffer LO, ERC/DRC, SPICE, meccanica, hardware, TX e PCBWay ancora non eseguiti.

---

# V0.3 — 10 novembre 2026 — Core PLL THT pin-to-net

- Sviluppo vero del nucleo PLL candidato: ML145151YP DIP28 e TC74AC74P(F) DIP14, **tutti i 42 pin mappati**, reti logiche, sequenza RX e 270 parole N.
- Quarzo THT Citizen 10,24 MHz CL18pF trovato a catalogo e carico stimato ~17,727pF; emerge il limite ±30ppm/±50ppm per la SSB.
- Prestudio VCO LC con 220nH e Ceq 87,33–75,70pF su gamma LO. Modello numerico riproducibile; NON VCO reale.
- BOM candidato THT con 13 righe, passivi di avvio e interfacce ancora da completare.
- Creati 32 test V0.3 e regressioni V0.2 riagganciate alla baseline `CONFIGURAZIONE_V0.2.json`; workflow GitHub aggiornato.
- Restano tutti OPEN: schematico KiCad nativo, VCO/buffer/loop, SPICE, ERC/DRC, hardware, gate produzione e TX.

---

# V0.2 — 10 novembre 2026 — Frequenze e sintetizzatore tradizionale THT

- Piano RX a 270 posizioni A–F, con 30 ALFA, CH9 D/9 e codici N a 14 bit; sorgente Python di rigenerazione e CSV.
- IF1/LO/immagini calcolate, 24 test statici V0.2 e 12 regressivi V0.1 superati.
- Alternative PLL: MC145151P2 legacy + SN74AC74N /2 oppure CD74HC4046AE + contatori THT; nessuna BOM finale.
- Aggiornati rapporto, stato, decisioni, istruzioni per nuove chat. Nessun KiCad, SPICE, prototipo, ordine o TX.

---

# Changelog

## V0.1 — 10 novembre 2026 — Fondazione progetto THT indipendente
- Confermata architettura prevalentemente analogica THT, costruzione manuale e fabbricazione PCB nude via PCBWay.
- Delimitate funzioni incluse/escluse e scelta accordatore manuale con bypass.
- Definiti protocollo di continuità, registro decisioni, rischi, piano di sviluppo e gates.
- Preparati test strutturali riproducibili e manifest SHA-256 del pacchetto V0.1.
- Non realizzati schemi KiCad, PCB, simulazioni circuitali, prototipi o misure. **NO FAB / NO TX.**
