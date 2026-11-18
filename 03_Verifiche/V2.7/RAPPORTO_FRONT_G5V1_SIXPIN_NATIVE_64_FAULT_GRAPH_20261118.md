# FRONT G5V-1 — native 64-state physical contact topology screen (18 Nov 2026)

The actual **five-sheet six-physical-pin native KiCad9 candidate** was merged in [#349](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/349): main `06f1847c843a1addd05e3ca4c9fed2744b257d39`; final head `8045c3488c5405895945614509e789f678b9e8e2`; CI run #44271061438 FAST/FULL/Required **3/3 success**. Native ERC0, 22 networks, 72 physical pin endpoints, compared against 71 abstract. Original FRONT five-pin design remains unchanged.

This regression adds `03_Verifiche/V2.7/verify_front_g5v1_sixpin_native_64_fault_graph.py` to FULL. Exports the real integrated KiCad9 candidate netlist, verifies six OEM K1901 numbered terminal-to-net connections, series audio R1902, connectors and both COM5/COM6, then screens all 2^6 binary scenarios: coil energized, NC stuck open, NO welded, individual COM5 and COM6 disconnected from PCB, AF_GND return open. Uses independent graph reachability and explicit logical expectations for input-ground path and volume-source path; rejects missing return and unexpected energization continuity. Both COM are modeled as parallel mechanical bonds to the same internal common. This is a *topological screening model*.

**Not a product safety qualification:** R1902 impedance/AC leakage, return ground potential, contact bounce/arcing, relay winding tolerance, PCB trace failures, driver VCE saturation PVT, latching and transient physics are not modeled. Presence of NC topology does not guarantee silence with welded NO, open return, contact failures or underdriven coil. This branch produces no PCB, DRC, physical proof, regulatory decision or authority to operate transmitter. Issue #27/#292 remain open.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
