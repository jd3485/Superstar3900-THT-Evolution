# V2.6 — Audit componenti critici presso i produttori (12 novembre 2026)

**Risultato importante:** lo script inventario precedente includeva erroneamente tre PWR_FLAG senza componente fisico (PWR701, PWR801, PWR802), omettendo invece **Q801, D804 e R1011**. Le righe erano 138 ma sbagliate! Il nuovo estrattore esamina **ogni blocco simbolo distinto**, richiede footprint e in_bom/on_board yes e verifica esattamente 138 riferimenti fisici. Tutti i componenti del CAD sono ora presenti. Le 3 posizioni ripristinate non sono variazioni dello schema elettrico.

## Ricerca ufficiale per sei posizioni ad alto rischio

| Ref | Codice e fonte ufficiale | Stato verifica produzione |
|---|---|---|
| **Q801** | Infineon **IRF9540NPBF** TO-220, https://www.infineon.com/part/IRF9540N | **ATTIVO_CONFERMATO** sul codice esatto. Non valida automaticamente VGS ±20V, SOA, fault o derating |
| **U802** | TI **TL431BCLP** TO-92, https://www.ti.com/product/TL431/part-details/TL431BCLP | **ATTIVO_CONFERMATO**, ma versione commerciale 0..70°C; qualificare ambiente e guasti |
| **U801** | TI **LM393N/NOPB** ACTIVE PDIP-8, https://www.ti.com/product/LM393-N/part-details/LM393N/NOPB | **DA_VERIFICARE:** il CAD ha il descrittivo LM393N_DIP8_DUAL, non l'MPN d'ordine /NOPB; confrontare 36V abs, temperatura 0..70°C, pinout |
| **U401** | Lansdale **ML145151YP** PDIP28, https://lansdale.com/datasheets/ML145151_ML145152_ML145155_ML145156_ML145157_ML145158_revA.pdf | **DA_VERIFICARE:** datasheet del codice esatto come equivalente MC145151P2; Lansdale dichiara produzione di IC legacy, ma **non conferma fabbricazione corrente di questo MPN in particolare** |
| **U402** | Toshiba **TC74AC74P(F)** DIP14, https://toshiba.semicon-storage.com/eu/semiconductor/product/general-purpose-logic-ics/detail.TC74AC74P.html | **DA_VERIFICARE:** codice d'ordine rappresentativo; Toshiba avverte che la forma specifica potrebbe non essere venduta |
| **U911** | ST **MC34063ABN** DIP8, https://www.st.com/en/power-management/mc34063ab.html ; https://estore.st.com/en/products/power-management/dc-dc-switching-converters/buck-boost-regulators.html | **CONFLITTO_FONTI**: scheda prodotto ST Active, alcune pagine eStore NRND. Richiedere conferma scritta al produttore |

**Conteggio corretto delle 138 posizioni:** 2 MPN esatti con fonte ufficiale Active, 1 conflitto fra fonti ST, 135 **DA_VERIFICARE**. I sei componenti prioritari sopra sono stati esaminati; l'intero resto non viene dichiarato qualificato.

**Prossimi passi:** confermare con Lansdale che **ML145151YP venga effettivamente fabbricato adesso** (non solo stock/NOS/die banking), disponibilità e minimo d'ordine. Chiarire con ST status MC34063ABN. Valutare più ampia temperatura per TL431/LM393 prima della V2.7; procedere al doppio power-good indipendente (Issue #27) soltanto con componenti attivamente prodotti e qualifica elettrica. **NO FAB, NO TX, NO BATTERIA/VEICOLO**. Nessun CAD cambiato; ADR-001 due PCB e S-meter analogico confermati.
