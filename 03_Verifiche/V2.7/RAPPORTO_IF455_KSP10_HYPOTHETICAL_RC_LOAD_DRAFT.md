# V2.7 — carico complesso RC ipotetico su KSP10/IF455 (NON OEM)

**14 novembre 2026 — studio in bozza, nessun componente qualificato.**

## Problema e perimetro

La PR #164 ha usato solo terminazioni resistive 1,5/2kΩ. Un ingresso a filtro ceramico ha impedenza complessa e funzione di trasferimento dipendenti dalla frequenza, da misurare con il componente reale. Prima di scegliere il filtro o un buffer, questa verifica quantifica soltanto la **sensibilità del banco KSP10** a una componente capacitiva fittizia in parallelo al carico resistivo.

Il verificatore `03_Verifiche/V2.7/verify_if455_ksp10_hypothetical_complex_rc_load_native.py` esporta le reali netlist standalone KiCad9 KSP10 e tank IF455, controllando i nodi pin↔net. Usa il banco ngspice **generico** già esistente, sorgente 50Ω ipotetica, tank IF455 1mH+R16,5Ω e KSP10 a 6V, CIN 10nF senza variazioni del CAD. Varia il solo **surrogato di carico in uscita**: R=1,5/2kΩ × Cpar=0/100/330/1000pF × beta BJT generica 40/80/160 × 445/455/465kHz = **72 analisi AC native**. Esporta tensioni complesse tank, porto e buffer e fase relativa; calcola separatamente Z(R||C)=1/(1/R+jωC) e confronta le tensioni con il riferimento esclusivamente resistivo.

**I valori Cpar sono casi di stress inventati, non caratteristiche dichiarate né misurate di NextGen FB455 o Murata LTM455.** L'RC non modella risonatori ceramici, perdita di inserzione, reiezione, ripple, terminazioni reali, carico retroazionato, larghezza di banda o linearità. Non qualificare selettività AM/FM/USB/LSB/CW, rumore, mixer SBL-1+ LO-driven, BJT OEM, Q/SRF tank o PCB con questi risultati. Non approvare né un MPN né un valore C in KiCad. Le PR #123/#143 restano draft; issue #141 rimane aperta.

## Quality gate

Il nuovo script è invocato nella FULL CI esistente `ci/full_regressions.py`, senza workflow supplementari. Richiede 72 solver ngspice completi, netlist KiCad9 e controllo di carico complesso, senza waiver. Solo la CI sul commit finale può certificare il passaggio del test; nessun esito è dichiarato prima del suo completamento. MAIN V2.6 e BOM invariati, PCB MAIN/FRONT non esistenti. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
