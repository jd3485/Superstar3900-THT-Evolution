# FRONT mute — isolated six-pin G5V-1 KiCad9 native harness (18 Nov 2026)

## Scope
Created **new isolated, real .kicad_sch**, not a product replacement: `04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_G5V1_SIXPIN_ISOLATED_NATIVE_CANDIDATE.kicad_sch`.
Fork of the existing standalone mute laboratory schematic; retains its passives, connectors and net labels while replacing **K1901** with explicitly numbered physical G5V-1 pins and a provisional six-pad THT footprint field. OEM: NC1→AF_GND, coil2→COIL_PLUS_LAB, COM5 and COM6→RELAY_COM_AUDIO, coil9→COIL_MINUS_LAB, NO10→VOL_WIPER_TO_AMP. Both COM connections are drawn and labelled separately. The original five-pin FRONT parent and existing library remain unchanged.

Native FULL regression `03_Verifiche/V2.7/verify_front_g5v1_sixpin_isolated_harness_native.py` exports both netlists under KiCad9 and rejects mismatches against OEM six-pad maps. It also verifies the original FRONT K1901 remains five-pin. CI registration is in `ci/full_regressions.py`.

## Limitations and mandatory gates
This is an **isolated schematic candidate**, not an integrated FRONT hierarchy or finished PCB. Footprint is an OEM candidate, not physically verified. No qualified relay drive across PVT, fail-safe contact supervision, power-good or safety evidence; issue #292/#27 stay open. KiCad ERC / native netlist / CI on this PR's final SHA must be read from Actions, never presumed. Next technical step: integrate into true FRONT hierarchy only after independent review of all parent partition mappings; assess coil driver and NC fault behavior separately. No board-level DRC.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
