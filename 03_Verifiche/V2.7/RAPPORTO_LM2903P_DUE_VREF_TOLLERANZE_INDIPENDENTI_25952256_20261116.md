# V2.7 — criticità tolleranze A/B indipendenti nel doppio fault VREF

16 novembre 2026. Verifica analitica vincolata a **netlist KiCad9 reale** del banco THT isolato, non qualifica safety.

La precedente regressione 101.376 corner usa lo **stesso vettore di otto tolleranze** per entrambi i canali LM2903P: questa correlazione artificiale non copre l'indipendenza fisica dei 16 resistori di sensing e soglie (otto A, otto B). Nuova regressione native `verify_dual_lm2903p_split_vref_independent_tolerances_native.py` mantiene 60 pin/14 reti e le due VREF esterne separate, ma applica tutte le 256 combinazioni ±1% a ciascun canale in modo indipendente.

**25.952.256 corner matematici** = 256² tolleranze × 11 VIN sintetiche × 6 VREF_A × 6 VREF_B. Calcolo esatto mediante prodotto delle cardinalità di consensi dei due canali, equivalente a enumerazione completa cartesiana; non si dichiarano 26 milioni di simulazioni SPICE. A VIN13,8V e REF A/B nominali: **65.536** consensi ideali. Fuori VIN9..16V: **231.760** falsi consensi ideali, dei quali **131.072** con entrambe VREF1,25V e **100.688** con entrambe VREF5V. Il risultato differisce da 1.028 casi della precedente correlazione tolleranze: non confrontare conteggi come probabilità o rischio fisico, essendo denominatori diversi.

Resta un banco isolato senza VREF OEM indipendenti, senza supply5V qualificata, OC e GND comuni, senza limitazione guasti ingressi o doppio interruttore serie fail-OFF. Nemmeno l'ERC o il modello deterministico provano protezione reale. #27 APERTA, MAIN V2.6/FRONT non modificati, niente PCB. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
