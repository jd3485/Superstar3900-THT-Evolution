#!/usr/bin/env python3
"""Run ALL original 19 KiCad9/ngspice legacy suites in ONE verified KiCad9 container.

The 20th original workflow (verifica_v02) is ALWAYS run in ci/fast_regressions.py.
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
 "cad_native_v22.yml":7,"cad_native_v23.yml":7,
 "boost_v07.yml":2,"ngspice_v14_vco_frontend.yml":2,
 "pll_tristate_v09.yml":2,"vco_spice_v06.yml":8,"vtune_driver_v08.yml":2,
}
EXPECTED_ALL_WORKFLOWS=20
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
        assert "run" in st and not st.get("if"), f"Unexpected conditional run step {name}: {st}"
        seen_run+=1
        cmd=st["run"]
        assert isinstance(cmd,str) and cmd.strip(),(name,st)
        commands.append((st.get("name","Unnamed legacy step"),normalized_command(cmd)))
    assert seen_run==RUN_COUNTS[name],f"{name}: {seen_run} commands not {RUN_COUNTS[name]}"
    return commands

def main()->None:
    assert len(RUN_COUNTS)==19
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
         "plus_fast_suites":10,"deduplicated_install_steps":sum(c is None for steps in compiled.values() for _,c in steps)},flush=True)
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
            print("RUN_REAL_LEGACY_STEP",name,label,flush=True)
            subprocess.run(["bash","-e","-o","pipefail","-c",cmd],cwd=ROOT,
                          env=os.environ.copy(),check=True)
            executed+=1
        print("::endgroup::",flush=True)
    print("PASS_FULL_HISTORICAL_19_WORKFLOWS_AND_ALL_NATIVE_KICAD9_GATES",{"executed_commands":executed},flush=True)

if __name__=="__main__":
    main()
