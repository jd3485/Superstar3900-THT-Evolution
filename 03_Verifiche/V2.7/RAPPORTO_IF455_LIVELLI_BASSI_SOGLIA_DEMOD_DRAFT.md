# V2.7 — interfaccia IF455, livello di prova e limite del rivelatore AM generico

**13 novembre 2026 — ricerca di dimensionamento, NON specifica definitiva di sensibilità RX.**

## Separare i diversi punti della catena

La tensione del generatore posto prima di `RGEN=50Ω` e del `C1601=10pF` nel modello IF455 non è la tensione d'antenna del CB. Il livello reale su `IF455_TANK_OUT` dipenderà dal guadagno RF e IF, conversione mixer, carico reale, AGC, regolazioni e filtri che nel master V2.6 non sono ancora validati o collegati. Non è quindi corretto definire **una sensibilità radio in µV** a partire da uno sweep con questo generatore ideale.

**Interfaccia da qualificare:** pin elettrici `IF455_TANK_OUT` e ritorno IF, impedenza complessa a 455kHz rispetto al nodo del filtro; una definizione del punto in cui la tensione di prova è misurata, RF carrier peak e AM 1kHz 50% di profondità; guadagno disponibile a monte, margine sul rivelatore, distorsione e SNR audio con rumore del sistema. Servono livelli minimi e massimi *misurati al pin*, non desunti dal generatore SPICE.

## Esperimento verificabile ora: transitorio a 455 kHz a livelli inferiori

File `03_Verifiche/V2.7/verify_if455_lowlevel_envelope_native.py`, che riutilizza senza alterare il precedente deck KiCad-bench `spice/if455_j113_am455_generic_jfet_transient.cir`. Dieci simulazioni native in GitHub Actions a passo massimo 25ns e 12ms:

- generatore ideale AM 455kHz, modulazione 1kHz/50%, **100µV, 1mV, 10mV, 100mV, 500mV** *di picco della sorgente artificiale*, non del filtro/antenna;
- per ciascuno due corner JFET `JGEN` generici, IDSS modellato 2mA, VTO −0,5V e −3V (non macromodello onsemi);
- rivelatore generico `DGENERIC` sulla via LC diretta e su LC→JFET→rivelatore; `VLAB6=6V` ideale, ESR bobina 16,5Ω ipotizzata, origine 50Ω; stesso 455kHz + audio 1kHz;
- misure native dell'AF picco-picco e della tensione RF positiva sull'uscita del filtro, controllo riproducibilità caso 500mV (PR #105) e valori finiti per tutti i casi.

**Regola di interpretazione essenziale:** un valore AFpp non nullo in ngspice senza rumore NON significa che quel livello sia distinguibile in un ricevitore reale. Non ci sono **noise figure, SINAD, SNR, distorsione armonica, AGC né attenuazione FM/SSB**. I valori normalizzati `Vout/Vin` cambiano col funzionamento non lineare del diodo; non si può inferire una soglia precisa del semiconduttore dal solo picco-picco.

## Gate tecnico successivo dopo le misure

1. Ottenere i dati del mixer/IF e del carico del tank nel master per stabilire **Z complessa** vista dal rivelatore e sorgente reale, includendo Q e banda 455kHz.
2. Stabilire un target di livello RF alla demodulazione e una metrica minima SNR/SINAD con simulazioni noise e misure fisiche; allineare AM, FM, SSB e AGC anziché presumere lo stesso diodo per tutte le modalità.
3. Caratterizzare il reale onsemi J113 con dati OEM e l'esatto diodo THT OEM attivo, incluso leakage/capacitance e risposta PVT, e poi con un banco fisico prima di fissare il CAD.

**Questa PR non modifica il master né propone valore ottimizzato dei componenti. PCB-MAIN e PCB-FRONT non progettate, DRC non applicabile. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Risultati verificati su GitHub Actions, 13/11/2026

La [PR #108](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/108) è **MERGED** commit `a7e67b5c001cbb809b3876d0907aaddf07e6a691`. La run [#43484801445](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43484801445) sul final head `c98af789d7e528eaea280754d6b437ef87acd25d` ha **FAST/FULL/required 3/3 SUCCESS**, 111 comandi legacy e `PASS_NGSPICE_IF455_10_LOWLEVEL_GENERIC_DIODE_J113_CASES_NO_SENSITIVITY_CLAIM_NO_FAB_NO_TX`. Tutti i valori seguenti derivano da ngspice nativo, senza rumore.

| Sorgente simulata AM 455kHz, picco | AFpp diretto, modello generico | AFpp con J113, VTO−0,5V/IDSS2mA | AFpp con J113, VTO−3V/IDSS2mA |
|---:|---:|---:|---:|
| 100µV | 0,804167µV | 0,665367µV | 0,463908µV |
| 1mV | 8,041947µV | 6,653845µV | 4,639164µV |
| 10mV | 80,44396µV | 66,5626µV | 46,39673µV |
| 100mV | 0,8103563mV | 0,6688448mV | 0,4654612mV |
| 500mV | 23,925459mV | 25,212924mV | 5,823876mV |

Nel modello **sotto 100mV** l'uscita AFpp cresce quasi proporzionalmente al generatore e resta **~0,8% del picco di portante generato** nel percorso diretto. Fra 100mV e 500mV compare un cambio marcato della risposta del modello, mentre lo stadio J113 può anche peggiorare il risultato. Non ricavare una precisa tensione di soglia del diodo da questi dati: le reti LC e le capacità parassite contribuiscono e il risultato non include rumore, distorsione o prestazioni garantite OEM. La prova rimane un segnale di rischio che il rivelatore AM generico non è una base sufficiente per stimare la sensibilità RX.

**Decisione tecnica:** nessuna variante dei follower BJT/JFET è qualificata. Per proseguire serve un modello verificato di **guadagno e impedenza complessa IF** dal mixer fino al punto rivelatore, oltre a una specifica AM audio SNR/SINAD e alle distinte modalità FM/SSB. Il prossimo test efficace non è soltanto ampliare il range del generatore ideale: deve calcolare il budget di rumore e di conversione con parametri fisici del percorso. Master KiCad MAIN V2.6 e due PCB invariati. NO FAB/TX.
