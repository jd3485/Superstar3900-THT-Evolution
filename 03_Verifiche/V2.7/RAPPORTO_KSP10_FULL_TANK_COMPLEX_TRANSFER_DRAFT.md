# V2.7 — KSP10 full IF455 tank: complex transfer and loading (DRAFT)

14 November 2026. This experiment extends merged PR #162, which calculated only isolated base/port impedance. The same generic 6V KSP10 emitter-follower now loads the actual shared *model* of the 455kHz LC tank; complex voltages are sampled at tank, coupling output and follower output.

## Native method

`verify_if455_ksp10_full_tank_complex_transfer_native.py` exports KiCad9 standalone KSP10 and IF455 native netlists and verifies pin/net contracts. The laboratory ngspice deck reused from the 54-case J113/KSP10 shared tank comparison contains the hypothetical 50-ohm generator, L=1mH with Rseries=16.5 ohm, C=10+82+30pF and other previously defined resistors, KSP10 6V generic BJT model, 22k/10k base bias and 2k2 emitter. Sweep generic beta 40/80/160 × nominal dummy resistive load 1.5k/2k ohm × temporary CIN 10p/100p/1n/10n × 445/455/465kHz = **72 independent native AC solves**. Capture real and imaginary voltage components and calculate complex tank-to-output gain including phase, not only magnitude. Check 10p to 10n load effect at both tank and output; print raw per-case metrics in CI.

A full-tank network response is not equivalent to OEM performance. The shared circuit is itself an unqualified RLC model and its 50-ohm generator is *not* the LO-driven SBL-1+ IF impedance. The resistive dummy is not a true complex ceramic filter. No manufacturer transistor noise/nonlinear model, large-signal compression, thermal variation, frequency-dependent ceramic impedance, production coil Q/SRF, real PCB or AM/FM/USB/LSB/CW channel selection is included.

## Gate, boundaries and decisions

This script is a mandatory additional command within existing `ci/full_regressions.py`; no extra Actions workflow. **No values are selected for integration** by this simulation; master V2.6, candidate THT KiCad drawings, BOM and MAIN/FRONT PCB remain unchanged. Verify FULL CI on final PR head, then decide whether to merge verification-only work. Production and transmission prohibitions unchanged: **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.
