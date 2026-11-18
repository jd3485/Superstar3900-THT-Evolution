# FRONT G5V-1 six-terminal NC mute attenuation vs dual COM solder faults — 18 Nov 2026

PR [#352](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/352) **MERGED** main `2eb28bd2245e08330c688c5ab60008290c0a7b33`, final head `190756d2d91e3d80c9a4e34d1efbe88273e07d5e`, run #44283080410 FAST/FULL/Required **3/3 success**. Native KiCad9 FRONT G5V-1 dual COM network and two-solver finite-impedance AC checks are in main, unqualified.

New native regression `03_Verifiche/V2.7/verify_front_g5v1_sixpin_com_open_attenuation_native.py` explicitly screens whether breaking one or both physical COM5/COM6 solder paths degrades an otherwise deenergized NC shunt. It exports the actual five-sheet six-pin candidate KiCad9 netlist, verifies actual relay physical COM and connector pins, and sweeps 48 **illustrative** AC combinations with 2 COM solder finite values, 2 NC contact resistances, 3 frequencies, 2 coupling capacitances and 2 cable source impedances. Independent reduced network and nodal verification cross-check representative states.

The key functional invariant is **both COM solder paths open = NC path open**, despite a nominal NC position; single COM bond failure cannot strengthen this ground shunt in the idealized model. Reported relative damping is a hypothetical circuit simulation, not a receiver audio or noise specification. None of this addresses shared AF_GND reference loss (unbounded), relay mechanics, OEM minimum contact load, coil PVT under dual BC337 transistors, cable shielding or board layout.

No PCB/DRC/hardware qualification. Issues #27/#292 stay open. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
