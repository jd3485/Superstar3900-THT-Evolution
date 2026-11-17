# PMOS two-stage gate RC step — synthetic native-net envelope (17 November 2026)

This *isolated* KiCad9 THT lab retains 24 symbols, 54 pins and 14 electrical nets. The new FULL regression checks both 47k source-to-gate resistors, sink paths and source/gate Zener connectivity in the exported native netlist.

For each of the two stages: 3 × Rgs ±5%, 3 × **assumed** aggregate gate capacitances (1/10/100 nF), 4 × hypothetical OFF-state leakage sink currents (0/5/25/100 µA), 2 × hypothetical source potentials (13.8 and 48 V), and 4 × elapsed times (0/1/3/5 τ) give 288 artificial RC steps per stage, 576 total. Formula is `|Vgs|(t) = min(Vsource,Ileak·Rgs)·(1−exp(−t/(Rgs·C)))`, starting at gate-source voltage 0. Analytic 54/288 cases per stage reach ≥2 V, 36/288 ≥4 V, with maximum ~4.902 V; time constants range 44.65 µs to 4.935 ms. Thresholds 2/4 V are markers only, **not** real IRF9540NPBF Vth distributions or switching thresholds.

The initial-condition and first-order assumption does **not** model real gate capacitance, charge, Miller effect, semiconductor nonlinearities, driver currents or PCB parasitics. It does not establish leakage magnitude, guaranteed OFF, recovery time, Zener behavior, or safety. 48 V is a mathematical fault point and cannot be applied to hardware. Future work: authentic OEM gate charge and leakage bounds across PVT, common supply fault and startup tests, measured RF/EMI/load conditions. Issue #27 remains OPEN.

PR #336 merged on main `844cde2d4c45e4cf28e53bb65071f9fb38135d80` after run #44075051941 FAST/FULL/Required SUCCESS, but hardware remains unqualified. Current RC review stays DRAFT pending its own final SHA CI. No new MAIN/FRONT PCB or production DRC.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
