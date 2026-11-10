# Registro prove V0.5

**Nuova suite:** `03_Verifiche/V0.5/test_v05.py` (34 controlli aritmetici, pin-net e sicurezza RX). Regresso previste V0.1(12), V0.2(24), V0.3(32), V0.4(34), V0.5(34) = **136** controlli.

**Prima della pubblicazione:** GitHub CI `NOT_RUN` sul nuovo commit. Non affermare PASS fino a verifica dell'ultima run.

**SPICE:** `VCO_COLPITTS_CANDIDATE_V0.5.cir` è un circuito testuale compatibile con un progetto di simulazione ngspice; esecuzione, convergenza, frequenza/swing e validazione transistor/varicap **NOT_RUN**.

**KiCad ERC/DRC:** `NOT_RUN` (nessuna PCB); V0.4 schematico prescaler rimane presente e recuperabile.

**Hardware, PCBWay e TX:** `NOT_RUN` — non ordinare, non alimentare TX, non emettere.

## Esito GitHub Actions realmente verificato

- Pull request [#1](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/1), integrata su `main`; commit di merge `adcf50decfb035839b60e381cce489dc59803369`.
- [Run PR 42815333235](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42815333235): **SUCCESS** dopo correzione del test storico V0.4.
- [Run main 42815442825](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42815442825): **SUCCESS**, commit `adcf50d`. Cinque suite software: V0.1 (12), V0.2 (24), V0.3 (32), V0.4 (34), V0.5 (34) = **136 test**, tutte le suite eseguite con successo.
- La prima run sulla PR aveva evidenziato un test V0.4 dipendente dai primi 200 caratteri del file handoff: corretto in branch, con esito successivamente PASS, prima del merge.
- **Non eseguiti**: ngspice reale sul deck V0.5, KiCad nativo ERC/DRC, prototipi, misure RF. **NO FAB / NO TX**.
