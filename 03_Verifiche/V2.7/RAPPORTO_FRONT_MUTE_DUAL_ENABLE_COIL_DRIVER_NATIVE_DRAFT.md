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
