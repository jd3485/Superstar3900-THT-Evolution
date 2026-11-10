# Registro nativo CAD — pilot V1.0

- 2026-11-10 run GitHub [42857108005](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42857108005): KiCad CLI 9.0.9, **ERC 0 violazioni** circuito isolato, libreria THT esportata, netlist/SVG esportati, determinismo generatore PASS.
- 2026-11-10 run regressioni [42858156232](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42858156232): 254 storici +18 nuovi = **272 test Python PASS**.
- Nuovo controllo Python `verify_kicad_netlist_v10.py` deve essere eseguito dopo l'esportazione della netlist; il proprio esito verrà riportato nel report CI finale. NON implica loop PLL chiuso.
- KiCad master completo, PCB e DRC: **NOT_RUN**. Simulazioni hardware reali e fabbricazione PCBWay **NOT_RUN; NO FAB / NO TX**.
