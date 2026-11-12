# Audit OEM lotto 3 — Schottky, induttore boost e fusibile (12/11/2026)

## Perimetro e risultato
Inventario fisico V2.6: **138** posizioni THT, **6** `ATTIVO_CONFERMATO` e **132** `DA_VERIFICARE`. Nessun campo lifecycle promosso. Questo rapporto documenta specifici SKU individuati, un rischio elettrico verificabile e una questione di conformità. **Non costituisce calcolo PVT completo, simulazione SPICE vendor, prova fisica o rilascio BOM.** Nessuna variazione CAD/netlist.

### D701, D804, D805, D920 — diodi Vishay 1N5819
Pagina tecnica OEM [Vishay 1N5819](https://www.vishay.com/en/diodes/schottky/do41-204al/) elenca **1 A / VRRM 40 V / DO-41 (DO-204AL)**. [Tabella qualità produttore](https://www.vishay.com/en/product/88525/tab/quality/) identifica i codici commerciali **1N5819-E3/54** e **1N5819-E3/73** e conformità RoHS **con esenzioni**. Il valore attuale CAD non sceglie tra gli SKU, quindi resta incompleto. La pagina catalogo/qualità non è una prova esplicita che lo SKU esatto sia ancora prodotto: chiedere conferma di lifecycle attuale.

**Rischio elettrico da affrontare prima dell'approvazione:** 40 V è il massimo nominale di tensione inversa ripetitiva, non un margine per fault fino a 48 V o picchi induttivi. I quattro diodi sono in reti diverse e non vanno trattati come automaticamente intercambiabili: per ciascuno calcolare tensione inversa massima ai nodi, perdita inversa in temperatura, potenza diretta e surge. **D920** lavora sul boost circa 28 V: controllare reverse peak, overshoot e ringing; non dichiarare violazione accertata senza forma d'onda. **D804/D805** appartengono al circuito di controllo prima dell'interruttore high-side, quindi servono verifiche guasti e limiti del LM393. Qualunque sostituzione richiederà verifica pad e terminali.

### L920 — Bourns RLB0914-681KL
[Datasheet Bourns](https://www.bourns.com/docs/product-datasheets/rlb.pdf) elenca **680 µH ±10%, DCR max 1.6 Ω, Irms tipica 0.49 A, Isat tipica 0.9 A**. [Comunicazione PCN OEM](https://www.bourns.com/docs/technical-documents/product-change-notifications/Bourns_IC25041_Marking_Ink_PCN.pdf) cita lo SKU esatto fra i codici toccati da modifica dell'inchiostro di marcatura. **PCN non equivale a conferma attuale che nuovi lotti siano prodotti su ordinazione.** Non promuovere lifecycle senza dichiarazione SKU o stato di ordinabilità dal produttore. Verificare inoltre corrente di picco boost, saturazione e variazione dell'induttanza con temperatura/corrente; ESR e layout RF/EMI.

### F701 — Littelfuse 0251.500MXL
Oltre al certificato RoHS OEM già registrato, la [dichiarazione REACH Littelfuse](https://www.littelfuse.com/assetdocs/reachsvhc-declaration-contain0251?assetguid=960ab68a-ff37-4886-a374-9ec47e957443) del **15/05/2026** identifica il codice esatto e segnala **piombo (Pb) in saldatura**, con concentrazione indicata del materiale **85–95%**. Questo dato **non significa** che l'intero fusibile sia composto per l'85–95% da piombo. Verificare conformità del prodotto finito e fattibilità di un codice THT alternativo se necessario. La dichiarazione ambientale non dimostra produzione corrente, né coordinamento elettrico F701/D702.

## Prossimi gate e operazioni
1. Ottenere riscontro lifecycle OEM su **1N5819-E3/54** o **1N5819-E3/73**, **RLB0914-681KL**, **0251.500MXL**, senza confondere catalogo, certificate e produzione.
2. Completare analisi per-diodo dei 40 V su ciascuna rete (caso normale, reverse, guasto singolo, sovratensione, temperatura e transitori); se i margini non bastano, identificare equivalenti THT da qualificare, non sostituire alla cieca.
3. Valutare picco di corrente L920, saturazione, termica, efficienza boost e EMI; confronto con THT alternativo solo dopo verifica.
4. Restano prioritari U401 ML145151YP e L501 Coilcraft 150-05J08L per prova produzione corrente. Verificare MPN specifici per passivi e connettori.
5. Dopo qualifica documentale e simulazioni reali: branch CAD, KiCad 9 ERC e netlist pin-pad-net, gate CI final HEAD. **Non** richiedere PCB layout/DRC finché non esiste la scheda.

**Divieti:** NO FAB / NO GERBER di produzione / NO TX / NO BATTERIA-VEICOLO. CAD V2.6 invariata; BLOCK release ancora attivo.
