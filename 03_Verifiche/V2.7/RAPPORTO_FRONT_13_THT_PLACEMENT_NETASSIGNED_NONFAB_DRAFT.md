# V2.7 — PCB-FRONT: placement fisico preliminare dei 13 riferimenti THT, con pad/net reali (NON FAB)

**15 novembre 2026.** Primo artefatto di **placement KiCad9 reale** per il FRONT parziale. Non è una nuova PCB destinata alla produzione, non è una geometria pannello approvata e non equivale a sbroglio o DRC0.

## File CAD e separazione funzionale

`04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT/FRONT_CONTROL_13REFS_PLACEMENT_NONFAB.kicad_pcb` contiene **13 footprint THT con coordinate fisiche in mm** e **28 pad pin→net assegnati** sulla base delle **12 reti reali** dei tre fogli figli del root `FRONT_CONTROL_PARTIAL_V2_7_DRAFT.kicad_sch`. Nessuna traccia nelle prime revisioni; ora solo i quattro nodi LED LAB hanno 13 segmenti, senza via o zona rame; nessun contorno Edge.Cuts e nessun foro di fissaggio; dunque non esiste una PCB realmente completata, né sono eseguibili accettazioni di fabbricazione.

| Zona di studio (coordinate indicative, NON quote di pannello) | Riferimenti | Funzione |
|---|---|---|
| x=30–90mm | J1301, RV1301, J1302 | AF: volume pot 3 pin e due header verso rivelatore e LM386 |
| x=130–175mm | J2201, R2201, R2202, D2201, D2202 | Illuminazione LED 5V **LAB**; massa separata |
| x=220–309mm | J1801, RV1801, R1801, R1802, J1802 | S-meter passivo; driver e bobina ancora NON qualificati |

**Attenzione:** RV1301 e RV1801 mantengono l'impronta `TH_FRONT:Potentiometer_THT_3Pin_PROVISIONAL`, che riproduce **soltanto** tre fori di connessione 2,54mm; non rappresenta albero, fissaggio al pannello, corpo, ingombro dinamico né componente OEM. I connettori sono riferimenti elettrici 1×2 generici non polarizzati (non approvati per vibrazione). I LED sono posizionati con pad THT generici, non rispetto a finestre reali. Le resistenze sono assiali THT 7,62mm passo nominale.

Le 3 zone sono **isolate elettricamente**: nessun ritorno audio viene congiunto al ritorno LED o alla massa dello S-meter; gli 8 nodi di collegamento esterni non autorizzano alcuna alimentazione del pannello da MAIN.

## Estensione CAD successiva: quattro reti LED LAB fisicamente sbrogliate (PR tecnica in verifica)

Il file FRONT di placement ora contiene **13 veri segmenti di rame da 0,5 mm** connessi ai pad di J2201, R2201, R2202, D2201 e D2202: **4 reti illuminate di solo banco** `ILLUM_5V_LAB`, `ILLUM_RETURN_LAB`, `ILLUM_LED1_A`, `ILLUM_LED2_A`. I rami di alimentazione/anodi stanno su `F.Cu` (7 segmenti); il **ritorno LAB** è su `B.Cu` (6 segmenti) e risale ai pad THT passanti. Non sono introdotti via, piani o outline. **Le altre otto reti** (volume e S-meter) sono rimaste senza alcuna pista e non sono state collegate tra loro o alla rete LED. L'artefatto resta un **placement parzialmente sbrogliato NONFAB**, senza alcuna dimensione pannello approvata, anche se i quattro sottocircuiti LED sono topologicamente connessi.

Il gate nativo dello stesso file è stato reso più restrittivo: corrispondenza esatta dei **13 segmenti**, larghezza, piano, coordinate, quattro net-ID e connettività pad→segmento→pad per ogni rete LED; respinge qualsiasi traccia audio/S-meter, RAM, rail MAIN, modifica delle 28 assegnazioni pad↔net, via, rame riempito o Edge.Cuts. Anche le guardie storiche V0.3/V0.4 consentono solo questo preciso artefatto dichiarato non fabbricabile e la PCB LED LAB precedente; nessun bypass generico alle schede arbitrarie.

Il fatto che le quattro reti LED risultino connesse nel modello non rappresenta **DRC=0**, validazione EMI, illuminazione frontale approvata, termica o produzione. La meccanica e l'interfaccia MAIN/FRONT restano da qualificare. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Gate CAD nativo e limiti di progetto

`03_Verifiche/V2.7/verify_front_13ref_netassigned_placement_native.py` estrae strutturalmente dall'artefatto i 13 footprint, i relativi 28 pad e i loro codici rete, confrontando **tutte** le coppie ref/pad con le 12 partizioni dell'ERC/netlist del FRONT. Esegue inoltre **kicad-cli pcb export pos** nativo a garanzia che KiCad9 possa aprire il file e identificare le coordinate di tutti i componenti THT. Fallisce se trova segmenti diversi dai 13 tracciati LED LAB consentiti, via, rame riempito, outline di fabbricazione, pad SMD, riferimenti duplicati, pin↔net alterati o potenziometri non marcati come PROVISIONAL. Aggiunto come gate FULL.

**Vincoli ancora aperti:** misure/fori/altezza chassis Superstar 3900 Evolution, MPN e orientamento di due veri potenziometri THT, lato frontale e orientamento fisico scheda, ingombri S-meter/display/manopole, fissaggi, cavi a connettori polarizzati, protezioni e schermature, guida massa e collegamenti da MAIN, tensione/driver S-meter, provenienza/limiti LED, TX disabilitata. In particolare la disposizione in x è solo geometria di studio, non la larghezza o lunghezza effettiva del prodotto.

**Nessuna DRC0 di prodotto:** l'artefatto è intenzionalmente privo di piste sulle 8 reti audio/S-meter e privo di bordo, quindi i controlli di routing/manifattura saranno applicati esclusivamente a una vera scheda completata, dopo aver qualificato la geometria. Vietati Gerber di fabbricazione, ordine PCB, TX, test su batteria/veicolo.

**Stato verificato:** [PR #248](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/248) MERGED su main `648d201d46c743bc359d5f0af7bb3904faef6bd1`; [CI #43723761801](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43723761801) FAST/FULL/required **SUCCESS 3/3** sul final SHA tecnico `d61112274581d3684dfae91e9ac9a801ae102b84`. Log nativo `PASS_KICAD9_FRONT_13_THT_FOOTPRINTS_28_PADS_12_ISOLATED_NETS_PLACEMENT_ONLY_NO_OUTLINE_NO_ROUTING_NO_FAB`; KiCad9 `pcb export pos` ha esportato correttamente tutte e 13 le posizioni; 111 regressioni storiche PASS. Le guardie di sicurezza V0.3/V0.4 sono state aggiornate per ammettere **solo** LED LAB e FRONT 13-ref NONFAB e respingere qualsiasi altro PCB, routing o Edge.Cuts. **Nessuna DRC0 prodotto dichiarata**: la scheda rimane intenzionalmente aperta, senza piste e senza bordo. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
