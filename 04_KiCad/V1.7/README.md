# V1.7 KiCad9 INPUT FUSE + SCHOTTKY + BIDIR TVS / six pages

Aprire `PLL_RX_HIERARCHICAL_MASTER_V1.7.kicad_sch` con KiCad9, sesto child `INPUT_FUSE_REVERSE_TVS_V1.7.kicad_sch`. J701 raw 13.8V -> F701 Littelfuse axial 500mA -> D701 1N5819 K1/A2 -> U601 protected input. D702 ST P6KE20CA bidir fra FUSED_RAW e GND; parent sheet pins fisici per +13V8_PROTECTED e GND. Eliminato lab bypass J601 dal POWER5 solo in V1.7. Sorgenti V1.6 intatte.

I due footprint F701 e D702 sono da selezionare. Il TVS NON protegge da sovratensione continua. Nessun fuse coordination/surge RF/hardware; NON collegare a veicolo o batteria. No PCB, NO FAB / NO TX.

**Verifiche native:** run [42921509495](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/42921509495) PASS ERC0/54 reti/6 pagine. Il comando `node 04_KiCad/V1.7/genera_gerarchia_input_v17.js --check` confronta bit-per-bit tutti i 5 schemi derivati dalla V1.6; `--write` li rigenera senza modificare le sorgenti V1.6. Il nuovo foglio e la libreria custom V1.7 sono le due sorgenti native originali.
