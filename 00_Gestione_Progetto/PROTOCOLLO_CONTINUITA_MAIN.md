# Protocollo permanente di continuità THT

1. **Autonomia assoluta:** nessun fork, dipendenza o sincronizzazione con la versione SMD. Le specifiche e le decisioni vigenti sono **solo** quelle della repository THT.
2. **Fonte di verità:** `main` contiene l'ultima revisione progettuale integrata. Un tag precedente è una fotografia immutabile, non necessariamente la revisione più recente.
3. **Ripresa in ogni chat:** verificare HEAD `main`, tag, PR e CI, poi README, handoff, stato e ultimo rapporto. Non dipendere dalla memoria delle chat.
4. **Progettazione incrementale reale:** ogni revisione aggiunge un sottosistema o risolve una dipendenza tecnica, non solo controlli ripetuti. Produrre specifiche, topologie, componenti THT, pinout, BOM, calcoli e test quando pertinenti.
5. **Revisioni e merge:** usare branch/PR temporanei se utili; integrare in `main` solo revisioni coerenti. Test FAIL o blocchi sostanziali vanno riportati e risolti, non occultati.
6. **Preservazione:** cronologia Git e tag, sorgenti precedenti e documenti storici sempre recuperabili. Ogni modifica significativa a una decisione aggiorna registro, documenti impattati, rapporto e handoff.
7. **Evidenze:** separare espressamente PASS/FAIL/SKIP/NON ESEGUITO e distinguere test statici, modello matematico, simulazione SPICE, KiCad ERC/DRC, verifica CAD meccanica, misure di laboratorio, test EMC/normativi.
8. **THT rigoroso:** nessun componente SMD sulle schede e nessun adattatore SMD→DIP. Se una funzione richiede SMD, cercare un'architettura differente o sottoporre a decisione esplicita una rinuncia funzionale.
9. **Produzione:** PCBWay fabbrica **le sole PCB nude**; acquisto, saldatura e montaggio componenti sono interni. Nessun acquisto, produzione o abilitazione TX è implicato da una simulazione riuscita.
10. **Obiettivo PCB:** una PCB principale integrata è la preferenza di progetto. La necessità tecnica di schede separate o componenti meccanici su telaio va motivata e approvata prima di cambiare l'obiettivo.
11. **Sicurezza:** nessuna trasmissione RF e nessun prototipo dichiarato operativo o sicuro senza verifica hardware, protezioni, requisiti normativi e autorizzazioni pertinenti. Interblocchi progettuali fail-closed.
12. **Manifest:** ciascun `MANIFEST_SHA256_Vx.y.csv` è legato alla sua specifica baseline/versione; non confrontare il manifest storico di un tag con il `main` di revisioni successive.
