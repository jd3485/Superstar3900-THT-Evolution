# FRONT G5V-1 six-terminal native five-sheet hierarchy candidate — 18 November 2026

## Actual CAD delta
Adds `04_KiCad/V2.7_DRAFT/FRONT_CONTROL_PARTIAL_G5V1_SIXPIN_CANDIDATE.kicad_sch` and corresponding KiCad project. This is a **parallel unqualified five-sheet hierarchy**, not a replacement of the legacy partial FRONT. Volume, LED, meter, mute driver, and four intersheet audio/coil joins are retained. Only the mute child sheet reference points to the isolated OEM six-physical-terminal candidate merged after PR #348. K1901 NC1/coil2/COM5+COM6/coil9/NO10 have explicit KiCad pins and candidate THT footprint. Original parent and all its children stay untouched.

## Native verification and gates
New FULL regression `03_Verifiche/V2.7/verify_front_g5v1_sixpin_hierarchy_candidate_native.py` invokes `kicad-cli sch erc --exit-code-violations` and exports native KiCad9 netlists from both parent hierarchies. It asserts all nonrelay pin→net assignments unchanged, exactly one extra OEM relay endpoint (second COM6), 22 expected electrical nets, and both physical COM pads on RELAY_COM_AUDIO. The expected 72 vs 71 pin endpoints and ERC0 are **requirements for CI, not pre-certified results**; only claim them on completed final-SHA FULL logs.

**Critical safety limits:** This is an *alternative draft*, not the shipped FRONT master; no PCB, DRC, complete receiver, relay voltage/current PVT, contact failure/safety proof, physical OEM pin-gauge review or mating cable qualification. Coil driver includes two series switches and can fall below OEM must-operate voltage. Reject product migration until safety #27 / relay #292 are addressed. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

## Integration
Commit/PR to be confirmed by GitHub final HEAD, FAST/FULL/Required. The five-sheet legacy draft and MAIN V2.6 remain intact.
