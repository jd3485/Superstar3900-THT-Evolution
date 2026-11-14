# V2.7 — 1 mH IF455 coil parasitic capacitance / SRF sensitivity

**14 November 2026 · Bench hypothesis only, NOT an OEM inductor characterization.**

## Discovered risk

Previous IF455/mixer load benches projected an ideal **1 mH** coil with a provisional **16.5 Ω series resistance** out to **30 MHz**. This is not sufficient to establish the physical coil impedance or mixer port return loss at RF: the inductor's winding capacitance, self-resonance, winding loss/Q, insulation and construction are not yet characterized by an OEM model for a selected exact THT MPN. The 30 MHz results are **topology algebra**, not validated RF hardware results.

For an *isolated ideal* 1 mH inductance with hypothetical parallel Cp:

| Hypothetical Cp | Ideal isolated fSRF = 1/(2π√LCp) |
|---|---|
| 0.1 pF | ≈ 15.915 MHz |
| 1 pF | ≈ 5.033 MHz |
| 10 pF | ≈ 1.592 MHz |

None of those capacitances is asserted as a measured/typical/min/max value for L1601. The **assembled tank** has external 82+30pF and output loading: its resonance is different and is not the isolated-coil SRF above. Near or above real inductor SRF the simple one-Cp surrogate itself can fail; multiple winding modes and fixture parasitics are not included.

## Published candidate MPN metadata, not an RF qualification

The actual standalone KiCad value for L1601 is `1mH_DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED`. Independent distributor product listing [DigiKey, Delevan 2500-28J](https://www.digikey.it/it/products/detail/delevan/2500-28J/3479912) lists **1mH**, **16.5Ω maximum DCR**, **88mA**, **Q 60 at 790kHz**, and **minimum SRF 2.8MHz**, THT axial unshielded. Delevan [2025 magnetics catalog](https://www.delevan.com/-/media/Project/Altramotion/shared/files/Literature/brand/Delevan/pdf/delevan-2025-magnetics-catalog.pdf) indexes the `2500-28J` 1000µH / 16.5Ω / 88mA part and the 2.8MHz minimum SRF field. These are **part-level specified limits/conditions, not a measured Cp or real fixture Z(jω) curve**. The minimum SRF is NOT the exact SRF, and therefore cannot be substituted for a measured winding capacitance or used to prove the exact impedance at 30MHz. The simulations remain explicitly hypothetical, and the 16.5Ω modeling as constant **RF** loss is unjustified by a DC resistance maximum.

## Native evidence and reproducibility

New `03_Verifiche/V2.7/verify_if455_coil_parasitic_srf_native.py` exports the **actual native KiCad9 IF455 netlist** to guard J1601/1→C1601/1→L1601, while preserving the physical candidate schematic. In temporary SPICE decks it adds **Cp=0/0.1/1/10pF** across the entire 1mH+16.5Ω coil branch, runs ngspice **AC at 455kHz, 1MHz and 30MHz**, and records **12 complex input-port Z results**. An independently derived complex nodal-admittance formula for the tank, output load and input coupling is checked against *every* native complex Z result (relative error below 2e-5). The established ideal-Cp=0 455kHz result is explicitly pinned to the previously tested value. All hypothetical modifications are temporary and source models are not claimed.

## Qualification gate

No change to the actual C1601=10pF/L1601=1mH schematic, master V2.6, footprint or BOM. Before an IF diplexer or 30MHz termination is selected, select a real **currently manufactured THT inductor** with manufacturer Q vs frequency, SRF/impedance-vs-frequency, DCR/tolerance, mechanical footprint and assembly parameters, then validate on real hardware. Test mixer IF conditions, LO spurs and unwanted-frequency termination with OEM data and RF measurements. No PCB DRC; both PCB layouts remain absent. [PR #123](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) stays draft and unqualified.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
