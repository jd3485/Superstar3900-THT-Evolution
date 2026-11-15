#!/usr/bin/env python3
"""Native IF455->KSP10->AM455 vs direct detector, both FRONT/LM386-loaded.

Six 50-ns timestep ngspice nonlinear model cases; source, coil/BJT and diode
are generic. NOT OEM device approval or genuine radio sensitivity. Do not
connect physically to main, do not authorize FAB/TX or an automotive supply.
"""
from pathlib import Path
import math
import subprocess
import tempfile
from verify_if455_ksp10_am455_combined_native import metric
from verify_am455_front_lm386_loaded_ac_native import check_actual_cad
from verify_interboard_audio_contract_native import exported_nets,require

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"04_KiCad/V2.7_DRAFT"
DECK=ROOT/"03_Verifiche/V2.7/spice/if455_ksp10_am455_front_lm386_loaded_generic_comparison.cir"
REFERENCE=ROOT/"03_Verifiche/V2.7/spice/if455_ksp10_am455_combined_generic_transient.cir"
BUF=BASE/"IF455_KSP10_FOLLOWER/IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT.kicad_sch"
DRIVES=(0.5,2.0)
POSITIONS=(0.1,0.5,0.9)
PREFIX=".param fc=455k fa=1k depth=0.5 amp=2 rail=6 gain=80 wiper=0.5"

def main():
    check_actual_cad()
    original=DECK.read_text(encoding="utf-8")
    old=REFERENCE.read_text(encoding="utf-8")
    assert original.count(PREFIX)==1
    assert ".tran 0.05u 12m 0 0.05u" in original
    assert original.count(".model DGENERIC")==1
    assert original.count(".model QGEN")==1
    assert original.count("RVP_TOP_")==2
    assert original.count("RVP_BOT_")==2
    for line in old.splitlines():
        # Existing original RF/IF/QGEN circuit component card may not drift.
        if line.startswith(("BIFD ","BIFB ","RGEN","C160","L160","RCOIL",
                            "D1501","R1501","C1501","C1502","R1502",
                            "VLAB ","C170","R170","Q170",
                            ".model ")):
            assert line in original,("Prior established model silently changed",line)
    for path in (BUF,BASE/"FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"):
        assert path.is_file()
    with tempfile.TemporaryDirectory(prefix="tht_if_am_front_buffer_loaded_") as td:
        root=Path(td)
        buf=exported_nets(BUF,root/"buf.net")
        require(buf,"IF455_TANK_OUT",("J1701","1"),("C1701","1"))
        require(buf,"IFBUF_AC_OUT",("C1702","2"),("J1702","1"))
        require(buf,"VLAB6_IFBUF_ONLY",("Q1701","3"),("J1703","1"))
        require(buf,"IF_BENCH_GND",("J1703","2"),("J1702","2"))
        rows=[]
        for drive in DRIVES:
            for pos in POSITIONS:
                text=original.replace(PREFIX, PREFIX.replace("amp=2",f"amp={drive}").replace("wiper=0.5",f"wiper={pos}"))
                assert text!=original
                filepath=root/f"amp{drive}_w{pos}.cir"
                logfile=filepath.with_suffix(".log")
                filepath.write_text(text,encoding="utf-8")
                run=subprocess.run(["ngspice","-b","-o",str(logfile),str(filepath)],
                                   cwd=root,capture_output=True,text=True,timeout=180)
                log=logfile.read_text(encoding="utf-8",errors="replace") if logfile.exists() else ""
                run.check_returncode()
                assert "Error:" not in log and "fatal" not in log.lower(),log[-2000:]
                direct=metric(log,"loaded_direct_af_max")-metric(log,"loaded_direct_af_min")
                buffered=metric(log,"loaded_buffered_af_max")-metric(log,"loaded_buffered_af_min")
                directdet=metric(log,"direct_max")-metric(log,"direct_min")
                bufd=metric(log,"buffered_max")-metric(log,"buffered_min")
                assert all(math.isfinite(x) and x>0 for x in (direct,buffered,directdet,bufd)),(
                    drive,pos,direct,buffered,directdet,bufd)
                assert direct<directdet and buffered<bufd,("Unexpected passive input gain",drive,pos)
                result=(drive,pos,direct,buffered,buffered/direct)
                rows.append(result)
                print("KSP10_IF455_AM455_LOADED_COMPARE_GENERIC",{
                    "source_peak_V":drive,"wiper":pos,
                    "direct_LM386_pin3_Vpp":round(direct,9),
                    "buffer_LM386_pin3_Vpp":round(buffered,9),
                    "buffer_to_direct_ratio":round(buffered/direct,6),
                    "BJT_OEM_model":False,"diode_OEM_model":False,
                    "active_LM386_gain_included":False},flush=True)
    assert len(rows)==6
    for drive in DRIVES:
        d=[v for a,p,v,b,ratio in rows if a==drive]
        b=[v for a,p,v,b,ratio in rows if a==drive]
        assert all(x<y for x,y in zip(d,d[1:]))
        assert all(x<y for x,y in zip(b,b[1:]))
    print("PASS_NGSPICE_6_IF455_KSP10_AM455_FRONT_LM386_GENERIC_LOADED_COMPARISONS_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
