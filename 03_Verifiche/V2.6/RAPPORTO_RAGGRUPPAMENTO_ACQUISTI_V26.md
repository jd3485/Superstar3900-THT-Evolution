# Preparazione audit acquisti THT V2.6 — raggruppamento deterministico (12 novembre 2026)

## Stato e problema
L'inventario reale V2.6 ha **138 posizioni fisiche**: 45 resistori, 42 condensatori, 22 connettori, 11 diodi, 9 IC, 5 transistor, 2 induttori, un fusibile e un quarzo. Sono presenti **114 gruppi distinti di (valore CAD, impronta)**; un gruppo non prova che le posizioni siano elettricamente equivalenti o che abbiano lo stesso MPN ordinabile. L'audit originale resta **6/138 ATTIVO_CONFERMATO; 132/138 DA_VERIFICARE**.

## Modifica sostanziale agli strumenti
- Nuovo `group_procurement_v26.py`: esporta `RAGGRUPPAMENTO_ACQUISTI_V26.csv` da `INVENTARIO_MPN_V26.csv` senza modificarne alcuna riga. Ogni gruppo conserva refs fisiche, numero di posizioni, riassunto lifecycle e prossimo controllo; nessuna rete KiCad toccata.
- `verify_mpn_inventory_v26.py` verifica che i 114 gruppi coprano esattamente tutte le 138 refs senza perdite o duplicati. La conferma OEM e il gate `--release` restano **per singola posizione**, indipendenti dal raggruppamento.
- La nuova suite Python è collegata al verificatore di inventario già presente nelle regressioni storiche; la validazione nativa completa va comunque lasciata alla CI di PR sullo SHA finale. Nessuna prova locale KiCad o SPICE è dichiarata.

## Procedure successive
1. Trattare innanzitutto gli insiemi ad alto riuso: condensatori bypass 100n/100nF, 10µF e resistori 10k/47k. Prima di assegnare un solo MPN a un gruppo, verificare tensione, dielettrico, Q, TCC, ESL/ESR, tolleranza, potenza e dimensioni per **ogni riferimento**: uguale footprint/valore non implica uso equivalente.
2. Registrare codici OEM ordinabili *esatti* e lo stato di fabbricazione attivo per ogni ref. La disponibilità a magazzino e l'esistenza di datasheet non sono prova di fabbricazione.
3. Componenti a maggiore rischio architetturale U401 (Lansdale ML145151YP) e L501 (Coilcraft 150-05J08L) richiedono risposta ufficiale sullo SKU e nuovi lotti fabbricati. L920 Bourns e F701 Littelfuse restano in verifica.
4. Separare **C805 = DNI** da componenti realmente da montare prima di emettere distinta di assemblaggio; per il gate storico la posizione continua a essere monitorata fino a decisione CAD documentata.
5. Procedere alla vera V2.7 circuitale e PCB soltanto dopo il gate produttivo completo; Issue #27 sicurezza rimane indipendentemente aperta.

Nessun nuovo MPN è stato dichiarato ACTIVE con questa revisione. **NO FAB / NO TX / NO batteria / NO veicolo.**
