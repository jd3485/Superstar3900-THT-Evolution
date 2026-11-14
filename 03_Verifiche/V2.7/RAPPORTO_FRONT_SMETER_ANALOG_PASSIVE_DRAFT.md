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
