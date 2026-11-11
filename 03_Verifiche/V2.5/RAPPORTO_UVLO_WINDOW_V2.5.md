# V2.5 — LM393B undervoltage cutoff THT window candidate, NOT hardware-qualified

New seven-sheet KiCad9 master `04_KiCad/V2.5/PLL_RX_HIERARCHICAL_MASTER_V2.5.kicad_sch`, derived reproducibly from preliminary V2.4. V2.3 remains the last merged electrical revision of main; V2.4 and V2.5 are in PR #28 DRAFT.

## Real electrical change compared to V2.4

- U801 **pin5 IN_B+** moved from GND to new net **UVLO_SENSE**. U801 **pin6 IN_B-** stays VREF2V5 (existing TL431 cathode). U801 **pin7 OC_B** changes from explicit NC to existing **CMP_OUT**, shared with U801 pin1 OC_A. This is a wired-AND of two open-collector outputs. Any active-low comparator prevents Q802 pull-down of PFET gate, and R1008 existing gate-source pulls PFET gate toward OFF. This is a *functional window circuit candidate*, NOT a single-fault fail-closed interlock.
- R1012 **Yageo MFR-25FBF52-36K** 36 kOhm 1%, 0.25W metal-film axial THT: FUSED_RAW -> UVLO_SENSE. R1013 **Yageo MFR-25FBF52-10K** 10 kOhm 1%, 0.25W axial THT: UVLO_SENSE -> GND. Both candidate KiCad DIN0207 axial footprints. Nominal UVLO VIN = Vref*(1+36k/10k)=**11.5 V** (assuming 2.5 V Vref).
- R1001 changed value to **Vishay PR01000101801JR500, 1.8k 5% 1W axial** (previous 3.3k); same candidate PR01 THT footprint. Idealized model estimates TL431 Icat at 11V min **1.36mA**, at 13.8V min **2.38mA**, with 820Ω +/-5%, D804 Vf 0.25..0.65V, LM393 Icc 0.5..1mA, R1001 5% and Vref 2.45..2.55V. Vendor transient, regulator tolerance and hot/leakage model absent; **not proof of TL431 regulation under all PVT**.
- Existing D806 Diotec 1N5352B 5W and R1011 Vishay PR03 820Ω/3W from V2.4 are preserved; no RF/PLL/VTUNE pin-net changes.

## Assumed operating window and evidence

The 36k/10k +/-1% divider with illustrative Vref 2.45..2.55 V predicts an UVLO trip window 11.095..11.915 V (not a guaranteed -40..+85C band). The existing OVP comparator A nominally interrupts near 16.5V (its own hysteresis PVT unqualified). Comparator B does not add hysteresis. The shared CMP_OUT may modify A hysteresis behaviour during undervoltage. All thresholds need system transient/thermal tolerance verification with vendor-grade models.

Primary references:
- TI [LM393-N](https://www.ti.com/lit/ds/symlink/lm393-n.pdf): dual open-collector comparator with input common-mode restrictions; **no assumption of valid output with out-of-range supply or reference**.
- TI [TL431](https://www.ti.com/product/TL431): cathode bias minimum depends on variant and conditions.
- Yageo [MFR-25FBF52-36K](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-36K/9138141), [MFR-25FBF52-10K](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-10K/13219): 1% THT 0.25W.
- [Vishay PR01000101801JR500](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/PR01000101801JR500/595999): 1.8k 1W 5% axial.

## Crucial unresolved hazards

A failed-open TL431 can raise reference above the LM393 valid input common-mode range; a failed Zener can expose U801 to >36 V; neither fault guarantees a SAFE state. Gate Q801/Q802, pin electrical stress, startup/brownout transients, F701 fuse/D702 TVS coordination, source energy, reversed power, thermals, 48V sustained input, reference divider aging, open/short resistor faults, wiring and footprint mechanical qualification all remain OPEN. There is **no independent power-good or output mute** monitoring true +5V, PLL lock and VANA20, and no hysteresis on U801B. Real hardware tests, independent review and vendor SPICE must precede any safety claim.

## CAD gate for this draft

Use cost-optimized CI on final HEAD. New workflow `.github/workflows/cad_native_v25.yml` is **manual only** and its native commands also run within `ci/full_regressions.py`; verify generator bit-exact, genuine 7-sheet KiCad9 ERC0, real V2.4->V2.5 native pin-net comparison (only U801/5 and U801/7 moved; 2 new resistors, R1001 value changed), 133/133 THT footprint fields, 7 SVG, and all historical regressions. **No PCB/DRC exists**. Do NOT merge PR #28 as safety-qualified. NO FAB / NO TX / NO BATTERY / NO VEHICLE.
