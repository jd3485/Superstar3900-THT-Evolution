#!/usr/bin/env python3
"""Native ngspice IF455 PASSIVE RESISTOR THERMAL NOISE input/output budget.

A 1V AC voltage source in series with each physical resistor is used as its
independent small-signal Johnson-noise transfer probe; the resulting squared
gains are multiplied by 4*k*T*R and summed as UNCORRELATED PSDs. This is
equivalent to linear superposition in a classical resistor-noise network.
No active device / diode / coil RF loss vendor model / receiver NF is claimed.
"""
from pathlib import Path
import math
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
PRIOR=ROOT/"03_Verifiche/V2.7/RAPPORTO_IF455_PORT_Z_COMPLESSA_BANDA_AC_DRAFT.md"
TANK=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
K_B=1.380649e-23 # J/K exact SI
TEMP_K=290.0 # BENCH ASSUMPTION; neither component spec nor ambient guarantee
START_HZ,STOP_HZ,COUNT=451000,459000,81 # 8kHz RF integration window, illustrative
LOADS={
    "reference_R100k":{"extra":"","resistors":{"RGEN":50.0,"RCOIL":16.5,
        "RDAMP":47000.0,"RLOAD":100000.0},"transfer_455":0.835055562},
    "JFET_GATE_PASSIVE":{"extra":"C_GIN out gate 10p\nR_GATE gate gate_tail 1Meg\nV_N_GATE gate_tail 0 DC 0 AC {gate_ac}\nC_GPAR gate 0 7p",
        "resistors":{"RGEN":50.0,"RCOIL":16.5,"RDAMP":47000.0,
        "RLOAD":100000.0,"GATE":1000000.0},"transfer_455":0.665186786}
}
FREQ_STEP=(STOP_HZ-START_HZ)/(COUNT-1)
assert FREQ_STEP==100
def deck_text(load,excitation):
    resistor_sources={name:(1 if name==excitation else 0) for name in load["resistors"]}
    signal_ac=1 if excitation=="SIGNAL" else 0
    gate=load["extra"].format(gate_ac=resistor_sources.get("GATE",0))
    return f"""* Thermal resistor noise via linear native SPICE transfer probes.
* RCOIL 16.5ohm is DCR-as-RF assumption; thermal contribution consequently uncertain.
* Vendor JFET input gate C and leakage are PASSIVE surrogates, not OEM.
.title IF455 passive resistor Johnson noise RF budget - never antenna sensitivity
VSIGNAL src 0 DC 0 AC {signal_ac}
RGEN src gen_r 50
V_N_RGEN gen_r gen DC 0 AC {resistor_sources['RGEN']}
C1601 gen tank 10p
L1601 tank lt 1m
RCOIL lt coil_r 16.5
V_N_RCOIL coil_r 0 DC 0 AC {resistor_sources['RCOIL']}
C1602 tank 0 82p
C1603 tank 0 30p
R1601 tank damping_r 47k
V_N_RDAMP damping_r 0 DC 0 AC {resistor_sources['RDAMP']}
C1604 tank out 10p
R1602 out load_r 100k
V_N_RLOAD load_r 0 DC 0 AC {resistor_sources['RLOAD']}
{gate}
.control
set wr_singlescale
ac lin {COUNT} {START_HZ} {STOP_HZ}
wrdata rf_complex_out.dat vr(out) vi(out)
quit
.endc
.end
"""
def spectrum(deck,folder):
    folder.mkdir()
    path=folder/"native.cir"
    path.write_text(deck,encoding="utf-8")
    log=folder/"native.log"
    cmd=subprocess.run(["ngspice","-b","-o",str(log),str(path)],
        cwd=folder,capture_output=True,text=True)
    report=log.read_text(encoding="utf-8",errors="replace") if log.is_file() else ""
    cmd.check_returncode()
    assert "Error:" not in report and "fatal" not in report.lower(),report[-1600:]
    data=folder/"rf_complex_out.dat"
    assert data.is_file(),("No native ngspice data",report[-1200:])
    rows=[]
    for line in data.read_text(encoding="utf-8").splitlines():
        try: values=tuple(float(x) for x in line.split())
        except ValueError: continue
        if values:
            assert len(values)==3 and all(map(math.isfinite,values)),values
            rows.append((values[0],complex(values[1],values[2])))
    assert len(rows)==COUNT,(len(rows),report[-600:])
    assert abs(rows[0][0]-START_HZ)<1 and abs(rows[-1][0]-STOP_HZ)<1
    assert all(abs(f-(START_HZ+i*FREQ_STEP))<1 for i,(f,z) in enumerate(rows))
    return [v for f,v in rows]

def main():
    sch=TANK.read_text(encoding="utf-8")
    prior=PRIOR.read_text(encoding="utf-8")
    assert "EW_GKG50015_10to50pF_THT_CANDIDATE_TRIM" in sch
    assert "16,5Ω" in prior and "455k" in prior
    assert set(LOADS)=={"reference_R100k","JFET_GATE_PASSIVE"}
    for label,load in LOADS.items():
        with tempfile.TemporaryDirectory(prefix="tht_if455_thermal_") as td:
            folder=Path(td)
            sig=spectrum(deck_text(load,"SIGNAL"),folder/"signal")
            transfer=abs(sig[COUNT//2])
            assert abs(transfer-load["transfer_455"])/load["transfer_455"]<0.01,(
                "Changed PR110 nominal AC baseline",label,transfer,load["transfer_455"])
            psd=[0.0]*COUNT
            contributions={}
            for name,ohms in load["resistors"].items():
                response=spectrum(deck_text(load,name),folder/name)
                voltage_psd=4*K_B*TEMP_K*ohms
                individual=[voltage_psd*abs(v)**2 for v in response]
                psd=[total+item for total,item in zip(psd,individual)]
                at455=math.sqrt(individual[COUNT//2])
                # Integrate over a defined RF interval 451k..459k, NOT audio noise
                integrated=sum((individual[i]+individual[i+1])/2*FREQ_STEP
                               for i in range(COUNT-1))
                assert integrated>0 and math.isfinite(integrated)
                contributions[name]={
                    "resistance_ohms":ohms,
                    "RF_output_noise_at_455_V_per_sqrtHz":round(at455,14),
                    "integrated_RF_output_noise_Vrms":round(math.sqrt(integrated),12)}
            total_density=math.sqrt(psd[COUNT//2])
            integrated_total=sum((psd[i]+psd[i+1])/2*FREQ_STEP
                                  for i in range(COUNT-1))
            integrated_noise=math.sqrt(integrated_total)
            input_ref=total_density/transfer
            # Verify exact physical variance addition and nonzero Johnson noise.
            sum_individual=sum(
                contributions[k]["integrated_RF_output_noise_Vrms"]**2
                for k in contributions)
            assert abs(sum_individual-integrated_total)/integrated_total<0.005
            assert total_density>0 and integrated_noise>0 and input_ref>0
            results={
                "load_case":label,"temperature_K_ASSUMED":TEMP_K,
                "RF_integration_band_Hz":[START_HZ,STOP_HZ],
                "IF455_ideal_1V_transfer_at_455":round(transfer,9),
                "RF_output_noise_at_455_V_per_sqrtHz":round(total_density,14),
                "RF_output_integrated_8kHz_Vrms":round(integrated_noise,12),
                "source_referred_equivalent_at_455_V_per_sqrtHz":round(input_ref,14),
                "individual_resistor_contributions":contributions,
                "NOT": "NO active noise, IF gain, diode audio SNR/SINAD, real RF coil Q, antenna sensitivity"}
            print("IF455_NATIVE_PASSIVE_THERMAL_RF_NOISE_BUDGET",results,flush=True)
    print("PASS_NGSPICE_IF455_PASSIVE_THERMAL_RF_RESISTORS_2_LOADS_NOT_NF_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":main()
