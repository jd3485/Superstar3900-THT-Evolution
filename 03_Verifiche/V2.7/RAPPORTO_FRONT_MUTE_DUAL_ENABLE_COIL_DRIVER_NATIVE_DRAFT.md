# V2.7 — Driver bobina mute a doppio consenso, candidato THT KiCad9

**15 novembre 2026 · SCHEMA ELETTRICO REALE SOLO DA BANCO · NO FAB / NO TX**

## Architettura

Lo schema nativo `04_KiCad/V2.7_DRAFT/FRONT_MUTE_COIL_DRIVER/FRONT_NC_MUTE_DUAL_ENABLE_COIL_DRIVER_V2_7_DRAFT.kicad_sch` ha due NPN astratti THT in serie sul ritorno bobina mute SPDT K1901: transistor superiore Q1911 tra `COIL_MINUS_LAB` e `SERIES_MID`; Q1912 tra `SERIES_MID` e `DRIVER_GND`. Q1911 richiede `ENABLE_AUDIO_LAB` e Q1912 `POWER_GOOD_LAB` **entrambi positivi** per eccitare la bobina. Le basi hanno R1911/1912 1,5kΩ e pull-down R1913/1914 10kΩ. D1911 collega catodo a `COIL_PLUS_LAB` e anodo a `COIL_MINUS_LAB` come diodo di ricircolo candidato. J1911 alimentazione 5V+GND lab, J1912 audio-enable+GND, J1913 power-good+GND, J1914 bobina verso J1903 dello schema contatto; i connettori THT restano di laboratorio.

**La sorgente POWER_GOOD non è stata progettata**: è un input esterno non qualificato, non un comparatore di soglia e non un supervisore di rail. Non esiste ancora un MPN di relè, bobina, doppio NPN, diodo o supervisore elettricamente qualificato. Pinout fisici, dissipazione, carico minimo di contatto, flyback, saturazione, margini di alimentazione, tolleranze, interferenze, ESD e ritorni di massa non sono provati.

## Verifica

Il gate `03_Verifiche/V2.7/verify_front_nc_dual_enable_coil_driver_native.py`, eseguito dalla FULL CI, verifica ERC0 KiCad9 vero, netlist esportata con **8 reti esatte** e J1914 ↔ J1903 (K1901/4,5), isolamento delle due basi, della rete intermedia, dei quattro connettori e del diodo orientato. Controlla l'invarianza della PCB FRONT 13 THT / 35 piste NONFAB.

Lo screening DC **analitico illustrativo** enumera 48 casi:
- rail ipotetico 4,5/5/5,5 V, comandi input 4,5/5,0 V;
- bobina fittizia 250/330/500/1000 Ω, due VCEsat 0,15/0,30 V;
- VBE ipotizzata 0,8 V, forced β obiettivo 10, Rbase 1,5 kΩ e Rpull-down 10 kΩ.

Calcola `Icoil = (Vrail-2VCEsat)/Rcoil` e disponibilità di corrente base per entrambi gli NPN. Sono **ipotesi di progetto da verificare OEM**, non modello vendor né simulazione ngspice della bobina o dei transistor. La doppia serie non garantisce copertura di guasti correlati: un transistor saldato ON, un falso power-good alto o un comando sempre attivo possono permettere eccitazione non voluta, mentre corti bobina/driver potrebbero sovraccaricare le uscite. L'assenza di rail porta i transistor OFF soltanto nell'ipotesi di transistor non in corto; il relè NC fisico non è provato.

## Limiti e gate successivi

1. Scegliere un relè THT in produzione con contatti per segnali audio a basso livello e bobina adatta alla corrente reale; ingegnerizzare e verificare picchi, contatti, rimbalzo, rilascio, vibrazione.
2. Definire MPN/foglio dati OEM NPN/diode e valori di corrente/calore, condizioni rail startup/brownout; il diodo può rallentare rilascio, alternativa clamp da progettare per tempi di mute.
3. Realizzare supervisore **vero** che mantenga inibito audio su alimentazione non valida e disconnessione cablaggio; qualificare richiesta power-good e comando per sicurezza, EMI, diagnostica guasti, condensatori e contatti.
4. Risolvere failure NC/NO saldato, AF_GND aperta e ingresso LM386 flottante con mitigazione fisicamente indipendente. Nessuna certificazione safety, nessuna DRC prodotto.
5. Non collegare questo CAD autonomo alla MAIN o alla FRONT PCB fisica finché non sono chiusi OEM e gate sopra.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## 16/11/2026 — D1911 Vishay 1N4007-E3/54, candidato CAD THT (non rilasciato)

Candidato **Vishay 1N4007-E3/54**, rettificatore assiale **DO-41 / DO-204AL**, 1 A IF(AV), 1000 V VRRM, non equivalente a un test reale di energia bobina. [Datasheet OEM Vishay](https://www.vishay.com/docs/88503/1n4001.pdf); [scheda del codice esatto e stato commerciale active presso DigiKey](https://www.digikey.com/en/products/detail/vishay-general-semiconductor-diodes-division/1N4007-E3-54/868990). Lo stato produttivo OEM dell'esatto MPN resta da verificare direttamente prima della BOM finale. In KiCad D1911/1=**K** su `COIL_PLUS_LAB`, D1911/2=**A** su `COIL_MINUS_LAB`; footprint candidato `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal`. La polarità è intenzionalmente bloccante durante energizzazione. L'uso di un ricircolo semplice può aumentare il tempo di rilascio del relè: **misura reale, induttanza, corrente di guasto, impulso, dissipazione e risposta mute non qualificate**. Nessuna modifica PCB reale né rilascio al montaggio. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

## 16/11/2026 — Analisi RL con diodo D1911: 216 casi, solo decadimento corrente

La K/A del diodo è già verificata sul netlist KiCad9; in spegnimento ideale con entrambi gli NPN aperti e diodo conduttivo, la bobina obbedisce alla **sola equazione elettrica** `L di/dt + R i + Vf = 0`, da cui `t(f)=(L/R) ln[(I0+Vf/R)/(f I0+Vf/R)]`, `I0=(Vrail−2·VCEsat)/R` e `E0=L·I0²/2`. Test aggiunto al gate nativo esistente: 2 nominali Omron DC5/DC6 (167/240Ω), 3 rail (4,6/5/5,5 V), 3 tolleranze (±10%), 3 induttanze *puramente illustrative* (20/100/500 mH), 2 Vf (0,55/0,9 V) e 2 VCEsat per transistor (0,15/0,3 V) = **216 scenari**. Controllo indipendente della soluzione a t50/t10, monotonia, accelerazione per Vf più alta.

Risultato calcolato per **corrente al 10%** nell'intero sweep: **0,10052–5,59395 ms**; energia magnetica iniziale modellata **0,002296–0,299246 mJ**. Questi valori **NON sono tempi di release del relè, non sono un envelope garantito, né energia/avalanche rating OEM**. L effettiva dipende da corrente, nucleo, temperatura; la forza meccanica dei contatti può variare con corrente e posizione; il diodo reale ha recupero, VF e dissipazione dipendenti dal tempo. I due relè Omron sono già esclusi dallo screening indipendente base-drive/pickup; quindi nessuna previsione operativa di K1901 è autorizzata. Un guasto D1911 cortocircuitato può cortocircuitare la bobina/rail quando pilotato; guasto aperto può imporre sovratensione ai transistor. Necessario selezionare relè OEM compatibile, ottenere L(corrente)/release-time, qualificare clamp e fare banco con oscilloscopio e misure di contatto AF. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

## 16/11/2026 — footprint fisici resistori R1911–R1914

Assegnato nello schema KiCad nativo THT a **tutti e quattro** i resistori (R1911, R1912 1k5 base; R1913, R1914 10k pulldown) `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal`: assiale DIN0207 corpo 6,3×2,5 mm, passo 10,16 mm, pad numerati 1↔2 come simbolo. Il verificatore KiCad9 esistente richiede precisamente **4 footprint** e continua a validare ERC/netlist, oltre a 48 screening DC e 216 RL puramente analitici. Questo non assegna un produttore reale, wattaggio/tolleranza/derating termico definitivo né rende valida la corrente di base: l'esclusione Omron DC5/DC6 rimane. Nessuna PCB aggiornata; `NO FAB / NO TX / NO BATTERIA / NO VEICOLO`.

## 16/11/2026 — Q1911/Q1912 onsemi BC33725BU, pin↔pad OEM in schema THT

Fonte primaria [onsemi BC337-FSC/D rev.3 aprile 2024](https://www.onsemi.com/pdf/datasheet/bc337-fsc-d.pdf), p.1 pinout effettivo **1=C, 2=B, 3=E** per BC33725BU TO-92 straight (CASE 135AN), marcatura BC33725; p.2 VCEO 45V, IC DC 800mA, dissipazione ambientale 625mW a 25°C, derating 5mW/°C, VCEsat **massima 0,7V soltanto a IC=500mA/IB=50mA**. Il dato non garantisce 0,15–0,30 V nei nostri corner di corrente molto inferiore né dimostra pilotaggio con base 1k5. [DigiKey BC33725BU](https://www.digikey.it/it/products/detail/onsemi/BC33725BU/975529) indica active, ma mantenere requisito conferma OEM di produzione prima della BOM finale.

Integrato **realmente** nei simboli KiCad embedded e libreria TH_COIL il mapping C1/B2/E3 e assegnati Q1911/Q1912 all'esatto candidato `BC33725BU_ONSEMI_CANDIDATE_NOT_DRIVER_RELEASE`, footprint `Package_TO_SOT_THT:TO-92_Inline` coerente col PACKAGE OEM. Aggiornato il gate nativo 8 reti per `COIL_MINUS_LAB↔Q1911/1`, `SERIES_MID↔Q1912/1`, basi `Q1911/2` e `Q1912/2`, emitter entrambi /3, senza modificare l'architettura elettrica o la PCB nonfab. Non collegare un pinout BC337 generico alternativo senza confermare il produttore esatto. **I valori ipotetici dei test DC/RL non diventano parametri OEM garantiti.** Restano non qualificati bobina/contatti K1901, rail, VCEsat effettiva, tempi di rilascio, clamp e analisi fail-safe. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO**.

## 16/11/2026 — 36 stati guasto transistor e doppio consenso (logica, non hardware)

Il precedente controllo tautologico dei quattro comandi è sostituito da una matrice di **36 casi**: AUDIO_ENABLE × POWER_GOOD (4), Q1911 (normal/stuck_on/stuck_off) e Q1912 (normal/stuck_on/stuck_off). Modello di due interruttori in serie ideali, dopo la verifica dei pin C1/B2/E3 della netlist KiCad9: **5 casi** eccitano la bobina senza entrambi i consensi e **5 casi** impediscono l'eccitazione pur avendo entrambi i consensi. Il marker native PASS_FRONT_DUAL_NPN_36_FAULT_STATES_EXPOSE_UNSAFE_ENERGIZATION_NONFAB documenta l'assenza di immunità al guasto stuck-ON, non un rilascio fail-safe. Inalterati schema, ERC, 8 reti, DC 48 e RL 216. Esclusi bobina aperta/corta, NO saldato, AF_GND aperta, rail transitori, tempi meccanici e guasti correlati. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## 16/11/2026 — correzione KiCad reale R1913: shunt base-emettitore di Q1911

**Modifica elettrica intenzionale**: la terminazione R1913/2, prima su DRIVER_GND, è spostata nello schema nativo alla rete SERIES_MID, che coincide con emettitore Q1911/3 e collettore Q1912/1. R1913 da 10 kΩ diventa quindi uno shunt effettivo **base-emettitore Q1911**; R1914 resta base-emettitore Q1912 a massa. Con Q1912 disattivato, il nodo SERIES_MID può fluttuare: il vecchio pull-down a massa non fissava VBE di Q1911 e non era corretto chiamarlo shunt base-emettitore. Questa correzione controlla la differenza B-E statica nel modello resistivo, **non** prova comportamento su transienti, ESD, brownout, guasti BJT o copertura fail-safe. La verifica netlist nativa richiede R1913/2 univocamente in SERIES_MID e l'assenza da DRIVER_GND. Screen DC 48 casi e Omron OEM aggiornati: corrente resistiva R1913 = VBE/10 kΩ, anziché (VBE+VCEsat)/10 kΩ; i valori di VBE/VCEsat restano assunti, non garantiti da onsemi. Rieseguire FAST/FULL/Required sul branch definitivo; non trasferire al PCB FRONT senza qualificare relè, rail e ritorni. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
