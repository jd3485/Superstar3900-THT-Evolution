#!/usr/bin/env python3
"""Run ALL original 22 KiCad9/ngspice legacy suites in ONE verified KiCad9 container.

The additional original workflow (verifica_v02) is ALWAYS run in ci/fast_regressions.py.
No ERC/DRC waiver, no best-effort test skipping, and no fake pass on failure.
Only separate installation steps and GitHub artifact/checkout steps are deduplicated.
"""
from __future__ import annotations
import os,re,subprocess,sys
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
RUN_COUNTS={
 "cad_native_v10.yml":8,"cad_native_v11.yml":6,"cad_native_v12.yml":6,
 "cad_native_v13.yml":6,"cad_native_v14.yml":7,"cad_native_v15.yml":6,
 "cad_native_v16.yml":6,"cad_native_v17.yml":8,"cad_native_v18.yml":9,
 "cad_native_v19.yml":7,"cad_native_v20.yml":9,"cad_native_v21.yml":7,
 "cad_native_v22.yml":7,"cad_native_v23.yml":7,"cad_native_v24.yml":6,"cad_native_v25.yml":6,"cad_native_v26.yml":6,
 "boost_v07.yml":2,"ngspice_v14_vco_frontend.yml":2,
 "pll_tristate_v09.yml":2,"vco_spice_v06.yml":8,"vtune_driver_v08.yml":2,
}
EXPECTED_ALL_WORKFLOWS=23
ALLOWED_USES=("actions/checkout@v4","actions/upload-artifact@v4")
INSTALL_NGSPICE_RE=re.compile(r"^\s*sudo\s+.*apt-get\s+install\s+.*\bngspice\b.*$",re.MULTILINE)

def normalized_command(cmd:str) -> str|None:
    if "add-apt-repository" in cmd:
        assert "kicad-cli version" in cmd and "apt-get" in cmd, "Unexpected KiCad install step"
        return None
    if "apt-get" in cmd:
        lines=cmd.splitlines()
        kept=[]
        for line in lines:
            if "apt-get update" in line or ("apt-get install" in line and "ngspice" in line):
                continue
            kept.append(line)
        cleaned="\n".join(kept)
        assert "apt-get" not in cleaned and "add-apt-repository" not in cleaned, "Unreviewed installer"
        return cleaned if cleaned.strip() else None
    return cmd

def load_steps(name:str) -> list[tuple[str,str|None]]:
    yml=ROOT/".github/workflows"/name
    raw=yaml.safe_load(yml.read_text(encoding="utf-8"))
    assert isinstance(raw,dict) and "jobs" in raw, name
    jobs=raw["jobs"]
    assert isinstance(jobs,dict) and len(jobs)==1, "Unexpected extra job in "+name
    job=next(iter(jobs.values()))
    assert job.get("runs-on"), "Missing original runner metadata: "+name
    steps=job["steps"]
    seen_run=0
    commands=[]
    for st in steps:
        assert isinstance(st,dict), "Invalid legacy step"
        if "uses" in st:
            assert st["uses"] in ALLOWED_USES and "run" not in st, (name,st)
            continue
        assert "run" in st, f"Missing original run step {name}: {st}"
        seen_run+=1
        condition=st.get("if")
        if condition:
            assert name=="vco_spice_v06.yml" and condition=="github.event_name == 'workflow_dispatch'", (name,condition)
            # Original five v06 exploratory steps were push-only, never part of PR checks.
            # Keep explicitly executable for manual full-run and standalone dispatch.
            if os.getenv("ENABLE_HISTORICAL_EXPLORATORY")!="true":
                commands.append((st.get("name","v06 exploratory"),"__ORIGINAL_PR_CONDITION_FALSE__"))
                continue
        cmd=st["run"]
        assert isinstance(cmd,str) and cmd.strip(),(name,st)
        commands.append((st.get("name","Unnamed legacy step"),normalized_command(cmd)))
    assert seen_run==RUN_COUNTS[name],f"{name}: {seen_run} commands not {RUN_COUNTS[name]}"
    return commands

def main()->None:
    assert len(RUN_COUNTS)==22
    workflow_dir=ROOT/".github/workflows"
    actual={p.name for p in workflow_dir.glob("*.yml")}
    expected=set(RUN_COUNTS)|{"verifica_v02.yml"}
    # The unified gate and one obsolete pilot do not count as legacy; reject other untracked workflow.
    unknown={name for name in actual-expected
             if not name.startswith("ci_") and not name.startswith("zz_pilot_")}
    assert not unknown, "New unreviewed workflow lacks CI coverage: "+str(unknown)
    compiled={name:load_steps(name) for name in RUN_COUNTS}
    total=sum(len(st) for st in compiled.values())
    assert total==sum(RUN_COUNTS.values())
    print("CI_FULL_MANIFEST_VERIFIED",{"workflows":len(compiled),"legacy_run_steps":total,
         "plus_fast_suites":10,"deduplicated_install_steps":sum(c is None for steps in compiled.values() for _,c in steps),
         "original_v06_conditional_skips":sum(c=="__ORIGINAL_PR_CONDITION_FALSE__" for steps in compiled.values() for _,c in steps)},flush=True)
    if "--audit-only" in sys.argv: return
    v=subprocess.run(["kicad-cli","version"],capture_output=True,text=True,check=True).stdout.strip()
    assert re.match(r"^9\.0\.\d+",v), "Wrong KiCad CLI version: "+v
    subprocess.run(["ngspice","--version"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    subprocess.run(["node","--version"],check=True)
    executed=0
    for name,steps in compiled.items():
        print("::group::"+name,flush=True)
        for label,cmd in steps:
            if cmd is None:
                print("DEDUPED_INSTALL_ONLY",name,label,flush=True)
                continue
            if cmd=="__ORIGINAL_PR_CONDITION_FALSE__":
                print("ORIGINAL_PR_CONDITION_FALSE",name,label,flush=True)
                continue
            print("RUN_REAL_LEGACY_STEP",name,label,flush=True)
            subprocess.run(["bash","-e","-o","pipefail","-c",cmd],cwd=ROOT,
                          env=os.environ.copy(),check=True)
            executed+=1
        print("::endgroup::",flush=True)
    # New standalone V2.7 audio draft: fail the FULL gate on any native
    # schematic ERC violation or missing pin/net in the exported netlist.
    pilot=ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_RX_MONO_LM386_V2_7_DRAFT.kicad_sch"
    if pilot.exists():
        print("::group::V2.7 RX AUDIO THT PILOT NATIVE KIcad9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_audio_draft_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    front=ROOT/"04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch"
    if front.exists():
        print("::group::V2.7 FRONT_VOLUME THT NATIVE KiCad9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_front_volume_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    if (ROOT/"04_KiCad/V2.7_DRAFT/FRONT_VOLUME/FRONT_VOLUME_THT_V2_7_DRAFT.kicad_sch").exists():
        print("::group::V2.7 MAIN-FRONT AUDIO INTERBOARD NATIVE PIN CONTRACT",flush=True)
        subprocess.run([sys.executable, "-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_interboard_audio_contract_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Independent 6V audio lab regulator, not connected to the master V2.6.
    psu=ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V/AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch"
    if psu.exists():
        print("::group::V2.7 THT LAB-ONLY AUDIO PSU LM317 NATIVE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_audio_psu_lm317_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    if (ROOT/"04_KiCad/V2.7_DRAFT/AUDIO_PSU_6V/AUDIO_PSU_LM317_6V_LAB_DRAFT.kicad_sch").exists():
        print("::group::V2.7 AUDIO 6V PSU TO LM386 NATIVE PIN CONTRACT",flush=True)
        subprocess.run([sys.executable, "-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_audio_6v_supply_contract_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # New ngspice behavioral rail-step study. This exercises REAL transient
    # simulation, not LM317/LM386 vendor semiconductor models. No PCB release.
    spice=ROOT/"03_Verifiche/V2.7/spice/audio_6v_lab_rail_step_behavioral.cir"
    if spice.exists():
        print("::group::V2.7 AUDIO 6V LAB RAIL STEP NATIVE NGSPICE BEHAVIORAL",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_audio_rail_step_ngspice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # 455kHz AM-only THT diode envelope pilot: real native KiCad9 schematic,
    # not an SSB/FM detector or integrated receiver board.
    am455=ROOT/"04_KiCad/V2.7_DRAFT/AM455_ENVELOPE/AM455_ENVELOPE_THT_V2_7_DRAFT.kicad_sch"
    if am455.exists():
        print("::group::V2.7 AM455 ENVELOPE THT BENCH NATIVE KICAD9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_am455_bench_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # Bench 455kHz AM envelope behavior with a deliberately GENERIC diode model.
    # This does NOT replace the native KiCad ERC, IF gain or OEM qualification.
    am455_spice=ROOT/"03_Verifiche/V2.7/spice/am455_envelope_1khz_generic_diode_bench.cir"
    if am455_spice.exists():
        print("::group::V2.7 AM455 1KHZ AM DEMOD GENERIC DIODE NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_am455_generic_diode_spice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # IF455 1mH/122.2pF passive THT lab tank, with PROVISIONAL coil mechanics.
    # Real KiCad9 ERC and pin-net exports; no receiver passband certification.
    tank=ROOT/"04_KiCad/V2.7_DRAFT/IF455_TANK/IF455_TANK_THT_V2_7_DRAFT.kicad_sch"
    if tank.exists():
        print("::group::V2.7 IF455 PASSIVE THT LC TANK NATIVE KICAD9",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_tank_native.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # IF455 coil-loss/coupling load and retuning comparison: actual ngspice AC.
    # Behavioral RLC only (not OEM Q/SRF or production filter qualification).
    if (ROOT/"03_Verifiche/V2.7/spice/if455_loaded_tank_ac_comparison.cir").exists():
        print("::group::V2.7 IF455 LOADED LC 455K NATIVE NGSPICE AC SWEEP",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_loaded_ac_ngspice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # OEM Delevan active candidate 2500-28J, RF Q at 455k not qualified.
    # Actual native ngspice +/-5% inductance & illustrative SRF parasitic
    # shows why fixed IF tank must NOT be released for manufacturing.
    if (ROOT/"03_Verifiche/V2.7/spice/if455_delevan_2500_28j_tolerance_ac.cir").exists():
        print("::group::V2.7 IF455 DELEVAN CANDIDATE TOLERANCE NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_delevan_tolerance_ngspice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    # THT IF455 active EW GKG50015 10-50pF trimmer candidate: real ngspice
    # range coverage, not a claim of Q/ESR, mechanical footprint or RF release.
    if (ROOT/"03_Verifiche/V2.7/spice/if455_trimmer_gkg50015_tuning_envelope.cir").exists():
        print("::group::V2.7 IF455 VARIABLE 10TO50PF TRIM THT NATIVE NGSPICE",flush=True)
        subprocess.run([sys.executable,"-B",
                        str(ROOT/"03_Verifiche/V2.7/verify_if455_trimmer_range_ngspice.py")],
                       cwd=ROOT,check=True)
        print("::endgroup::",flush=True)
    print("PASS_FULL_HISTORICAL_22_WORKFLOWS_AND_ALL_NATIVE_KICAD9_GATES",{"executed_commands":executed},flush=True)

if __name__=="__main__":
    main()
