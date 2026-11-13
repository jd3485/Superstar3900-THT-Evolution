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
