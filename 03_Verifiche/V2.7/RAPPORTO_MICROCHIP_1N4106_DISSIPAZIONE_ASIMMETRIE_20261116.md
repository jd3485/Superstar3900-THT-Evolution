# V2.7 — 1N4106-1 THT: Zener dissimili, stress termico e R2102

16 novembre 2026 — **screen analitico NON modello I/V del produttore, NON sicurezza elettrica qualificata**.

## Perimetro

La regressione `03_Verifiche/V2.7/verify_microchip_twin_zener_thermal_fault_native.py`, registrata in FULL, esporta la netlist KiCad9 del banco isolato `MAIN_SECONDARY_OVP_Q804_Q805_Q806_LOW_CURRENT_ZENER`, PR #306 già integrata. Esige 27 pin fisici in 8 reti e catodi D2101/D2102 sul source comune flottante, anodi sul gate comune. **Non altera nessuno schematico MAIN o FRONT.**

Lo script attraversa 7.680 combinazioni matematiche con: source imposto 0, 13,8, 20, 24, 36, 48 V; R2101 44,65/49,35 kΩ; R2102 9,5/10,5 kΩ; **due Zener indipendenti** Vz sintetico 11,4/12,6V, resistenza dinamica sintetica 0,1/10Ω per ogni ramo; temperatura -40, 25, 85, 125°C; stati entrambi sani, D2101 aperto, D2102 aperto, entrambi aperti, D2101 in corto. Il solutore di bisezione KCL modella il gate ma **non risolve il source realmente flottante, i transitori o l'I/V vendor**. Il modello mostrerà la distribuzione asimmetrica di corrente, ma non ne garantisce alcuna ripartizione fisica.

## Limiti OEM Microchip che lo script conserva come limiti di interpretazione

Fonti OEM: [pagina Microchip 1N4106-1 In Production](https://www.microchip.com/en-us/product/1n4106-1-zener-diode) e [datasheet 1N4099-1..1N4135-1](https://ww1.microchip.com/downloads/aemDocuments/documents/HRDS/ProductDocuments/DataSheets/1N4614-1-1n4627e3%2B%2C1N4099-1_1N4135-1_e3.pdf).

- 1N4106-1 nominale 12V a **IZT=250 µA**, ZZT massimo **200Ω misurato a IZT**, IZM max **32mA** a condizioni dichiarate, max potenza **500mW** a 25°C e decrescente verso zero a 175°C. Coefficiente termico massimo del valore Zener **+0,080%/°C** misurato nel campo OEM, non una curva I/V garantita.
- Lo script confronta il valore di rating Zener, ma **non lo estende impropriamente** a correnti inferiori a 250 µA, a qualunque coppia di componenti in parallelo o in presenza di surge. L'equazione linearizzata di corrente (`max(0,(Vgs−Vz)/Rz)`) resta interamente sintetica.
- **R2102 è una resistenza THT generica non ancora qualificata OEM**. Con source ipotetico 48V, corto dello Zener e R2102 al minimo **9,5kΩ**, dissipazione teorica `48²/9500 ≈ 0,24253W`. Una resistenza commerciale da 0,25W avrebbe margine nominale minimo e potrebbe essere sovraccaricata a temperatura elevata, senza che la footprint DIN0207 garantisca un rating. È un **finding obbligatorio** per dimensionamento e derating; nessun rating R2102 è stato approvato.
- Lo Zener a 125°C secondo il modello lineare di derating **0,5W×(175−125)/150 ≈0,1667W**, utilizzabile unicamente come limite statico nominale per l'esame di rischio, non per dissipazione transitoria o ambiente misurato.
- Un solo ramo D2101/D2102 in corto impone nel modello `Vgs≈0`, disabilitando idealmente il MOSFET; non soddisfa da sé funzionalità, tempi, rilevamento del guasto e degradazione. **Entrambi aperti** eliminano il clamp, e Q806 in corto C–E può comandare ON senza ENABLE, non mitigato dagli Zener paralleli.

## Gate aperti

Serve qualificare una tipologia concreta di R2102 che tolleri PVT e fault con margine, full current Zener I/V e temperatura, 1N4106-1 footprint/meccanica DO-35, condivisione non garantita, supervisore autonomo OVP/UVLO alimentato in sicurezza, isolamento alette TO-220, review di indipendenza, PCB reale e misure. Il master MAIN V2.6 resta parziale e non si autorizzano 48V, batterie, veicoli, fabbricazione o TX.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
