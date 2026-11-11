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

# V1.4 — VCO Colpitts THT e SN74AC14N su 4 fogli KiCad9: ERC 0, 50 reti native, 33 reti legacy non alterate, collegamenti VTUNE→D501/2 e U520→U402/3 PASS ([KiCad 42892782874](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42892782874)). ngspice con ingresso analogico caricato 4 punti eseguito ([42892783098](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42892783098)); margine minimo inverso varicap 0,376 V: **VCO/buffer/PLL NON qualificati RF**, coil e PCB incompleti. NO FAB / NO TX.

# V1.3 — gerarchia KiCad9 RX PLL verificata: 3 pagine, ERC 0 violazioni, 33/33 reti con partizioni di tutti i pin identiche alla V1.2, U401 e U803 su sheetpath distinti. [CI native run 42884939754](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42884939754). Il VCO e la PCB restano non integrati. NO FAB / NO TX.

# V1.2 CAD FIRST — primo foglio KiCad integrato PLL U401/U402 + filtro RC/LM358: ERC 0 violazioni, 33 reti e 28 gruppi pin-net verificati in [Actions 42878584174](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42878584174). Schema elettrico parziale PIATTO, non radio completa o PCB. NO FAB / NO TX.

# V1.1 CAD-02 — vero PLL digitale RX THT U401/U402 + quarzo in KiCad 9; ERC nativo 0 violazioni, netlist 22 reti verificate sul sottoblocco (run 42870145756). Non è PLL completo, non è PCB. NO FAB / NO TX.

# **V1.0 CAD-first pilot: KIcad9 ERC reale 0 violazioni, 8 net esportate e verificate pin-per-pin, 272 test software PASS sul branch.** Non è la radio completa. Leggere il report V1.0. **NO FAB / NO TX**.

# NUOVA POLITICA DI PROGETTAZIONE — CAD-FIRST V1.0 (pilot, V0.9 elettrica resta riferimento)

Da ora il risultato prioritario è lo **schema completo KiCad nativo** e la **PCB THT unica quando praticabile**, con calcoli, SPICE, firmware, test e BOM in parallelo. Avviato il primo sottoschema **PDout/LM358 filtrato**, derivato dal lavoro CAD non integrato della PR #5, con artefatti veri in `04_KiCad/V1.0/`. È un *isolated CAD study*, non PLL reale o circuito da fabbricare. Le sue R901=22k e C901=100n sono una **variante non qualificata** differente dal precedente modello V0.9 R10k/47k e C1µF.

**Stato nativo KiCad ERC:** controllare la run del workflow `cad_native_v10.yml` prima di riportare PASS. **Non esiste ancora un PCB .kicad_pcb integrato**. `NO FAB / NO TX`.

Procedura obbligatoria: [`METODO_CAD_FIRST_V1.0.md`](00_Gestione_Progetto/METODO_CAD_FIRST_V1.0.md), [`MATRICE_COPERTURA_CAD_V1.0.csv`](00_Gestione_Progetto/MATRICE_COPERTURA_CAD_V1.0.csv).

---

# STATO CORRENTE — V0.9 (10 novembre 2026)

**Nuovo passo elettrico:** il phase detector A del PLL THT `U401 ML145151YP` usa `PDout pin4` a tre stati `+5V / GND / HIGH-Z`. La V0.8 aveva progettato il driver LM358N partendo da `PD_FILTER` senza definire come fosse generato. Nella V0.9 abbiamo creato il primo sottoblocco filtro RC THT **R90110k/47k + C9011µF**, con prova ngspice di impulsi positivi, negativi e alta impedenza. Risultati di sei vere transienti con **switch surrogati ideali**, non con il ML145151 fisico.

**Risultato qualificato soltanto nel modello:** tensione del condensatore sale con impulsi positivi, scende con negativi e resta quasi fissa a breve termine durante Hi-Z. R901/C901 è **solo candidata e non è un filtro PLL approvato**; compensazione, Kvco locale, Kphi, capture e phase margin NON sono simulati. **R902 100MΩ è componente fittizio per perdita numerica** da NON ordinare.

Il progetto resta 100% THT, indipendente, storico V0.1–V0.8 completo. **NO FAB / NO TX; schematico KiCad completo/ERC/DRC NON ESEGUITI**. File: `01_Specifiche/V0.9/PDOUT_TRISTATE_FILTRO_V0.9.md`, `03_Verifiche/V0.9/RAPPORTO_TECNICO_V0.9.md`, `03_Verifiche/V0.9/PDOUT_TRISTATE_SURROGATE_V0.9.cir`. Prossima V1.0: loop PLL realmente chiuso e KiCad nativo.

---

# STATO CORRENTE — V0.8 (10 novembre 2026)

**Nuovo circuito candidato interamente THT per l'alimentazione e il pilotaggio VTUNE:** U701 MC34063ABN PDIP8 con target27V e corrente di soglia ricalcolata (Rsc0,47Ω, L470µH Bourns RLB0914-471KL candidata); D701 Vishay SB160 60V assiale; U702 LM317T TO220 a circa20,022V con precarico R7132,4kΩ0,5W per minimo carico; U803 LM358N PDIP8 in configurazione non invertente ×4 da **PD_FILTER** a VTUNE. **19 pin IC / 22 passivi documentati**, BOM25 righe.

**ngspice** ha eseguito 6 test del **driver IDEALE, non dell'LM358 reale**. Per PD_FILTER2/2,5/3,75V -> VTUNE~8/10/15V con rail19,05V e headroom assunta3V. Caso headroom4,3V: VTUNE soltanto14,75V (**FAIL margine**). I dati non validano PLL closed-loop, rumore o regolazione reale MC34063 e LM317.

**Nessun nuovo schematico KiCad integrato, ERC/DRC e prototipo NON ESEGUITI.** Nessuna BOM/PCB fabbricabile, NO FAB / NO TX.

Documenti: `01_Specifiche/V0.8/VTUNE_POWER_DRIVER_THT_V0.8.md`, `03_Verifiche/V0.8/RAPPORTO_TECNICO_V0.8.md`, `03_Verifiche/V0.8/VTUNE_DRIVER_BEHAVIORAL_V0.8.cir`, `04_KiCad/V0.8/`. Prossima V0.9: simulazione reale componenti dove reperibili, timing Ct, anello PLL, protezioni e CAD.

---

# STATO CORRENTE — V0.7 (10 novembre 2026)

**Alimentazione analogica VTUNE THT — PROGETTO PRELIMINARE**: U701 ST MC34063ABN DIP8 (boost dalla linea11–15,5V protetta a circa24V) più U702 TI LM317 TO-220 (linea~18,287V) e rete RC 10Ω/100µF per alimentare un futuro driver analogico PLL. Pin-net **11 pin su 11**, BOM THT e calcoli di duty, Ipk, partitori e margini. **La rete non è ancora disegnata in schematico KiCad nativo, né qualificata con componenti reali.**

**Tre veri ngspice su un MODELLO COMPORTAMENTALE IDEALE**, NON su MC34063/LM317 fisici: media Vboost23,9967V @11V, 24,0096V @13,8V e24,0221V @15,5V; proprietà del modello, non un prodotto RF-low-noise. Limiti: margine Ipk a11V appena24mA nel calcolo tipico; switching EMI non misurata; drive ad alta tensione può non arrivare a15V nel worst case. **No PLL chiuso, NO FAB / NO TX.**

**VCO V0.6 candidata B invariata:** L166nH, 2×2N3904, doppio BB204G TO-92, C470pF, R1,2kΩ, +5V RF; 5 punti SPICE con avvio realistico 36,048–39,196MHz, ma modelli vendor non qualificati. Per la nuova chat leggere `RIPRENDI_IN_UNA_NUOVA_CHAT.md`.

File nuovi: `01_Specifiche/V0.7/ALIMENTAZIONE_VTUNE_THT_V0.7.md`, `04_KiCad/V0.7/`, `03_Verifiche/V0.7/RAPPORTO_TECNICO_V0.7.md`, `03_Verifiche/V0.7/MISURE_BOOST_V0.7.json`. **Prossima V0.8:** circuito VTUNE/PLL dinamico e alimentazione fisicamente qualificabile, poi CAD KiCad/ERC.

---

# STATO ATTUALE — V0.6 (10 novembre 2026)

**Prima verifica ngspice reale.** Il circuito Colpitts della V0.5 è stato **RESPINTO**: a VTUNE 3,2–7,5 V oscilla solo a 38,306–38,350 MHz e polarizza in diretta i varicap (+0,51..+0,54 V). Sono stati provati modelli e avvii diversi per evitare falsi positivi.

**Nuova CANDIDATA B, solo modello SPICE:** VCO THT Q501/Q502 2N3904 + BB204G TO-92 doppio, VCC=5V, R503=1,2kΩ, C504=470pF, L501 effettiva 166nH candidata (bobina regolabile da scegliere), VTUNE=8–15V. Con avvio da zero senza UIC, ngspice rileva **36,04773–39,19647 MHz** nei cinque punti, A−K sempre negativo, VR picco massimo nel modello 17,75V. La finestra contiene LO 36,310–39,000MHz, **ma non prova tutti i 270 canali né il comportamento fisico**.

**Bloccanti:** VTUNE fino a 15V supera alimentazione 13,8V; serve architettura THT silenziosa per il driver/rail o riduzione della tensione richiesta. Varicap BB204G legacy, modelli SPICE sintetici, VCO non integrato KiCad, nessun ERC/DRC, controllo lock/filtro PLL non validati. **NO FAB / NO TX.**

Aprire `03_Verifiche/V0.6/RAPPORTO_TECNICO_V0.6.md`, `03_Verifiche/V0.6/MISURE_SPICE_V0.6.json`, `03_Verifiche/V0.6/VCO_COLPITTS_CANDIDATE_B_V0.6.cir`, `01_Specifiche/V0.6/VCO_SIMULAZIONE_E_CORREZIONI_V0.6.md`.

**Prossima V0.7:** affinamento componenti e tolleranze, driver VTUNE, startup completo, loop PLL, buffer prescaler/LO e primo circuito CAD completo. Ogni revisione è cumulativa su GitHub, progetto indipendente, PCBWay solo PCB nude e saldatura interna.

---

# STATO ATTUALE — V0.5 (10 novembre 2026)

**Sviluppo concreto VCO:** primo circuito a componenti THT con Q501/Q502 2N3904-AP (Colpitts + emitter follower), D501 BB204G (due varicap in parallelo con polarità corrette), L501 150nH, R/C di bias, disaccoppiamenti e prima **netlist SPICE non ancora eseguita**. Modello C(V) e accordo nominale di 270 canali ora ≈3,13–6,95V, con **Cfixed_eff 61pF ASSUNTA**, non misura. I margini di tolleranza non sono certificati.

**Correzione importante:** il filtro candidato della V0.4 attenua il tono PFD 5kHz solo −1,73dB nel modello ideale. Confrontato con filtro due poli −41,43dB, **NON qualificato per stabilità PLL**. Un driver THT +12V tipo LM358N è solo candidato: la tensione PLL PDout 5V non può generare direttamente ~7V.

**Controllo RX:** riferimento Python di cambio canale con mute fail-closed, CH9, lock/ref/power validi e 270 canali, mai TX. Non è firmware PIC programmabile.

File: `01_Specifiche/V0.5/VCO_COLPITTS_THT_V0.5.md`, `03_Verifiche/V0.5/VCO_COLPITTS_CANDIDATE_V0.5.cir`, `02_Piano_Frequenze/V0.5/vco_dualvar_model_v05.py`, `03_Verifiche/V0.5/RAPPORTO_TECNICO_V0.5.md`.

**Stato:** SPICE non eseguito, KiCad VCO non disegnato, ERC/DRC e prototipi NON ESEGUITI, NO FAB / NO TX. Prossima V0.6: eseguire e correggere SPICE, margini PLL, poi schema KiCad reale.

---

# STATO ATTUALE — V0.4, 10 novembre 2026

**Nuovo:** studio analitico del VCO THT (varactor BB204G storico TO-92, L220nH e capacità totale teorica) e primo **sottoschema nativo `.kicad_sch`** del divisore RX U402 TC74AC74P(F) DIP14, completo di simboli locali e quattro connettori THT. **Non è ancora un circuito PLL completo né un file verificato dall'app KiCad:** ERC/DRC/SPICE/hardware NON ESEGUITI. Scelta controller semplice PIC18F47Q43-I/P PDIP40 come candidato, senza firmware/pinout finali.

**V0.4:** `01_Specifiche/V0.4/VCO_PLL_CONTROLLO_V0.4.md`, `04_KiCad/V0.4/PLL_PRESCALER_RX_V0.4.kicad_sch`, `02_Piano_Frequenze/V0.4/vco_tuning_v04.py`, `03_Verifiche/V0.4/RAPPORTO_TECNICO_V0.4.md`. Le suite V0.1/0.2/0.3 restano cumulative e si aggiunge la suite V0.4.

**Prossima V0.5:** circuito oscillatore transistor + varicap pin-numbered, buffer LO, filtro loop basato su Kvco/Kphi e controller/pinout; validazione KiCad nativa quando eseguibile. **NO FAB / NO TX**, PCBWay solo PCB nude e montaggio interno.

---

# STATO ATTUALE — V0.3, 10 novembre 2026

La V0.3 trasforma lo studio PLL in un **primo nucleo circuitale pin-to-net THT**, con U401 Lansdale ML145151YP DIP28 e U402 Toshiba TC74AC74P DIP14; 42/42 pin documentati, primi passivi e X401 Citizen 10,240 MHz HC49 THT. Componenti **candidati non acquistati**, ML145151YP da richiedere a quotazione, riferimento del quarzo non adeguato per SSB ad alta precisione senza ulteriore progettazione. **Non esiste ancora un .kicad_sch nativo, VCO, loop filter dimensionato, PCB o scheda operativa**. Il progetto rimane 100% THT, con TX disabilitata.

**Nuovi elaborati:** `01_Specifiche/V0.3/PLL_CORE_CIRCUITO_V0.3.md`, `04_KiCad/V0.3/PLL_U401_U402_PINNET_V0.3.csv`, `07_Componenti/BOM_PLL_CORE_V0.3.csv`, `03_Verifiche/V0.3/RAPPORTO_TECNICO_V0.3.md`.

**Prossima revisione V0.4:** chiudere sourcing del PLL, progettare VCO/buffer e filtro, controller dei 270 canali, iniziare lo schema KiCad nativo, verificare compatibilità; vietato ordinare PCB o abilitare TX finché non chiusi i gate.

---

# STATO ATTUALE — V0.2 integrata in main (10 novembre 2026)

**270 posizioni RX documentate**: 6 bande A–F con 30 ALFA, CH9 D/9 27,065 MHz; tabella verificata nel percorso `02_Piano_Frequenze/V0.2/`. Proposta di PLL classico THT: IF1=10,695 MHz candidata, LO1 high-side 36,310–39,000 MHz, quarzo 10,240 MHz /2048 = 5 kHz, divisore /2 e N integer 3631..3900. Due architetture alternative in studio; nessun circuito approvato, MC145151P2 legacy non prodotto da NXP.

**V0.2: 24 test aritmetici/statici PASS; V0.1: 12 test regressivi PASS**, non sono simulazioni elettriche. Nessun KiCad/ERC/DRC, SPICE o prova hardware. **NO FAB / NO TX.**

**Prossima V0.3:** studio circuitale del PLL con componenti THT autentici, verifica dei pin e del timing, progettazione di VCO e alimentazioni; prima leggere l'ultimo README, handoff e rapporto tecnico.

---

# Superstar 3900 THT Evolution

**Revisione iniziale V0.1 — 10 novembre 2026.** Progetto **nuovo e indipendente** di ricetrasmettitore CB prevalentemente analogico, ispirato all'esperienza d'uso del Superstar 3900, con **soli componenti elettronici THT sulle schede** e PCB destinati alla fabbricazione presso PCBWay, **assemblati e saldati internamente**.

> **STATO ATTUALE: DEFINIZIONE DEI REQUISITI E ARCHITETTURA CANDIDATA.** Non esiste ancora uno schema elettrico completo, né un PCB KiCad da produrre. Nessuna simulazione elettronica, ERC/DRC o prova hardware è stata eseguita. **NO FAB / NO TX**.

## Scopo
Sviluppare una radio con bande A–F, 270 posizioni di ricezione (6 × [40 canali ordinari + 5 ALFA]), AM/FM/USB/LSB/CW, comandi fisici, CH9 prioritario, ricezione sensibile e selettiva, accordatore **manuale** con bypass, strumenti RF, funzione PA audio e alcune funzioni analogiche accessorie. I modi/frequenze TX e la potenza RF **non sono autorizzati né definiti** da questa scelta di progetto.

Sono **esclusi**: DSP audio avanzato, sintesi PLL RF moderna altamente integrata, Dual Watch, CTCSS/DCS, VOX, accordatore automatico. Un **PLL tradizionale con VCO/divisori** è invece una soluzione ammessa, ancora da selezionare.

## Indipendenza
Questo progetto **non è un fork** e non utilizza l'altra radio come dipendenza, né ne segue i numeri di versione. Si adotta soltanto un metodo di sviluppo simile: moduli, revisioni incrementali, verifiche reali, documentazione, storicizzazione, controllo delle modifiche e un protocollo di ripresa da chat nuove.

## Prossima revisione
**V0.2: piano di frequenze e specifica di sintesi THT.** Definire tabella completa delle 270 posizioni RX, frequenze IF candidate, ipotesi di PLL e requisiti di precisione/stabilità; confrontare componenti disponibili in THT e definire verifiche riproducibili. Nessun componente da acquistare prima della valutazione.

## Leggere per riprendere
1. `RIPRENDI_IN_UNA_NUOVA_CHAT.md` e `00_Gestione_Progetto/PROTOCOLLO_CONTINUITA_MAIN.md`.
2. `00_Gestione_Progetto/STATO_PROGETTO.md` e `00_Gestione_Progetto/REGISTRO_DECISIONI.md`.
3. Il rapporto della revisione corrente in `03_Verifiche/` e il piano dei moduli.
4. Su GitHub verificare **HEAD di `main`**, tag, PR e CI prima di pianificare la revisione seguente. La sezione più recente e i rapporti correnti prevalgono sulle note storiche.

## Struttura
- `00_Gestione_Progetto/`: governance, stato, decisioni, rischi, roadmap, changelog.
- `01_Specifiche/`: requisiti e architettura di blocco.
- `02_Piano_Frequenze/`: frequenze, sintetizzatore e controlli numerici.
- `03_Verifiche/`: test, rapporti, simulazioni e registri.
- `04_KiCad/`: sorgenti circuitali e PCB **solo quando creati veramente**.
- `05_Produzione_PCBWay/`: vincoli e gate di fabbricazione; **non un ordine**.
- `06_Manuali/`: manuali tecnici e d'uso da costruire.
- `07_Componenti/`: BOM candidata e componenti da qualificare.
- `08_Firmware_Prototipi/`: eventuale controllo digitale semplice, senza DSP avanzato.
- `09_Archivi_Precedenti/`: snapshot degli elaborati modificati, quando necessari.

## Verifiche V0.1
Il rapporto `03_Verifiche/V0.1/RAPPORTO_TECNICO_V0.1.md` separa controlli di coerenza sui file da prove elettriche. Rieseguire `python3 -m unittest discover -s 03_Verifiche/V0.1 -p 'test_*.py' -v` dalla radice.

## Pubblicazione
Repository privata del progetto: `https://github.com/jd3485/Superstar3900-THT-Evolution`. La fonte della revisione integrata è `main`. Vedi `GITHUB_PUBBLICAZIONE.md` per la procedura di verifica e manutenzione.
