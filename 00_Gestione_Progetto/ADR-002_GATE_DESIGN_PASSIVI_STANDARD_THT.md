# ADR-002 — Qualifica THT proporzionata al rischio: progettazione versus fabbricazione

**Approvata dall'utente il 12 novembre 2026.** Modifica ed esplicita il precedente criterio di bloccare la progettazione V2.7 finché tutti i 138 componenti avessero un MPN OEM certificato. **Non elimina il criterio di produzione corrente prima della distinta finale** e non modifica l'ADR-001 delle due PCB.

## Tre gate separati

1. **Gate di progettazione degli schemi (progressivo, per sottocircuito).** Le resistenze e i condensatori standard possono essere scelti per specifica funzionale: valore, tolleranza, stabilità, tensione, potenza, temperatura, dielettrico, ESR/ESL e sagoma THT compatibile. Un codice OEM esatto e la certificazione della fabbricazione corrente **non sono prerequisiti globali** per disegnare la successiva funzione della radio. L'assenza di un MPN standard non autorizza a utilizzare package SMD o impronte fittizie. Ogni sottocircuito con criticità RF, alimentazione o sicurezza resta sospeso in attesa delle verifiche necessarie; nessuna inferenza di sicurezza dall'ERC.
2. **Gate di rilascio CAD integrato.** I cambiamenti reali di V2.7 devono avere pin/net corretti, footprint THT ragionevoli, nuova export netlist ed ERC nativo KiCad9, regressioni, test appropriati, review e CI sul commit finale. Nessuna modifica «di riempimento» per chiudere falsamente i blocchi. I componenti unici/critici richiedono verifica di fattibilità di approvvigionamento e caratterizzazione sufficiente **prima di congelare il circuito che ne dipende**; se non disponibile, documentare riserva o percorso alternativo. Il disegno preliminare di sottosistemi indipendenti può proseguire con STOP di release fisica.
3. **Gate prima di BOM definitiva, PCB pronta per fabbricazione e ordini.** Ogni componente **effettivamente montato** in entrambe le PCB deve avere codice d'ordine OEM esatto, dichiarazione OEM di produzione corrente, marcatura THT, geometria/pin-pad, conformità, parametri e fonti aggiornate. Per posizioni DNI bisogna decidere e documentare l'assenza fisica prima di rimuoverle dal denominatore di assemblaggio. Rimane valido il rigoroso `verify_mpn_inventory_v26.py --release` finché non esisterà un controllo finale di assemblaggio di pari rigore che consideri DNI e nuove refs: NON introdurre waiver o consentire un --release verde su MPN non verificati.

## Categorie operative nel classificatore
- **STANDARD_PASSIVE**: R/C industrialmente comuni e realmente intercambiabili **solo dopo verifica delle specifiche elettriche e meccaniche specifiche della posizione**. Nessuna ricerca seriale inutile su uno stesso MPN prima della nuova bozza.
- **RF_PRECISION**: carichi del quarzo, ceramici pF e componenti VCO; dielettrico C0G/NP0, Q, ESR, microfonicità, temperatura e parassiti prima di fissare il blocco.
- **UNIQUE_RF**: PLL ML145151YP U401, L501 Coilcraft, varactor D501, quarzo X401; verifica produttiva o alternativa qualificabile prima del congelamento.
- **SAFETY_POWER**: OVP/UVLO, fusibile/TVS e componenti che determinano regolazione, boost, fault, dissipazione; la disponibilità di resistenze standard **non** esonera dall'analisi delle soglie e dei guasti (#27).
- **INTERFACE_THT**: test header/connettori; schemi possibili su requisiti di interfaccia ma geometria, accoppiamenti e MPN obbligatori prima del layout finale.
- **DNI_REVIEW**: C805 non si qualifica come componente montato finché lo stato DNI non sia confermato nel CAD/BOM.

Questa classificazione è **cautelativa e preliminare**: `03_Verifiche/V2.6/classify_design_risk_v26.py` assegna 138 riferimenti a classi con motivazione e contiene asserzioni di copertura. L'insieme dei componenti standard non conferisce automaticamente un'omologazione o un requisito di performance raggiunto; altri componenti possono essere riclassificati verso classi più rigorose per ragioni circuitali dopo review.

## Priorità operative
A. Non proseguire con la ricerca seriale di 45 resistenze e 42 condensatori generici solo per autorizzare schemi. Conservare le fonti già raccolte nei report PR #41–#49.
B. Valutare **U401** e **L501** OEM attuali o alternative reali THT, prima di congelare PLL/VCO; **L920** e componenti protezione sono gate indipendenti dei blocchi 20V e 13.8V.
C. Continuare **V2.7 nelle sezioni indipendenti** con cambiamenti veri KiCad9 e validazioni elettriche. La precedente frase «STOP V2.7 finché tutti i 138 non sono verificati» è sostituita da **STOP alla finalizzazione dei sottocircuiti critici non qualificati** e da **STOP alla fabbricazione/BOM definitiva**. Questa revisione di policy non è essa stessa un rilascio V2.7.

**Invariati**: due PCB 100% THT, NO FAB, NO GERBER di produzione, NO ORDINI PCB, NO TX, NO alimentazione da batteria/veicolo, review di sicurezza indipendente, e DRC da effettuare solo su PCB reali.
