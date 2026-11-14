# V2.7 — onsemi KSP10BU THT: emitter follower with nominal 1.5k/2k IF ceramic input

**2026-11-14 — Bench-only generic BJT; NOT production-approved.**

## Reuse existing architecture, do not substitute imaginary BJT

The *actual* standalone KiCad9 `IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT.kicad_sch` already has 10 THT positions, onsemi candidate **KSP10BU**, explicit pin1 **BASE**, pin2 **EMITTER**, pin3 **COLLECTOR**, bench rail 6V, bias resistors 22k/10k, emitter 2.2k, coupling capacitors 10n and 100k output reference. [Previous native generic BJT 9 corners](RAPPORTO_KSP10_IF455_GENERIC_BJT_DC_AC_CORNERS_DRAFT.md) at 5.5/6/6.5V × assumed BETA40/80/160 generated 455kHz output input-voltage ratios about 0.967–0.973 with **100kΩ load and without an IF455 tank**. Those do NOT characterize a filter input.

The [NextGen FB ceramic family OEM datasheet](https://www.nextgencomponent.com/uploads/soft/20241011/1-241011155152A8.pdf) uses **1500/2000Ω nominal input/output** resistive test termination depending on exact part. Nominal input resistance is not an actual frequency-dependent ceramic impedance, passband, attenuation, output load or noise figure.

## New native regression

`03_Verifiche/V2.7/verify_if455_ksp10_ceramic_load_native.py` guards genuine KiCad9 pin nets Q1701 (B1/E2/C3), input coupling, output coupling and 6V bench rail, plus the isolated IF455 input port. The original PR99 generic BJT `spice/if455_ksp10_generic_bjt_bias_ac.cir` is reused unchanged except the temporary `R1704` load value and rail/BETA; **27 real ngspice native transient DC and 455kHz AC cases** at 5.5/6/6.5V, illustrative BETA40/80/160 and resistive output dummy 100k, 2k or 1.5kΩ.

Each case records base/emitter/rail DC, emitter current as `Vemitter/2.2k`, output/AC source ratio. It verifies benchmark continuity `6V/BETA80/100k -> 0.970670` and normalized loaded transfer for all 18 lowered-load comparisons against same rail/BETA 100k baseline. As the load is capacitively coupled, DC bias must remain unchanged by load resistance in the *ideal deck*. No real KSP10 low-level noise, ESD, RF gain/Q, VBE/β distribution, temperature, output IMD, short circuit, filter 2k source/output match, LO-driven mixer, or crystal stage is represented.

## Comparison with J113: caution on distinct tests

The J113 [PR148](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/148) was characterized against an IF455 passive tank in the *same generic deck*, while this KSP10 generic bench has only a 50Ω generator and **no tank**. Do NOT compare their absolute Vout/Vsource as an apples-to-apples winner. The correct immediate comparison is within each buffer's own 100k/2k/1.5k load ratio. The later channel-noise/weak-AM/IMD analyses must use identical sources, tank, ceramic output and detector loads to rank any actual THT parts. Previous onsemi J113 weak-AM transient result at 24.34% of the direct path remains a real screening blocker.

## Decision gate

A KSP10 model with 0.9+ V/V is still an **idealized follower**, not a qualified 455kHz interface. No transistor substitution or hardware change is authorized. Obtain a genuine OEM spice or bounded measurable device model/actual samples for KSP10BU, measured 6V bias across temperature and BETA, low-level noise and two-tone IMD, and controlled actual ceramic 1500/2000Ω source/load condition. Before use, verify current production status, package pin orientation and finished PCB holes. [Issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141) remains open for AM/FM/USB/LSB/CW targets. A06 [PR123](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) and FB455 [PR143](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) footprints remain **DRAFT**. Master V2.6 7 sheets/138 refs unchanged, real PCB MAIN and FRONT absent and no DRC/release BOM.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
