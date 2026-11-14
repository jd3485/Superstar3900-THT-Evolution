# V2.7 — IF455 one-tank channel-offset response is not a channel filter

**Status 2026-11-14: engineering bench characterization, NOT a regulatory or receiver bandwidth target.**

## Required design decision

The currently integrated **master V2.6 is NOT a completed AM/FM/SSB receiver**. The IF455 candidate is an **isolated**, *single* 1mH/82pF+30pF tuned network; downstream detector loading and actual SBL-1+ mixer output impedance are not qualified. A -3dB passband around **42.6kHz** for the optimistic 16.5Ω proxy with 100kΩ bench load was measured in [PR138](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/138), with the 82.7286Ω *hypothetical* loss scenario widening to about **53.7kHz**. Those figures are not channel selectivity.

Before ordering an IF filter, **define the supported RX modes, channel raster/spacing, occupied IF bandwidth, adjacent-channel rejection, insertion loss, group delay, detection topology and realistic output loading** from the actual architecture and applicable target standard. The current repository does not yet support assigning a universal 3kHz SSB / 6kHz AM / 10kHz FM target as approved specifications. The offset examples below are diagnostic frequencies, not standards.

## New native verification

`03_Verifiche/V2.7/verify_if455_channel_selectivity_native.py` exports the genuine native KiCad9 IF455 netlist and tests J1601, C1601, L1601 and ground connectivity. It runs **four native ngspice 300–650kHz AC sweeps**, all with *hypothetical* 50Ω Thevenin upstream source: output loads 100kΩ-only and a passive gate-RC surrogate; coil-loss assumptions 16.5Ω DCR-as-RF proxy and 82.7286Ω illustrative Q790-equivalent moved hypothetically to 455kHz. No KiCad or physical component value is modified.

Each sweep records the peak frequency, interpolated two-sided -3dB bandwidth and the transfer amplitude **at exactly 455kHz**, then computes **relative voltage attenuation** at ±3, ±5, ±10, ±20 and ±40kHz *with both upper and lower side reported separately*. For a lower/higher-frequency test point, `20·log10(|H(455k)| / |H(455k±Δf)|)` is reported, so even negative rejection would remain visible. No absolute channel spacing or regulatory mask is claimed.

The native CI intentionally guards that the modeled rejection at **at least one of the ±10kHz offsets remains below 3dB** for every existing single-tank case, thereby surfacing the insufficiency of this loose tank as a standalone narrow-channel filter. This does NOT prove adjacent-channel rejection, modulation fidelity, recovered AF SNR, cascade response, transmitter cleanliness, or performance against any service specification. Actual architecture needs a **dedicated, selected and qualified IF channel filter/chain** following a separately evaluated mixer interface.

## No-fab gate

No physical modification to KiCad, the seven-sheet V2.6 master, mixer IF C1601, L1601, BOM or PCB. The mixer A06 footprint remains draft PR #123. Do not infer genuine channel selectivity until the receiver requirements and physical IF parts are qualified. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
