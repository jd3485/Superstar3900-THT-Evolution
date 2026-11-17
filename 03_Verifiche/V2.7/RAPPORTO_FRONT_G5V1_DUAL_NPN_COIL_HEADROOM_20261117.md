# FRONT G5V-1 DC5 mute relay: dual-NPN 5V coil voltage headroom (17 Nov 2026)

## Real electrical structure
KiCad9 native export of `FRONT_CONTROL_PARTIAL_V2_7_DRAFT.kicad_sch` establishes that K1901 symbolic pin4/COIL_PLUS_LAB shares the supply with J1911 pin1 and J1914 pin1, that K1901 pin5/COIL_MINUS_LAB connects Q1911 collector (pin1), that Q1911 emitter (pin3) connects Q1912 collector (pin1) at SERIES_MID, and Q1912 emitter (pin3) returns to DRIVER_GND. Flyback diode D1911 pin2 is at coil-minus. This is **two NPN VCE(sat) drops in series**; do not treat a 5V rail as 5V *across the coil*.

## OEM device vs model assumptions
Aratas/Omron official [G5V-1 K048-E1 datasheet](https://www.aratas.com/system/files/datasheet_pdf/K048-E1.pdf), p1, standard 5V coil: 167Ω ±10% at **23°C**; 30mA nominal; max must-operate voltage **80% rated = 4.0V** at 23°C. These are OEM specs, not invented. No vendor-verified BC33725BU VCE(sat) at sufficient forced beta/temperature is yet integrated; **0.1/0.3/0.6V per transistor are hypothetical corners, not guaranteed upper or lower bounds**.

A new KiCad9-parent-netlist-anchored FULL regression `03_Verifiche/V2.7/verify_front_g5v1_dual_npn_coil_headroom_native.py` sweeps four hypothetical 5V rail cases 4.5/4.75/5.0/5.25V × three hypothesized VCE(sat) for Q1911 × three for Q1912 × 167Ω ±10% (three cases): **108 scenarios**. Using `Vcoil=max(0,Vrail−VCEsat1−VCEsat2)`, the ideal results are **78/108 at or above 4.0V, 30/108 below 4.0V**, 3.3–5.05V applied to the coil, and 17.96–33.60mA with 23°C nominal coil resistance tolerance. A 5.05V relay coil case from rail 5.25V is **not** a production rating or a transient/surge allowance. Worst corners show inadequate OEM 23°C guaranteed pick-up threshold; the board's actual 5V source/load, transistor forced beta, base current, dropout, temperature and coil winding self-heating are unqualified.

## Design consequences
The dual-series NPN may support a safety intent (both enables required), but under-drive may leave the FRONT audio relay muted, may cause chatter or delayed release if intermittent, and complicates fail-NC claims. Do not reduce redundancy or connect coil directly as a shortcut. Need OEM transistor curves and thermal data, regulator limits, released 6-pad G5V-1 footprint/pin-map on actual board, and an independent contact/AF_GND failure analysis. The existing FRONT 13-ref partial layout does not include K1901; no actual full FRONT PCB or hardware DRC can be claimed.

Parent [PR #343](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/343) **MERGED** main `f4a38756dd0da843c9b219b3a4648610dc74d190`, run #44129980006 FAST/FULL/Required SUCCESS; this new work requires separate green checks. #292 open.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
