# V2.7 — Mixer SBL-1+ IF-port termination: native port contract and test-only load matrix

**Date 2026-11-14 · Technical draft only; not a qualified mixer–filter interface.**

## Manufacturer evidence and the unresolved design requirement

Mini-Circuits official SBL-1+ datasheet: https://www.minicircuits.com/pdfs/SBL-1%2B.pdf (level-7 LO, IF DC–500 MHz, pins IF3+IF4 tied). Official application notes https://www.minicircuits.com/appdoc/AN00-009.html and https://www.minicircuits.com/appdoc/AN00-011.html explain how mixer characterization uses controlled **50-ohm port conditions** and that unexpected IF load impedance can influence distortion and intermodulation. https://minicircuits.com/appdoc/FILTS8-2.html discusses why constant-impedance filtering/termination across unwanted frequencies matters, rather than a narrow 455-kHz voltage reading.

These are **measurement conditions**, not evidence that the exact operating nonlinear SBL-1+ IF source impedance is a 50-ohm resistor at 455 kHz or its harmonics. The present standalone KiCad9 candidate has MX1701/3+4 connected to J1703/1, no 50-ohm termination or mixer output diplexer. The separate IF455 candidate J1601/1 feeds a nominal 10 pF coupling capacitor; it **must not** be called a matched 50-ohm mixer load.

## Native regression and bounds

The new `03_Verifiche/V2.7/verify_mixer_if_termination_native.py` exports **both actual KiCad9 netlists**, checks the correct IF3/IF4/GND and input pin relations, and asserts that a physical 50-ohm termination/diplexer is NOT present (no silent hardware claim). Then **9 native ngspice AC simulations** use the existing nominal passive IF455 deck and test hypothetical upstream series source R=50/1000/10000 ohms times a **test-only** shunt across the IF-port source node: none, 100, 50 ohms. The script records actual 455-kHz AC amplitudes and checks the baseline 10-pF/50-ohm source from prior V2.7 regressions.

The resistor load is across the test node at 455 kHz. It is **not** a low-pass/diplexer and may not maintain a broadband 50-ohm impedance across IF mixing products, DC or LO/RF leakage. It does not model the frequency-dependent nonlinear mixer, source voltage variations with load, noise, compression, IF power, or resistive thermal dissipation under real operation. The 10 pF filter and 16.5-ohm coil loss proxy remain unqualified.

## Architecture gate

Do not assign any new termination resistor, transformer or diplexer to the real mixer/KiCad master until measured or vendor-validated SBL-1+ IF port impedances and the required unwanted-signal handling are established, and the filtering/loading topology is analyzed jointly with receiver noise and adjacent-channel response. Any intended 50-ohm **termination at the port** must be distinguished from a source-model resistor, and its thermal/LO-leakage/IF signal loading verified. Existing master V2.6, standalone candidate values and both not-yet-existing PCBs remain unchanged. No production BOM qualification or real DRC.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
