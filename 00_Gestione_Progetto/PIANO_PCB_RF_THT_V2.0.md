# V2.0 — piano operativo di ingegneria PCB THT RF/PLL, NON un layout approvato

## Decisione progettuale
Non si apre un progetto `.kicad_pcb` produttivo fino a quando mancano blocchi fondamentali del ricevitore: RF input/preselector, 1st mixer, IF1, IF2, demodulatori AM/FM/SSB, audio, controller e I/O front panel. La V2.0 collega la sorgente VTUNE20 per facilitare la chiusura del PLL RX, ma **non** rappresenta una radio completa. Il progetto SMD deve restare separato.

## Vincoli che bloccheranno ogni autorizzazione della PCB
1. **Schemi:** gerarchia completa THT con pin-net verificati, ERC0 senza waiver arbitrari, interfacce RX/RF/IF/LO/VTUNE/5V/13V8 fissate, powergood/mute definiti e tutti i componenti safety critical con MPN.
2. **Footprint:** BOM→symbol→footprint univoca, package/pinout documentati, L920 radial terminal pitch, L501 RF inductor, F701 fusibile, D702 TVS e dispositivi meccanici selezionati; verificare 3D e misure con calibro; TO-220 di U912 output TAB isolato dal telaio/massa.
3. **Partizionamento RF:** loop ad alta di/dt MC34063 (R920/L920/U911/D920/C923) compatto e distante da VCO L501, varactor BB204G, reference PLL, IF e cavi antenna; FB divider R922/R923 lontano dallo switch SW20_NODE; ritorni condensatori input/output a bassa impedenza; piano GND continuo dove appropriato, evitare tagli che facciano circolare ritorni RF; giudicare isolamento con misure EMC e spur.
4. **Integrità e rumore:** stima impedenza stackup fab, ritorni e piani, filtraggio `VANA20_FILT` vicino a U803, decoupling U401/U402/U520 VCC analog/digital, test phase noise, jitter, ripple RF, lock/hold lock nei 270 canali e temperature richieste.
5. **Verifica fisica:** DRC0 sul vero PCB e review di clearance, trivellazioni THT, annular rings, soldermask, silk/assembly, bow/twist, thermal relief; verifica proprietà BOM e netlist; clearance piste di commutazione; nessun Gerber ordinabile prima di review indipendente.
6. **Qualifica ingressi e alimentazione:** fonte 13.8V e corrente di corto reali; fusibile interrupt/I²t e TVS surge coordinati, inversione, sovratensione continuativa, load dump, EMI, dissipazione U601/U912/Q801; nessuna connessione veicolo/batteria in fase CAD.
7. **Punti misura:** richiedere testpoint THT sui nodi +13V8_RAW, FUSED_RAW, +13V8_PROTECTED, +5V_REG e rami, BOOST_SENSE, SW20_NODE solo con sonda appropriata, VBOOST28, VREG20_RAW, VANA20_FILT, VTUNE_RAIL, PDOUT, LO1, GND locale; misure con massa corretta senza loop lungo.
8. **Processo:** schematic freeze→parts freeze→footprints→floorplan/PCB stackup→placement→routing→ERC/DRC/netlist CI→gerber drill checks→independent layout review→test coupon/fixture→prototype test; NO bypass.
9. **Produzione:** non generare file Gerber production-ready finché manca verifica elettrica vendor/lab e firma di approvazione. NO FAB / NO TX.

## Blocchi da completare per prossimo avanzamento
Protezione ingresso, powergood fail-closed, modello full loop PLL/VCO, RF preselector/mixer/IF/demod/audio/controller, front panel e cavi, selezione magnetici/filtro RF; solo allora layout completo e producibile. La conformità ERC e aritmetica V2.0 non è una garanzia di assenza difetti.
