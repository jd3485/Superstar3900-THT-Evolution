# Two-stage PMOS OFF gate leakage — exploratory DC screen (17 November 2026)

## Native CAD contract
The new `verify_two_stage_off_gate_leakage_native.py` checks the actual KiCad9-exported netlist of the isolated 24-component THT lab, 54 pins and 14 nets, against the existing full pin-to-net reference. It verifies each 47k source-gate pullup and 10k sink resistor as separate physical components and both candidate 1N4106-1 branches. No change to radio MAIN V2.6 and no production PCB.

## Independent first-order screening assumption
The BJT is **commanded OFF**. Assume an external sink of 0/1/5/10/25/50/100 µA from each gate to return, 47k ±5%, source levels 0/5/9/13.8/20/48 V. With both Zeners assumed OPEN, fixed source and **hypothetical ideal return bound**, `|Vgs| = min(Vsource, Ileak*Rgs)`. This model is not an OEM leakage specification or a physical return clamp. It omits Cgs, gate charge, transient switching, body diode currents, thermal coupling, wiring, and high-voltage rail protection. Values above nominal rail are abstract fault-screen inputs, not permitted hardware operation.

126 cases per stage, 252 total. Of 126 per stage: 30 attain at least 2 V and 15 at least 4 V hypothetical magnitude; maximum 4.935 V at 100 µA and Rgs +5%. Those 2/4 V thresholds are **arbitrary markers**, NOT a characterized Vth or guaranteed turn-on for IRF9540N. A gate-to-return sink could therefore create appreciable bias even with logic command OFF; actual semiconductor leakage and current pathways require data/measurements. If Rgs is OPEN and leakage flows, this simple DC model cannot predict a bounded gate state.

## Qualification boundary / next evidence
Obtain OEM maximum leakage curves and tolerances of KSP42BU and power FET across temperature and abnormal supply, then characterize source stiffness, Zener knee under µA current and common supply/return faults using genuine simulations/hardware. No independence or fail-closed claim arises from identical per-stage counts. Issue #27 OPEN. Native CAD gate is FULL CI-only; local environment lacks KiCad9, so verification remains pending final PR SHA Actions.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
