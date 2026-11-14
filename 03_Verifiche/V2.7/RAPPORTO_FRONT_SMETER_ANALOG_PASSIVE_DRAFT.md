# V2.7 draft — PCB-FRONT interfaccia passiva S-meter analogico

**Stato:** CAD KiCad9 standalone di laboratorio, NON PCB-FRONT integrata, NON validazione del movimento né del driver. Rispetta ADR-001 (S-meter a lancetta, PCB-FRONT distinta). Il nuovo circuito **non implica una sorgente S-meter disponibile sulla PCB-MAIN** e non porta TX al frontale.

## Contratto candidato nel vero schematico

`04_KiCad/V2.7_DRAFT/FRONT_SMETER/FRONT_SMETER_THT_V2_7_DRAFT.kicad_sch`:

- `J1801/1` = `METER_DRIVE_CANDIDATE`, solo ingresso analogico esterno MAIN ancora non progettato.
- `RV1801/1` = `METER_DRIVE_CANDIDATE`; `RV1801/2` = `METER_TRIM_OUTPUT`; `RV1801/3` = `METER_RETURN`. Potenziometro THT 10k linear B candidato, impronta a tre pad **PROVISIONAL — DO NOT FAB**.
- `R1801/1` = `METER_TRIM_OUTPUT`; `R1801/2` = `METER_POS_LIMITED`. R serie 100kΩ nominali, 0,25W, candidata. Footprint THT assiale standard geometrica, MPN e derating non qualificati.
- `J1802/1` = `METER_POS_LIMITED`; `J1802/2` = `METER_RETURN`, per un **movimento panel-mounted esterno**, non un meter elettronico SMD.
- `J1801/2` = `METER_RETURN`; segnale di ritorno distinto da masse audio, RF e chassis finché interfaccia e cablaggio non sono definiti.

Lo schema usa un partitore passivo più limitazione serie: `Icoil = (Vdrive*alpha)/(R1801+Rcoil+Rth(alpha))`, dove `alpha` è la posizione del cursore e `Rth` la resistenza Thevenin del potenziometro. **Non conoscere la tensione MAIN e la corrente FSD del movimento impedisce di dimostrare che 100k protegga davvero lo strumento**, o che si raggiunga il fondo scala. Non usare il valore come dimensionamento definitivo. Per questo il candidato resta isolato, senza driver attivo, batterie, rail, massa condivisa o protezioni dichiarate qualificate.

## Verifiche e limiti

`03_Verifiche/V2.7/verify_front_smeter_native.py` esegue ERC KiCad9 vero e esportazione nativa della netlist; impone 4 componenti, nove pin, quattro reti distinte con collegamenti esatti, controlla il footprint THT a tre fori incluso e i banner NO FAB. `ci/full_regressions.py` rende obbligatorio il test in FULL. Gli ERC/verifiche saranno considerati superati **solo a valle del gate Actions**. Il master MAIN V2.6, il vecchio FRONT_VOLUME e i due progetti PCB rimangono invariati; non esiste PCB-FRONT, nessun PCB DRC è eseguibile.

**Qualifiche obbligatorie prima del circuito definitivo:** modello/marca movimento e sua disponibilità, `Rcoil`, corrente piena scala, tensione max ammissibile, sensibilità allo shock e calibrazione (scala S e tensione del rivelatore, AGC, tempi e dinamica), misure di Vdrive reale, guasto open/short/wiper, eventuale buffer high-Z, resistenza serie e trim dimensionati, protezione ESD/EMI, cavo MAIN/FRONT, connettori polarizzati, fissaggio, illuminazione, MPN THT attivi, clearance e verifiche di banco. `RV1801` usa la stessa impronta dimostrativa non meccanicamente verificata di FRONT_VOLUME: non utilizzabile in produzione.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Verifica corrente / guasti della rete S-meter — estensione analitica

`03_Verifiche/V2.7/verify_front_smeter_current_fault_envelope.py` è un gate tecnico vincolato ai valori **ancora candidati** visibili nello schema `RV1801=10kΩ`, `R1801=100kΩ`. Il verificatore costruisce il modello Thevenin del partitore per posizione cursore `alpha`, resistenza del generatore `Rs` e carico strumento `Rcoil`: `Rtop=(1-alpha)*Rpot`, `Rbot=alpha*Rpot`, `Vth=Vsource*Rbot/(Rs+Rtop+Rbot)`, `Rth=(Rs+Rtop)*Rbot/(Rs+Rtop+Rbot)`, `Icoil=Vth/(Rth+R1801+Rcoil)`. Un sistema indipendente di due equazioni ai nodi con conduttanze verifica 135 combinazioni (Vsource ipotetico 3,3/6/20V × Rs 100/1000/10000Ω × Rcoil 100/1000/5000Ω × cinque posizioni interne). Non è una simulazione OEM o un valore di drive MAIN misurato.

**Controesempi essenziali, non specifiche radio:** con generatore ideale e bobina cortocircuitata, 100kΩ limitano la corrente a 60µA a 6V ma a 200µA a 20V. Quindi un movimento ipotetico da 100µA FSD **non raggiunge** il fondo scala a 6V, mentre uno ipotetico da 50µA FSD può essere **sovrapilotato** a 20V. Se R1801 si cortocircuita e Rcoil=100Ω, 6V possono produrre circa 60mA nel modello: non esiste vera protezione garantita contro il guasto del limitatore. Per un potenziometro ideale di 10kΩ alimentato a 20V senza carico, la potenza di pista è 40mW; la potenza ammissibile e il derating del potenziometro reale non sono noti. Contatto del cursore aperto e R1801 aperta danno corrente statica nulla nel modello, **non validano** scariche induttive, transitori né ESD.

**Decisione:** i valori 100k/10k rimangono DRAFT, **né sicuri né calibrabili** senza `Vdrive_max`, impedenza sorgente MAIN, Rcoil, FSD, condizioni di sovratensione e degrado dei contatti, rating elettrici/termici, risposta dinamica e MPN. La CI blocca regressioni matematiche ma non sostituisce banco fisico. Non integrare il driver nel master o nel layout PCB-FRONT sulla base di questi stress fittizi. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.

## Contratto del cablaggio lato FRONT verso MAIN — frontiera di isolamento verificabile

Il nuovo `03_Verifiche/V2.7/verify_smeter_front_harness_isolation_native.py` esporta tre **netlist KiCad9 reali**: FRONT S-meter, FRONT volume e MAIN audio RX standalone. Vincola senza tolleranze aggiuntive le quattro reti/nove pin del circuito S-meter e le tre reti previste nel FRONT volume. In fase attuale il solo **ipotetico connettore lato FRONT** del meter è `J1801`: pin 1 = `METER_DRIVE_CANDIDATE`, pin 2 = `METER_RETURN`. **Nessun pin MAIN di provenienza è specificato**, né `GND` o `AF_GND` sono connessi a `METER_RETURN` nel CAD. Questo **non** è un cavo approvato, non definisce il connettore accoppiato, la polarizzazione, schermatura, corrente ammissibile o cablaggio reale.

Il gate rifiuta qualsiasi corto, connessione addizionale, rete TX/PTT/power o assegnazione impropria ai pin del dominio meter; confronta i domini con `DEMOD_AUDIO` / `VOL_WIPER_TO_AMP` / `AF_GND` del FRONT volume e il pilot MAIN audio. È isolamento **tra schemi standalone**, non misura d'isolamento EMC o di un cablaggio costruito. Non confondere l'alimentazione `AUDIO_6V_LAB` del pilot RX con la sorgente S-meter: manca ancora l'origine reale AGC/detector/driver sulla MAIN V2.6.

**Gate prima dell'unione fisica:** selezionare misuratore e datasheet (FSD/Rcoil), progettare drive MAIN con tensioni massime e guasti verificati; poi introdurre **entrambi** i connettori veri e un contratto pin↔pad↔cavo con protezioni ESD/EMI, ritorni coerenti, contatti polarizzati e verifica di invertito/open/short. Un solo cambio di nome delle reti non costituisce integrazione. Master MAIN V2.6 e layout restano invariati. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## Revisione CAD: due limitatori serie indipendenti, R1801 + R1802

Il disegno nativo ora contiene **cinque componenti / cinque reti / undici pin**: `R1801` (100kΩ THT nominali, candidata) dal cursore `METER_TRIM_OUTPUT` alla rete `METER_LIMIT_STAGE1`; `R1802` (100kΩ THT nominali, candidata) da `METER_LIMIT_STAGE1` a `METER_POS_LIMITED` verso `J1802/1`. I due componenti **fisici** sono distinti e vengono controllati nella netlist KiCad9, non costituiscono un'unica resistenza teorica né una protezione di sicurezza certificata. La corrente nominale ideale a fine corsa è `Vdrive/(200kΩ+Rcoil)`, assumendo sorgente ideale e circuito integro, senza altri percorsi di guasto.

La suite KCL analitica confronta ancora **135** casi con due nodi indipendenti usando `Rlim=200kΩ`; aggiunge il cortocircuito del solo R1801 e del solo R1802, in entrambi i casi con 100kΩ superstiti; inoltre doppio corto, resistenza aperta e cursore aperto soltanto in DC. Controesempi ipotetici con bobina cortocircuitata e sorgente ideale: a **6V** nominali 30µA, singolo corto 60µA; a **20V** nominali 100µA, singolo corto 200µA. Se entrambe le resistenze vanno in corto, con una bobina fittizia da 100Ω e 6V si ottengono circa 60mA. La ridondanza mitiga **un particolare guasto singolo** rispetto al precedente limitatore unico, ma può rendere impossibile il fondo scala richiesto e **non protegge** da guasti comuni, PCB/cablaggio, sovratensioni non caratterizzate o connettori invertiti. Valori, potenza dissipata, tolleranze, FSD e test reali restano da qualificare. I precedenti paragrafi a **quattro componenti, quattro reti e 100kΩ totali** descrivono la revisione storica precedente PR #172/#174, non lo stato CAD aggiornato. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.
