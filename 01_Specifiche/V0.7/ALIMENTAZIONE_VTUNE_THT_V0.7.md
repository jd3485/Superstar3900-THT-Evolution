# V0.7 — Sorgente VTUNE THT da 13,8 V: boost + regolatore lineare, dimensionamento iniziale

**Data:** 10/11/2026. **Vincoli:** scheda 100% THT; no TX, no ordine PCB. **Non è un circuito certificato**: nessun modello di MC34063ABN o LM317 realmente eseguito, nessuna validazione del rumore RF, schema KiCad non completato.

## 1. Dipendenza funzionale risolta a livello di topologia

Il VCO candidata B V0.6 ha richiesto **VTUNE 8–15V** per coprire LO 36,310–39,000 MHz in 5 punti del modello ngspice con accensione VCC da zero. La radio è alimentata a circa 13,8V nominali e non può ricavare 15V con soltanto un LDO. La soluzione di studio V0.7 separa:
```text
13,8V nominali -> protezione/filtraggio ingresso (NON PROGETTATI)
                    -> U701 MC34063ABN DIP-8 boost a ~24V (candidato)
                    -> U702 LM317T TO-220 regolatore a ~18,3V
                    -> R712 10ohm / C712 100uF RC di isolamento
                    -> +18V_VTUNE_FILTERED / futuro driver analogico
                           -> VTUNE 8-15V, powergood/mute ancora da implementare
RF-VCO Q501/Q502: rail +5V RF SEPARATA; il boost NON deve alimentare direttamente il tank.
```
Tutti i componenti elencati sono THT, compresi regolatori, diodo, bobina, condensatori e resistenze. **MC34063 è uno switching regulator, non un sintetizzatore PLL moderno**: non reintroduce nessuna delle funzioni escluse. La sua commutazione è però una **potenziale fonte di interferenze** in ricezione, da misurare e contenere.

## 2. Componenti candidati e nodi (NON schematico definitivo)

**U701 ST MC34063ABN**, DIP-8, ordinabile come versione THT dichiarata *Active / volume production* dal produttore. Fonte: https://www.st.com/en/power-management/mc34063ab.html e https://www.st.com/resource/en/datasheet/mc34063eb.pdf
**U702 TI LM317**, TO-220, piedinatura 1 ADJUST, 2 OUTPUT e tab metallico in uscita, 3 INPUT secondo datasheet TI; **tab non è GND**, prevedere isolamento se accoppiato al telaio. Fonte: https://www.ti.com/product/LM317
**D701 1N5819**, DO-41 assiale 1A/40V, anodo `SW_NODE`, catodo `VBOOST24`; fonte: https://www.st.com/resource/en/datasheet/1n5819.pdf

**Rete di studio**:
- U701 pin1 SW_NODE, pin2 GND, pin3 CT_NODE, pin4 GND, pin5 BOOST_FB, pin6 VIN_FILT, pin7 VIN_SENSE, pin8 VIN_FILT. Pin7 campiona VIN oltre R701=1Ω; L701=470uH (radiale/assiale THT candidato, I_sat e SRF **da scegliere**) tra VIN_SENSE e SW_NODE. D701 SW_NODE→VBOOST24.
- `R702=21,8kΩ` da VBOOST24 a BOOST_FB; `R703=1,2kΩ` da BOOST_FB a GND. `C702=470pF` da CT_NODE a GND è un **candidato**: f≈40kHz è **un'assunzione progettuale**, NON dimostrata da C702. `C701=47uF/35V` VBOOST24→GND. `C700=47uF/25V` VIN_FILT→GND e 100nF ceramico THT di bypass.
- LM317: input pin3 VBOOST24, output pin2 VREG18_RAW, adjust pin1 ADJ18. `R710=240Ω` VREG18_RAW→ADJ18, `R711=3,24kΩ` ADJ18→GND; un `C711=10uF/25V` su ADJ18 è candidato per migliorare PSRR e richiede diodi di protezione al regolatore secondo datasheet. `C710=10uF/35V` sull'ingresso, `C713=10uF/25V` sull'uscita. La topologia delle protezioni LM317 non è ancora chiusa.
- `R712=10Ω` VREG18_RAW→VANA18_FILT; `C712=100uF/25V` VANA18_FILT→GND. RC isolato verso il futuro circuito del filtro PLL/driver. Va verificata la stabilità del regolatore con i condensatori e l'ondulazione effettiva.

La tabella `04_KiCad/V0.7/VTUNE_ALIMENTAZIONE_PINNET_V0.7.csv` mappa **11/11 pin** dei due IC con i nomi delle reti. `04_KiCad/V0.7/VTUNE_PASSIVI_NETS_V0.7.csv` descrive connessioni candidate R/L/C/D; **non è una netlist KiCad valida o uno schematico finale**.

## 3. Dimensionamento preliminare e ipotesi esplicite

Parametri assunti da verificare sulla radio reale: VIN protetta **11–15,5V**, Vboost≈24V, carico di studio 15mA massimo, f_switch **40kHz** ipotizzata, Vsat switch1V, Vf diode0,5V, L470uH, Rsc1Ω, soglia di sense tipica circa0,33V. Il circuito MC34063 effettivo può saturare, saltare impulsi e operare in diversi regimi: non affermare che siano valori di produzione.

Da formule datasheet boost, a VIN=11V:
- (t_{on}/t_{off}=(24+0.5-11)/(11-1)=1.35), duty ideale ≈57,45% (contro max 80% nominale IC);
- a40kHz, `ton≈14,36us`, `toff≈10,64us`;
- incremento corrente ideale in induttore da zero durante ON (ΔI≈(11-1)*14.36us/470uH≈0.306A). Soglia corrente da `Rsc=1Ω`: ~0,33A **tipica**, margine minimo appena 0,024A! In CCM la corrente di picco è superiore al ΔI, quindi il limitatore potrebbe intervenire. **BOCCIARE L/Rsc come chiusi per PCB finché non si simulano i modelli IC e worst case.**
- riferimenti boost (senza compensazione, ripple e carico): `Vboost≈1,25*(1+21,8k/1,2k)=23,958V`. Con ±2% riferimento e ±1% resistori il semplice valore statico è ≈23,0385–24,9054V (calcolo esatto nel codice), **non una garanzia dell'alimentatore fisico**.

LM317 con R710=240Ω, R711=3,24kΩ e I_ADJ assunta 50µA → `VREG18_RAW≈18,287V`. Per Vref 1,2–1,3V e Iadj 0–100µA (gamma di studio, NON tolleranza qualificata) → **17,4–19,174V**. Headroom nominale boost→LDO ~5,67V; al worst-case combinato teorico rimane margine da verificare considerando dropout, ripple e discontinuità di rete.

RC 10Ω/100µF: polo ≈159,15Hz; attenuazione **idealizzata e non caricata** a 40kHz di circa **−48dB**; a carico15mA la caduta statica è 0,15V. Il filtraggio **non garantisce** di cancellare spurie / armoniche / modulazione della fase RF, né dimostra un convertitore silenzioso. Il layout di potenza deve mantenere il loop di switching lontano da VCO, preselettore RX, FI e PLL.

## 4. Driver VTUNE rimane APERTO

L'alimentatore rende **possibile in principio** una linea di servizio >15V. **Non genera ancora VTUNE**: serve un driver analogico THT che traduca l'uscita effettiva del phase detector U401 (da confermare su datasheet) in una tensione controllabile con sufficiente range, basso rumore e stabilità in anello. `LM358N` DIP-8 è solo candidato: un'uscita high-side assunta VCC−2V offre margine limitato. Con valori pessimistici, Vreg_min17,4V−0,15V RC−2V=15,25V; se headroom fosse 3V, **14,25V (FAIL)**. Perciò non è stata approvata alcuna connessione a VTUNE, alcuna banda di loop/phase margin, e l'abilitazione RX deve restare fail-closed senza POWER_GOOD e PLL_LOCK hardwired verificati.

Sarebbe preferibile ridurre il fabbisogno massimo di VTUNE del VCO e/o aumentare il margine regolato, dopo simulazioni con componenti reali e le condizioni di alimentazione vere. In ingresso protezione inversione, TVS, fusibile e riferimenti massa RF rimangono aperti.

## 5. Simulazioni eseguite e limiti

Il deck `03_Verifiche/V0.7/BOOST_THT_BEHAVIORAL_V0.7.cir` usa un interruttore comandato idealmente e un comparatore ideale: **non è il macromodello di MC34063**, non include regolatore LM317, livelli EMI, efficacia della protezione, saturazione della bobina o switching jitter. Run GitHub Actions `boost_v07.yml` ripete 3 transienti a Vin11/13,8/15,5V con Iload15mA nominali e registra valori medi/min/max. **I valori ~24V dimostrano solamente la coerenza di un'astrazione**, non prestazioni di fabbricazione.

### Gate aperti
- Sourcing reale U701/U702, C e L THT; **L 470uH Isat≥0,5A e resistenza DC / SRF da documentare**.
- Dispositivo MC34063 transitorio vero con timing datasheet e Ipk, regolazione a VIN/Iout/temp, condensatori ESR e overshoot, protezioni input.
- Linea regolata LM317 realistica, ripple switching sul VCO, segnali powergood e mute, rail Vtune e phase detector, hardware TX lock.
- Schemi KiCad nativi completi, footprint certificati, ERC/DRC, layout separazione massa/EMI, prove di banco e revisione PCBWay.

**Non ordinare componenti per produzione né inviare PCBWay; NO FAB / NO TX.**
