# V2.7 — IF-port exploratory shunt admittance across frequency

**2026-11-14. Not qualified for hardware and not a selected diplexer.**

## Engineering reason

The SBL-1+ output IF load cannot be represented by a single 455-kHz transfer number. Mini-Circuits application note [AN00-009](https://www.minicircuits.com/appdoc/AN00-009.html) explicitly describes mixer characterization with pads providing 50-ohm ports at fundamental and significant harmonics; [AN00-011](https://www.minicircuits.com/appdoc/AN00-011.html) warns of reflected products with an unmatched IF-amplifier input. The [Mini-Circuits diplexer paper](https://www.minicircuits.com/app/FILTS8-2.pdf) documents the role of unwanted IF/sum-frequency termination. These references **do not** establish an actual 50-ohm SBL-1+ IF source impedance or approve any specific diplexer for this radio.

## Native 12-case experiment

`03_Verifiche/V2.7/verify_if_port_shunt_frequency_native.py` exports native KiCad9 netlists of existing standalone mixer and IF455 filter and preserves the unmodified IF3/IF4 source port and 10-pF C1601.

Four *temporary SPICE-only* trial branches at the IF filter input are tested using native ngspice AC current injection: NONE; R50 directly to ground; series R50+C100 pF to ground; series R50+C1 nF to ground. Three frequencies: **455 kHz, 1 MHz, 30 MHz**, for **12 native ngspice runs**. All scenarios share the same ideal, *unqualified* 1-mH/82-pF/30-pF/47-kΩ IF455 passive network with 16.5-Ω coil resistance approximation, and 10-pF output coupling/100-kΩ load.

For each case, export complex input-port impedance. Independently compute the branch admittance `Ybranch=1/Zloaded - 1/Zunloaded` and compare against the closed-form R/C shunt admittance. This guard detects misconnections or mistaken placement (e.g. mistakenly putting termination in series with the mixer) without pretending to qualify real mixer harmonic impedances.

A series RC shunt **is not a diplexer**: even if it drains higher frequencies more strongly than 455 kHz, it supplies no complementary, controlled low-pass path from mixer to IF filter and no demonstrated broadband match. At 30 MHz even the ideal model is not vendor-predictive: pad/lead parasitics, 1-mH inductor self-resonance, THT placement and RF return currents are unmodeled. The current source is a *small-signal probe*, not a measured source power level, and computed voltages from 1-A probing are ratios, not expected real operating levels.

## CI failure and parser correction — 14 November 2026

The first [Actions run #43587582419](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43587582419) **FAILED** in the new native test after KiCad/legacy checks, because ngspice `wrdata` emitted **one** correctly formatted AC row at 455000 Hz for the narrow `ac lin 2 455000 455001` request, while the parser incorrectly required exactly two. The recorded numeric sample was `18530.8105 - j19747.3349 Ω` for the unshunted baseline, consistent with the earlier IF455 port model. The parser now accepts one or two *native* samples while requiring a finite complex value and the **exact requested frequency on the first row**; no sample is synthesized and no electrical assertions are relaxed. Final CI still required before merging.

## Next gate

To propose real integration, characterize (or obtain valid OEM measurements for) SBL-1+ IF-port impedance under LO +7 dBm and realistic LO/RF inputs across desired and unwanted spectral products. Then design a frequency-defined two-path IF network, check input reflection, RF leakage, noise, conversion loss, component Q/SRF/tolerances, and only then create real THT CAD. Existing V2.6 seven-sheet master, V2.7 standalone schematics, PR #123 unqualified A06 footprint, BOM, and both absent PCB layouts are unchanged. No DRC or fab authorization.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
