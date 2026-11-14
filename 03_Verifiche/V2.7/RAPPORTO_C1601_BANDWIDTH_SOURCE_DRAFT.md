# V2.7 — IF455 C1601 nominal passband sensitivity vs hypothetical source impedance

**Status: exploratory, no hardware or source-model qualification. Date: 2026-11-14.**

## Why the 455 kHz scalar comparison is insufficient

The previous 15-case AC sweep measured the passive filter output at 455 kHz. A larger voltage at this **single** frequency need not mean better selectivity or a suitably centered passband. The source impedance of a Mini-Circuits SBL-1+ mixer IF port depends on actual LO excitation, RF excitation, IF termination and nonlinear conversion; the 50/1k/10k Ω resistors here are *not* vendor mixer specifications.

## Independent additional native check

`03_Verifiche/V2.7/verify_if455_c1601_bandwidth_native.py` repeats 15 *native* ngspice AC transfers (C1601=10/47/100/470/1000 pF × hypothetical Rs=50/1000/10000 Ω) over **300–650 kHz**, 1401 linear samples including exactly 455 kHz. It uses the existing, audited passive deck but varies C1601 **only inside transient temporary SPICE source files**, not KiCad. For every case it outputs peak frequency and amplitude, interpolated two-sided -3 dB crossings, -3 dB width, illustrative peak/BW and normalized amplitude at 455 kHz. Both -3 dB crossings must exist within the sweep; otherwise required CI fails closed. Established C1601=10 pF source-dependent transfer values are checked against prior regressions.

The nominal model includes ideal 1 mH, 82 pF + 30 pF trimming, coil loss 16.5 Ω **unqualified DCR stand-in**, damping 47 kΩ, output 100 kΩ and 10 pF output coupling. These are neither component-tolerance sweeps nor real measured parameters. Peak/BW is merely a *shape descriptor* for this bench circuit, not a complete receiver selectivity or adjacent-channel figure.

## Decisions explicitly not yet justified

This check **does not select 47 pF or any other C1601 value**, does not estimate actual mixer loading, noise figure, sensitivity, LO leakage, AGC, AM/FM/SSB bandwidth or PCB parasitic response. Existing C1601 remains 10 pF. A qualified change requires actual mixer IF port impedance, filter-Q and detector load over signal level, frequency, PVT and bench measurements, then native KiCad/ERC/network verification. The A06 footprint is separately unqualified on PR #123.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
