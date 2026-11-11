# V2.5 — Revisione circuitale: retroazione condivisa OVP/UVLO (BLOCCANTE)

La netlist KiCad V2.5 verificata su PR #28 condivide U801 pin1 e pin7 sul nodo `CMP_OUT`. R1005 (1 MΩ) collega `CMP_OUT` al nodo `CMP_PLUS` del comparatore OVP, R1004 (100 kΩ) collega lo stesso `CMP_PLUS` a `VREF2V5`. Il canale B UVLO, nel portare basso CMP_OUT, altera dunque la soglia di comparazione OVP. Non esiste isteresi autonoma del canale UVLO.

## Screening numerico riproducibile

Lo script `audit_interazione_ovp_uvlo_v25.py` calcola `CMP_PLUS=(Vref/R1004+Vout/R1005)/(1/R1004+1/R1005)` e la corrispondente tensione grezza equivalente tramite R1002=56,2k e R1003=10k. Ipotesi ideali: Vref=2,5 V; Vout LOW=0,25 V; Vout rilasciato=2,5 V. Risultati: OVP circa **15,196 V** con uscita bassa e **16,550 V** con uscita rilasciata ideale; scostamento **1,354 V**. Screening in 144 scenari di tolleranze illustrative; nessuna validazione PVT vendor.

**Limite:** il nodo rilasciato non è risolto con carichi reali R1006/R1007/Q802 e saturazione LM393. Nessun modello temporale, termico o di guasto TL431, LM393 o MOSFET. Il test PASS indica la presenza dell'interazione nel modello passivo, NON la sicurezza o il funzionamento reale. Non aggiungere un singolo resistore `CMP_OUT`–`UVLO_SENSE` come presunta soluzione: il feedback dei due canali rimarrebbe accoppiato.

Per il prossimo circuito: valutare uscita e rete di retroazione UVLO indipendenti, poi verificare con datasheet, simulazioni realistiche e laboratorio le rampe, il chatter, le soglie, il common-mode, i guasti singoli e la risposta del gate high-side. PR #28 resta DRAFT, issue #27 OPEN. Nessuna PCB/DRC/Gerber e NO FAB / NO TX / NO BATTERIA / VEICOLO.

Fonti: https://www.ti.com/product/LM393-N ; https://www.ti.com/lit/ug/tidu020a/tidu020a.pdf
