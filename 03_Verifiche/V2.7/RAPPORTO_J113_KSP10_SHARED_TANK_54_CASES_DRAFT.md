# V2.7 — J113 versus KSP10BU on a common IF455 source/tank, 54 AC cases

**14 November 2026. Screening evidence only: both active devices use generic SPICE, not validated OEM models.**

## Why earlier absolute gains cannot be compared

The J113 standalone bench in [PR148](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/148) includes an actual IF455 nominal passive tank at its 50Ω hypothetical input and a **10pF tank-to-gate coupling**. The KSP10BU standalone in [PR154](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/154) was driven directly by a 50Ω source without that tank, and uses **10nF tank-to-base coupling** in its independently drafted cascade. The old numerical amplitudes are therefore *not* evidence that one device is better.

## Fairer controlled native ngspice comparison

`03_Verifiche/V2.7/verify_if455_j113_ksp10_shared_tank_native.py` exports the **three actual native KiCad9 schematics** (standalone IF455 tank, onsemi J113 TO-92 candidate, KSP10BU TO-92 candidate) to protect pin B/E/C versus D/S/G and IF455 tank source connections. It simulates the same **1V AC 50Ω source**, `C1601=10pF`, `L1601=1mH` with an **unqualified ideal 16.5Ω series loss**, `C1602=82pF C1603=30pF R1601=47k`, `C1604=10pF` and `R1602=100k`. Both follower families have exactly the same 6V trial rail and output coupling C10n, with a resistor-only effective ceramic input dummy **100k/2k/1.5kΩ**. Device models/bias remain their existing case-specific generic NJF/BJT values, not matched for noise/linear swing, because real biases differ by design.

To avoid hiding the essential difference, **both followers are run with either 10pF or 10nF tank-to-device input coupling**. J113: generic `VTO=-0.5/-1.5/-3V` × illustrative `Idss=2/10mA` = **6 corners**; KSP10: hypothetical `BETA=40/80/160` = **3 corners**. Total: `(6+3) × 2 couplings × 3 loads = 54` actual **ngspice AC** 455kHz test decks. For each: tank output, actual buffer output, buffer/tank ratio, absolute device-input amplitude; matched 1.5/2k-to-100k load sensitivity. Crucially, a numerical anchor pins prior verified **J113/10p/2k/−3V/2mA 455kHz** transfer `0.261831624V/V`. KSP10 10p and J113 10n are counterfactual *SPICE only*, **not changed KiCad capacitors**.

## Interpretation and gates

A common source and tank permits limited comparison of *these generic models under an identical input network*. This is still not a level playing field for production: the transistor noise power/gain correlations, temperature/lot variability, non-linear distortion, actual ceramic filter impedance Z(f), downstream filter output termination, SBL-1+ IF source under LO drive and BFO/AM/SSB/FM/CW detection are unknown. The common input source remains a hypothetical 50Ω Thevenin generator and the tank idealized RF loss model was flagged by [PR136](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/136) and [PR138](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/138). **Do not select J113 or KSP10, or replace 10nF with 10pF in actual KiCad**, using this study alone.

The isolated designs' earlier weak-AM [J113 PR106](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/106) and KSP10 nonlinear generic detector tests are not directly comparable unless a unified full chain is simulated, with small-/large-signal stimuli and noise. User-accepted RX modes AM/FM/USB/LSB/CW remain open to quantitative channel mask selection [issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141). Draft footprints SBL1+ [PR123](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) and NextGen FB455 [PR143](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) remain unassigned and unqualified.

**Master 7-sheet V2.6, native candidate schematics/BOM/PCB unchanged. MAIN/FRONT physical PCB absent; no board DRC or fab approval. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
