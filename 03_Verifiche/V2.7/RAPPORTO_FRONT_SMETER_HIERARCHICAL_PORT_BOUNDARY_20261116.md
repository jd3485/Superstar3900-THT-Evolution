# FRONT S-meter: due porte gerarchiche isolate verso la sorgente MAIN ancora da progettare

**16 novembre 2026 — integrazione KiCad9 candidata, non qualificata.**

La scheda FRONT di studio a cinque fogli conteneva il S-meter come foglio senza porte sul master. Il connettore J1801 era presente nel foglio figlio, ma mancava l'attraversamento gerarchico esplicito. Nel candidato aggiornato:
- J1801/1 (`METER_DRIVE_CANDIDATE`) e J1801/2 (`METER_RETURN`) sono associati a due `hierarchical_label` passivi nel foglio figlio, conservando la loro distinta identità elettrica e le reti dei resistori R1801/R1802;
- il foglio FRONT master dichiara due sheet pin passivi corrispondenti con due corti fili su **reti separate** e due etichette corrispondenti. Non si collega ad altri fogli, alimentazioni, audio o massa `AF_GND`;
- i verificatori `verify_front_partial_hierarchy_native.py` e `verify_smeter_front_harness_isolation_native.py` devono controllare **KiCad9 ERC senza violazioni**, esportazione netlist master, 5 fogli, 32 riferimenti, 22 reti, 71 pin e domini separati.

Questo è solo un confine elettrico di progetto FRONT: NON introduce sorgente/ritorno su MAIN, guaina cavo, connettori di accoppiamento reali, ground-bond, driver S-meter, calibrazione, FSD certificata o schema PCB fabbricabile. I vincoli della PR #289 (FSD ipotetica, guasto resistori) restano validi e non equivalgono a un'autorizzazione di alimentare la bobina.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
