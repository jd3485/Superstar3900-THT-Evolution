#!/usr/bin/env python3
"""Fail-closed native KiCad9 integration of unchanged V2.6 MAIN and V2.7 RX audio.

Does NOT approve or implement electrical ties between PLL/RX and LM386.
Independent input netlists must preserve EVERY component and ALL actual
pin-connected net partitions. New wrapper is not a product PCB or FAB gate.
"""
from pathlib import Path
from collections import Counter
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
KICAD=ROOT/"04_KiCad"
MASTER=KICAD/"V2.7_DRAFT/MAIN_RADIO_PARTIAL_V2_7_DRAFT.kicad_sch"
V26=KICAD/"V2.6/PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch"
AUDIO=KICAD/"V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"


def native_nets(sch,destination):
    cp=subprocess.run(["kicad-cli","sch","export","netlist",
        "-o",str(destination),str(sch)],cwd=ROOT,
        capture_output=True,text=True,timeout=120)
    print("MAIN_PARTIAL_EXPORT",sch.name,cp.stdout,cp.stderr,flush=True)
    cp.check_returncode()
    t=destination.read_text(encoding="utf-8")
    assert "(components" in t and "(nets" in t,(sch,t[:900])
    comp=t.split("(components",1)[1].split("(libparts",1)[0]
    refs=set(re.findall(r'\(comp\s+\(ref\s+"([^"]+)"\)',comp))
    tail=t.rsplit("(nets",1)[-1]
    matches=list(re.finditer(
        r'\(net\s+\(code\s+"?\d+"?\)\s+\(name\s+"([^"]+)"\)',tail))
    assert matches
    partitions={}
    for i,m in enumerate(matches):
        sub=tail[m.end():matches[i+1].start() if i+1<len(matches) else len(tail)]
        pins=frozenset(re.findall(
           r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)',sub))
        assert pins,(sch.name,m.group(1))
        if pins in partitions:
            raise AssertionError(("Net partition duplicated",sch.name,m.group(1)))
        partitions[pins]=m.group(1)
    return refs,partitions


def main():
    s=MASTER.read_text(encoding="utf-8")
    assert s.count('(sheet (at ')==2
    assert '../V2.6/PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch' in s
    assert '"AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"' in s
    assert '(wire ' not in s and '(junction ' not in s
    assert 'NO FAB' in s and 'NO TX' in s
    assert MASTER.with_suffix(".kicad_pro").is_file()
    tab=(MASTER.parent/"sym-lib-table").read_text(encoding="utf-8")
    fpt=(MASTER.parent/"fp-lib-table").read_text(encoding="utf-8")
    for name in ("THT_V10","THT_V11","THT_V14","THT_V15",
                 "THT_V17","THT_V18","THT_V20","THT_V24","TH_AUDIO"):
        assert '(name "'+name+'")' in tab,name
    for name in ("THT_V21","THT_V22","THT_V23"):
        assert '(name "'+name+'")' in fpt,name
    with tempfile.TemporaryDirectory(prefix="tht_main_v27_") as tmp:
        d=Path(tmp)
        erc=d/"integrated_erc.rpt"
        cp=subprocess.run(["kicad-cli","sch","erc","--exit-code-violations",
             "-o",str(erc),str(MASTER)],cwd=ROOT,
             capture_output=True,text=True,timeout=180)
        print("MAIN_PARTIAL_ERC_STDOUT",cp.stdout,cp.stderr,flush=True)
        if erc.exists():
            print("MAIN_PARTIAL_ERC_REPORT",erc.read_text(encoding="utf-8"),flush=True)
        cp.check_returncode()
        a=native_nets(V26,d/"v26.net")
        b=native_nets(AUDIO,d/"audio.net")
        c=native_nets(MASTER,d/"wrapper.net")

    old_refs,old_parts=a
    aud_refs,aud_parts=b
    all_refs,all_parts=c
    assert len(old_refs)==138,(len(old_refs),sorted(old_refs))
    assert len(aud_refs)==12,(len(aud_refs),sorted(aud_refs))
    assert old_refs.isdisjoint(aud_refs),("Reference collision",old_refs&aud_refs)
    assert all_refs==(old_refs|aud_refs),(all_refs-(old_refs|aud_refs),(old_refs|aud_refs)-all_refs)
    # All net groups must be conserved with no accidental audio↔RF ground ties.
    expected=Counter(list(old_parts)+list(aud_parts))
    actual=Counter(all_parts)
    assert expected==actual,(
        "V2.6 MAIN or RX audio pin-net partition changed or unintended short",
        "missing",[(sorted(p),n) for p,n in (expected-actual).items()][:12],
        "extra",[(sorted(p),n) for p,n in (actual-expected).items()][:12])
    assert sum(map(len,all_parts))==sum(map(len,old_parts))+sum(map(len,aud_parts))
    print("MAIN_PARTIAL_V27_KICAD9_NATIVE",{
        "V26_original_refs":len(old_refs),
        "RX_audio_temporary_refs":len(aud_refs),
        "combined_original_reference_count":len(all_refs),
        "V26_net_partitions_unchanged":True,
        "audio_net_partitions_unchanged":True,
        "no_unintended_audio_RFPll_power_ground_tie":True,
        "product_radio_MAIN_PCB_exists":False,
        "RF_IF_PLL_TX_and_supply_qualified":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_KICAD9_MAIN_PARTIAL_150REFS_ALL_V26_AND_AUDIO_PIN_NETS_UNCHANGED_ERC0_NO_FAB",flush=True)


if __name__=="__main__":
    main()
