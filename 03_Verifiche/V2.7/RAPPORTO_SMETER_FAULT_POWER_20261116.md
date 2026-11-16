# V2.7 — S-meter FRONT: bilancio dissipazioni e scenari di guasto resistivo

16 novembre 2026. **Modello di verifica, NON circuito hardware qualificato.**

Rete verificata da netlist KiCad9 FRONT: J1801 pin1/pin2; RV1801 pista 10 kΩ e cursore; R1801 + R1802 ciascuno 100 kΩ; J1802 movimento analogico candidato con resistenza ipotetica. Il verificatore `03_Verifiche/V2.7/verify_smeter_fault_power_native.py` controlla **675 combinazioni**: 5 tensioni di sorgente, 3 Rout, 3 Rcoil positive ipotetiche, 0/1/2 resistenze limitatrici in corto e 5 posizioni cursore. I valori sono candidati, non tensioni operative accertate.

Per ogni configurazione, dalla KCL già validata dalla PR #297, verifica l'identità **Vopen × Isource = P_Rout + P_track_alto + P_track_basso + P_Rserie_rimanenti + P_Rcoil**, e il bilancio terminale. Fallisce se il circuito KiCad9 cambia pin↔net o se una singola identità energetica fallisce.

- **Scenario sano ipotetico**: sorgente ideale 11 V, 20 kΩ Rcoil, due 100 kΩ integri, cursore massimo. Ipista 1,1 mA, Icoil 50 µA, **Ppista 12,1 mW**, totale R1801+R1802 0,5 mW, Pcoil 0,05 mW, Ptotale 12,65 mW.
- **Scenario di guasto non approvato**: sorgente ideale 20 V, Rcoil 1 kΩ, entrambi i 100 kΩ cortocircuitati, cursore massimo. **Pcoil 400 mW**, Ppista 40 mW. Potenziale grave sovraccarico del movimento, non protezione accettabile.
- I massimi su griglia includono il caso guasto; non equivalgono a massimi reali, perché non modellano corti cavo, contatti, scariche ESD, open return, driver saturato, potenziometro interrotto, coil non lineare o potenza nominale MPN.

L'architettura alternativa di sink 5V non è collegata al percorso storico; non dedurre un prodotto completo né una sorgente MAIN. Prima di fabbricare occorre scegliere FSD/OEM, limiti di potenza, comportamento fault di driver+cavo+meter, protezione indipendente e derating, misure su carico fittizio, ERC/DRC della PCB reale.

**NO FAB / NO TX / NO BATTERIA / NO VEICOLO.**
