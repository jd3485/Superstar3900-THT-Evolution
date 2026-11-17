# Two-stage PMOS THT gate release: ideal initial-charge test (17 November 2026)

## Scope and native CAD gate
The isolated **KiCad9** two-stage anti-series PMOS experiment is unchanged: 24 physical THT components, **54 pins / 14 native nets**, with both stages' 47k source-to-gate pullups, 10k driver sink branches and twin Zener source/gate orientation checked against an exported KiCad netlist. This revision adds a separate release transient, **not** another PCB or independent safety circuit.

## Model and test
On loss of the hypothetical ON command, let `v=|Vgs|` initially be 5 or 12 V and let a *constant hypothetical* residual sink current remain active. With Rgs = 44.65/47/49.35 kΩ and assumed lumped gate capacitance = 1/10/100 nF, the ideal differential equation is `C dv/dt = I_sink - v/Rgs`. Exact solution at multiples of tau=Rgs*C is `v(t)=I_sink*Rgs+(v0-I_sink*Rgs)*exp(-t/tau)`. Sink currents: 0/5/25/100 µA; times 0/1/2/3/5 tau. There are **360 combinations per stage, 720 in total**. Numerical implicit trapezoidal integration (1024 steps) independently cross-checks the analytical formula within 0.1 mV.

Analytical markers per stage: 189/360 at or above 2 V, 171/360 at or above 4 V, including 18/360 at or above 4 V at five tau. The minimum ideal residual drop over this matrix is 0.0336897 V, for an assumed initial 5 V with no sink after 5 tau. Tau extremes are 44.65 µs and 4.935 ms. **These marker levels are arbitrary**, not manufacturer ON/OFF thresholds or guaranteed recovery criteria.

## Critical limitations and gates
- The capacitances are hypothetical, **not** measured/OEM Ciss; non-linear Qg, Miller coupling, drain voltage slew, switching current, source movement, and PVT are absent.
- Constant residual sink is assumed, not demonstrated for a failed or disabled BJT circuit. A nonzero sink gives a nonzero asymptotic gate bias; **there is no guaranteed OFF state**.
- The RC test is analytical, cross-checked numerically, and anchored to KiCad9 exported connectivity in FULL CI. It is **not** an ngspice vendor transistor transient, physical bench test, EMC test or hardware safety qualification.
- The PCB-MAIN and PCB-FRONT remain incomplete; issue #27 remains OPEN. Do not connect to a vehicle or battery and do not energize RF TX.

Parent integration: PR #337 merged in `1995012ad3585bbe86cdbd212668d5768d984367`, run #44076803996 FAST/FULL/Required SUCCESS. This new revision requires **its own** final-HEAD FAST/FULL/Required SUCCESS and audit before merge. Current branch is not integrated until then.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
