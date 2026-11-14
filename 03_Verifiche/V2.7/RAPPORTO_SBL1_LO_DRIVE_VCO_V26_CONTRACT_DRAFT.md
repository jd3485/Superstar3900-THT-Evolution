# V2.7 — contract LO SBL-1+ vs VCO RX THT V2.6 (non qualificato)
14 novembre 2026. Test nativo in `03_Verifiche/V2.7/verify_sbl1_lo_drive_budget_native.py`, da invocare nella FULL CI.

## OEM e vincoli
Mini-Circuits SBL-1+ originale https://www.minicircuits.com/pdfs/SBL-1%2B.pdf : level 7, **+7 dBm LO nominale**, RF/LO 1–500 MHz, IF DC–500 MHz, pin8=LO; massa pin2/5/6/7; IF pin3 e 4 esternamente connessi, RF pin1. +7 dBm corrispondono a **5,011872 mW** consegnati a un carico 50Ω **puramente resistivo assunto**, 0,500593 Vrms e 1,415893 Vpp **sul carico** per sinusoide. Le impedenze portuali RF/LO del mixer possono variare con frequenza e drive, **non** sono un carico 50Ω esatto garantito.

## Rischio identificato
L'attuale file **reale** `04_KiCad/V2.6/VCO_RX_AND_LOBUF_V2.6.kicad_sch` espone `J523/1 = LO1_ANALOG_OUT` e `J522/1 = LO1_CMOS_BUFFERED` con contatti di ritorno J523/2 e J522/2 su GND. Il nuovo test richiede l'esportazione **KiCad9 nativa** della netlist VCO e mixer, verifica quei quattro pin, l'ingresso mixer `MX1701/8` e i GND, e impedisce che le reti analogica e CMOS siano cortocircuitate. Le due parti sono **standalone**, mai unite elettricamente. Il buffer `U520 SN74AC14N` è logica CMOS: non considerare l'uscita square-wave una sinusoide RF pulita o un generatore +7 dBm con impedenza verificata.

### Sinusoide di Thevenin a 50Ω *ipotetici* (non dati misurati)
Formula sorgente a vuoto: `Vpp_src = 2√2 √(0.001 × 10^(7/10) × 50) × (1+Rs/50)`.
- Rs=0Ω → **1,4159 Vpp** nominali a vuoto, coincidenti col carico ideale.
- Rs=10Ω → **1,6991 Vpp**.
- Rs=25Ω → **2,1238 Vpp**.
- Rs=50Ω → **2,8318 Vpp**.
- Rs=100Ω → **4,2477 Vpp**.
- Rs=200Ω → **7,0795 Vpp**.

Il test calcola anche il valore di potenza consegnata e ne ricostruisce +7dBm, senza modelli di transistor o SPICE vendor. Il carico del mixer reale è complesso/LO-driven, quindi nessuno dei numeri sopra autorizza un interfacciamento diretto.

## Rischi bloccanti
1. Misurare/calcolare `LO1_ANALOG_OUT` e `LO1_CMOS_BUFFERED` della V2.6 su carico RF reale con VCO alimentato in banco protetto: spettro, armoniche, fase/PN, livello disponibile, isolamento, bias, startup e assorbimento. **Non autorizzato hardware al momento**.
2. Progettare una rete RF THT di buffer/amplificazione, filtering e adattamento verso il mixer level7, includendo dissipazione, stabilità, EMC/ground e differenze OEM; non confondere J522 CMOS con driver analogico approvato.
3. Piano di iniezione per riferimento RF=27,000MHz/IF=455kHz: LO alto 27,455MHz o basso 26,545MHz **solo casi numerici**, NON selezione del piano di canale, reiezione d'immagine, copertura VCO PLL o conformità RF.
4. Qualificare la footprint A06 separatamente in PR #123 (draft) e la compatibilità PCN26-011, senza sovrapporre le PR.

**Nessuna modifica KiCad alla V2.6, nessuna PCB, DRC, BOM o TX autorizzati. NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
