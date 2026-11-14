# V2.7 — filtro IF di canale THT: selezione OEM preliminare + footprint FB455 candidata

**2026-11-14 · NON qualificato, nessuna assegnazione KiCad alla radio, NO FAB.**

## Perché la selezione è necessaria

[Issue #141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141) stabilisce che il ricevitore deve supportare **AM/FM/USB/LSB/CW**, ma i criteri quantitativi di filtro e il piano IF (10.695 MHz / 455 kHz candidati) restano **TBD**. In [PR #140](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/140), il solo tank IF455 presenta meno di 1 dB di attenuazione a ±10kHz nel caso base. Non dichiararlo filtro di canale.

## Fonti OEM e confronto non intercambiabile

| Topologia / MPN | IF | Banda (attenuazione e convenzione) | Z nominale | Package | Stato |
|---|---:|---|---:|---|---|
| NextGen **FB455K0000L005**, 5 pin, 455kHz ceramico multipolo | 455kHz ±1kHz centratura | **±6kHz a −6dB *min***; selectivity (50dB) ±12.5kHz *max* nella tabella OEM, **stopband garantita 45dB min**, non assumere 50dB | 2000Ω source/load, circuito Rg+R1=R2 | DIP/THT Case 11070, 11×7×8mm | Distributore DigiKey **Active** (Marketplace, lotto minimo e lead time da verificare) |
| NextGen **LTM455DW00L003**, ceramic 5 pin | 455kHz | **10kHz BW**, convenzione del distributore da convalidare sul foglio OEM del MPN | 1500Ω | THT 5 pin, 9.5×6.5×6.6mm | DigiKey Marketplace **Active**, non ancora footprint verificata |
| NextGen **LTM455FW00L005**, ceramic 5 pin | 455kHz | **6kHz BW**, convenzione del distributore da confermare con datasheet specifico | 1500Ω | THT 5 pin, 9.5×6.5×6.6mm | DigiKey Marketplace **Active** |
| ECS **ECS-10.7-7.5B** quarzo monolitico (4 poli), first IF alternative | **10.700 MHz** | **7.5 kHz** full nominal, 3dB guaranteed ±3.75kHz min in ECS MCF table | **1800Ω // 4pF** | HC-49/U ×2, THT (verify each pin map) | OEM site currently catalogs series; procurement status TBD |
| Murata **CFWLA455KF1Y-B0** (historical reference only) | 455kHz | 6kHz BW (distributor) | 2000Ω | THT 5 pin | **OBSOLETE — DO NOT SELECT** |

**OEM NextGen FB source** [specification PDF, case 11070 Rev A4 Oct 10 2024](https://www.nextgencomponent.com/uploads/soft/20241011/1-241011155152A8.pdf), visually checked pages 2–5: p3 **BOTTOM VIEW** has lead 4/3/2/1 on long row and pin5 offset beside pin4 (not a five-column grid); p4 **measurement circuit** specifies `Rg+R1=R2=source/output impedance`, input pin1, grounded pins2/3/4, output pin5. p5 specifications for **FB455K0000L005** are series reference in FB450K0000L007 document, **not a signed per-MPN certificate**, so manufacturer must confirm exact sold suffix/lot. OEM schematic shows neither an automatic 50Ω mixer match nor a model of the passband shape.

DigiKey references:
- [FB455K0000L005](https://www.digikey.co.uk/en/products/detail/nextgen-components/FB455K0000L005/21853572)
- [LTM455DW00L003](https://www.digikey.com/en/products/detail/nextgen-components/LTM455DW00L003/27784816)
- [LTM455FW00L005](https://www.digikey.com/en/products/detail/nextgen-components/LTM455FW00L005/27784807)
- [Murata obsolete](https://www.digikey.co.uk/en/products/detail/murata-electronics/CFWLA455KF1Y-B0/4419721)
- [ECS-10.7-7.5B OEM](https://ecsxtal.com/products/filters/crystal-mcf-filters/ecs-10.7-7.5b/).

## New actual KiCad9 isolated footprint candidate — not approved

`04_KiCad/V2.7_DRAFT/FILTER_IF455_NEXTGEN_CANDIDATE/FB455_CANDIDATE.pretty/FB455_11070_UNQUALIFIED.kicad_mod` stores five *native through-hole pads* with labels 1..5 and explicit NO FAB. The pad coordinate construction originates from the OEM **BOTTOM VIEW** with pin4=(0,-2.15), pin3=(2.9,-2.15), pin2=(5.8,-2.15), pin1=(8.4,-2.15) and pin5=(0.8,+2.15) mm, converted by **provisional horizontal X reflection** for KiCad PCB TOP. Note the **pin5 +0.8mm offset near pin4**. Because the OEM page-3 **TOP VIEW has no pin1 orientation cue**, the chosen PCB-TOP reflection axis MUST be checked against the real branded case before pin1 placement, etching, or assembly. Candidate pad diameters **1.5mm** and drills **0.8mm** are *design guesses*: manufacturer lead width approx 0.2±0.05mm in side projection alone does NOT qualify the 3D lead, plating, finished-drill, solder meniscus, hole-to-mold positions, body tolerances or factory process. **Never assign the footprint into real schematic before confirmation.**

`03_Verifiche/V2.7/verify_fb455_case11070_provisional_native.py` extracts genuine native KiCad9 IF455 schematic nets to protect existing J1601→C1601→L1601 wiring, validates all five new pad/function coordinates against the *OEM bottom-view-derived* provisional coordinate table and executes **native KiCad9 SVG footprint export**. No filter component has been integrated or simulated as an unrealistically ideal passband. This is pin-pad contract evidence, not PCB DRC.

## Architecture/qualification gates

The current mixer benchmark assumes various Thevenin source Rs; it does **not** prove matching to **2000Ω** nor a compensated network. A real filter must have characterized termination `Rg+R1=R2=2000Ω`, insertion loss/bandwidth PVT under intended input/output stages, and pin5 isolation from ground and shield. **Do not simply replace C1601 with the filter**, or copy the same footprint to LTM candidates.

ECS 10.700 MHz crystal filter cannot directly substitute the candidate **10.695 MHz** first-IF oscillator/plan: **5kHz frequency error** is material relative to its 7.5kHz bandwidth. FM/AM/SSB/CW may require separate selectable filters/paths, not one universal BW. Quantified masks remain open [#141](https://github.com/jd3485/Superstar3900-THT-Evolution/issues/141).

Main V2.6 (seven sheets/138 refs) unchanged; both PCB layouts missing, no PCB DRC/actual RF characterization/parts qualification. Existing [PR #123 SBL1 A06](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/123) remains draft unqualified.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
