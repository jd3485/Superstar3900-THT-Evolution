# V2.7 — PTV09A-4 Bourns: impronta THT candidata per FRONT, non autorizzata alla produzione

**15 novembre 2026 — componente da confrontare, non scelta finale.** Fonte primaria: [Bourns PTV09 Series, datasheet OEM](https://www.bourns.com/docs/product-datasheets/ptv09.pdf) (dimensionale PTV09A-4, terminali 1/2/3, schematico e dati ambientali). Il modello di ordine **PTV09A-4020F-B103** è riportato *Active* e THT da distributore DigiKey, ma questo **non equivale alla conferma OEM di produzione attiva sul singolo MPN**. Prima della distinta va verificato sul sito del costruttore e con canali autorizzati. `-4` significa **horizontal/rear mount, senza boccola**; `B103` lineare 10 kΩ, che **non è automaticamente una legge audio logaritmica appropriata** per il volume. La compatibilità del profilo meccanico con il frontalino Evolution non è stata misurata.

## Riscontro dimensionale e CAD nativo

Dal disegno OEM PTV09A-4 si ricava l'**interasse complessivo di 5,0 mm** fra i tre contatti, con pin 2 cursore, 1/3 estremi. L'impronta esistente della scheda di studio usa **0 / 2,54 / 5,08 mm**, diversa da 0 / 2,50 / 5,00 mm OEM. Creato pertanto un nuovo **file footprint KiCad9 autonomo**, senza modificarne schema, PCB o disposizione delle 35 piste:

`04_KiCad/V2.7_DRAFT/FRONT_PLACEMENT/TH_FRONT_OEM_CANDIDATES.pretty/Potentiometer_Bourns_PTV09A4_5mm_THT_CANDIDATE_NOT_FOR_FAB.kicad_mod`

Il file candidato ha 3 pad THT, posizionati a -2,50/0/+2,50 mm con assegnazione **1=terminale, 2=wiper, 3=terminale**. **ATTENZIONE:** fori passanti 1,0 mm e corpo/courtyard sono **assunti per studio** e non approvati per PTV09A-4: non sono stati qualificati orientamento dei terminali deformati, ritenzione, ingombro alberino, interasse dei fissaggi e prospettiva del disegno OEM. Il codice impedisce che questo footprint ancora incompleto venga assegnato ai due RV del layout corrente. Il gate `03_Verifiche/V2.7/verify_front_ptv09a4_oem_pitch_candidate_native.py` verifica i tre pad, il passo esatto, i 35 segmenti del PCB invariati e richiede **esportazione SVG nativa KiCad9 dal footprint library** nella suite FULL.

## Esito CI nativo verificato

La [PR #254](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/254) è stata **MERGED** su main SHA `b62c56dc257354d24c3d29392531d0c49b04e211`, final HEAD `3d0d277e876b27cba42f62d5def39a0d64c4b624`. [Actions #43747364174](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43747364174): **FAST/FULL/required 3/3 SUCCESS**, 111 regressioni storiche e risultato `PASS_KICAD9_BOURNS_PTV09A4_3THT_PINS_5MM_CANDIDATE_SVG_NO_PRODUCT_SWAP_NO_FAB`. L'esportazione SVG di KiCad9 ha elaborato la libreria originale senza errori. **Questo convalida solo i 3 pad e la leggibilità CAD del candidato**, non corpo, albero, boccola, fori di fissaggio, affidabilità ambientale o disponibilità OEM; il file di placement FRONT resta con gli stessi due footprint temporanei da 5,08mm e 35 piste.

## Gate elettrico, termico e di prodotto

- Datasheet OEM PTV09: **-10/+50 °C** operativo, 0,05 W nominali, 20 Vcc massimi, IP40, durata dichiarata 10.000 cicli, tolleranza nominale ±20%. Questi dati **non bastano** per garantire ambiente abitacolo assolato, condensa/vibrazione, escursioni in magazzino, resistenza al lavaggio o requisiti RF audio; necessaria specifica ambientale di prodotto.
- **RV1301 volume** 10 kΩ: valutare un esatto codice THT con curva logaritmica/audio se richiesto da ergonomia, rumore di scorrimento e interazione col rivelatore; `B103` lineare è solo una variante meccanica di confronto.
- **RV1801 S-meter**: stessa resistenza nominale 10 kΩ nello studio, ma punto di lavoro/dissipazione/driver e funzione trim non sono qualificati.
- Il disegno proprietario non sostituisce la misura reale della profondità disponibile, dell'altezza asse, delle manopole, della parete del pannello e delle tolleranze dell'insieme MAIN/FRONT.
- La PCB-FRONT attuale rimane **13 footprint THT/28 pad/12 reti/35 piste** ma senza Edge.Cuts e DRC0 di prodotto, con le vecchie due impronte **PROVISIONAL**; nessun assemblaggio autorizzato.

Nessuna approvazione di fabbricazione, trasmissione, batteria o veicolo. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**


## Schermatura geometrica pad THT (studio successivo, 15 novembre 2026)

Il gate `verify_front_ptv09a4_oem_pitch_candidate_native.py` ora calcola anche il
margine geometrico preliminare dei tre pad nella libreria candidata, senza
cambiare il PCB di studio: diametro rame **1,8 mm**, foro finito
**provvisorio 1,0 mm**, anello radiale nominale **0,4 mm**, passo adiacente
**2,5 mm** e distanza minima nominale rame-rame **0,7 mm**.
Controlli fail-closed: numerosità/pin 1-2-3, quota 5,00 mm, forma
circolare/rettangolare, dimensioni/fori immutati, anello minimo
0,4 mm, separazione rame almeno 0,5 mm e permanenza delle 35
piste/footprint precedenti nella board NONFAB.

Questo è uno **screen geometrico nominale** sui parametri della libreria,
non un valore garantito dal produttore, non una prova delle tolleranze di
foratura/registrazione/solder-mask, non DRC e non autorizza sostituzione
del potenziometro. Il fabbricante del PCB e l'OEM del componente devono
qualificare foro, lead e quote meccaniche, taper audio, ambiente e stato
produttivo dell'MPN esatto. KiCad9 SVG nativo va eseguito nella FULL CI
sull'HEAD finale della PR; nessuna verifica KiCad locale è stata dichiarata.
**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
