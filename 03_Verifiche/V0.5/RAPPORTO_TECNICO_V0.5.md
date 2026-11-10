# Rapporto tecnico V0.5 — VCO Colpitts THT e controllo RX fail-closed

**10 novembre 2026.** Progetto THT autonomo. Questa revisione progetta un **primo circuito candidate completo di nodi** per la sezione oscillatore a transistor + emitter-follower, non una radio assemblata o una PCB valida.

## Avanzamenti ingegneristici
1. **VCO a transistor candidato:** Q501/Q502 2N3904-AP TO-92, rete di feedback Colpitts C502=68pF C503=220pF, bobina L501=150nH, componenti di polarizzazione DC, disaccoppiamenti, circuito di accoppiamento isolato C506 e output LO1_ANALOG_OUT. **Primo circuito SPICE con netlist completa** e modelli illustrativi in `03_Verifiche/V0.5/VCO_COLPITTS_CANDIDATE_V0.5.cir`. Le caratteristiche dei modelli BJT/varactor non sono quelle certificate dai produttori; nessun test hardware.
2. **Doppio varicap:** D501 BB204G TO-92 con entrambe le giunzioni in parallelo, anodi pin1+pin3 al nodo VAR_A, catodo comune pin2 a VTUNE_RAIL. C504 da TANK a VAR_A blocca la DC e R505 assicura potenziale definito agli anodi. Conferma pinout da documentazione storica Philips; **BB204G non approvato all'acquisto, NOS/stock non garantito**.
3. **Dimensionamento ideale ricalcolato:** L=150nH, C_fixed_eff **61pF** (incertezze incluse) e C_DCblock=1000pF. Fit di capacità basato su C3=36,5pF midpoint e C30=14pF tipica, Vj assunto 0,8V; modello 270 RX richiede circa **3,13–6,95V**. Questo non include certezza di oscillazione né capacità reali/tolleranze a 37MHz.
4. **Robustezza non garantita:** combinazioni indicative L±5% e C_fixed_eff±5pF possono NON coprire tutti i canali tra Vtune 3..8V. Il VCO richiederà taratura LC trimmer, margine e qualificazione dei valori reali.
5. **Filtro PLL V0.4 non accettabile come progetto definitivo:** nel modello ideale la rete 2,2k/10k/100n attenua il ripple 5kHz solo circa **1,73dB**. È sviluppato un confronto a due poli 10k+10n, 10k+100n con attenuazione teorica ≈**41,43dB**, MA senza Kphase, Kvco e margine di fase. Nessuna di queste due reti ha la stabilità del PLL provata.
6. **Interfaccia controllo:** il segnale PDout del PLL U401 a 5V non alimenta direttamente una richiesta Vtune di quasi 7V. Uno stadio attivo THT candidata U602 **LM358N PDIP8 a 12V e guadagno ideale ×2** è proposto, ma **NON inserito nella netlist VCO e NON validato**. Il controllo deve evitare varicap forward bias, sovratensioni e perdita lock.
7. **Gestione RX:** modello Python che applica N e CH9, impone RX mute al cambio, verifica lock/ref/power validi per tick consecutivi e reset. Non è firmware PIC reale e non abilita mai TX.
8. **THT e forniture:** Q501/Q502 pin1 E, pin2 B, pin3 C (MCC 2N3904-AP; confrontare footprint al momento della progettazione). D501 1 A1, 2 K, 3 A2. BOM V0.5 con elementi candidati e vincoli.

## Test e simulazioni: differenze fondamentali

| Categoria | Stato V0.5 | Limitazione |
|---|---|---|
| Suite software V0.1...V0.5 | 12+24+32+34+34=**136 test predisposti** | Eseguire GitHub Actions e registrare esito; non test RF |
| Analisi matematica LC, filtro, curva C(V) | **ESEGUITA nel modello Python** | Parametri assunti, nessuna qualifica |
| Netlist SPICE VCO | **CREATA** | Esecuzione ngspice non disponibile localmente; NON ESEGUITA nel pacchetto iniziale |
| KiCad GUI/CLI ERC/DRC | **NON ESEGUITI** | Non installato; nessun sottoschema VCO nativo |
| Oscillazione hardware, VCO gain/phase noise, EMI | **NON ESEGUITI** | Zero prototipi |
| Produzione PCBWay e TX | **BLOCCATE** | NO FAB / NO TX |

**Importante:** un deck SPICE non prova funzionamento finché non viene realmente eseguito e analizzato. Non dare come conseguito il lock PLL, né la stabilità. Si dovrà misurare/simulare anche il reale swing e verificare ogni fase di start e i transitori.

## Decisioni tecniche non chiuse
- BB204G è legacy, alternativa varicap THT reperibile deve essere trovata prima della PCB.
- LM358N come buffer Vtune è ancora **candidato**; i valori del filtro non sono una compensazione PLL finale.
- Trasferimento da SPICE candidate a KiCad richiede simboli, footprint verificati, ERC nativo, unione con U401/U402 e poi layout RF, ancora non realizzati.

## Prossima revisione V0.6
Eseguire la netlist con ngspice, misurare frequenza/swing e startup, correggere il circuito, fissare margini e tolleranze; progettare driver PLL/VCO con modello dinamico, reperibilità e pinout completi. Importare la topologia del VCO nel CAD KiCad e verificare ERC nativo quando disponibile. Solo dopo progressi misurabili, passare a mixer RX e FI.

**Verdetto V0.5:** topologia VCO THT cablata in SPICE e modello controllo RX documentati; **nessuna dichiarazione di funzionamento o fabbricabilità**. NO FAB / NO TX.
