# STATO ATTUALE — V0.9 (10 novembre 2026)

**PDOUT DEL PLL A TRE STATI, NON UNA SORGENTE DI TENSIONE DC:** ML145151YP PDout pin4 fornisce impulsi positivi/negativi in fase di correzione ed è alta impedenza in lock; LD pin28 non può essere trattato come un interblocco RX senza qualificazione temporale. Progettata la prima interfaccia con R901=22kΩ/C901=100nF THT, LM358N PDIP8 già studiato a guadagno4, C805 marcato **DNI** per non duplicare C505 VTUNE del VCO. **NON È UN PLL COMPENSATO**.

**Nuove prove:** modellazione di piccolo segnale su 4 tratti KVCO V0.6, smorzamento ideale ζ≈0,33–0,53 (potenziale sovraelongazione). Eseguite 3 transienti ngspice con phase-detector a tre stati IDEALE e perdite ASSUNTE 0/20/100nA, effettiva deriva VTUNE fino60mV su15ms alla condizione 100nA; non vero PLL né circuito vendor.

**CAD:** primo schema nativo parziale `04_KiCad/V0.9/PLL_LOOP_RX_PARTIAL_V0.9.kicad_sch` e generatore riproducibile, KiCad9 native ERC eseguito sul foglio isolato; verificare ultimo rapporto CI prima di dichiarare PASS. Mancano U401/U402 e VCO nello stesso sheet, driver alimentatore reale, ERC completo radio e layout/DRC.

**GATE:** progetto PCBWay ancora non pronto. No prove hardware, NO FAB / NO TX. Prossima V0.10: loop PLL compensato e sorgente boost realistica, interblocchi mute/LD e CAD integrato.

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
