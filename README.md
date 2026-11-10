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
