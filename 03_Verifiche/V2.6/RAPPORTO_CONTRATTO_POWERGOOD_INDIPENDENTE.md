# V2.7 pre-CAD — Contratto tecnico di secondo power-good indipendente (NON una revisione KiCad)

**Scopo:** definire e verificare *prima* di disegnare la nuova sezione un requisito chiaro per evitare i bypass OVP/UVLO documentati dalla PR #34: un secondo attuatore di disconnessione **in serie** e un secondo supervisore OVP+UVLO alimentato/riferito con modalità di guasto separate. Entrambi i percorsi devono dare consenso per alimentare il carico. Questi elementi **non esistono ancora** nel master KiCad V2.6.

## Architettura candidata, da ingegnerizzare

`FUSED_RAW -> Q801 (interruttore attuale, attivo solo con OVP1 && UVLO1) -> Q804 [SECONDO INTERRUTTORE CANDIDATO] (attivo solo con OVP2 && UVLO2) -> rail protetta finale`.

Il nome `Q804` è provvisorio e **non** identifica MPN, tensioni ammissibili, footprint né schema realizzato. La nuova unità deve poter bloccare l'alimentazione anche se Q801, Q802 o Q803 sono guasti in corto. Per evitare una falsa ridondanza, OVP2 e UVLO2 non devono dipendere dagli stessi output, gate-sink, supply inaffidabile o singolo TL431 della prima catena. Un futuro segnale **PG_OK** e **MUTE** separato, di default inibito, deve essere verificabile su RX/audio e su eventuali comandi TX futuri (non presenti e non autorizzati).

## Requisiti testabili

1. Su VIN fuori dal dominio normale (OVP negato o UVLO negato), **nessuna singola** avaria modellata come 'stuck allow' in un percorso deve rendere ON la rail finale.
2. Un corto C-E di Q802 o Q803, il corto D-S di Q801, oppure un'uscita di uno dei due supervisori bloccata a consenso non devono eludere l'altro veto *se realmente indipendente*.
3. Guasto comune che imposti **entrambi** i percorsi a consenso rimane pericoloso; una sola condizione condivisa upstream non può essere definita indipendente.
4. Nuovo schema obbligatorio: reale secondo dispositivo di interruzione e comparatori/reference/drive THT; definire guasti APERTO/CORTO, tensioni assolute, leakage, dissipazione, VGS, startup/brownout, peak faults e carichi. L'input non deve vedere +48 V o transitori automotive per presunzione.
5. Verifiche KiCad9: export nativo, ERC0, Q801/Q804 in serie con continuità netlist, tutte le connessioni THT, confronto invarianti V2.6; ngspice con modelli vendor quando reperibili, test di laboratorio e DRC solo su PCB reale.

Il test `03_Verifiche/V2.6/screen_independent_pg_contract_v26.py` valuta **48 casi ideali** (12 modalità tra cui sano, singoli corti, uscite stuck-allow, un solo riferimento guasto); mostra che la catena attuale può aggirare OVP/UVLO, mentre un'ipotetica doppia catena **perfettamente indipendente** impedisce l'abilitazione in quei casi. Testa esplicitamente anche un guasto comune a due percorsi, che **NON** è coperto. Con input netlist KiCad9 verifica l'esatta topologia V2.6 e l'**assenza** del secondo MOSFET: non confondere il contratto con uno schema già realizzato.

**Non è una qualifica hardware né una nuova revisione CAD.** Non esiste ancora PG/MUTE, né Q804, né un secondo riferimento. Il comportamento dei MOSFET, le correnti, gli ingressi reali dei comparatori e il dominio di tensione non sono simulati. La raccomandazione è un punto di partenza **da sottoporre a confronto con alternative** (due controlli che interrompono rail diverse, relè off-by-default, inibizione carichi), non un componente già selezionato.

**Priorità:** Issue #27 finché la reale protezione non è implementata; conservare ADR-001 (due PCB, frontale Evolution e S-meter a lancetta). No fabbricazione, gerber, TX o collegamento veicolo/batteria.

Fonti: [Texas Instruments LM393-N](https://www.ti.com/product/LM393-N) (Vs massimo 36 V), [TI TL431 datasheet](https://www.ti.com/lit/ds/symlink/tl431.pdf) (corrente minima di regolazione), [precedente audit singolo guasto](RAPPORTO_Q802_Q803_GUASTO_SINGOLO.md).
