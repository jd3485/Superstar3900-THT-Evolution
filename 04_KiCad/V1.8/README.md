# V1.8 — Circuito OVP continuo CANDIDATO 100% THT nel master KiCad9

Aprire `PLL_RX_HIERARCHICAL_MASTER_V1.8.kicad_sch`, sesto foglio `INPUT_FUSE_REVERSE_TVS_OVP_V1.8.kicad_sch`. Tra F701 e D701 è ora collegato Q801 IRF9540NPBF (S3 upstream, D2 downstream, G1). R1001..1010, U801 LM393N PDIP8, U802 TL431BCLP TO-92, Q802 2N3904 TO-92 e D803 zener 12V realizzano la logica con isteresi candidata. V1.7 preservata.

`node 04_KiCad/V1.8/genera_ovp_v18.js --check` confronta bit-per-bit gli otto file CAD ricostruiti dalle sorgenti storiche; `--write` li rigenera. **Non collegare a batteria/veicolo**: LM393 alimentata dal bus d'ingresso è esposta a >36V, nessun test di surge, TVS/fuse o termica, nessuna qualifica EMI, VCO, PLL, test PCB. **NO FAB / NO TX**.
