# V2.6 — Studio UVLO con isteresi indipendente (NON schema approvato)

La V2.5 ha due uscite LM393 collegate su CMP_OUT; il feedback OVP R1005=1M dipende anche dallo stato UVLO. L'audit V2.5 ha documentato tale accoppiamento.

## Topologia candidata da portare a KiCad
- Separare U801/7 su UVLO_OC, mantenendo U801/1 su CMP_OUT.
- R1014 **4,7k THT**: VREF2V5 → UVLO_OC (pull-up indipendente).
- R1015 **470k THT**: UVLO_OC → UVLO_SENSE (feedback positivo).
- D807 **Schottky 1N5819 THT candidata**, anodo CMP_OUT, catodo UVLO_OC: UVLO basso dovrebbe forzare CMP_OUT basso, mentre OVP basso dovrebbe non modificare UVLO_OC.

Con R1012=36k, R1013=10k, R1015=470k, Vref ipotizzata 2,5V, VOL ipotizzato 0,25V e VOH idealizzato a 2,5V, la soglia UVLO in salita risulta ~11,672V e quella in discesa ~11,500V; isteresi teorica ~0,172V. Formula: Vin=Vref*(1+Rtop/Rbottom+Rtop/Rfeedback)-Rtop*Vout/Rfeedback.

**CRITICO:** la caduta del diodo D807 aumenta il livello LOW su CMP_OUT e potrebbe lasciare Q802 parzialmente polarizzato; il leakage a caldo potrebbe falsare UVLO_OC. Valutare datasheet vendor, corrente pull-up, pin common-mode, Vref TL431, soglie PVT, rampe e guasti. Nessun modello vendor o prova hardware eseguita. La proposta non costituisce ancora una revisione CAD V2.6, né qualifica un fail-closed.

Prossimo gate: nuovi sette fogli KiCad V2.6 conservando il master V2.5, ERC0 e controllo pin/net, test transitori con modelli vendor, analisi del gate Q802, qualifica del diodo e footprint. PR #28 DRAFT e issue #27 OPEN. **NO FAB / NO TX / NO BATTERIA / VEICOLO.**

Fonti: https://www.ti.com/product/LM393-N ; https://www.vishay.com/docs/88525/1n5817.pdf (consultare datasheet preciso 1N5819 prima della scelta).
