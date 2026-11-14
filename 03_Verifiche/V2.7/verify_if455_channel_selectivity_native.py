#!/usr/bin/env python3
"""Native IF455 single-tank channel-offset selectivity characterization.

Results are passive ngspice voltage ratios, NOT regulatory masks or full
AM/FM/SSB receiver qualification. Offset rejection is normalized to exactly
455kHz, independently of filter peak. No RF mixer or OEM 455kHz Q model.
"""
from pathlib import Path
import math
import tempfile
from verify_interboard_audio_contract_native import exported_nets,require
from verify_if455_two_port_source_impedance_native import (
    TANK, spicedeck, run_spice, bandwidth, FSTART, FSTOP, N, LOADS
)

F_IF=455000
STEP=(FSTOP-FSTART)/(N-1)
OFFSETS_HZ=(3000,5000,10000,20000,40000)
SOURCE_R=50
LOSS_CASES=(("DC16P5_AS_RF_PROXY",16.5),
            ("Q790_EQ82P729_TRIAL",2*math.pi*790000*0.001/60))
def value_at(data,frequency):
    i=round((frequency-FSTART)/STEP)
    assert 0<=i<len(data) and abs(data[i][0]-frequency)<1,(frequency,i)
    v=data[i][1].imag
    assert v>0 and math.isfinite(v)
    return v
def main():
    with tempfile.TemporaryDirectory(prefix="tht_if455_channel_mask_") as tmp:
        root=Path(tmp)
        sch=TANK.read_text(encoding="utf-8")
        net=exported_nets(TANK,root/"if455.net")
        require(net,"IF455_SOURCE",("J1601","1"),("C1601","1"))
        require(net,"IF455_TANK",("L1601","1"),("C1601","2"))
        require(net,"IF_BENCH_GND",("J1601","2"),("L1601","2"))
        assert '(property "Value" "1mH_DELEVAN_2500-28J_CANDIDATE_NOT_QUALIFIED"' in sch
        assert abs(STEP-250)<1e-9
        summaries=[]
        for load_name,load in LOADS:
            for loss_name,loss_ohms in LOSS_CASES:
                dest=root/f"{load_name}_{loss_name}"
                dest.mkdir()
                deck=spicedeck(SOURCE_R,load,"transfer")
                tag="RLOSS ltail 0 16.5"
                assert deck.count(tag)==1
                deck=deck.replace(tag,f"RLOSS ltail 0 {loss_ohms:.12g}")
                (dest/"transfer.cir").write_text(deck,encoding="utf-8")
                data=run_spice(dest/"transfer.cir",dest,"transfer")
                vcenter=value_at(data,F_IF)
                curve=[(f,complex(v.imag,0)) for f,v in data]
                peak,peak_amp,left,right,bw=bandwidth(curve)
                assert left<peak<right and peak_amp>=vcenter
                offsets={}
                for offset in OFFSETS_HZ:
                    vlow=value_at(data,F_IF-offset)
                    vhigh=value_at(data,F_IF+offset)
                    # Rejection positive only when offset signal is attenuated;
                    # negative values signal an unwanted amplification off tune.
                    lower_db=20*math.log10(vcenter/vlow)
                    upper_db=20*math.log10(vcenter/vhigh)
                    assert all(math.isfinite(x) for x in (lower_db,upper_db))
                    offsets[str(offset)]={"low_side_rejection_dB":round(lower_db,4),
                                          "high_side_rejection_dB":round(upper_db,4),
                                          "worst_side_rejection_dB":round(min(lower_db,upper_db),4)}
                record={"passive_load":load_name,"loss_scenario":loss_name,
                        "peak_Hz":round(peak,1),"minus3dB_bandwidth_Hz":round(bw,1),
                        "reference_455_Vout_over_Vsrc":round(vcenter,9),
                        "channel_offset_dB":offsets,
                        "regulatory_mask_qualified":False,
                        "AM_FM_SSB_receiver_bandwidth_qualified":False}
                print("IF455_SINGLE_TANK_CHANNEL_OFFSET_NATIVE",record,flush=True)
                summaries.append(record)
        assert len(summaries)==4
        for record in summaries:
            # A 10kHz adjacent signal is NOT attenuated by >=3dB on both
            # sides in this 40-60kHz-wide single-resonator model.
            assert record["channel_offset_dB"]["10000"]["worst_side_rejection_dB"]<3,record
        original=next(x for x in summaries
                      if x["passive_load"]=="R100k_BENCH_REFERENCE"
                      and x["loss_scenario"]=="DC16P5_AS_RF_PROXY")
        assert abs(original["reference_455_Vout_over_Vsrc"]-0.835055562)<1e-6
        assert abs(original["minus3dB_bandwidth_Hz"]-42556.7)<2
    print("PASS_NATIVE_KICAD9_IF455_FOUR_CHANNEL_OFFSET_NGSPICE_SWEEPS_NO_RECEIVER_MASK_NO_FAB_NO_TX",flush=True)

if __name__=="__main__":
    main()
