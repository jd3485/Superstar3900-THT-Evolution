# V1.3 — reale gerarchia KiCad9 RX PLL THT
Prima di KiCad9 CI: PENDING. Un root schematico `PLL_RX_HIERARCHICAL_MASTER_V1.3.kicad_sch` carica due sottoschemi nativi: U401/U402/quarzo (21 simboli), filtro R901/C901 e U803 LM358 (12 simboli). PDout tri-state e GND ora passano tra fogli mediante HLabel nei child + pin nei sheet + due fili reali nel root. Non si usano global label per aggirare connessioni tra child. L'interfaccia master non è ancora quella definitiva.

Le sorgenti V1.0/V1.1/V1.2 sono preservate, il generator JS riproduce i 3 file KiCad9; la CI effettua ERC nativo, SVG 3 pagine, doppio export netlist e **equivalenza integrale delle partizioni di pin** (tutte le 33 reti), oltre a distinguere sheetpath U401 e U803.

Vincoli: alimentazioni esterne J402/J902 e VTUNE esterno J903; VCO, LO buffer, MCU e regolatori assenti. Non esiste PCB. Filtri e VCO non qualificati per lock/stabilità/SSB; niente misura RF, DRC o fabbricazione. **NO FAB / NO TX**.
