# V2.7 — carico AF AM455 → potenziometro FRONT → ingresso LM386: trasferimento passivo AC

**15 novembre 2026.** Progettazione analitica dell'interfaccia già rappresentata dai contratti KiCad9 di PR #224/#230. Questo studio non dichiara chiusa la catena elettrica fisica e non cambia il master MAIN (166 riferimenti): quantifica invece l'effetto reale **nel modello passivo lineare** del carico AF combinato, prima di introdurre collegamenti fra i fogli.

## Topologia confermata nelle tre netlist KiCad9 native
- AM455 J1502/1 ← C1502/2 = 100 nF in serie dall'inviluppo; R1502 = 100 kΩ a IF_BENCH_GND, punto caricato dal potenziometro frontale.
- FRONT J1301/1 → RV1301/1 da 10 kΩ nominali; terminale 3 e J1301/2 = AF_GND; wiper 2 → J1302/1.
- MAIN J1202/1 → C1201 = 100 nF serie → R1201 = 10 kΩ serie → U1201 pin 3 (LM386); J1202/2 è GND. L'impedenza di ingresso LM386 = **50 kΩ tipici** da rapporto TI, non minimo garantito; 25 kΩ e 75 kΩ sono **solo ipotesi di sensitività**, non limiti OEM.
- Non è possibile trattare IF_BENCH_GND, AF_GND e GND come già collegate in sicurezza nel PCB: questo studio assume idealmente un riferimento equipotenziale soltanto per la funzione di trasferimento.

## Modello e controlli
Per frequenza f e posizione wiper p (frazione da massa, 0 < p < 1), si definiscono Ralto=(1-p)·10 kΩ, Rbasso=p·10 kΩ, Zamp=10 kΩ + 1/(j2πf·100 nF)+Rin, Zw=Rbasso || Zamp e ZL=100 kΩ || (Ralto+Zw). Il trasferimento dalla tensione ideale **prima di C1502** all'ingresso U1201 pin 3 è:
`H(f,p)= [ZL/(ZL+1/(j2πf·100 nF))] · [Zw/(Ralto+Zw)] · [Rin/Zamp]`.

Un secondo calcolatore **indipendente**, con risoluzione nodale KCL complessa per nodo AF J1502, wiper e U1201/3, verifica ampiezza e fase con massimo errore assoluto 3e-10, e residuo KCL 1e-8. La regressione copre 5 frequenze (100/300/1000/3000/10000 Hz), 5 posizioni wiper (1/10/50/90/99%) e 3 Rin esemplificativi (25/50/75 kΩ): **75 casi**. Verifica monotonia di attenuazione con wiper per ciascuna frequenza/Rin e assenza di guadagni passivi >1. Il test esporta realmente le netlist KiCad9 e controlla la polarità logica/identità delle reti e dei pin. Nessuna esecuzione ngspice né modellazione OEM viene attribuita a questo test.

## Risultati calcolati con la formula passiva, Rin=50 kΩ (NON misurati)
| f | Wiper 10% | 50% | 90% | 99% |
|---:|---:|---:|---:|---:|
| 100 Hz | 0,03935 | 0,18675 | 0,32282 | 0,35237 |
| 300 Hz | 0,07061 | 0,34062 | 0,61356 | 0,67824 |
| 1 kHz | 0,08084 | 0,39339 | 0,72446 | 0,80667 |
| 3 kHz | 0,08196 | 0,39925 | 0,73727 | 0,82170 |
| 10 kHz | 0,08209 | 0,39993 | 0,73877 | 0,82347 |

L'aumento di trasferimento fra 100 Hz e 1 kHz deriva dall'accoppiamento capacitivo e dal carico complesso. Anche al 99% a 1 kHz il modello attenua a ~0,807 anziché arrivare all'unità: è importante non progettare margine IF/AGC assumendo che potenziometro e ingresso LM386 non carichino il segnale. Guadagno **attivo** LM386 (nominalmente 20 V/V) non è incluso, né sono derivate potenza speaker, distorsione o volume percepito. La legge acustica reale con potenziometro lineare e logaritmico rimane da stabilire.

## Gate ancora aperti
1. Diodo 1N4148 reale, dipendenza da ampiezza/corner/PVT, dinamica di inviluppo e interazione RF455 con tank: **questo è un modello passivo linearizzato a valle del diodo**, non una prova di sensibilità o SINAD.
2. Potenziometro fisico con legge/MPN/pinout/rotazione, resistenza di contatto e tolleranza; amp LM386 resistenza ingresso reale con common-mode e bias; requisiti di THD, livelli AF e altoparlante.
3. Impedenza e schermatura dei cavi, ritorni di massa/chassis, protezione EMI/ESD, disaccoppiamento sorgente audio 6 V, funzionalità AM/FΜ/SSB (il rivelatore attuale è **AM-only**).
4. Verificare il test FULL su HEAD finale e documentare il suo run ID **prima del merge**. Questa matematica non autorizza connessioni reali al MAIN o nuove PCB.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
