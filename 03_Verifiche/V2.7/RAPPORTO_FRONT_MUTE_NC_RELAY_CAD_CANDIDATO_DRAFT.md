# V2.7 — Contatto mute NC normalmente a massa, candidato KiCad9 THT isolato

**15 novembre 2026 · sperimentale · nessuna qualifica OEM / sicurezza prodotto**

## Perché

PR #257 ha identificato il guasto terminale basso del volume `RV1301/3`:
a volume nominale 1% l'amplificatore potrebbe vedere una tensione
normalizzata di 0,714219 invece di 0,008192 (modello passivo 1 kHz).
La PR #259 ha dimostrato che una resistenza di bypass abbassa
necessariamente il volume massimo sano. La mitigazione candidata deve
separare la disponibilità audio dal semplice elemento regolatore.

## CAD reale isolato

Nuovo file nativo editabile:
`04_KiCad/V2.7_DRAFT/FRONT_MUTE_NC_RELAY/FRONT_NC_MUTE_CONTACT_THT_V2_7_DRAFT.kicad_sch`.

Contiene quattro simboli/oggetti reali: `K1901` relay SPDT candidato THT
5 pin (nessun footprint assegnato), J1901 ingresso audio e AF_GND
dal potenziometro, J1902 uscita verso LM386 e AF_GND,
J1903 alimentazione bobina **LAB non qualificata**.
Pin/partizioni attese:
- K1901 pin1 COM → J1902/1 (`AMP_INPUT_MUTED`);
- K1901 pin2 NC → J1901/2, J1902/2 (`AF_GND`);
- K1901 pin3 NO → J1901/1 (`VOL_WIPER_TO_AMP`);
- K1901 pin4 bobina + → J1903/1 (`COIL_PLUS_LAB`);
- K1901 pin5 bobina − → J1903/2 (`COIL_MINUS_LAB`).

**Nell'ipotesi fisica del contatto reale**, la bobina non eccitata
collega ingresso amplificatore a massa sul contatto NC: silenziamento
per assenza di alimentazione di controllo e durante startup,
**solo se il contatto NC e AF_GND sono realmente integri**.
Il segnale può attraversare il contatto NO soltanto se un futuro
driver eccita volontariamente la bobina con power-good valido.
Un relay SPDT THT con bobina reale, geometria e produttore non è
stato ancora selezionato: non esiste garanzia di comportamento fisico
sulla base della sola rappresentazione CAD.

## Verifica obbligatoria

`03_Verifiche/V2.7/verify_front_nc_relay_contact_native.py` deve
eseguire KiCad9 ERC nativo, esportazione di netlist KiCad9 dei tre
schematici FRONT volume / candidato mute / MAIN LM386, controllo
**esatto** delle cinque reti senza collegamento accidentale tra
massa/circuito bobina/segnale, e conservazione della PCB NONFAB
13 THT, 28 pad, 12 net, 35 piste, che **non contiene K1901**.
Il test viene aggiunto alla FULL CI e non concede waiver ERC.

## Blocchi progettuali espliciti

1. MPN relay OEM **ancora prodotto** con contatto adatto al **livello
   minimo di segnale audio** e resistenza/ossidazione/bounce verificati;
   carico minimo di contatto, tensione bobina, potenza termica,
   ritenuta/rilascio e vibrazioni da datasheet OEM.
2. Driver THT con protezione bobina, alimentazione limitata e
   supervisor/power-good fail-closed, verifica guasti rail, transistor,
   comando bloccato HIGH, massa e coil open/short.
3. Il guasto `AF_GND` esterno, contatto NC ossidato/aperto/saldato,
   cablaggio errato o bobina permanentemente eccitata **non è mitigato**
   da questa versione; impossibile parlare di fail-safe a guasto singolo.
4. L'ERC **non** verifica che NC sia realmente chiuso meccanicamente
   quando la bobina è spenta; servono datasheet, revisione
   indipendente e misure. L'input LM386 in lavoro resta isolato
   dal FRONT schematico principale: nessuna integrazione hardware.
5. Nessuna scheda fabbricabile, DRC o qualifica audio/RF/veicolare.

**Stato:** candidato di topologia del contatto; **non approvato
come circuito di sicurezza**. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.
