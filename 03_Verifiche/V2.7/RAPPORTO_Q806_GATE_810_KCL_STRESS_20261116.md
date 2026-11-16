# V2.7 — Q806 gate/Zener: potenza e guasti con due solutori KCL indipendenti

**16 novembre 2026 — studio aritmetico legato alla netlist reale KiCad9, NON simulazione OEM / NON prova fisica.** Il banco di riferimento è `04_KiCad/V2.7_DRAFT/MAIN_SECONDARY_OVP_Q804_Q805_Q806_DRIVER/MAIN_SECONDARY_OVP_Q804_Q805_Q806_NPN_LAB_V2_7_DRAFT.kicad_sch` integrato con PR #303. L'analisi NON modifica nessuna rete del master MAIN V2.6 o della PCB FRONT.

La regressione nativa `03_Verifiche/V2.7/verify_q806_gate_stress_kcl_native.py` esporta la netlist KiCad9 del banco e verifica i collegamenti fisici Q804/Q805 source/gate, R2101, R2102, D2101, Q806 collector/emitter. Valuta **810 scenari** con Vsource imposto 0/5/8/12/13,8/16/20/24/36/48 V, R2101 e R2102 ±5%, Zener ipotetico nominale 11/12/13 V, sua resistenza dinamica sintetica 0,1/1/10 Ω. Q806 è assunto un sink perfetto su return: **non è un modello onsemi KSP42BU** e il source comune fluttuante non è risolto da questo screen.

Due solutori per la stessa KCL: bisezione `(Vsource−Vgate)/R2102 = Vgate/R2101 + max(0,(Vgate−Vz)/Rz)`, confronto con soluzione algebrica a tratti, più bilancio corrente e potenza. Il modello di Zener `Vz+Iz×Rz` è **ipotetico**, non proveniente da curva OEM, e non valida derating, impulso, recovery, temperatura o surge.

Gate principali: quando D2101 è **OPEN** si calcola `|VGS| = |Vsource|×R2101/(R2101+R2102)`; a 48 V nominali ~**39,58 V**, sopra il massimo assoluto dei PMOS ±20 V. Un corto **collettore–emettitore Q806**, anche con ENABLE=0, produce teoricamente **11,38 V** di bias gate a Vsource=13,8 V; dunque una sola linea ENABLE bassa non garantisce OFF con guasto BJT. Con corrente di perdita puramente ipotetica 10µA, R2101 47k può introdurre **0,47 V** di offset gate: il limite OEM di perdita reale non è ancora confrontato. La potenza resistiva R2102 e la potenza Zener sono analitiche e non indicano rating o disponibilità di un componente montabile.

Lo script blocca il gate quando KCL, conteggi, segnalazione dei fault o reti reali non coincidono. Il test **non prova integrità dei componenti**, resistenza termica, layout, guasti simultanei, soglie del nuovo supervisore, carico della radio o avviamento/EMI.

**Prossimi blocchi tecnici:** protezione gate-source fail-safe su guasto aperto del clamp, supervisore indipendente alimentato in modo realmente protetto, guasti del sink, reversibilità del carico, datasheet OEM e qualificazione meccanica/termica dei componenti, prove vendor e fisiche con autorizzazioni. Issue #27 rimane aperta. **NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
