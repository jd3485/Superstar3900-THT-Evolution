# FRONT NC mute K1901 — OEM G5V-1 DC5 six-pad physical footprint candidate (17 Nov 2026)

## Real CAD delivered (isolated, NOT deployed)

Added KiCad footprint file `04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/TH_MUTE_OEM_CANDIDATE.pretty/G5V-1_DC5_OEM_6PIN_CANDIDATE.kicad_mod`. All six pads are actually defined as **through-hole** with 1mm drill and 2mm pad diameter, dimensions at 2.54mm grid. Bottom-view hole drawing from [Aratas/Omron OEM G5V-1 K048-E1, p4](https://www.aratas.com/system/files/datasheet_pdf/K048-E1.pdf) was compared with the [existing KiCad upstream Relay_SPDT_Omron_G5V-1 footprint](https://github.com/KiCad/kicad-footprints/blob/master/Relay_THT.pretty/Relay_SPDT_Omron_G5V-1.kicad_mod) for front-view orientation.

**Top-view KiCad pad centers (mm):** pin 1 (0,0), 2 (0,2.54), 5 (0,10.16), 10 (5.08,0), 9 (5.08,2.54), 6 (5.08,10.16). This matches the publicly maintained KiCad G5V-1 6-pad geometry, but independent mechanical review and actual socket/relay sample fit remain mandatory. Outline/courtyard are illustrative candidate values. Not a production board, no Edge.Cuts, no DRC sign-off.

**OEM physical pin-to-net proposal, not applied to schematics:** NC 1 → AF_GND, coil 2 → COIL_PLUS_LAB, COM 5+6 → RELAY_COM_AUDIO, coil 9 → COIL_MINUS_LAB, NO 10 → VOL_WIPER_TO_AMP. The **current** K1901 schematic in the FRONT partial parent is still abstract with five electrical pins and Footprint="". It is **intentionally not assigned** to this footprint: the six-pad candidate will be physically incorrect if grafted onto a five-pin symbol without an independently reviewed OEM six-pin schematic symbol and netlist migration.

Regression `03_Verifiche/V2.7/verify_front_g5v1_oem_sixpad_footprint_candidate_native.py` checks all six pad numbers, positions, drill and through-hole properties, the OEM electrical assignment, and the **actual** KiCad9 exported current FRONT netlist. It fails closed on a premature direct five-pin-to-six-pad substitution and is wired to FULL CI.

## Qualification gates still unresolved

1. Migrate K1901 to a six-physical-pin THT symbol in a separate controlled revision, preserving explicit contact/mute and coil partitions and verifying native ERC/netlist.
2. Confirm exact G5V-1 DC5 ordering status / availability, relay sample height, envelope and pin gauge; do not infer production from a historic distributor stock record alone.
3. Qualify the actual two-series BC337 coil drive over source tolerance/base drive/PVT, relay must-operate voltage, contact minimum load and failure modes. Real FRONT PCB placement/DRC, AF_GND continuity, cable and safety reviews are absent.
4. No fabrication, PCB ordering, TX, battery or vehicle installation is authorized.

Parent [PR #345](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/345) integrated to main `970e980e91d268abe71a7b45faf5342e3a0a88b3` after run #44137551958 all three required CI gates success. This new footprint candidate must pass its **own** final-SHA CI before main integration. Issues #292, #27 remain open.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
