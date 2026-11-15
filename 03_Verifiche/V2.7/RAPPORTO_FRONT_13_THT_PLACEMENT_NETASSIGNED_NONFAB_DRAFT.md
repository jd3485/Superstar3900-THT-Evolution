# V2.7 — PCB-FRONT: placement fisico preliminare dei 13 riferimenti THT, con pad/net reali (NON FAB)

**15 novembre 2026.** Primo artefatto di **placement KiCad9 reale** per il FRONT parziale. Non è una nuova PCB destinata alla produzione, non è una geometria pannello approvata e non equivale a sbroglio o DRC0.

## File CAD e separazione funzionale

`04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT/FRONT_CONTROL_13REFS_PLACEMENT_NONFAB.kicad_pcb` contiene **13 footprint THT con coordinate fisiche in mm** e **28 pad pin→net assegnati** sulla base delle **12 reti reali** dei tre fogli figli del root `FRONT_CONTROL_PARTIAL_V2_7_DRAFT.kicad_sch`. Nessuna traccia, via o zona rame, nessun contorno Edge.Cuts e nessun foro di fissaggio; dunque non esiste una PCB realmente completata, né sono eseguibili accettazioni di fabbricazione.

| Zona di studio (coordinate indicative, NON quote di pannello) | Riferimenti | Funzione |
|---|---|---|
| x=30–90mm | J1301, RV1301, J1302 | AF: volume pot 3 pin e due header verso rivelatore e LM386 |
| x=130–175mm | J2201, R2201, R2202, D2201, D2202 | Illuminazione LED 5V **LAB**; massa separata |
| x=220–309mm | J1801, RV1801, R1801, R1802, J1802 | S-meter passivo; driver e bobina ancora NON qualificati |

**Attenzione:** RV1301 e RV1801 mantengono l'impronta `TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL`, che riproduce **soltanto** tre fori di connessione 2,54mm; non rappresenta albero, fissaggio al pannello, corpo, ingombro dinamico né componente OEM. I connettori sono riferimenti elettrici 1×2 generici non polarizzati (non approvati per vibrazione). I LED sono posizionati con pad THT generici, non rispetto a finestre reali. Le resistenze sono assiali THT 7,62mm passo nominale.

Le 3 zone sono **isolate elettricamente**: nessun ritorno audio viene congiunto al ritorno LED o alla massa dello S-meter; gli 8 nodi di collegamento esterni non autorizzano alcuna alimentazione del pannello da MAIN.

## Gate CAD nativo e limiti di progetto

`03_Verifiche/V2.7/verify_front_13ref_netassigned_placement_native.py` estrae strutturalmente dall'artefatto i 13 footprint, i relativi 28 pad e i loro codici rete, confrontando **tutte** le coppie ref/pad con le 12 partizioni dell'ERC/netlist del FRONT. Esegue inoltre **kicad-cli pcb export pos** nativo a garanzia che KiCad9 possa aprire il file e identificare le coordinate di tutti i componenti THT. Fallisce se trova copper-routing, via, rame riempito, outline di fabbricazione, pad SMD, riferimenti duplicati, pin↔net alterati o potenziometri non marcati come PROVISIONAL. Aggiunto come gate FULL.

**Vincoli ancora aperti:** misure/fori/altezza chassis Superstar 3900 Evolution, MPN e orientamento di due veri potenziometri THT, lato frontale e orientamento fisico scheda, ingombri S-meter/display/manopole, fissaggi, cavi a connettori polarizzati, protezioni e schermature, guida massa e collegamenti da MAIN, tensione/driver S-meter, provenienza/limiti LED, TX disabilitata. In particolare la disposizione in x è solo geometria di studio, non la larghezza o lunghezza effettiva del prodotto.

**Nessuna DRC0 di prodotto:** l'artefatto è intenzionalmente privo di piste e bordo, quindi i controlli di routing/manifattura saranno applicati esclusivamente a una vera scheda completata, dopo aver qualificato la geometria. Vietati Gerber di fabbricazione, ordine PCB, TX, test su batteria/veicolo.

**Stato iniziale:** test FAST/FULL/required ancora da verificare sul final SHA della PR tecnica. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
