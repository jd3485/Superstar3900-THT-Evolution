# V2.7 — Primo schema KiCad9 THT LM2903P PDIP8 finestra UVLO/OVP

16 novembre 2026 — **BANCO ISOLATO PRE-SUPERVISORE, NON QUALIFICATO**.

## CAD effettivo e connessioni

Progetto: `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_LM2903P_WINDOW/MAIN_SECONDARY_LM2903P_WINDOW_LAB_V2_7_DRAFT.kicad_sch` con lib simboli locale, tabella e progetto KiCad9. Il nuovo **U2201 TI LM2903P PDIP8** (candidato, footprint `Package_DIP:DIP-8_W7.62mm`) ha 8 pin reali: 1 OC OUT1; 2 IN1−; 3 IN1+; 4 GND; 5 IN2+; 6 IN2−; 7 OC OUT2; 8 VCC. **Non sono shortate le due uscite separatamente comandate** ma *wired-OR* sul nodo `WINDOW_GOOD_OC_BIASED_LAB`: con pullup R2207 10k al rail 5V esterno, ciascuna può tirare basso per fault di finestra. La qualità della segnalazione, il default sicuro e l'interpretazione delle polarità non sono garantiti: una perdita 5V spegne il pullup, ma senza controllo hardware del driver tale nodo non è un interlock.

Componenti THT reali collocati nel banco:
- `R2201=100k` VIN_RAW→VIN_SENSE, `R2202=5k` VIN_SENSE→RETURN (ingressi U2201 pin3 e pin6).
- `R2203=50k` VREF_2V5 esterno→OVP_REF, `R2204=20k` OVP_REF→RETURN (pin5).
- `R2205=85k` VREF_2V5 esterno→UVLO_REF, `R2206=20k` UVLO_REF→RETURN (pin2).
- `R2207=10k` VCC5V esterno→OUT1+OUT2 (pin1/pin7).
- `J2201..J2204` connettori a 2 poli THT VIN/RETURN, 5V/RETURN, VREF/RETURN, finestra/RETURN. I rail di 5V e 2,5V sono **forniture ipotetiche ESTERNE**, non generatori progettati o qualificati.

`03_Verifiche/V2.7/verify_lm2903p_pdip8_window_native.py` incluso in FULL richiede ERC KiCad9 nativa, **30 pin reali/8 reti**, verifica pin numerici dell'LM2903P e componenti del partitore, 128 casi PVT sintetici per soglie UVLO e OVP. Non esiste alcuna PCB e dunque nessun DRC PCB.

## Correzione ERC sullo schematico reale

La prima esecuzione native KiCad9 della PR #311 (run #43853071247) ha correttamente **FALLITO**: 2 errori `power_pin_not_driven` su U2201 VCC/GND, 9 warning `endpoint_off_grid` sulle connessioni U2201. Risoluzione progettuale nel banco (da ricontrollare in nuova CI): spostata la singola istanza U2201 e tutte le connessioni della finestra su griglia 2,54 mm; definito su J2202 un simbolo locale distinto `BENCH_SUPPLY_PORT_THT_2PIN` con pin di uscita di potenza **che rappresentano esplicitamente una sorgente esterna su connettore fisico**, sia VCC5V che RETURN. Non è un `PWR_FLAG` o un'alimentazione reale progettata: il simulatore/ERC vede solo il contratto formale della sorgente esterna presunta. **Non affermare supply qualificata, indipendenza dal MAIN, protezione rail o sicurezza**. Nessun waiver, nessuna esclusione delle violazioni ERC.

## Limite fisico immediato — critical input fault

Se R2202 si apre, U2201 pin3/pin6 possono salire al valore VIN_raw ipotetico fino a **48V**, nonostante Vsense nominale a VIN48V sia ~2,286V. Non vi sono attualmente diodi di clamp ingresso, limitatori di corrente indipendenti, TVS/transient protection, hysteresis, né power-good sulla supply. **NON alimentare questo schema**, non connetterlo all'interruttore secondario né considerarlo protezione OVP funzionante. La mancanza di rail indipendente è esplicita.

Per la prossima revisione: sviluppare rete di protezione del pin anche con R2201/R2202 OPEN/SHORT e VCC/reference assenti, gate vero indipendente non bypassabile da Q806 C–E corto, componenti OEM THT con package/footprint verificati e prove PVT reali. Il source 48V è soltanto una variabile di guasto di laboratorio, **non un VIN consentito**.

Fonti OEM: <https://www.ti.com/product/LM2903/part-details/LM2903P> e <https://www.ti.com/lit/ds/symlink/lm2903.pdf>. Necessaria verifica finale della disponibilità e MPN esatto.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
