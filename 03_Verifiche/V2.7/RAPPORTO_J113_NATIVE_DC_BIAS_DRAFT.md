# V2.7 — J113 THT: current-source self-bias DC rail and current KCL

**14 November 2026 — generic JFET model; not onsemi production characterization.**

## Purpose

[PR #150](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/150) found that provisional source resistors **680Ω and 1kΩ** produce *less* 455kHz output voltage than the original **2.2kΩ** for every tested 1.5k/2k load and generic NJF corner. It did **not** print DC operating-point voltages or branch currents. Before any bias decision, the 6V laboratory J113 circuit must be independently screened for source bias, rail current and voltage headroom.

The existing isolated native KiCad9 onsemi **J113 TO-92** schematic has OEM pin contract **1 drain / 2 source / 3 gate**, 6V trial supply, gate=DC ground through 1MΩ and source resistor 2.2kΩ. It is not connected to the main receiver. The onsemi [datasheet](https://www.onsemi.com/pdf/datasheet/mmbfj113-d.pdf) is required for real operating/current/thermal limits; the SPICE generic `VTO`, `Idss`, junction capacitances and series resistances are *hypotheses*, not OEM guaranteed values.

## New native DC evidence

`03_Verifiche/V2.7/verify_if455_j113_native_dc_bias.py` exports true KiCad9 netlists for the J113 standalone and the IF455 tank, checks source/drain/gate, returns and coupling connections, then runs **18 native ngspice short-transient settling/DC bias probes**: Rsource `680/1000/2200Ω` × generic NJF `VTO=-0.5/-1.5/-3V` × hypothetical `Idss=2/10mA`. The original J113 generic model is imported from the already CI-verified script, with **no** physical KiCad/BOM edits. In each case the 455kHz source has AC excitation but **DC=0**, the coupling capacitors block the resistive 2kΩ filter-input dummy, and the 6V supply powers only the J113.

The test records actual `Vgate`, `Vsource`, `Vdrain`, `Vgs`, `Vds`, and supply/source currents from ngspice; checks independent `I_source=Vsource/R_source` against `-I(VLAB)` with relative tolerance <=1%, enforces gate/rail DC and positivity of the drain–source headroom, and compares nominal 2.2kΩ branch-current values with the lower resistor alternatives at matched NJF corners. The supply current here is a model current, **not measured total power consumed by the whole radio**. A positive Vds margin or KCL consistency is **not** a JFET safe operating area, gm/noise/compression, temperature/lot or PCB qualification. The existing weak-input AM corner with output AF only 24.34% of the direct detector remains a blocker even if all 18 DC equations pass.

## Interpretation and next gate

Use the reported model DC corner ranges to decide whether the *candidate* deserves a separate nonlinear large-signal distortion/thermal/noise study. **Retain the present 2.2kΩ source resistor**, do not select an alternative or approve a buffer from this experiment. Physical qualification requires real onsemi J113 lots, measured ID–VGS vs temperature, controlled 455kHz low-level noise and large-signal two-tone overload/IMD, real ceramic filter source/load terminations, OEM mixer port loading, and independent 6V bias/thermal review. Master MAIN V2.6, isolated J113 CAD, KiCad footprints/BOM, and absent PCB MAIN/FRONT are unchanged; PR #123 A06 and PR #143 FB455 remain draft.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
