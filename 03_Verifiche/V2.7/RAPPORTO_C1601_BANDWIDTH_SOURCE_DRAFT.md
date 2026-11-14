# V2.7 — IF455 C1601 nominal passband sensitivity vs hypothetical source impedance

**Status: exploratory, no hardware or source-model qualification. Date: 2026-11-14.**

## Why the 455 kHz scalar comparison is insufficient

The previous 15-case AC sweep measured the passive filter output at 455 kHz. A larger voltage at this **single** frequency need not mean better selectivity or a suitably centered passband. The source impedance of a Mini-Circuits SBL-1+ mixer IF port depends on actual LO excitation, RF excitation, IF termination and nonlinear conversion; the 50/1k/10k Ω resistors here are *not* vendor mixer specifications.

## Independent additional native check

`03_Verifiche/V2.7/verify_if455_c1601_bandwidth_native.py` repeats 15 *native* ngspice AC transfers (C1601=10/47/100/470/1000 pF × hypothetical Rs=50/1000/10000 Ω) over **300–650 kHz**, 1401 linear samples including exactly 455 kHz. It uses the existing, audited passive deck but varies C1601 **only inside transient temporary SPICE source files**, not KiCad. For every case it outputs peak frequency and amplitude, interpolated two-sided -3 dB crossings, -3 dB width, illustrative peak/BW and normalized amplitude at 455 kHz. When both -3 dB crossings exist within the sweep, the result is classified BRACKETED and reports its interpolated bandwidth. When a crossing does **not** exist, the case is explicitly classified OUTSIDE_300_650KHZ_WINDOW with null bandwidth and edges; this is an unqualified observation, not an inferred passband. The unchanged 10 pF baselines **must** remain fully bracketed or CI fails. Established C1601=10 pF source-dependent transfer values are checked against prior regressions.

The nominal model includes ideal 1 mH, 82 pF + 30 pF trimming, coil loss 16.5 Ω **unqualified DCR stand-in**, damping 47 kΩ, output 100 kΩ and 10 pF output coupling. These are neither component-tolerance sweeps nor real measured parameters. Peak/BW is merely a *shape descriptor* for this bench circuit, not a complete receiver selectivity or adjacent-channel figure.

## CI failure and corrective interpretation

The first FULL run [#43584881817](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43584881817) **FAILED**, because a 470 pF trial peaked at the 300 kHz lower boundary and the prior test asserted that all -3 dB boundaries were contained in the 300–650 kHz window. This failure is an **important model discovery**, not a reason to suppress failed regressions or fabricate bandwidth values. The repaired test records such cases as unbracketed, preserves all simulations and validates nominal 10 pF baselines. Any full-bandwidth estimate outside the given window requires a separate extended frequency sweep and model review.

## Decisions explicitly not yet justified

This check **does not select 47 pF or any other C1601 value**, does not estimate actual mixer loading, noise figure, sensitivity, LO leakage, AGC, AM/FM/SSB bandwidth or PCB parasitic response. Existing C1601 remains 10 pF. A qualified change requires actual mixer IF port impedance, filter-Q and detector load over signal level, frequency, PVT and bench measurements, then native KiCad/ERC/network verification. The A06 footprint is separately unqualified on PR #123.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
