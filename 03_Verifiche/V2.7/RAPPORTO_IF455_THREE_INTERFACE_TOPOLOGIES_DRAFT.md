# V2.7 — mixer-to-ceramic IF455: resistive, ideal L-match and unity-buffer alternatives

**Date 2026-11-14 — native KiCad9 interface boundary; ideal bench tests only, not a selected receiver design.**

## Source and engineering premise

NextGen [FB 455kHz Case 11070 OEM family datasheet](https://www.nextgencomponent.com/uploads/soft/20241011/1-241011155152A8.pdf) calls for a defined source and output load. Specifically **Rg+R1=R2=nominal 1500 or 2000Ω** in its test apparatus. Mini-Circuits [AN00-009](https://www.minicircuits.com/appdoc/AN00-009.html) describes mixers under controlled 50Ω lab conditions but explains that VSWR varies with frequency, LO drive and loading. **Neither statement qualifies an effective 50Ω SBL-1+ Thevenin IF source under our radio's LO conditions**. Existing [PR #144](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/144) establishes the resistive OEM test loading, not a physical design.

## Native electrical topology comparison

New `03_Verifiche/V2.7/verify_if455_three_interface_topologies_native.py` exports *real KiCad9* netlists from unmodified standalone mixer and IF455 test filter to check IF3+4, J1703, J1601/C1601 and grounded return. In temporary decks, four interface candidates, two hypothetical sources **50Ω / 500Ω**, two resistive **filter-input dummies 1500Ω / 2000Ω**, and three frequencies **445/455/465kHz** give **48 native ngspice AC cases**:

1. Direct: voltage divider, no matching components.
2. OEM reference series resistor: `R1=Znom−Rg`, with nominal `Vload/Vsrc=0.5` for this resistive dummy. This does not constitute a mixer output match.
3. **Ideal two-reactive-element low-pass L-match** only at nominal 455kHz: `Q=sqrt(Znom/Rg−1)`, `L_series=Rg·Q/ω0`, `C_shunt=Q/(Znom·ω0)`. This satisfies `Zin(455kHz)=Rg+j0` with ideal lossless L/C, not broadband or physical RF impedance matching. The elevated voltage into a high impedance load is **not power gain**.
4. **Ideal E-controlled unity buffer**: hypothetical input `100kΩ`, output `100Ω`, gain=1, no bias/noise/linearity/power/supply. It cannot predict any available THT buffer or real SBL-1+ operating conditions.

Every complex output voltage at all 48 points must agree with *independent analytical* divider/AC complex impedance equations. The report shows both absolute voltage ratios and ±10kHz ratios **relative to each model's own 455kHz output**. Neither voltage ratio nor component Q is a receiver noise figure/insertion-loss or full selectivity prediction.

## RF implementation gate

Do not copy an ideal L-match inductor or 100kΩ input buffer onto actual KiCad. At 455kHz the illustrative 50→2000Ω L-match requires roughly **109µH series and 1.09nF shunt** (check computed values from native CI). Real THT inductors must pass Q/SRF/DCR/PVT, screening of coupling and undesired IF/LO/RF conversion products, layout and ground-return characterization. The theoretical match is frequency selective and does not replace a broadband termination/diplexer for mixer output mixing products. Any buffer must be based on an **actual actively produced THT device**, with measured bias voltage/current, source drive, max input swing, current/noise/IMD, stability, startup and failure modes.

The NextGen ceramic itself is **not** simulated: the input dummy 1500/2000Ω models a single-frequency testing load, not insertion loss, ripple, group delay, or real frequency-dependent input impedance. Its required output termination R2 is also not modeled. The standalone IF455 tank is not magically a ceramic filter and does not establish approved mode-specific masks; issue [#141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141) remains open.

No changes to physical MAIN V2.6 or isolated candidate KiCad schematics; zero real PCBs and no PCB DRC. Provisional OEM-sensitive footprints [PR #123 SBL-1+](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) and [PR #143 FB455](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) remain draft, no physical build allowed.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
