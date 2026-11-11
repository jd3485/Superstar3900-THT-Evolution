# KiCad9 V2.1 — 7 fogli con 20V VTUNE reale + footprint THT F701/D702

Questa revisione eredita **l'intero V2.0 a sette fogli** e modifica **solo i due campi footprint** del foglio ingresso:
- F701: Littelfuse PICO II `0251.500MXL`, `THT_V21:Fuse_Littelfuse_PICOII_0251_500MXL_P12.70mm`.
- D702: ST P6KE20CA `THT_V21:TVS_ST_P6KE20CA_DO15_P12.70mm`.

Il `POWER20_VTUNE_BOOST_LDO_V2.1.kicad_sch` mantiene MC34063ABN / LM317T, VANA20_FILT, U803 pin8, L920 candidato con footprint ancora da scegliere e tutti gli altri net originali. Master `PLL_RX_HIERARCHICAL_MASTER_V2.1.kicad_sch`.

Repro: `node 04_KiCad/V2.1/genera_footprint_v21.js --check`; CI completa KiCad9 verifica **72 gruppi netlist** invariati, 7 pagine SVG, 2 SVG footprint, ERC0 e audit BOM/footprint (segnalerà L501 e L920). Sorgente V2.0 e repo SMD intatti. **NO FAB / NO TX**.
