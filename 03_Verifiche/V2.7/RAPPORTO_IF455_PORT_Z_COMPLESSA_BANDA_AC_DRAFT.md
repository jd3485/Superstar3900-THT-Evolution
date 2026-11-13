# V2.7 — IF455: impedenza complessa d'uscita e banda a −3 dB (ngspice nativo)

**13 novembre 2026. Revisione di caratterizzazione della sola rete IF455 passiva, non progetto definitivo del ricevitore.**

## Domanda ingegneristica

I test precedenti #101–#108 hanno confrontato tensioni d'inviluppo su circuiti diodos/active generic senza specificare **quanto il filtro IF455 è effettivamente caricato** né il comportamento in frequenza del nodo di connessione. Senza impedenza complessa e larghezza di banda non è possibile selezionare in maniera affidabile un buffer BJT/JFET o parlare di selettività RX, SNR/SINAD e sensibilità.

Lo script `03_Verifiche/V2.7/verify_if455_passive_port_impedance_selectivity_native.py` esegue **otto analisi AC indipendenti native ngspice**: 4 modelli di carico × (transfer + impedenza d'uscita vista dal carico) su **300–650kHz in 1401 punti**, comprendendo 455kHz esatto. Acquisisce i fasori **Re/Im**, non usa la sola ampiezza del diagramma. Con la sorgente disattivata in AC, inietta **1 A di prova** tra massa e nodo `out`; pertanto `V(out)/1A` è l'impedenza complessa di Thevenin vista dal port, incluso il carico di caso: l'esperimento è una misura di porta del circuito **caricato**, non la sola impedenza intrinseca senza i carichi. La sorgente di prova non esiste nell'hardware e non autorizza alcun collegamento fisico.

## Modello e 4 scenari

Riprende i valori del circuito KiCad9 standalone `IF455_TANK_THT_V2_7_DRAFT.kicad_sch`, con verifica incrociata delle costanti del deck AC storico `if455_downstream_input_load_ac.cir`: L1601=1mH, **16,5Ω ESR RF solo ipotizzata dai dati DCR**, C1602=82pF, C1603 trimmer fermo a 30pF, C1601=10pF ingresso, C1604=10pF uscita, R1601 damping 47kΩ, R1602 uscita 100kΩ, generatore 50Ω idealizzato.

1. Uscita 100kΩ di riferimento, senza altro carico.
2. Shunt **10kΩ** illustrativo a valle.
3. Shunt **1kΩ** illustrativo a valle.
4. Surrogato passivo d'ingresso JFET: **C1801 10pF** a nodo gate con ritorno **1MΩ** e parassita illustrativo **7pF** verso massa. **Non è il J113 fisico**, non include gm, corrente di gate, PVT o accoppiamento interno.

Per ogni carico il test misura l'ampiezza relativa Vout/Vgeneratore a 455k, `f_peak`, limiti a −3 dB, banda, **Q caricato indicativo=f_peak/BW** e impedenza complessa effettiva Re(Z)/Im(Z) a 455k. Richiede che la banda sia realmente racchiusa nell'intervallo e che i carichi resistivi 1k e 10k producano gli effetti attesi, senza imporre arbitrariamente una frequenza centrale né un Q di successo.

## Limiti obbligatori per l'interpretazione

- Il picco AC della rete LC con trimmer fisso a 30pF **non** può essere spacciato per centraggio automatico a 455k: l'errore e il tuning range OEM vanno trattati separatamente.
- Il filtro qui è **un solo risonatore caricato**: la banda calcolata non è la banda AM completa di un ricevitore CB e il Q non sostituisce una maschera di selettività per interferenti, immagine, IF multistadio, FM/SSB.
- DCR 16,5Ω non equivale necessariamente a ESR AC a 455kHz, e non copre auto-risonanza, saturazione, perdite core e interavvolgimento; modello OEM Delevan/EW trimmer ancora da validare.
- Aggiungere un buffer o un rivelatore reale può modificare il nodo. Nessuna prova della **noise figure**, noise floor, IMD, AM THD, SINAD, AGC o sensibilità d'antenna, nessun test hardware e nessun PCB reale. Non si promuove un MPN sulla sola base di questo script.
- Il master gerarchico MAIN V2.6 di 7 fogli/138 refs resta intatto; questa è una verifica nuova e sostanziale del port del prototipo THT passivo standalone. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Risultati misurati con ngspice nativo: Actions #43494725977

La [run #43494725977](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43494725977), commit `204d6e2d69670683853182ff81af23947bc2a56a`, ha eseguito realmente le **otto analisi AC** previste. FULL con 111 comandi legacy `PASS_FULL_HISTORICAL_22_WORKFLOWS_AND_ALL_NATIVE_KICAD9_GATES` e marker `PASS_NGSPICE_IF455_PASSIVE_4_LOADS_AC_COMPLEX_Z_BANDWIDTH_NOT_RECEIVER_NO_FAB_NO_TX`. Valori riportati con arrotondamento dei log:

| Carico modellato | f picco (kHz) | Trasferimento massimo V/V | f−3dB inf–sup (kHz) | BW−3dB (kHz) | fpeak/BW (indice, NON Q OEM) | |H(455k)| | Z porta a 455kHz (Ω) |
|---|---:|---:|---:|---:|---:|---:|---|
| R100k riferimento | 454,750 | 0,835107 | 435,081–477,638 | 42,557 | 10,686 | 0,835056 | 33540,957 − j15429,214 |
| +R10k shunt | 440,250 | 0,224274 | 423,542–460,959 | 37,418 | 11,766 | 0,180772 | 7959,536 − j723,061 |
| +R1k shunt | 439,000 | 0,031007 | 425,474–455,239 | 29,765 | 14,749 | 0,022074 | 975,865 − j10,781 |
| Ingresso JFET **surrogato passivo** (C10p + R1M/C7p gate) | 450,250 | 0,686172 | 433,342–469,638 | 36,296 | 12,405 | 0,665187 | 21582,105 − j19978,026 |

**Interpretazione fisica:**
- Il filtro non deve essere approssimato con un `50Ω`, `1kΩ` o `100kΩ` puramente resistivo all'uscita: nel modello, il riferimento ha `Zout(455k)=33,54k−j15,43kΩ`, con modulo ≈36,92kΩ.
- Lo shunt 10k riduce `|H(455k)|` da 0,8351 a 0,1808 (**21,65%** del riferimento), mentre 1k lo riduce a 0,02207 (**2,64%** del riferimento) e sposta il picco da 454,75 a 439,0kHz.
- Anche il surrogato JFET considerato ad alta impedenza produce un **carico reattivo significativo**: picco 450,25kHz (−4,50kHz dal riferimento) e `|H(455k)|=0,6652` (**79,66%** del riferimento). Questo NON rappresenta tutte le impedenze d'ingresso del dispositivo reale.
- ATTENZIONE: i valori `fpeak/BW` degli shunt possono **crescere** pur riducendosi drasticamente il trasferimento. Non chiamarli 'Q fisico della bobina' né interpretare l'aumento come filtro migliore: sono indici della *funzione di trasferimento fra due nodi con accoppiamento capacitivo*, modificata da smorzamento, spostamenti di picco e carico.
- `Z porta` è misurata **con il carico incluso** e con la sorgente 50Ω cortocircuitata in AC, non è l'impedenza intrinseca del tank scollegato da tutto. Il trimmer resta fissato a 30pF e la frequenza di picco è una proprietà di questa specifica rete modellata; non è una prova di tolleranze, accordatura finale, AM selectivity o SNR.

**Decisione di progetto:** non inserire KSP10/J113 nel master sulla base di un rapporto AFpp generic. Servono una definizione del punto IF455 fra mixer/stadio IF/filtro/rivelatore, impedenza reale (o banda su carico), spettro di rumore e tensione IF utile ai pin, modalità AM/FM/SSB e target verificabili prima di stabilire valori di adattamento. Questa analisi identifica ora numericamente il *budget di carico passivo* al port, ma non chiude nessuna qualifica OEM né la progettazione PCB.
