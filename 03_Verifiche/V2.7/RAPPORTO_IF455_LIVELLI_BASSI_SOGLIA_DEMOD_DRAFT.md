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
