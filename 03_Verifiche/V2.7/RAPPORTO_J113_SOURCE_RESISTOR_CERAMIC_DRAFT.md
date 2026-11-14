# V2.7 — J113 THT: source self-bias resistor vs ceramic nominal load, 36 native cases

**2026-11-14 — screening generico, non selezione componenti né qualifica hardware.**

## Existing bench and unresolved failure

The 6V onsemi **J113** THT source follower exists already as a real isolated native KiCad9 schematic `04_KiCad/V2.7_DRAFT/IF455_J113_SOURCE_FOLLOWER/`. The [onsemi OEM datasheet](https://www.onsemi.com/pdf/datasheet/mmbfj113-d.pdf) gives **TO-92 pin 1 drain, pin 2 source, pin 3 gate**; pinouts from other J113 manufacturers can differ. The device specifications are switching JFET parameters, not guaranteed noise or gm at 455kHz in this receiver.

The earlier [PR #148](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/148) benchmarked 18 small-signal AC generic NJF corners for the present **source self-bias resistor 2.2kΩ** and resistive load 100kΩ/2kΩ/1.5kΩ. The generic low-current / VTO=−3V corner with 2kΩ load produced `Vout/Vgenerator=0.261831624` at 455kHz. Critically, earlier J113 AM transient analysis measured only **0.2434 of the direct AF amplitude** at its worst modeled weak-signal corner: this is not resolved by gain at one AC frequency.

## New design-variable check

New `03_Verifiche/V2.7/verify_if455_j113_source_bias_load_native.py` imports the **existing** approved-to-test generic J113 + IF455 passive tank deck; it does not invent a new transistor model. It exports both real KiCad9 netlists, guarding drain/source/gate, source R2.2k and coupling and IF455 C1601 pin/net. It runs 36 native `ngspice` AC 445–465kHz sweeps under a *hypothetical* 50Ω generator source:

- Source self-bias resistor **680Ω, 1000Ω, 2200Ω (current bench)**, **SPICE-only**.
- Generic NJF `VTO = −0.5, −1.5, −3V` × illustrative `IDSS = 2, 10mA`.
- Output load resistors **1500Ω or 2000Ω**, representing only the nominal input *resistance* of shortlisted NextGen ceramic filters, not their complex impedance or transfer.
- Per-case response at 455kHz and relative 445/465kHz amplitude. Each R680/R1000 result is compared with its *same-corner R2200 reference*; the prior J113 2kΩ worst-case numeric baseline is pinned as an independent regression.

The trial resistor may change the DC source operating point and transconductance in ngspice's internal operating point, but **no independent DC bias current/voltage output has been characterized here**. Therefore do not infer a safe 6V device voltage, thermal margin, linear swing, noise, RF stability or improved minimum detectable signal from AC results. Especially, **relative voltage gain is not sensitivity, noise figure, dynamic range, or demodulated AF distortion**.

## Engineering release gate

Do not replace the source 2.2kΩ in KiCad or conclude that a 680Ω or 1kΩ trial is better without independent model/measurement: obtain actual onsemi J113 drain current vs VGS and temperature, 455kHz noise source/gm/IMD and a physical bias/overload/temperature sweep with a real 1500/2000Ω ceramic-filter input terminated per OEM. Preserve previous weak-signal AM failure as an explicit blocker. Master V2.6 and standalone THT schematics unchanged; both real PCB MAIN/FRONT still absent. Draft [PR #123 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) and [PR #143 FB455](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) remain unqualified.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
