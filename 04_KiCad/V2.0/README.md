# V2.0 — Footprint THT meccanici F701+D702 e preflight KiCad9

Aprire `04_KiCad/V2.0/PLL_RX_HIERARCHICAL_MASTER_V2.0.kicad_sch`. Il sesto foglio contiene due footprint **locali reali** assegnati ai dispositivi già presenti F701 0251.500MXL e D702 ST P6KE20CA. `THT_V20.pretty` contiene due footprint THT per montaggio assiale a passo **12,70mm proposto** e relativo `fp-lib-table`.

`node 04_KiCad/V2.0/genera_footprint_v20.js --check` ricostruisce file CAD bit per bit dalla V1.9 senza modificarla. CI KiCad9 esporta SVG dei footprint e tutti i sei schemi, esegue ERC0 e verifica le 64 partizioni native V1.9→V2.0 uguali.

**Non è una scheda PCB**, non c'è DRC del layout, non ci sono Gerber. I due montaggi assiali sono **candidati** finché la piegatura dei terminali e il solder process non vengono verificati. F701/D702 non proteggono automaticamente un veicolo; corrente d'ingresso, inrush, load-dump, coord. I²t, 36V LM393, RF e tutta la radio restano senza qualifica. **NO FAB / NO TX.**
