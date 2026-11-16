# V2.7 — banco THT Q806 con doppio Zener a bassa corrente Microchip 1N4106-1

**16 novembre 2026 — candidato KiCad9 NON qualificato; divieto assoluto FAB/TX/BATTERIA/VEICOLO.**

## Modifica materiale verificabile

Schematic separato `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_LOW_CURRENT_ZENER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_LOW_CURRENT_ZENER_LAB_V2_7_DRAFT.kicad_sch`, derivato dal banco THT dual Zener D2101/D2102 PR #305 senza alcuna modifica al master MAIN V2.6 o FRONT.

**D2101 e D2102** sono entrambi cambiati da 1N4742A DO-41 a candidato OEM **Microchip 1N4106-1, 12V, 500mW, ±5%, assiale THT DO-35 (DO-204AH)**, con impronta generica KiCad `Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal` provvisoria e da confrontare con disegno meccanico OEM prima di ordinare. Catodo pin1 di entrambi al `FLOATING_COMMON_SOURCE_LAB`, anodo pin2 al `COMMON_GATE_LAB`. R2101 47k, R2102 10k, Q804/Q805 IRF9540N e Q806 KSP42BU con R2103/R2104 rimangono sul banco. Attenersi al rapporto originale: le alette TO-220 non isolate costituiscono un possibile cortocircuito fra drain.

## Fonti OEM

- <https://www.microchip.com/en-us/product/1n4106-1-zener-diode>: il produttore indica **Status: In Production**, THT DO-35, 12 V, 500 mW ±5%. Verificato come candidato il 16-11-2026, non sufficiente da solo per una BOM finale.
- <https://ww1.microchip.com/downloads/aemDocuments/documents/HRDS/ProductDocuments/DataSheets/1N4614-1-1N4627e3%2B%2C1N4099-1_1N4135-1_e3.pdf>: famiglia assiale `1N4099-1 … 1N4135-1`. Per **1N4106-1** 12 V nominali a **IZT=250µA**, max impedenza di prova **ZZT=200Ω a IZT**. Diversamente dal vecchio onsemi 1N4742A caratterizzato a IZT=21mA. **ZZT massimo al solo IZT non garantisce una curva globale I/V, neppure una tensione-clamp certa fino a 5mA**. Temperatura/tolleranze/limiti meccanici richiedono dati OEM completi.

## Gate tecnici implementati

`03_Verifiche/V2.7/verify_q806_microchip_1n4106_low_current_native.py`, registrato in FULL, richiede **KiCad9 ERC 0 errori/warning e netlist reale 27 pin su 8 reti esatte** con verifica d'orientamento D2101/D2102, package simbolico e imprint THT. Esegue **1.944 casi matematici sintetici** su Vsource 0–48V, R ±5%, Vz ipotetico 11/12/13V, resistenza dinamica fittizia 0,1/1/10Ω, due Zener sani / singolo OPEN / doppio OPEN. Inoltre confronta il margine corrente disponibile con la soglia di caratterizzazione OEM 250µA, senza dedurre da ciò una curva vendor valida in ogni condizione.

La minima corrente disponibile è **zero** in molte condizioni di basso source, e quindi non c'è garanzia della caduta Zener a 250µA ovunque. In corrispondenza del rischio sintetico `|VGS|>20V` a clamp aperto, i rapporti fra R2101/R2102 e la corrente disponibile a una ipotetica Vz massima 12,6V permettono un confronto a 250µA: **non è una dimostrazione di tenuta a VGS**, specialmente per tolleranze termiche, corrente condivisa, guasto dei due componenti, comportamento dinamico del source fluttuante, reverse bias/EMC o corti driver.

**Bloccanti irrisolti**: supervisore indipendente e supply, protezione fail-safe da Q806 C–E SHORT, comportamento non ideale dei MOSFET, corrente di sharing twin-Zener, validazione PVT/surge/ESD/RFI, dissipazione reale e footprint/pad validati, effettiva interruzione primario-secondario, prove di laboratorio e PCB reale. ERC0 del banco non sblocca hardware, fabbricazione, TX o alimentazione con VIN48V.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
