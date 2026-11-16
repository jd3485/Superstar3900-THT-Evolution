# V2.7 FRONT mute — interferenza capacitivamente iniettata e guasto contatto NC

**Data:** 16 novembre 2026. Stato: controllo analitico candidato per PR, NON qualifica di relè/cavo/PCB.

## Modello ancorato a KiCad9

La netlist del master FRONT conferma COM di K1901 su R1902/1, resistore di serie R1902 (1 kΩ) verso nodo J1902/1 (`AMP_INPUT_MUTED`), e R1901 (100 kΩ) fra J1902/1 e `AF_GND`. Il pin NC K1901/2 è sul ritorno `AF_GND`; la MAIN audio di laboratorio inizia su J1202/1 → C1201 100 nF → R1201 10 kΩ → ingresso LM386, con Rin ipotetica 50 kΩ.

Per il solo caso **relè diseccitato NC chiuso e ritorno integro**, il nodo post-mute è drenato verso AF_GND da due rami in parallelo: R1901=100 kΩ e R1902=1 kΩ + resistenza del contatto NC. Con Rcontatto **ipotetica** 1 Ω: Rshunt = 100 kΩ || 1001 Ω = **991,079 Ω**. Se NC è interrotto mentre il ritorno di R1901 rimane valido, Rshunt=100 kΩ: l'impedenza di shunt cresce di circa **100,900 volte** (calcolo DC, non rapporto di tensione misurato).

## Sweep AC riproducibile

`verify_front_mute_nc_coupled_audio_fault_native.py` inietta una sorgente perturbatrice ideale da 1 V attraverso una capacità cavo *ipotetica* (10 pF, 100 pF, 1 nF, 10 nF). Per 5 frequenze (100, 300, 1000, 3000, 10000 Hz) e 3 resistenze NC (0,1 / 1 / 100 Ω), verifica **60 combinazioni con due stati NC** (=120 comparazioni) tramite **due solutori indipendenti**: riduzione impedenze e KCL complessa a due nodi. Fallisce se il circuito con NC aperto non provoca un maggiore trasferimento verso il pin 3 LM386 nelle condizioni modellate. Controlla che i valori e collegamenti siano realmente quelli delle netlist KiCad9 di FRONT master, relay e MAIN audio.

Il caso **AF_GND condivisa aperta** è espressamente **non calcolabile in questo modello a riferimento fisso**: entrambi i solutori devono rifiutarlo invece di creare una falsa massa. Non si assume corrente o tensione massima del cavo reale, né una capacità di accoppiamento certificata. Il comportamento con contatto saldato NO, transitori, rumore EMI/RF, PVT, massa flottante, guasti simultanei, caratteristiche minime del contatto meccanico e protezioni resta da qualificare.

Il risultato non prova mute fail-safe. Il cablaggio post-mute della PR #290 e il modello di ricezione AC della PR #291 restano prerequisiti concettuali; **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.
