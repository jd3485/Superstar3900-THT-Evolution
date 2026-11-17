# FRONT mute K1901 — six-hole OEM THT relay mismatch and coil screening (17 Nov 2026)

## Verified primary OEM source
Aratas (formerly Omron Components) product family **G5V-1** is currently marked **“In production”** on the manufacturer product page, viewed 17 Nov 2026: https://www.aratas.com/eu-en/products/relays/G5V-1 . This is a FAMILY status, not final sign-off for each ordering suffix. Official G5V-1 data sheet K048-E1: https://www.aratas.com/system/files/datasheet_pdf/K048-E1.pdf, first page (standard **5 VDC** type: rated 30 mA, nominal 167Ω, 150mW, ±10% coil resistance at 23°C) and **page 4** (manufacturer BOTTOM-VIEW **SIX mounting holes nominal 1mm**, 12.5 × 7.5 × 10mm envelope). SPDT (Form C), PCB through-hole. The official discontinuation page uses “G5V-1(Single crossbar)” as a *replacement for G2E-184P* discontinued 2010; this is **not** a G5V-1 discontinuation assertion.

## Native CAD finding — not a drop-in
K1901 in `04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch` is currently a deliberately **abstract five-pin** relay, `Footprint=""`. The native FRONT parent KiCad9 netlist shows K1901 pin1 COM, pin2 NC/AF_GND, pin3 NO/volume, pin4 coil+, pin5 coil-. The real G5V-1 package drilling drawing instead has **six physical terminals**. These schematic numbers are **not OEM physical pad numbers**. Merely setting an arbitrary library footprint or renaming the five-pin value to G5V-1 is strictly forbidden: a new independently mapped six-physical-terminal KiCad symbol and exact THT 6-pad footprint must be reviewed with the OEM BOTTOM-view layout, including any duplicated contact terminal and correct pin↔net assignment; verify netlist and real PCB pad correspondence.

The candidate 5V coil with 167Ω ±10% at 23°C draws hypothetically 27.22–33.27 mA at exactly 5.00V, and consumes 136.1–166.3mW. Nominal 150mW (OEM); standard model max must-operate voltage 80% of 5V (4.0V) at OEM test condition. **These are not guaranteed installed margins**: two stacked BC33725BU candidate NPNs, their VCE(sat) at needed I and base drive, rail droop, temperature, supply tolerance, startup and release need independent assessment. Do not assume 5.00V appears across the relay coil, nor that mute returns to NC on every single failure; AF_GND / welded NO still block fail-safety. The relay is a candidate only, not BOM approval.

## Regression and immediate blockers
`03_Verifiche/V2.7/verify_front_mute_g5v1_oem_candidate_gate_native.py` exports native FRONT parent KiCad netlist, locks the present five K1901 physical pin-to-net assignments, confirms missing footprint, records the OEM **six-hole conflict**, and audits coil nominal/tolerance bounds. Wired into FULL; no new CAD footprint, actual PCB, contact stress or mechanical qualification has been asserted.

Next coherent design step: create **separate six-pin candidate symbol/footprint** and independent test of TOP/BOTTOM pin mapping against OEM drawing; migrate K1901 only after a reviewed mechanical and electrical fit, verify 5V coil drive across PVT and ensure NC mute failure behavior. The existing FRONT 13ref partial PCB deliberately does not contain K1901.

Parent [PR #341](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/341) merged main `bcc324d5ae41d35d032d59555bc288f2aa7a1b97`, run #44123242864 FAST/FULL/Required SUCCESS. This new revision requires its own final SHA CI.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
