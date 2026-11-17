# V2.7 — guasti OPEN/SHORT ai resistori di gate dei due stadi PMOS THT

**17 novembre 2026 — laboratorio KiCad9 ISOLATO.** Topologia reale controllata: 24 componenti THT, 54 pin e 14 reti; coppie anti-serie Q804/Q805 e Q814/Q815, ciascuna con Rgs 47k, resistenza pilotaggio 10k, BJT dedicato, due diodi 1N4106-1 paralleli gate-source candidati. Le reti native sono verificate nel nuovo `verify_two_stage_gate_resistor_fault_native.py`; esecuzione registrata in FULL CI.

L'audit assume **entrambi i diodi Zener OPEN**, ovvero non introduce curve OEM fittizie. Enumerati 6 valori sorgente ipotetici (0, 13,8, 20, 24, 36, 48V), tre corner di ogni R ±5%, Rgs NOM/OPEN/SHORT, sink 10k NOM/OPEN/SHORT, driver OFF/SINK: **972 scenari matematici per stadio, 1.944 complessivi**. Il dominio non è operativo e non autorizza 36/48V.

Per ogni stadio: **216/972 gate FLOATING/INDETERMINATI** quando il pull-up è OPEN e manca percorso controllato; **54/972 corti ideali tra source e ritorno** con entrambi resistori SHORT e driver SINK, energia/corrente non calcolabili dal circuito resistivo ideale; tra i casi DC definiti **100/972 superano |Vgs|=20V** nel modello, con massimo teorico **48V**. Massima dissipazione resistiva nominale calcolata in corner: Rgs **0,051601W** e Rserie **0,242526W** (non valutano impulsi, derating né sicurezza). I due stadi presentano conteggi uguali per identico circuito, non per indipendenza di supply/return/comandi.

La categoria FLOATING non è un valore zero né un comando OFF sicuro: richiede analisi di leakage, capacità gate, scarica, startup/brownout e hardware. Il corto ideale senza impedenza è un indicatore di rischio, **non** una previsione numerica di corrente: servono F701, TVS, protezioni upstream, cablaggio, driver e SOA reali. Anche i modelli già presenti sulla topologia di source/body-diode individuano dipendenze comuni. L'analisi non costituisce qualifica OEM o prova di banco.

Issue #27 resta **OPEN**. MAIN e FRONT non dispongono di PCB finite. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
