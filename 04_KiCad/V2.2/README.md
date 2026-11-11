# V2.2 — L920 Bourns RLB0914-681KL footprint THT, seven-sheet native KiCad candidate

Stacked on V2.1 (PR #20) preserving all seven schematics/pin-net groups from V2.1.
**Exactly one component metadata change**: L920 in POWER20 now points to
`THT_V22:Inductor_Bourns_RLB0914_681KL_P5.00mm`.
F701/D702 remain in the local V2.1 library. Seven new native KiCad files are committed and
reproducible from V2.1 by `node genera_L920_v22.js --check`.

**Vendor (Bourns) geometry**: radial pitch 5.0 ±0.8 mm, lead nominal diameter 0.65 mm;
body max diameter 9.2 mm and max height 13 mm. Candidate drill 1.0 mm, pads 2.0 mm;
footprint is not an assembly sign-off. Exact reel/lead formation, hole tolerances, copper
clearances, pick-and-place, footprint actual fit and assembly rules require a sample and review.
Unshielded ferrite winding, boost magnetic interference not qualified.

**Electrical**: 680 µH ±10%; RDC max 1.60 ohm; Irms typical 0.49 A;
Isat typical 0.90 A (10% inductance drop typical); SRF min 1.6 MHz.
At 0.49 A, I²R with worst datasheet Rdc 1.6 ohm is 0.384 W (constant-temperature model).
No MC34063 peak-current, saturation-temperature, frequency, ripple or RF-EMI validation.

Official datasheet: https://www.bourns.com/docs/product-datasheets/rlb.pdf
CI must run on final SHA before any merge. L501 remains without footprint and RF qualification.
No PCB, no DRC, no Gerbers, no battery/vehicle connection.
**NO FAB / NO TX**.
