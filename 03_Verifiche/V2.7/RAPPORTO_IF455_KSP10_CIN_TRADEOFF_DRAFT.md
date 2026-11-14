# V2.7 — KSP10 IF455 input coupling: tank loading versus signal transfer

**14 November 2026, exploratory generic ngspice only; NOT a circuit change.**

## Existing evidence

[PR156](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/156) finally put J113 and KSP10 on the same idealized IF455 tank, and discovered that the physically *drafted* KSP10 has **10nF** input coupling from IF455 tank while J113 had **10pF**. For generic KSP10 β80, 2kΩ resistor-only dummy: 10nF gives only **0.124579814V/V** at the tank, whereas 10pF gives **0.462701267V/V**. The stronger base drive at 10nF does NOT imply a well-terminated IF tank.

## New native evidence

`03_Verifiche/V2.7/verify_if455_ksp10_coupling_tradeoff_native.py` exports genuine native KiCad9 KSP10 and IF455 schematic netlists and verifies transistor base/emitter/collector and tank pins. It reuses the exact already verified PR156 common 50Ω hypothetical source, LC IF455 (1mH/82+30pF etc.) and 6V bench supply. Only a **temporary ngspice CIN** is changed: **10, 22, 47, 100, 220, 470, 1000, 10000pF** × generic `BETA=40/80/160` × **1500/2000Ω resistor-only** dummy filter loads = **48 real native ngspice cases**.

For each case it logs both **tank voltage and buffer output voltage** at 455kHz, the base-drive level, tank ratio relative to the 10pF experiment and buffer ratio relative to the existing 10nF candidate. PR156 baseline at 10pF and 10nF with β80 and 2kΩ dummy is pinned numerically. It also reports the maximum output-amplitude capacitance per corner *as an unconstrained diagnostic*, not a candidate to install. A capacitor value is NOT approved merely by maximizing modeled Vout: the design must preserve band shape, source termination, unwanted mixer product absorption, adjacent-channel rejection and noise margin.

## Explicit nonqualifications

The original KSP10 schematic **continues to specify 10nF** and is not integrated into MAIN. Its 22k/10k bias and 2.2k emitter resistor remain unchanged. Models are generic BJT, 16.5Ω nominal DC-coil loss reused as ideal AC R, **no measured inductor SRF/Q or SBL-1+ IF source**. The model's 1.5/2kΩ dummy is not a real FB455 ceramic input `Z(f)` and there is no output filter transfer/insertion loss, OEM transistor noise/IMD, distortion or weak-AM sensitivity test. No actual KiCad/BOM/footprint/PCB changes are authorized.

**Next design gate:** measured/qualified IF455 tank output loading and BJT input Z(f), selection of a real decoupling topology or preamplifier operating point in a full TX-safe RX cascade, and per-mode filter targets under [issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141). Provisional mixer A06 footprint [PR123](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) and ceramic FB455 [PR143](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/143) remain unqualified draft. The MAIN and FRONT PCBs do not exist, no DRC PCB has occurred.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
