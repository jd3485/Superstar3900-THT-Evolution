# V2.7 — SBL-1+ A06 provisional footprint (NOT approved)
Date: 2026-11-13. Issue #122. Derived from Mini-Circuits **SBL-1+** datasheet and case-style **98-A Rev B, 03/15/12**. Official sources: https://www.minicircuits.com/pdfs/SBL-1%2B.pdf and https://www.minicircuits.com/WebStore/dashboardPdf?model=SBL-1%2B

## Native CAD artifact
`SBL1_A06_CANDIDATE.pretty/SBL1_A06_UNQUALIFIED.kicad_mod` is a **provisional KiCad9 through-hole pad layout**, not a qualified manufacturing footprint. The component in the existing standalone mixer schematic **retains an EMPTY footprint field**; the main V2.6 and both PCBs remain untouched. No PCB, no DRC, no Gerbers.

## Original drawing and geometric assumption
OEM drawing: case A06; A=.770 in (19.56 mm) to B=.800 in (20.32 mm), E=.370 in (9.40 mm) to F=.400 in (10.16 mm), G=.200 in (5.08 mm), pin K=.031 in (.79 mm), diameter tolerance ±.005 in (.127 mm). Other case dimensions C=.285–.310 in (7.24–7.87 mm), H=.20 in (5.08 mm) and J=.14 in (3.56 mm). The extracted drawing labels the **BOTTOM VIEW** with upper row from left to right 1/3/5/7, lower row 2/4/6/8. **Provisional** top-side coordinates mirror bottom-view x, retaining y. As viewed from top: top row 7/5/3/1, bottom row 8/6/4/2. Pads 5.08 mm x pitch, two rows 5.08 mm; the 2.00 mm annular copper pad and 1.10 mm drill are engineering candidates, not OEM PCB recommendations. Pin 1 square pad, schematic RF1 LO8 IF3+IF4 GND2/5/6/7.

**BLOCKER**: the manufacturer original PDF graphic has not been visually examined with independent top/bottom mirroring verification in this session. The online extracted figure provides textual layout, but not a signed-off drawing orientation or measured PCB coordinate table. The overall fabrication drawing's top/bottom orientation and physical pin1 blue bead MUST be independently cross-checked. The outline body maximum +0.5mm courtyard is preliminary, and no mechanical tolerance/meniscus/assembly inspection has been qualified. Drill/pad stack-up, plating, solder process, clearances and mechanical clearance shall be reviewed before any board is manufactured.

## Verification and explicit exclusions
`03_Verifiche/V2.7/verify_sbl1_a06_provisional_footprint.py` checks all 8 actual pad-number/coordinate pairs, drill/diameter/layers, pin1 rect and keep-out warnings. This is an **internal design consistency check**, not an independent OEM drawing certification. The FULL CI also executes the prior KiCad9 native schematic/ERC/netlist verification when green. No claims of actual RF LO+7dBm performance, conversion loss on IF455 filter, PCB DRC, OEM package approval, BOM qualification, or hardware verification.

## Next mandatory action
1. Capture the original case drawing image and independently check BOTTOM VIEW ↔ PCB TOP orientation and true center-to-center dimensions (not labels only).
2. Review pin1 index physically against the OEM blue bead, pin diameter and maximal glass meniscus, solder fillet, hole clearance.
3. If the review confirms geometry, rename candidate to approved **only via** technical PR, assign MX1701 footprint, run native KiCad9 ERC/exported netlist + footprint syntax/native pad report, and then review a real PCB separately.
4. If orientation or dimensions differ, **correct the candidate** and rerun CI before any assignment.
NO FAB / NO TX / NO BATTERIA / NO VEICOLO.
