# Registro nativo CAD — pilot V1.0

- 2026-11-10 run GitHub [42857108005](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42857108005): KiCad CLI 9.0.9, **ERC 0 violazioni** circuito isolato, libreria THT esportata, netlist/SVG esportati, determinismo generatore PASS.
- 2026-11-10 run regressioni [42858156232](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42858156232): 254 storici +18 nuovi = **272 test Python PASS**.
- Nuovo controllo Python `verify_kicad_netlist_v10.py` deve essere eseguito dopo l'esportazione della netlist; il proprio esito verrà riportato nel report CI finale. NON implica loop PLL chiuso.
- KiCad master completo, PCB e DRC: **NOT_RUN**. Simulazioni hardware reali e fabbricazione PCBWay **NOT_RUN; NO FAB / NO TX**.

## Validazione native netlist pin-per-pin — esito finale del pilot (branch)

[Run 42858721761](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42858721761) **SUCCESS**, KiCad CLI 9.0.9:

- `sch erc --exit-code-violations`: **0 violazioni**, nessuna waiver sul circuito isolato.
- `sch export netlist`: **PASS**; identificati **8 net reali** (alcuni con `/NET` perché KiCad prefissa i nomi gerarchici).
- `verify_kicad_netlist_v10.py`: **PASS_NETLIST_PARTIAL_ONLY**, controllati direttamente i riferimenti **J901/R901/C901/U803/R803/R804/R805/J902/J903/C803** e i pin per `PLL_PDOUT_3STATE`, `PD_FILTER`, `OPA_OUT_A`, `OPA_FB_A`, `OPA_OUT_B`, `VANA20_FILT`, `GND`, `VTUNE_RAIL`.
- Esportazione simboli KiCad e SVG schematico **PASS**. Generazione deterministica **PASS**.
- `NO FAB / NO TX`: 8 reti e zero errori ERC non equivalgono a circuito PLL chiuso, né a PCB / DRC, né a qualifica RF; le alimentazioni sono **esterne** e U401/U402/VCO non sono inseriti nello schematico.

La run Python [42858721619](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42858721619) è **SUCCESS 272 controlli** (254 V0.1–V0.9 +18 CAD-first).
