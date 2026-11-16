# V2.7 — banco THT Q804/Q805 anti-serie con gate driver Q806 KSP42BU 300 V

**16 novembre 2026 — KiCad9 isolato, non un supervisore OVP/UVLO e NON autorizzato per l'alimentazione hardware.** Il master MAIN V2.6, la PCB FRONT e tutti i file storici restano invariati.

## Modifiche reali e interfaccia di abilitazione

Schematic nativo `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_DRIVER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_NPN_LAB_V2_7_DRAFT.kicad_sch`. Q804/Q805 Infineon IRF9540NPBF P-MOS TO-220 con source in comune, drain esterni separati, R2101 47k source→gate (default OFF ideale), D2101 1N4742A nominale 12 V clamp source–gate, R2102 10k serie dal sink al gate. Qualifica magnetica/RF/termica/isolamento tabs TO-220 non eseguita.

- **Q806**: candidato onsemi **KSP42BU**, NPN TO-92 CASE 135AN **pin1 emitter** su `LAB_RETURN_ONLY`, **pin2 base** su `Q806_BASE_LAB`, **pin3 collector** su `DRIVER_SINK_LAB`, connesso a gate P-MOS *solo attraverso R2102*. Sostituisce preliminare **2N3904BU VCEO 40V**, scartato per margine insufficiente nello scenario fault VIN48V.
- **R2103** 4,7k dal connettore `J2103/1 ENABLE_LOGIC_5V_LAB` a Q806/2; **R2104** 100k fra Q806/2 e `LAB_RETURN_ONLY`. `J2103/2` ritorno. Il segnale ENABLE è **solo un ingresso di laboratorio**: non esiste ancora comparatore indipendente, reset qualificato, alimentazione monitorata né gate controllabile per guasti; non alimentare J2103.
- Source comune Q804/Q805 **non** è LAB_RETURN; tab metallico dei due TO-220 è **drain**: dissipatore comune senza isolamento corto-circuita l'ingresso verso l'uscita. Tutte le impronte sono **candidate THT**; R, Zener, connettori e geometrie non qualificati.

## Fonte OEM 16 novembre 2026 — candidate production audit

onsemi [KSP42/KSP43 Rev. 4 gennaio 2025](https://www.onsemi.com/pdf/datasheet/ksp43-d.pdf): KSP42BU TO-92 CASE135AN **E1/B2/C3**, **VCEO 300V**, VCBO 300V, VEBO 6V, IC 500mA, PC 625mW a 25°C. Le tabelle OEM elencano KSP42BU senza nota discontinued (**KSP43BU** è indicato discontinuato). [DigiKey KSP42BU](https://www.digikey.it/it/products/detail/onsemi/KSP42BU/1048030) attualmente riporta Active, ma servono comunque conferma diretta OEM e verifica del lead spacing/footprint prima della BOM definitiva. Per KSP42 VCE(sat) ≤0,5V è specificato **solo a IC=20mA, IB=2mA**; non estrapolare la saturazione a correnti, temperature o tensioni non coperte. Non confondere con onsemi **MPSA42G**, riportato obsoleto dal distributore.

## Verifiche e limiti espliciti

`03_Verifiche/V2.7/verify_ovp_q806_gate_driver_native.py` è registrato nella FULL: esige **ERC KiCad9 zero errori/zero warning** su schematico reale e confronto esatto degli **8 gruppi net** per **25 pin**, inclusi tutti i terminali E/B/C. Il test ideale esplora **7290** combinazioni ipotetiche (VIN0..48V, VBE0,65..0,95V, R a ±5%, caduta body diode 0,2/0,5/0,9V), con indipendenza dei terminali del gate, return e source; nessuna curva vendor SPICE o misura di banco.

- Per 5V ENABLE ipotetico, `IB = (5−VBE)/R2103 − VBE/R2104` predice ~0,81–0,97mA, senza dimostrare effettiva saturazione PVT di KSP42BU o gli effetti di transitori.
- Con Q806 OFF e source comune innalzato da body diode del PMOS a ipotetico VIN48V, collettore ideale può arrivare a ~47,8V. **2N3904BU 40V sarebbe sovrastressato**; **KSP42BU VCEO300V non supera quel limite specifico negli scenari statici definiti**, ma non c'è qualifica contro surge, SOA, isolamento, leakage, VBE reverse o bias del supervisore.
- **Guasto Zener D2101 OPEN:** Q806 ideale ON porterebbe `|VGS|≈VIN×R2101/(R2101+R2102)`, ~39,58V a 48V nominali, **oltre limite assoluto ±20V dei P-MOS**: il passaggio a KSP42BU NON risolve questo guasto.
- Con Q804 oppure Q805 corto D-S, l'altro body diode può alimentare l'uscita da uno dei due lati; il solo grafo anti-serie integro non assicura contenimento singolo guasto.
- L'analisi delle resistenze/correnti, dissipazione di Q806/R2102/D2101, timing ON/OFF, temperature, reverse polarity, riferimenti di tensione e compatibilità elettromagnetica rimane incompleta.

**Gate successivi:** vero supervisore indipendente con supply protetta da guasti primari e brownout, limitazione VGS a due fault, qualifiche OEM e footprints/pin-pad/tabs, simulazioni vendor, prove limitate e review indipendente prima di qualsiasi integrazione nel master, PCB e fabbricazione. Issue #27 resta aperta. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
