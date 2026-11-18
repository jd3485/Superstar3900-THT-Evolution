# FRONT G5V-1 six-pin native AC contact fault matrix — 18 November 2026

PR #350 was merged as main `0925c17254bc978689a08220f1aa2a324a8d883a` after run #44274041529 FAST/FULL/Required all **SUCCESS**. The 64-state electrical-graph screen checks continuity, not voltages.

This next engineering revision adds `03_Verifiche/V2.7/verify_front_g5v1_sixpin_ac_contact_fault_native.py`, anchored to the native KiCad9 five-sheet six-pin FRONT candidate and real R1902 (1k)/R1901 (100k) schematic networks. Every combination of coil state, NC stuck open, NO welded, COM5 open, COM6 open, and shared AF_GND open is evaluated: **64 physical fault states**. COM5 and COM6 are independent parallel paths to the physical relay common. Both disconnected disconnect all contact paths. A welded NO allows a source path even with a de-energized coil. Shared ground-open is **explicitly unbounded**, rather than treated as safe or solved with an invented reference.

For the 32 states with a defined reference, the test runs **1,152 complex AC combinations**: 3 frequencies × 3 cable coupling values × 2 source resistances × 2 NC resistances × 2 NO resistances, comparing two numerical formulations (collapsed Norton reduction vs independent two-node nodal KCL). These are **hypothetical** source/cable/contact parameters; numerical agreement is not a product safety proof. The test is in FULL CI and requires the final PR HEAD gates before merge.

No receiver PCB, DRC, physical contact resistance, EMI compliance, thermal PVT or component qualification has been performed. Retain issue #27/#292, preserve legacy FRONT, no fabrication or RF operation.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
