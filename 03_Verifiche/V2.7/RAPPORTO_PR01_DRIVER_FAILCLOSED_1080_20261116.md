# V2.7 — R2102 PR01 THT e guasti hard-sink del driver Q806

16 novembre 2026 — laboratorio **KiCad9 isolato**; test di fault ideali, senza hardware.

## Stato verificato

PR [#308](https://github.com/jd3485/Superstar3900-THT-Evolution/pull/308) MERGED su main SHA `de971b34c2d06279d2aef95dd990c0bda5c058b1`, run [#43847987766](https://github.com/jd3485/Superstar3900-THT-Evolution/actions/runs/43847987766), FAST/FULL/Required 3/3 SUCCESS, ERC KiCad9 0 errori/0 warning; 27 pin, 8 reti, 567 casi termici del PR01 THT. **36 corner** del modello superano il P70 nominale; R2102 resta candidato 10k ±5%, 1W nominale, non qualificato a temperatura estrema.

## Nuova prova distinta

`03_Verifiche/V2.7/verify_r2102_pr01_driver_fault_native.py` usa la vera netlist KiCad9 dello schematico `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_PR01_R2102/MAIN_SECONDARY_OVP_Q804_Q805_Q806_PR01_R2102_LAB_V2_7_DRAFT.kicad_sch`. Impone **27 pin/8 reti** esatte e percorre **1.080 corner**: source imposto 0/13,8/20/24/36/48V, R2101 44,65/47/49,35kΩ, R2102 9,5/10/10,5kΩ, Zener sani/aperti singolarmente o entrambi, stato driver Q806 sano disabilitato, abilitato, **C–E short**, R2102 **open** e **short**. Calcola un modello *unclamped* con pull-up source→gate e sink idealizzato, non la curva OEM Microchip 1N4106-1 né il source flottante dinamico.

Con **Q806 C–E corto** può esservi tensione gate-source sufficiente per ON anche se ENABLE è a zero: **non è fail-closed**. R2102 OPEN con R2101 sano porta OFF solo nel modello; R2102 SHORT aggira la limitazione di corrente di pilotaggio e non autorizza claim del clamp, soprattutto in doppio-open. La potenza di R2102 e il rating 1W non risolvono la dipendenza da Q806, la supervisione OVP/UVLO autonoma o la sicurezza del rail. Il programma stampa test **NONFAB**, esplicitando `driver_hardware_fail_closed: False`.

## Rischio architetturale e prossimo passo

La sola modifica di un resistore o di due Zener è una protezione **incompleta**. Progettare un supervisore indipendente OEM con propria alimentazione sicura, controllo UVLO+OVP e almeno due possibilità di disconnessione in serie che rimangano OFF durante fault singoli del driver. Occorrono review pinout/componenti THT, PVT e corrente di guasto, sezionamento power path, body diode e clamp reali, TVS, reset, prova di indipendenza e misure su banco prima di MAIN. Restano vietate fabbricazione, TX, alimentazione a 48V, batterie e veicoli. Issue #27 aperta.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
