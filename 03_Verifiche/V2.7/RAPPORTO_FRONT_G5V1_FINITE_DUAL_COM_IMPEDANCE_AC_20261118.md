# FRONT six-pin G5V-1 dual-COM finite-impedance AC screening — 18 Nov 2026

PR [#351](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/351) was **merged** as main `f09d3b6d9ae81ea0dce9b77d058ef8054681887e` from final head `ff712737bdba66a02405a241ae41877028bdc7c5`, after run #44278619593 FAST/FULL/Required **3/3 success**. The previous native six-terminal, 64-state relay AC analysis used ideal COM copper bonding.

This new FULL regression `03_Verifiche/V2.7/verify_front_g5v1_sixpin_dual_com_impedance_ac_native.py` exports the actual FRONT five-sheet G5V-1 six-pin candidate KiCad9 netlist and verifies both physical COM5/COM6, NC1, NO10, R1901/2 and ground. Two independently implemented **three-node complex nodal KCL and reduced Norton** methods screen finite hypothetical COM solder resistance 0.05Ω and 5Ω or open, both contact resistances 0.1Ω or 10Ω, relay coil on/off, NC stuck open, NO welded, frequencies 300/1000/3000 Hz, 100pF/1nF cable coupling and source resistance 10k/50k. This is 3,456 defined-reference cases plus 3,456 shared-return-open cases explicitly rejected as *unbounded/undefined*; 384 cases per class have both physical COM solder bonds open.

The test confirms numerical agreement, not that any resulting receiver audio level is safe. COM resistance values, input capacitance, source impedance and contact parameters are illustrative only. The OEM coil-operate margin, dual NPN driver PVT, worn/welded contacts, shared return, mechanical orientation and real PCB layout remain unqualified. This is a separate parallel candidate, not product release; issues #27/#292 stay OPEN.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
