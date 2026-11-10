# METODO CAD-FIRST — politica operativa permanente per Superstar 3900 THT Evolution

**Data di adozione:** 10 novembre 2026 — in continuità con le revisioni V0.1–V0.9, mai in sostituzione delle verifiche.
**Riferimento unico:** repository indipendente `jd3485/Superstar3900-THT-Evolution` su `main`. Repository SMD distinta, non modificata né importata.

## Risultato finale

Un unico **progetto KiCad elettrico completo**, con sezioni RF/IF/PLL/audio/alimentazioni/comandi e i relativi circuiti analogici THT; successivamente una PCB principale quanto più integrata possibile, tutti i footprint reali a foro passante, netlist coerente, layout RF, netclass/piani massa, DRC nativo, revisione DFM, BOM e (soltanto dopo i gate) Gerber e file di foratura per ordinare PCBWay PCB **nude**. Assemblaggio e saldatura interni. Niente SMD/adattatori.

## Regola di priorità (vincolante per ogni «continua»)

1. All'inizio di ogni revisione leggere HEAD `main`, questo documento, README, handoff, PR aperte, workflow CI e la sezione CAD attiva. Non modificare la repo SMD.
2. Lavorare **per blocchi che diventano schematici native .kicad_sch**: non considerare chiusa una funzione solo perché sono state prodotte tabelle di pin, SPICE o markdown.
3. Per ogni blocco avanzare contemporaneamente, quando pertinente, su: componenti THT e datasheet/MPN, schema KiCad realmente istanziato/pin numerati, netlist, simulazione o modello riproducibile, analisi worst-case, Python/CI, BOM e rapporto. Se impossibile CAD per un blocker fattuale, registrare esplicitamente l'ostacolo e risolvere un sottoblocco CAD indipendente nella stessa revisione ove ragionevole.
4. **Gerarchia e integrazione:** assicurare che i singoli fogli diventino sottoschemi coerenti dello stesso progetto elettrico. Connessioni tra moduli tramite pin gerarchici/globali controllati, non collegamenti immaginari su figure.
5. I file `.kicad_sch`, `.kicad_sym`, `.kicad_pcb` sono CAD effettivo **solo se apribili/esportabili dal KiCad nativo**. Non basta l'estensione. Preferire generatore deterministico con sorgente versionato, libreria locale e test di parità.
6. **Verifiche KiCad come gate:** `kicad-cli sch erc` per il sottoblocco esatto e per ogni futura integrazione, con report e ref della run; `kicad-cli sch export netlist`; quando esiste la PCB `kicad-cli pcb drc` e schema/PCB parity. ERC di foglio parziale ≠ ERC radio completa.
7. Test automatici storici V0.1–V0.9, simulazioni ngspice, firmware PIC THT, controlli normativi RX/TX, componenti e documentazione restano **obbligatori e paralleli**, non vengono sostituiti dal disegno CAD.
8. **Stati qualificati:** `CANDIDATE / CAD_NATIVE / ERC_PASS_SUBBLOCK / SIM_ONLY / CAD_INTEGRATED / PCB_PLACED / PCB_ROUTED / DRC_PASS / LAB_PASS`. Non definire una parte `DONE` mentre mancano i gate necessari; riportare separatamente `NOT_RUN` e `FAIL`.
9. PCBWay: **NO FAB** finché KiCad ERC e DRC sull'intera scheda non sono verdi, libreria pin/footprint comprovata, power/rf/EMI verifiche documentate, DFM e rischi accettati. **NO TX** durante questa fase, nessuna emissione o ordine impliciti.
10. Pubblicazione cumulativa: branch/PR se utile, suite test, merge coerente in `main`; mai cancellare baselines per mascherare errori. Ad ogni revisione registrare **quali pin/reti/footprint o piste sono stati aggiunti** e quali test fisici non sono stati eseguiti.

## Ordine di integrazione concreto

- **CAD-01**: recupero e convalida *nativa* del piccolo filtro PDout → driver LM358 THT; esito ERC e netlist reali. `V1.0` attuale usa R901=22k C901=100n come **variante sperimentale alternativa**, non sostituisce R901=10k/47k e C901=1µF del modello V0.9: parametrizzare e qualificare in seguito.
- **CAD-02**: PLL U401 ML145151 con prescaler U402, clock/quarzo e alimentazione, link ai segnali di filtro/driver, pinout da datasheet e transitori phase detector reali o best model; rimuovere moduli non approvati.
- **CAD-03**: VCO Colpitts, buffer LO e interfaccia di mixer RX + protezioni VTUNE; progredire dal vendor SPICE al CAD.
- **CAD-04**: supply +13.8V → +5/+20V pulita, protezione batteria, controlli powergood/mute, separazione buck/boost EMI.
- **CAD-05**: antenna e protezione ingresso, preselettore RF, AGC/mixer, IF1 10.695MHz, IF2 455kHz e demodulatori AM/FM/SSB/CW, audio e controlli.
- **CAD-06**: selettore bande/canali 270 RX, microcontrollore PIC THT e firmware, display/strumenti, interfacce meccaniche manual tuner + bypass.
- **CAD-07**: schema master gerarchico, netlist e ERC integrati, PCB principale, posizionamento e routing, DRC, revisione e produzione *solo dopo gate*.

**La priorità CAD non elimina calcoli, firmware, SPICE, BOM, test e documentazione: significa che ogni revisione deve contribuire visibilmente all'artefatto elettronico completo.**

## Mandato operativo autonomo THT — V1.1 (2026-11-10)

- **Responsabilità di sviluppo:** procedere autonomamente, revisione dopo revisione, dal progetto nativo KiCad agli schemi integrati e alla PCB principale, senza fermarsi per chiedere conferma su ogni singolo componente, valore preliminare, scelta di layout o test riproducibile. Le scelte tecniche reversibili devono essere motivate e versionate.
- **Doppio avanzamento obbligatorio:** ad ogni passaggio ottenere, ove realizzabile, un incremento concreto `.kicad_sch` oppure `.kicad_pcb` (pin/reti/footprint/posizionamento/piste), **insieme** a simulazioni, firmware THT, analisi di tolleranza/temperatura/rumore, validazione di datasheet, BOM, script e test pertinenti. Non spacciare documenti o test software per avanzamento fisico CAD.
- **Critica tecnica prima dei numeri di revisione:** se un elemento non può essere schematizzato correttamente, annotare la dipendenza e risolvere prima un altro blocco CAD autonomo. Non aumentare artificialmente le versioni.
- **Requisiti rigidi:** solo THT e progetto separato dalla versione SMD; un solo PCB principale ove tecnicamente praticabile; PCBWay esclusivamente PCB nude, montaggio e saldatura interni.
- **Qualifica progressiva:** prima sottoblocchi verificati con KiCad ERC/netlist, poi master gerarchico con ERC totale, quindi PCB piazzata/sbrogliata e DRC, revisione RF/EMI/termica, DFM, collaudo prototipo. Un PASS del sottoblocco non è un PASS della radio.
- **Quando coinvolgere il committente:** modifiche funzionali fondamentali, compromessi irreversibili, deroga THT, eventuale cambio da una a più PCB, acquisti/produzione e attivazioni RF. Nessun acquisto, ordine o TX viene autorizzato implicitamente.
- **Regola di pubblicazione:** conservare gli artefatti e le versioni storiche, aprire PR, verificare CI e integrare in main solo una revisione coerente; documentare PASS/FAIL/NOT_RUN separatamente. Non toccare il progetto SMD.
