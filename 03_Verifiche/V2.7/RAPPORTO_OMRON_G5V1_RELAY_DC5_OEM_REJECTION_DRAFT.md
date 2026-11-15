# V2.7 — Screen OEM Omron G5V-1 DC5: candidato NON qualificabile sul driver attuale

**15 novembre 2026 · valutazione OEM vera, NON integrazione prodotto**

## Fonti primarie

* [G5V-1 OEM ufficiale datasheet K048-E1, pagine 1–2](https://components.omron.com/eu-en/system/files/2023-01/datasheet_pdf/K048-E1.pdf), consultato e disegno pagina 1 verificato.
* [Scheda prodotto ufficiale G5V-1](https://www.aratas.com/eu-en/products/relays/G5V-1): famiglia G5V-1 e T90 **in production** al 15/11/2026.

Il modello G5V-1 con bobina **5 VDC** è THT, un polo SPDT,
sigillato, contatto Ag legato Au; OEM bobina **167 Ω ±10% a 23°C**,
**30 mA nominali**, 150 mW. Must-operate **≤80%** della tensione
nominale a 23°C; il datasheet cita il valore di riferimento
failure-rate contatto **1 mA a 5 VDC** (con condizioni proprie).
Non si può quindi dedurre adeguatezza ai **µV/µA** di un AF non ancora
misurato. **L'esistenza OEM e l'offerta in produzione non approvano
l'impiego in radio**.

## Incompatibilità con il progetto mute DRAFT

La PR #264 ha creato driver vero ma astratto: due NPN in serie
controllati da audio-enable e power-good LAB, Rbase 1,5 kΩ,
Rpull 10 kΩ, rail lab nominale 5 V. Il suo screening
**48 casi** aveva assunto **bobine 250–1000 Ω**. Il G5V-1 DC5 a
167 Ω è **FUORI da tale finestra**: non trasferire la qualifica.

Nuovo gate `verify_front_omron_g5v1_oem_relay_rejection_screen_native.py`
verifica netlist pin-nodo J1914/J1903 e calcola **36 condizioni**
(rail 4,5/5/5,5 V × input 4,5/5 V × resistenza bobina
150,3/167/183,7 Ω × VCEsat candidato 0,15/0,30 V).
Il calcolo DC ipotizza VBE 0,8V e forced beta 10 su ciascun NPN:
`Icoil=(rail-2·VCEsat)/Rcoil`, corrente base del superiore
con emettitore rialzato e due pull-down. Se la corrente disponibile
è inferiore a Icoil/10, **la saturazione non è dimostrata**.
Se la tensione bobina scende sotto 4 V (= 80% nominale OEM
a 23°C), **il pickup non è garantito**; non interpreta questo valore
come test automatico di rilascio. Le bande VCEsat/VBE non sono
garantite da un produttore NPN e la corrente reale AF è ignota.

Le risposte sono **esiti di un filtro di esclusione del candidato**,
non verifica PVT completa, DC vendor model, misure o certificazione:
una CI verde significa che il test ha *individuato* casi
insoddisfacenti previsti. **Non assegnare G5V-1 DC5** a K1901, né
modificare gli schematici della PR #264 senza riprogettare
base-drive, alimentazione, pickup/brownout e contatti dry audio.

## Prossime verifiche

Confrontare relè THT SPDT con coil più efficiente / tensione
disponibile, contatto affidabile per reali livelli misurati,
pinout e footprint OEM, dropout e flyback con rilascio più rapido,
origine power-good e sicurezza in caso di NO saldato e AF_GND aperto.
I circuiti THT attuali rimangono isolati e il PCB FRONT
13THT/28pad/12net/35 piste non viene modificato.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**

## CI tecnica, correzione di una condizione test

Il primo [run #43764261866](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43764261866) ha **FAST SUCCESS, FULL/Required FAIL**: l'asserzione finale di brownout confrontava per errore 5,0−0,3−0,3=4,4 V con 4,0 V, sebbene il caso che non garantisce pickup sia **rail minimo 4,5−0,3−0,3=3,9 V**. Corretto esclusivamente l'input alla verifica, senza attenuare le soglie o mascherare l'errore. FULL sul successivo HEAD obbligatoria; nessun merge di PR fallita.
