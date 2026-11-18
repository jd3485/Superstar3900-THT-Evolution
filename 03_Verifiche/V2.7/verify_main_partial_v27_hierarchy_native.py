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
IF455=KICAD/"V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT_MAIN_HIERARCHICAL_CANDIDATE.kicad_sch"
AM455=KICAD/"V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT_MAIN_HIERARCHICAL_CANDIDATE.kicad_sch"
BUFFER=KICAD/"V2.7_DRAFT/IF455_KSP10_FOLLOWER/IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT.kicad_sch"


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
    assert s.count('(sheet (at ')==5
    assert '../V2.6/PLL_RX_HIERARCHICAL_MASTER_V2.6.kicad_sch' in s
    assert '"AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"' in s
    assert '"IF455_TANK/IF455_TANK_THT_V2_7_DRAFT_MAIN_HIERARCHICAL_CANDIDATE.kicad_sch"' in s
    assert '"AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT_MAIN_HIERARCHICAL_CANDIDATE.kicad_sch"' in s
    assert '"IF455_KSP10_FOLLOWER/IF455_KSP10_FOLLOWER_THT_V2_7_DRAFT.kicad_sch"' in s
    # Exactly two physical IF→AM links plus two isolated J1502 AF port stubs.
    assert s.count('(wire (pts ') == 4 and '(junction ' not in s
    for wire in ('(xy 160.02 190.5) (xy 213.36 190.5)',
                 '(xy 160.02 195.58) (xy 213.36 195.58)',
                 '(xy 342.9 210.82) (xy 365.76 210.82)',
                 '(xy 342.9 215.9) (xy 365.76 215.9)'):
        assert wire in s,wire
    assert s.count('(pin "AM_DEMOD_AF_BENCH" passive')==1
    assert s.count('(label "AM_DEMOD_AF_BENCH" (at 365.76 210.82 0)')==1
    # One IF455 return pin plus two AM455 return pins (input and J1502 output).
    assert s.count('(pin "IF_BENCH_GND" passive')==3
    for name in ('IF455_FILTER_OUT','IF455_BENCH_IN','IF_BENCH_GND'):
        assert name in s
    amchild=AM455.read_text(encoding="utf-8")
    standalone=KICAD/"V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
    assert amchild.count('(hierarchical_label "AM_DEMOD_AF_BENCH"')==1
    assert amchild.count('(hierarchical_label "IF_BENCH_GND"')==2
    assert '(hierarchical_label "AM_DEMOD_AF_BENCH"' not in standalone.read_text(encoding="utf-8")
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
        d_if=native_nets(IF455,d/"if455.net")
        d_am=native_nets(AM455,d/"am455.net")
        d_buf=native_nets(BUFFER,d/"buffer.net")
        c=native_nets(MASTER,d/"wrapper.net")

    old_refs,old_parts=a
    aud_refs,aud_parts=b
    if_refs,if_parts=d_if
    am_refs,am_parts=d_am
    buf_refs,buf_parts=d_buf
    all_refs,all_parts=c
    assert len(old_refs)==138,(len(old_refs),sorted(old_refs))
    assert len(aud_refs)==12,(len(aud_refs),sorted(aud_refs))
    assert len(if_refs)==9,(len(if_refs),sorted(if_refs))
    assert len(am_refs)==7,(len(am_refs),sorted(am_refs))
    assert len(buf_refs)==10,(len(buf_refs),sorted(buf_refs))
    separate=[old_refs,aud_refs,if_refs,am_refs,buf_refs]
    assert sum(map(len,separate))==len(set().union(*separate)), "Duplicate reference between MAIN children"
    baseline_refs=set().union(*separate)
    assert all_refs==baseline_refs,(all_refs-baseline_refs,baseline_refs-all_refs)
    # Exported AM455 AF port must retain the same J1502 physical pin net
    # and must never share the IF455 detector input signal partition.
    signal_af=[p for p in all_parts if ("J1502","1") in p]
    ground_af=[p for p in all_parts if ("J1502","2") in p]
    assert len(signal_af)==len(ground_af)==1
    assert ("J1501","1") not in signal_af[0]
    assert ("J1501","2") in ground_af[0]
    assert signal_af[0].isdisjoint(ground_af[0])
    # The only intentional changes are merges of IF455 J1602 to AM455 J1501
    # on the signal (pin 1) and isolated return (pin 2) paths. Model the
    # expected native partitions from standalone exported netlists, not names.
    def containing(parts,endpoint):
        found=[p for p in parts if endpoint in p]
        assert len(found)==1,(endpoint,found)
        return found[0]
    expected=Counter(list(old_parts)+list(aud_parts)+list(if_parts)+list(am_parts)+list(buf_parts))
    intentional=[]
    for pin in ('1','2'):
        ip=containing(if_parts,('J1602',pin))
        ap=containing(am_parts,('J1501',pin))
        assert ip!=ap and expected[ip]==1 and expected[ap]==1
        expected.subtract([ip,ap])
        combined=ip | ap
        assert len(combined)==len(ip)+len(ap)
        expected.update([combined])
        intentional.append((pin,len(ip),len(ap),len(combined)))
    expected=+expected
    actual=Counter(list(all_parts))
    # All other connected groups (including V2.6 PLL, audio, KSP10)
    # remain identical, modulo the reviewed legacy standalone NC omission.
    # Native KiCad9 nested hierarchy omits isolated single-pin NC nets when
    # a source sheet becomes a child. This is NOT permission to alter any
    # electrically connected net: every multi-pin group must match exactly.
    # The eight known NC/isolated pins are an explicit reviewed allowlist;
    # do not generalize this exception or mask extra/missing connected pins.
    omitted_known_nc={
        ("U402","9"),("U402","8"),
        ("U520","6"),("U520","8"),("U520","10"),("U520","12"),
        ("U1201","1"),("U1201","8")
    }
    omitted=expected-actual
    added=actual-expected
    assert not added,("New or rewired MAIN nets",[(sorted(p),n) for p,n in added.items()])
    assert all(len(p)==1 and n==1 for p,n in omitted.items()),(
        "Missing connected net",[(sorted(p),n) for p,n in omitted.items()])
    missing_singletons={next(iter(p)) for p in omitted}
    assert missing_singletons==omitted_known_nc,(
        "Unexpected KiCad9 nested-only NC pin difference",missing_singletons)
    # Two intentional pairwise IF→AM joins reduce net count by exactly two;
    # pin endpoint count is unchanged. Equality of the complete partition
    # multisets above remains mandatory, with no unexplained merges.
    assert len(all_parts)==sum(map(len,(old_parts,aud_parts,if_parts,am_parts,buf_parts)))-len(omitted_known_nc)-len(intentional)
    assert sum(map(len,all_parts))==(
        sum(sum(map(len,p)) for p in (old_parts,aud_parts,if_parts,am_parts,buf_parts))-len(omitted_known_nc))
    print("MAIN_PARTIAL_HIERARCHY_NC_NETLIST_DIFFERENCE",{
        "nested_omitted_single_pin_nets":sorted(omitted_known_nc),
        "unrelated_electrically_connected_nets_preserved":True,
        "intentional_IF455_AM455_signal_return_merges":intentional,
        "NC_pins_reclassified_as_connected":False,
    },flush=True)
    print("MAIN_PARTIAL_V27_KICAD9_NATIVE",{
        "V26_original_refs":len(old_refs),
        "RX_audio_temporary_refs":len(aud_refs),
        "IF455_tank_temporary_refs":len(if_refs),
        "AM455_envelope_temporary_refs":len(am_refs),
        "KSP10_IF_buffer_temporary_refs":len(buf_refs),
        "combined_original_reference_count":len(all_refs),
        "V26_net_partitions_unchanged":True,
        "audio_net_partitions_unchanged":True,
        "IF455_tank_net_partitions_unchanged_except_two_reviewed_merges":True,
        "AM455_envelope_net_partitions_unchanged_except_two_reviewed_merges":True,
        "KSP10_buffer_net_partitions_unchanged":True,
        "no_unintended_audio_RFPll_power_ground_tie":True,
        "product_radio_MAIN_PCB_exists":False,
        "RF_IF_PLL_TX_and_supply_qualified":False,
        "NO_FAB_NO_TX":True},flush=True)
    print("PASS_KICAD9_MAIN_PARTIAL_176REFS_TWO_INTENTIONAL_IF_AM_LINKS_ALL_OTHER_CONNECTED_PIN_NETS_PRESERVED_ERC0_NO_FAB",flush=True)


if __name__=="__main__":
    main()
