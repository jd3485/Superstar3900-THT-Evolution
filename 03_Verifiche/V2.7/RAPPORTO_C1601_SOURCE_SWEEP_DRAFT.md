# V2.7 — C1601 source coupling sensitivity (bench only)

Date: 2026-11-14. **Unqualified exploratory calculation; no mixer model, no hardware approval.**

## Question

The real IF455 KiCad candidate currently has **C1601 = 10 pF in series** between source port J1601/1 and the tank. At 455 kHz the ideal magnitude of series reactance is approximately **34.979 kΩ**. That is not a 50 Ω match, nor proof that the mixer can drive the tank. The SBL-1+ IF output impedance is uncharacterized in this project, especially as a function of RF/LO drive and IF loading.

## Native, reproducible experiment

`03_Verifiche/V2.7/verify_if455_c1601_source_sweep_native.py` reuses the previously tested passive IF455 ngspice deck and checks **15 real AC simulations**: C1601 = 10/47/100/470/1000 pF × hypothetical Thevenin source resistance = 50/1000/10000 Ω. Reads 455 kHz exactly from the native linear AC sweep, reports transfer to detector port and post-source input, verifies finite outputs and independently cross-checks the established 10 pF/50 Ω baseline.

Only the **temporary SPICE deck** is varied. Existing KiCad schematic, BOM, footprint, mixer interface and all main boards are unchanged. Existing 1 mH coil, nominal 16.5 Ω loss proxy, 82+30 pF, 47 kΩ damping, 100 kΩ output and 10 pF output coupling are **assumptions**, not OEM or bench measurements.

## Gate interpretation

Even if every simulator job succeeds, **do not choose or change C1601** from these results. Before schematic integration: characterize complex IF source impedance/load curves of the OEM SBL-1+ at realistic +7 dBm LO; include the mixer nonlinear conversion/noise behavior and LO leakage; evaluate IF passband, detector input and source interaction; repeat with tolerance, temperature, parasitic layout and hardware samples. A linear passive source sweep cannot establish receiver gain, noise figure, adjacent-channel rejection or PCB readiness.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
