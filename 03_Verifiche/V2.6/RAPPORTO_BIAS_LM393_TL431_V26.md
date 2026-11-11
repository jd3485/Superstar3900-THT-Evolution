# Studio addizionale: bias reale R1011/R1001 verso LM393/TL431 (V2.6)

**Scopo:** affiancare all'audit termico R1011/D806 675 corner una verifica DC analitica che **includa** il carico di riferimento TL431 attraverso R1001=1k8, la corrente assunta di U801 e lo Zener D806 a 15V *idealizzato*. Il modello senza carico resta una stima conservativa della potenza sul resistore in alcuni casi, ma NON un modello della tensione effettiva del comparatore.

**Percorsi pin-net verificati solo con vera netlist KiCad9:** D804 A2 FUSED_RAW → K1 OVP_PRECLAMP → R1011 pin1 → R1011 pin2 OVP_CTL_VCC → U801 pin8, D806 catodo pin1 e R1001 pin1; R1001 pin2 → U802 TL431 catodo pin1 e REF pin3; D806 anodo pin2, U802 anodo pin2, U801 GND pin4.

**Equazione in ipotesi TL431 già in regolazione:** `(VIN−VF−V_CTL)/R1011 = I_LM393_assunta + (V_CTL−VREF)/R1001 + I_D806`. Se D806 si attiva si impone idealmente `V_CTL=15 V`. Se è aperto `I_D806=0`. Non descrive avvio, saturazione TL431, capacità, input common-mode LM393, consumo dinamico né resistenza/tensione Zener non lineare.

Griglia `screen_ctl_rail_bias_v26.py`: **2.268 combinazioni** di VIN 10/11,5/13,8/16,5/24/36/48 V; VF 0,2/0,4/0,7 V; R1011 779/820/861Ω; R1001 1710/1800/1890Ω; VREF 2,45/2,50/2,55V; corrente U801 *assunta* 0,5/1/2/3mA. **Non sono worst-case garantiti del produttore** e non autorizzano 48V.

Risultati indicativi:
- VIN **11,5 V**: controller V_CTL **6,286–8,470 V**; riferimento TL431 supposto in regolazione.
- VIN **13,8 V**: V_CTL **7,815–10,099 V**, corrente TL431 **2,896–4,323 mA**. D806 15V idealizzato **spento** in ogni corner della griglia. **Perciò NON è corretto assumere V_CTL=15V durante funzionamento nominale.**
- VIN **36 V**: Zener idealizzato attivo in tutti i corner; non valida la sicurezza a 36V.
- VIN **48 V**: corrente D806 idealizzata **27,175–35,018 mA**; molto inferiore alla corrente di prova 75mA della Diotec.
- A **48 V con solo D806 aperto e TL431 ancora funzionante**: V_CTL simulata **30,562–34,317 V**, sotto 36V in questa griglia. **Non garantisce** che l'LM393 sia salvo, perché dipende dal carico/fault mode: con anche TL431 aperto, la tensione può salire oltre 36V. Il report precedente indicava correttamente il rischio ma non distingueva questi due fault model.

**Qualifica ancora mancante:** corrente massima LM393 (soprattutto temperatura), comportamento TL431 minimo 0,4 mA a 25°C dalla specifica TI, eventuale TL431 con instabilità e guasti (open/short), caratteristica D806 a correnti inferiori a test, tensioni di common-mode U801 durante salita/discesa, immunità ESD e transitori D804/TVS/F701. Il confronto numerico è uno **screen** non una simulazione vendor o prova fisica.

Datasheet: TI [TL431](https://www.ti.com/lit/ds/symlink/tl431.pdf) — corrente minima di regolazione (dato a 25°C); TI [LM393-N](https://www.ti.com/product/LM393-N) — corrente tipica e Vs max36V; Vishay [PR03](https://www.vishay.com/docs/28729/pr010203.pdf); Diotec [1N5352B](https://diotec.com/en/product/1N5352B.html).

**PR #32 audit tecnico; resta draft fino a CI su HEAD finale.** Nessuna variazione elettrica, no validazione hardware. Issue #27 aperta. **NO FAB / NO TX / NO BATTERIA/VEICOLO**.
