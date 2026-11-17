# FRONT NC mute — OEM G5V-1 DC5 six-terminal mapping (17 Nov 2026)

Source: [Aratas/Omron OEM G5V-1 datasheet K048-E1, p. 4, **BOTTOM VIEW**](https://www.aratas.com/system/files/datasheet_pdf/K048-E1.pdf), visually checked on 17 Nov 2026. A single SPDT relay has **six physical THT terminals**, NOT the five abstract K1901 electrical pins. The drawing shows **coil terminals 2 and 9** (no polarity), **two internally connected contact COM terminals 5 and 6**, **NC terminal 1** and **NO terminal 10**. The published **bottom view** must be mirrored to derive a correct KiCad front/top view; this revision intentionally does NOT invent pad positions or approve the mechanical footprint.

## Native FRONT schematic migration contract
Current K1901 parent native netlist: 1=RELAY_COM_AUDIO, 2=AF_GND (NC mute), 3=VOL_WIPER_TO_AMP (NO), 4=COIL_PLUS_LAB and 5=COIL_MINUS_LAB. **These labels are symbolic and are not the OEM terminal numbers.** The proposed future OEM-to-net contract (not yet migrated) is:
- OEM 1 → AF_GND (NC)
- OEM 2 → COIL_PLUS_LAB
- OEM 5 and OEM 6 → RELAY_COM_AUDIO, *both required in the native footprint/netlist*
- OEM 9 → COIL_MINUS_LAB
- OEM 10 → VOL_WIPER_TO_AMP (NO)

The test `03_Verifiche/V2.7/verify_front_g5v1_six_terminal_oem_pin_map_native.py` exports the actual KiCad9 FRONT parent netlist; checks the historical five-terminal connectivity; defines the above explicit migration; and sweeps 3 ideal relay states (NC, NO, OPEN) × the 4 permutations of COM terminal 5/6 OPEN contact faults (**12 idealized connectivity cases**). With at least one COM lead electrically continuous, the NC path theoretically routes the muted input toward AF_GND; **if both leads are open, this path is lost**, and it is not fail-muted. Electrical continuity of just one COM pad does NOT qualify the device's internal mechanical/contact reliability, board integrity or safety. Contact welding, NC contact faults, AF_GND loss, coil-drive faults and cable parasitics remain separate hazards.

## Integration gates
A real six-pad TH symbol/footprint and OEM drawing TOP/BOTTOM mechanical verification are the next physical CAD activity; once a native 6-pin K1901 exists, this regression must be revised to fail-closed on the new actual pin mapping. Also qualify 5V coil/dual BC337 driver over PVT, latching/return timing, audio AF_GND and mute under single faults; an isolated lab is NOT product assurance. The historical FRONT 13-ref provisional PCB omits this relay and is not a production board.

Parent [PR #342](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/342) merged main `5b64ad3c5b76938435db48f6e3b0743d73460431` after run #44128102517 FAST/FULL/Required SUCCESS. This new review needs its **own** final-head CI. Issue #292 remains open.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
