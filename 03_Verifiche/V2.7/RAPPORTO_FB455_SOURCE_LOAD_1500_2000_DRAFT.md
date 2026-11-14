# V2.7 — ceramic IF455 1.5k/2k matching: OEM measurement conditions versus real RX interface

**2026-11-14 · Experimental bench boundary, no ceramic transfer function and no RF/mixer qualification.**

## Verified manufacturer condition (not an integration prescription)

NextGen Components [FB series Case 11070 datasheet, 2024-10-10](https://www.nextgencomponent.com/uploads/soft/20241011/1-241011155152A8.pdf), **page 4 measurement drawing**, explicitly prescribes **`Rg+R1=R2=Output/input Impedance`** at the manufacturer's test temperature. Page 5 names **FB455K0000L005** nominal **2000Ω** source/output termination (455kHz ceramic, ±6kHz **minimum** 6dB bandwidth, max 5dB insertion loss and 45dB **minimum** stopband attenuation in the reference conditions). **1500Ω** is a nominal alternative for other FB suffixes and related LTM candidates; per-MPN sheet and measurement convention still required.

Mini-Circuits [AN00-009](https://www.minicircuits.com/appdoc/AN00-009.html) characterizes diode mixers with controlled **50Ω** port terminations and notes that VSWR depends on frequency, LO power and loading. This does **not** establish a constant 50Ω complex Thevenin IF output for our unmeasured **SBL-1+**. The stand-alone KiCad9 SBL-1+ port J1703 is physically unconnected to an approved FB455 filter or matching circuit. Our first/second IF frequency plan is not frozen.

## Reproducible native electrical experiment

`03_Verifiche/V2.7/verify_fb455_1500_2000_termination_native.py` exports **two genuine KiCad9 netlists** and checks port mapping IF3+4→J1703/1 and J1601/1→C1601/1 plus grounds. Then twelve **native ngspice** single-frequency AC 455kHz test-only *resistive dividers* are simulated:

- hypothetical mixer source resistance `Rg=50,500,1500Ω`
- hypothetical ceramic nominal test input impedance `Znom=1500,2000Ω`
- either direct `R1=0` or the manufacturer's bench condition `R1=Znom−Rg` (nonnegative for all six combinations)

Each test uses **one ideal, resistive shunt input dummy of Znom**, NOT a ceramic filter model. The real filter output, insertion loss, selectivity, ripple, dynamic range, group delay and actual output load R2=Znom are **not** electrically modeled; the output requirement is recorded separately as an unimplemented port obligation. Independent Ohm's law `Vpin/Vsource=Znom/(Rg+R1+Znom)` is compared against the native complex-voltage ngspice result for all twelve runs. No `R1` is assigned to real KiCad or BOM.

For the illustrated `Rg=50Ω`, `Znom=2000Ω`: **direct** `Vpin/Vsource=2000/2050≈0.97561`; series `R1=1950Ω` at OEM test condition `Vpin/Vsource=0.5`, a drop of about **5.8dB in voltage relative to the direct resistive dummy**. The 1500Ω measurement condition would require `R1=1450Ω` under the **same hypothetical** 50Ω source, also yielding 0.5V/V in the resistor-only model. These are input-voltage division results, **NOT ceramic filter insertion loss, mixer conversion loss, overall RX gain, noise figure or real impedance match**. Matching resistor is neither a broadband IF diplexer nor an automatically advisable link.

## Explicit gating decision

**Do not place a 1950Ω or 1450Ω series resistor on the PCB simply because the manufacturer's measuring diagram uses one.** Determine realistic LO-driven SBL-1+ IF output impedance `Z(f, LO, RF, termination)`, harmonic rejection, filter source/load matching, mode-specific selectable bandwidth and system gain/noise budget. If use of FB455 is pursued, qualify exact sold MPN and lot, real THT footprint pin orientation, lead and finished-hole dimensions, 2000Ω load after filter output, and stopband/insertion-loss response with manufacturer fixture and in-circuit measurements. Preceding single IF455 LC tank C1601 is not a substitute for channel filtering; test order of mixer→preselect/buffer/diplexer→ceramic→IF amp rather than casually concatenating unmeasured loads.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.** MAIN V2.6 7 sheets/138 references unchanged; no PCB MAIN/FRONT or DRC. The [FB455 provisional footprint PR #143](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) and [mixer A06 PR #123](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) remain separately **DRAFT**. [Issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141) remains open.
