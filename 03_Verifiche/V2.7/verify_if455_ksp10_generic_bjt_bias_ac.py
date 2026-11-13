#!/usr/bin/env python3
"""Native ngspice 9-case bias/455kHz AC sweep for generic BJT surrogate.
Not an onsemi KSP10BU SPICE macro-model, RF noise or production qualification.
"""
from pathlib import Path
import math
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_ksp10_generic_bjt_bias_ac.cir"
SCH=ROOT/"04_KiCad/V2.7_DRAFT/IF455_KSP10_FOLLOWER/IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT.kicad_sch"
RAILS=(5.5,6.0,6.5)
BETAS=(40,80,160)

def read_rows(path):
    assert path.is_file(),path
    rows=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        try: nums=tuple(float(v) for v in line.split())
        except ValueError:continue
        if nums:rows.append(nums)
    assert rows and all(len(row)==4 and all(math.isfinite(v) for v in row) for row in rows),path
    return rows

def main():
    deck=DECK.read_text(encoding="utf-8")
    sch=SCH.read_text(encoding="utf-8")
    for term in (".param rail=6 gain=80","R1701 vcc base 22k",
                 "R1702 base 0 10k","R1703 emitter 0 2.2k",
                 "Q1701 vcc base emitter QGEN",
                 "C1701 input base 10n","C1702 emitter output 10n",
                 "R1704 output 0 100k","ac lin 3 454k 456k",
                 "NOT an onsemi/OEM"):
        assert term in deck,term
    for term in ("22k_TOP_BIAS_DRAFT","10k_BOTTOM_BIAS_DRAFT",
                 "2k2_EMITTER_SET_DRAFT","ONSEMI_KSP10BU_TO92_CANDIDATE"):
        assert term in sch,term
    results=[]
    with tempfile.TemporaryDirectory(prefix="tht_ksp10_bias_corner_") as tmp:
        root=Path(tmp)
        for rail in RAILS:
            for beta in BETAS:
                case=root/("rail_"+str(rail).replace(".","p")+"_beta_"+str(beta))
                case.mkdir()
                src=deck.replace(".param rail=6 gain=80",f".param rail={rail} gain={beta}")
                path=case/"candidate.cir"
                path.write_text(src,encoding="utf-8")
                logpath=case/"native.log"
                cmd=subprocess.run(["ngspice","-b","-o",str(logpath),str(path)],
                                   cwd=case,capture_output=True,text=True)
                log=logpath.read_text(encoding="utf-8",errors="replace") if logpath.exists() else ""
                cmd.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),log[-1200:]
                bias=read_rows(case/"ifbuf_bias.dat")
                ac=read_rows(case/"ifbuf_ac.dat")
                assert len(ac)==3,(rail,beta,len(ac))
                assert abs(ac[1][0]-455000)<1,(rail,beta,ac[1])
                base,emit,collector=bias[-1][1:]
                out,source=ac[1][1:3]
                gain=out/source if source else math.nan
                assert 0<emit<base<collector<7,("Unexpected bias",rail,beta,base,emit,collector)
                assert 0.35<(base-emit)<1.1,("Vbe generic corner",rail,beta,base,emit)
                assert abs(collector-rail)<0.03,(rail,beta,collector)
                assert math.isfinite(gain) and 0<gain<1.1,(rail,beta,gain)
                results.append((rail,beta,base,emit,(emit/2200)*1000,gain))
    assert len(results)==9
    for rail,beta,base,emit,ie_ma,gain in results:
        print("KSP10_GENERIC_BJT_CORNER",{"supply_V":rail,"beta_model":beta,
               "base_V":round(base,6),"emitter_V":round(emit,6),
               "emitter_mA":round(ie_ma,6),"ac455_output_to_source_gain":round(gain,6)},
              flush=True)
    print("PASS_NGSPICE_IF455_KSP10_GENERIC_BJT_9_BIAS_AC_CORNERS_NOT_OEM_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
