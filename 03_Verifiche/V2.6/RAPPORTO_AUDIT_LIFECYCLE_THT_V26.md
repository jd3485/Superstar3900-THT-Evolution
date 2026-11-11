# Audit componenti THT V2.6 — inventario riproducibile, non approvazione BOM

**Regola B approvata dall'utente (11 novembre 2026):** tutti i componenti finali, per PCB-MAIN e PCB-FRONT, devono essere THT e **attualmente in produzione presso il fabbricante**. Una scorta di distributore non è prova di produzione.

Questa prima fase produce un **inventario deterministico di tutti i 138 riferimenti CAD** della gerarchia KiCad9 V2.6: `03_Verifiche/V2.6/INVENTARIO_MPN_V26.csv`. Script di coerenza: `03_Verifiche/V2.6/verify_mpn_inventory_v26.py`. L'inventario non contiene 138 codici produttore certi: il campo KiCad `Value` talvolta contiene un valore generico o descrizione, e la libreria `lib_id` è un nome simbolo, **non** una prova di lifecycle. Tutte le righe rimangono esplicitamente `DA_VERIFICARE`, `mpn_exact_confirmed=NO` finché una fonte ufficiale sullo specifico codice non conferma stato e confezione.

## Verifica iniziale mirata — dispositivi ad alto rischio di disponibilità

- **U401, ML145151YP, PDIP28 (PLL): PRIORITÀ MASSIMA.** Il codice è legacy e non abbiamo trovato una conferma ufficiale attuale della produzione esatta in questo audit. **Non dichiararlo EOL senza evidenza, ma non approvarlo come attivo**. L'eventuale sostituzione può imporre riprogettazione PLL, divisori e controlli, non una sostituzione automatica.
- **U402, TC74AC74P(F), DIP14 (Toshiba):** la [pagina ufficiale Toshiba](https://toshiba.semicon-storage.com/eu/semiconductor/product/general-purpose-logic-ics/detail.TC74AC74P.html) presenta il codice ordinabile `TC74AC74P(F)`, package **DIP14 through-hole**, informazioni RoHS e documenti aggiornati nel 2026. È un **segnale positivo**, ma Toshiba precisa che i codici elencati sono rappresentativi e potrebbero non essere venduti nella forma esatta; quindi **stato produttivo da confermare** tramite produttore/canale autorizzato. Non segnare «attivo confermato» senza prova più forte.
- **U801 LM393N, U802 TL431BCLP, Q801 IRF9540NPBF, U911 MC34063ABN, L501 150-05J08L, L920 RLB0914-681KL:** priorità per conferma produttore MPN esatto, package, revisioni e parametri; la scelta del secondo interruttore/supervisore deve partire da MPN attivi verificati, non dal solo simbolo.
- Resistenze, condensatori, cristallo, connettori, diodi e fusibili richiedono **MPN esatto**, incluse serie/package e specifiche, prima della distinta finale. Non confondere valore nominale con un codice d'ordine.

## Procedura successiva
1. Verificare presso il **fabbricante** (data e URL) lo stato di ogni **MPN distinto**, prima i dispositivi che determinano l'architettura. Annotare `ATTIVO_CONFERMATO`, `DA_VERIFICARE` oppure `EOL_NRND` soltanto con prova documentata.
2. Per ogni sostituzione proposta: controllare pinout, footprint, caratteristiche RF, tensioni, tolleranze, corrente/termica, disponibilità e interazione con gli altri blocchi. **Non modificare la V2.6 per presunzione**.
3. Progettare la seconda catena power-good della Issue #27 **solo con candidati THT attivamente prodotti e qualificabili**, distinguendo schemi CAD da prove vendor/hardware.
4. Il file CSV è un inventario CAD e **non una BOM autorizzata**; mantenere divieto **NO FAB / NO TX / NO BATTERIA/VEICOLO**. ADR-001 due PCB e S-meter analogico restano vincolanti.

**Nessuna modifica a KiCad, nessuna PCB o DRC, nessuna approvazione produzione.**
