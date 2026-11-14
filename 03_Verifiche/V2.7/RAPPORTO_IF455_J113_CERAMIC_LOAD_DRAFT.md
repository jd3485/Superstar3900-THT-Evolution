# V2.7 — onsemi J113 IF455 THT buffer: does the candidate drive a 1.5k/2k ceramic input?

**14 November 2026 — bench-only generic NJF simulation, not a qualified RF design.**

## Reuse of existing work

The project *already has* a real KiCad9 native J113 source-follower prototype at `04_KiCad/V2.7_DRAFT/IF455_J113_SOURCE_FOLLOWER/IF455_J113_SOURCE_FOLLOWER_THT_V2_7_DRAFT.kicad_sch`, isolated and not connected to MAIN. [Earlier J113 report](RAPPORTO_IF455_ONSEMI_J113_SOURCE_FOLLOWER_DRAFT.md) and PR #106 used onsemi **J113**, pin1=D / pin2=S / pin3=G TO-92, 6V bench supply and self-bias Rsource 2.2k, with a generic NJF model. Those transient studies found broad performance variations and did **not** approve the J113: at weak 0.5V excitation the modeled AF output could be only 24% of the direct detector path. This revision does NOT treat the earlier weak-signal rejection as resolved.

[onsemi J113 datasheet](https://www.onsemi.com/pdf/datasheet/mmbfj113-d.pdf) provides TO-92 pinout and application limits. [DigiKey J113](https://www.digikey.com/en/products/detail/onsemi/J113/1048989) currently lists the THT TO-92 product as Active; inventory and lot authorization are separate. The J113 was designed primarily as a low-level analog switch and is not specified by the OEM as a 455kHz low-noise ceramic-filter driver.

## Native KiCad9 + actual nonlinear device equations (generic only)

`03_Verifiche/V2.7/verify_if455_j113_ceramic_load_native.py` exports genuine KiCad9 source-follower and IF455 LC tank netlists, guards J113 pin1/2/3, gate DC return and source/output coupling, and executes **18 ngspice AC native full-deck sweeps** 445–465kHz. The 6V drain rail, 2.2k source resistor, 10p gate injection, 1M gate return, 10n source-output coupling, LC tank and 50Ω hypothetical source follow the isolated existing bench. The semiconductor model is deliberately **generic** NJF with illustrative `VTO=(-0.5,-1.5,-3)V` and `IDSS=(2,10)mA` (beta=`IDSS/|VTO|²`; `CGS=5p CGD=2p RD=RS=20Ω` are guesses).

Three effective output load resistors per corner: **100kΩ** light bench reference, **2000Ω** candidate NextGen FB nominal input dummy, and **1500Ω** alternative ceramic nominal input dummy. The temporary output dummy replaces R1803=100k rather than adding it in parallel (in the 100k case it is identical to the physical schematic). For each load it records 455kHz tank/buffer voltage, small-signal transfer, and upper/lower ±10kHz relative magnitude. Then it compares the loaded output amplitudes against its own 100k baseline, *without censoring poor-performing corners*.

**The 1.5k/2k dummy is a resistor, not an actual ceramic filter.** The real vendor input impedance varies with frequency and its output must be terminated; this deck has no model of passband, insertion loss, group delay, noise figure, IMD, compression, BFO or actual SBL-1+ source impedances. A small-signal AC linearization around its generic NJF DC operating point is **not** a test of strong-signal linearity or a full J113 device qualification.

## Engineering gate

The candidate already failed to be uniformly superior to direct weak-signal AM reception in earlier generic corner screening. This additional 1.5k/2k load stress can confirm or reject simple assumptions about its ability to drive the proposed ceramic termination. Even if voltage ratios appear good, **do not integrate** until OEM-model/test transistor noise, gm & drain current at 6V, worst-case input swing, 2k output impedance, stability, detector behavior and system supply/failures are qualified with actual THT parts and a physically tested sample.

MAIN V2.6 (7 sheets/138 refs), mixer, IF455 tank, SBL-1+ and FB455 footprint candidates are unchanged. [PR #123](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) and [PR #143](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) remain **DRAFT** due to OEM package/lead mechanics; [issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141) for mode-specific selectivity remains open. No real PCB, no PCB DRC.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
