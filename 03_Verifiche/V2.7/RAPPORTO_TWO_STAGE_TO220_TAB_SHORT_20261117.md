# Two complete THT PMOS stages — drain-tab / common heatsink bypass hazard (17 November 2026)

## OEM mechanical/electrical boundary
According to the Infineon IRF9540NPbF package specification (TO-220AB; referenced in [issue #27](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/27)), **GATE=pin1, DRAIN=pin2, SOURCE=pin3, metal mounting tab=DRAIN**. The schematic symbol has only G/D/S, so tab shorts caused by mounting to uninsulated common metal may be **invisible to schematic ERC**. The physical PCB and heatsink arrangement **do not exist** and must not be declared verified.

## Real KiCad9 connectivity
The isolated KiCad9 two-stage bench exports 24 THT parts, 54 pins, 14 nets. Verified drain assignments:
- Q804 pin2 = PRIMARY_IN_DRAIN_LAB (IN)
- Q805 pin2 = SECONDARY_OUT_DRAIN_LAB (MID)
- Q814 pin2 = SECONDARY_OUT_DRAIN_LAB (MID)
- Q815 pin2 = FINAL_SECONDARY_OUT_LAB (OUT)

The native test `03_Verifiche/V2.7/verify_two_stage_to220_tab_drain_short_native.py` enforces every pin↔net partition and models possible metal-tab contacts as **bidirectional ideal shorts**. Graph includes directed intrinsic P-channel body diodes with both gate stages OFF. Among six possible single pair contacts, Q804–Q815 connects IN directly to OUT and defeats both stages simultaneously. Among 15 choices of two pair contacts, **9** yield an IN↔OUT bypass. An uninsulated common metal sink joining all four tabs unequivocally bypasses the isolation in the ideal graph. Q805–Q814 are already on the same MID drain net, but that does **not** permit a shared metal mount across IN/MID/OUT without electrical insulation.

This new regression is a **design hazard detector**, NOT real board layout, heat spreading, insulating bushings/pads, creepage/clearance, SOA, current/energy qualification, thermal calculation or production DRC. Do not assume heat sinks are grounded or tab-insulated; a deliberately qualified design must show component-by-component tab↔heatsink electrical isolation, mechanical fixing and thermal margin, plus independent review. Existing main and front boards remain incomplete; **issue #27 stays OPEN**. This hazard should be checked before selecting heatsinks and footprints for the true board.

Parent [PR #339](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/339) merged to main `970113fb30fb1e1fc60daf27feab0dabfee8848f` after run #44117310413 FAST/FULL/Required PASS; this new review requires its own final SHA CI and review.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
