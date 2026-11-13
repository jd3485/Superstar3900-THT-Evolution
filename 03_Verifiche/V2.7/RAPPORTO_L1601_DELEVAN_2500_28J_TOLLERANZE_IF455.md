# V2.7 — valutazione OEM L1601 per IF455, tolleranze e divieto di release

**Data:** 13 novembre 2026. **Stato:** candidato OEM identificato ma filtro IF455 **non qualificato**. Non sostituisce una vera bobina/trasformatore IF accordabile, e non rende la radio né il prototipo adatti alla fabbricazione.

## Fonti attuali e verifica candidati

**Candidato solo per sviluppo da banco: Delevan `2500-28J`**, indicato come **Active** su [DigiKey 2500-28J](https://www.digikey.com/en/products/detail/delevan/2500-28J/3479912) e [DigiKey UK 2500-28J](https://www.digikey.co.uk/en/products/detail/delevan/2500-28J/3479912) (consultazione 13/11/2026). Descrizione rivenditore: 1 mH, THT assiale, **±5% L**, **DCR massimo 16,5 Ω**, **Q 60 misurato a 790 kHz**, **SRF 2,8 MHz**, temperatura −55…+105°C, corpo **Ø 4,83 mm × 11,18 mm**, corrente nominale 88mA. Il sito evidenzia disponibilità, ma **stock e lead time sono variabili**, dunque non congelare la distinta su una fotografia dell'inventario.

**NON utilizzare i vecchi Xicon `42IF102-RC` come soluzione moderna senza redesign**: [Mouser 42IF102-RC](https://www.mouser.com/en/ProductDetail/Xicon/42IF102-RC?qs=Ip36MYbAomKdj%2FcM%252B72Baw%3D%3D) indica lifecycle **Obsolete**. Altri `42IF2xx` hanno dati storici su cataloghi, ma non una prova attuale di produzione/fornitura con data sheet e piedinatura verificati. Trasformatore IF a 2 avvolgimenti **non** è sostituibile 1:1 a una bobina a 2 pad: servirebbe schematico e footprint nuovi.

La scheda nativa KiCad9 `IF455_TANK_THT_V2_7_DRAFT.kicad_sch` marca ora L1601 `1mH_DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED`, **senza cambiare il footprint `TH_TANK:L_1mH_Axial_THT_PROVISIONAL`**. I due pad a passo 15,24 mm NON sono derivati da quota di piegatura/foro prescritta da Delevan, non sono sufficienti per fissare il diametro foro, la distanza dal corpo e l'orientamento. Non approvare questo footprint per CAD di produzione; verificare il datasheet manufacturer nativo e la piegatura/raggio minimo prima di generare eventuali Gerber.

## Perché un componente reperibile non basta

Per il tank nominale di PR #81, con **L 1 mH e C1602=110 pF, C1603=2,2 pF**, la frequenza LC *scarica* calcolata è **475,14 kHz**; la rete *accoppiata* di sola prova con input/output da 10 pF, generatore 50Ω, uscita 100kΩ e R bobina **30Ω assunta** aveva picco ngspice **454,5 kHz**. Un circuito reale aggiunge almeno tre incognite:
- ±5% della L: per un LC semplice, `Δf/f≈−0,5×ΔL/L`, quindi circa **±2,5% di frequenza (~11 kHz a 455 kHz)** anche prima di altre tolleranze;
- frequenza di autorisonanza 2,8MHz: se fosse descritta da L=1mH con un solo condensatore equivalente ideale, `Cpar≈1/((2π·2,8MHz)^2·1mH)≈3,23 pF`. È solo un **modello derivato**, non il dato di capacità realmente garantito per la bobina;
- il valore di **Q misurato a 790kHz non è Q a 455kHz**; la DCR 16,5Ω non coincide con la resistenza equivalente AC, che cambia con nucleo/frequenza e carico. Non utilizzare il Q=60 per inventare banda a −3dB della nostra sezione IF.

## Evidenze validate PR #83

La [PR #83](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/83) è **MERGED**, SHA `c9f1a473bf00080bf961693bd397eb9982df4667`; Actions [#43413234046](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43413234046) **3/3 PASS**, con 2001 punti AC nativi e picchi `466220Hz` L−5%, `454395Hz` Lnom, `443395Hz` L+5%, `448510Hz` con Cpar3.23pF assunta. Il test ha correttamente emesso il blocco `REJECT_FIXED_110PF_IF455_TANK_WITH_5PCT_COIL_UNTIL_TRIM_AND_RF_MEASUREMENTS` perché la soluzione senza trimmer non copre i corner. Successivamente PR #84 ha aggiunto C1602 82pF+C1603 trimmer 10–50pF e ha superato l'analisi di copertura di quattro corner nel modello (non prova RF reale). Restano non qualificati i footprint OEM di L1601 e C1603.

---

## Nuova prova ngspice che protegge dalla qualifica prematura

Deck `03_Verifiche/V2.7/spice/if455_delevan_2500_28j_tolerance_ac.cir` con **quattro reti simulate**:
1. L=0,95mH (−5%) / Cpar non modellata.
2. L=1,00mH nominale / Cpar non modellata.
3. L=1,05mH (+5%) / Cpar non modellata.
4. L=1,00mH + **3,23pF parassiti ipotetici** dalla relazione SRF sopra.

Per comparazione, in **tutti** i casi la resistenza serie bobina è 16,5Ω fissa **come scenario che usa il massimo DCR**, senza modello Q o temperatura; condensatori ideali, RGEN=50Ω, R shunt=47kΩ e RLOAD=100kΩ. `verify_if455_delevan_tolerance_ngspice.py` esegue un **vero ngspice `ac lin 2001 400k 510k`**, importa i 2001 campioni e verifica che i corner ±5% provochino un disallineamento significativo e che il contributo parassita sposti il centro. Il test **deve** segnalare `REJECT_FIXED_110PF_IF455_TANK_WITH_5PCT_COIL_UNTIL_TRIM_AND_RF_MEASUREMENTS` anche quando passa; `PASS` vuol dire soltanto **controllo di rischio riuscito**, non “filtro approvato”.

**Nessun ulteriore workflow Actions**: test integrato alla FULL KiCad9/ngspice esistente, i test RAPIDI e il required gate invariati. Non riportare risultati frequenziali di questo nuovo esperimento come misurati prima di esito CI effettivo sul commit finale.

## Decisione tecnica

L1601 = `Delevan 2500-28J` è un **MPN candidato preliminare e reale da catalogo**, ma **non una parte approvata per la PCB finale**. Il progetto IF455 necessita:
- architettura di filtro con **taratura** (trimmer THT C0G correttamente dimensionato oppure trasformatore IF regolabile realmente prodotto), definizione della banda necessaria per AM/FM e impedenze dello stadio a monte/a valle;
- simulazione sweep con L, C0G, ESR/Q, temperatura, RF coupling e componente reale; manuale RF/OEM, MPN meccanico, footprint verificato e misure sul banco;
- se la selettività richiesta richiede filtri ceramici multipolari e AGC, non promuovere il singolo LC passivo a filtro selettivo di canale.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO**. MASTER V2.6 MAIN 7 fogli/138 refs invariato, IF455 pilot e AM455 pilot rimangono separati; layout PCB-MAIN e PCB-FRONT **0%**, completamento complessivo **~20% stima**, non aumentare per aver reperito un componente.
