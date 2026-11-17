# THT two-stage gate Rgs OPEN/SHORT, hypothetical sink-current fault (17 November 2026)

## Physical topology checked
On the **isolated** KiCad9 two-complete-PMOS-stage bench, the new FULL regression exports the actual netlist and checks the invariant **24 THT components / 54 pins / 14 nets**. Each stage has a 47k source-to-gate Rgs, a 10k gate sink-series resistor and two 1N4106-1 source/gate clamp diodes. The test checks their real pin↔net topology before any analytical fault models.

## Synthetic models and scenarios
Three Rgs conditions: nominal 47k, OPEN, ideal SHORT. Three **assumed** capacitances 1/10/100 nF (not an OEM Ciss/Qg), initial |Vgs| 5/12V, sink leakage 0/25/100µA and times 0/50µs/500µs/5ms give **216 scenarios/stage, 432 total**.

For the nominal branch, `v(t) = I_sink Rgs + (v0-I_sink Rgs) exp[-t/(Rgs C)]`. For an ideal SHORT, `v(t)=0` (72 mathematical cases/stage), a **zero-ohm fault is not a physical zero-time guarantee**. For OPEN without a sink, a charged gate remains floating at initial voltage (24 cases/stage); without a modeled return there is **no guaranteed recovery**. For OPEN with persistent hypothetical sink, the **unclamped** ideal expression `v=v0 + I_sink t/C` grows without bound (36 increasing scenarios/stage); results can exceed hundreds of volts and are explicitly **unphysical**, not a prediction of real gate stress. Real Zener conduction, MOSFET gate breakdown, source/return motion, BJT leakage and Miller coupling are absent.

**Safety conclusion:** static continuity of two isolated 47k pullups does not show OFF safety if an Rgs opens. Even a nominal OFF-state gate needs bounded BJT leakage, realistic gate charge, actual Zener I–V over PVT, independent supply/enable sequencing and measurement. This is a fault-analysis regression, NOT a hardware qualification. Issue #27 remains OPEN. Both real MAIN/FRONT PCBs are absent.

Parent integration: [PR #338](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/338) merged main `c6299623faff3f55111fc412c6820d45a71872e2`; run #44114976980 FAST/FULL/Required SUCCESS. The new Rgs-fault review must pass its **own** final SHA CI; no mixing approval between PRs.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
