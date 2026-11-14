# V2.7 — 2500-28J Q(f) versus DCR: IF455 loss-model qualification gate

**14 November 2026. Exploratory test cases, no production or schematic qualification.**

## Component source and what can actually be inferred

Real KiCad9 standalone IF455 L1601 is labeled `1mH_DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED`. [Delevan 2500-28J on DigiKey](https://www.digikey.it/it/products/detail/delevan/2500-28J/3479912) lists **active** THT axial component, ±5% tolerance, **DCR maximum 16.5Ω**, **Q=60 at 790kHz**, and **minimum isolated SRF 2.8MHz**. These quantities MUST NOT be conflated:

- DCR max 16.5Ω is a DC limit, *not* guaranteed series AC loss at 455kHz.
- For an isolated nominal series inductor, `Q=ωL/Rac` gives `Rac ≈ 2π·790000·0.001/60 = 82.728607Ω` **at 790kHz** under an ideal lumped-series approximation. It is not a vendor-specified 455kHz loss. Near SRF and with winding/fixture parasitics, even this equivalent can mislead.
- The **minimum** self-resonance 2.8MHz does not give a single winding capacitance or broadband impedance curve. Final IF bandwidth and RX gain/noise cannot be inferred from the catalog alone.

## Reproducible native experiment

`03_Verifiche/V2.7/verify_if455_2500_28j_q_vs_dcr_native.py` exports the actual IF455 KiCad9 netlist and preserves L1601, J1601/1 and C1601 connectivity, then performs **8 native ngspice** 300–650kHz linear AC sweeps. With the existing nominal C1601=10pF, 1mH/82+30pF shunt tank, 47k damp, 10pF output, 50Ω *hypothetical* source and 100k output reference or passive gate RC, it varies **only temporary model RLOSS**: 16.5Ω (legacy DCR proxy); 41.3643Ω; 82.7286Ω; 165.4572Ω.

For both passive load assumptions it logs peak, interpolated two-edge −3dB bandwidth, 455kHz transfer and all parameters. It guards the established 16.5Ω baseline (0.835055562 V/V and 42556.7Hz bandwidth), so a silent change to the native bench is caught. The three larger resistance values are **sensitivity scenarios, not OEM Q at 455kHz**.

## Engineering decision

**The 16.5Ω series RF-loss model is NOT qualified.** Do not select coil, detector/IF amplifier, adjacent-channel rejection, C1601 or mixer diplexer from any of these sensitivity results. Acquire Delevan 2500-28J measured/guaranteed RF Q(f), equivalent RF resistance and impedance on realistic PCB at 455kHz and harmonics, with temperature/lot variance, and verify the real receiver IF bandwidth requirement. No alteration to master V2.6, IF455 candidate KiCad, BOM, footprints, RF hardware or PCB (MAIN/FRONT remain absent). [PR #123 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) remains draft and unqualified.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
