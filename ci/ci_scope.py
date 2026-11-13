#!/usr/bin/env python3
"""Decide whether a PR changes electrical/EDA/test policy; fail closed on unknowns."""
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path

def is_documentation_only(name: str) -> bool:
    p=Path(name)
    return p.suffix.lower() in {".md", ".rst", ".txt"} and (
        name.startswith("00_Gestione_Progetto/") or
        name.startswith("docs/") or
        name.startswith("03_Verifiche/") or
        name.startswith("04_KiCad/") or
        name in {"RIPRENDI_IN_UNA_NUOVA_CHAT.md", "README.md", "AGENTS.md"}
    )

# Strictly reviewed numerical-only files, *all executed* by fast_regressions.py.
# This is an exact allowlist, not an entire directory or file extension:
# CAD, SPICE, electrical pin-net tests, CI configuration and unknown files
# still require a full native KiCad9/ngspice regression run.
FAST_ONLY_ANALYTICAL = frozenset({
    "03_Verifiche/V2.7/verify_audio_load_envelope.py",
    "03_Verifiche/V2.7/AUDIO_LOAD_ENVELOPE_LM386_6V.csv",
    "03_Verifiche/V2.7/verify_audio_rail_current_graph_v27.py",
    "03_Verifiche/V2.7/LM386_GRAPH_6V_RAIL_CURRENT_BRACKETS.csv",
})

def is_fast_only(name: str) -> bool:
    return is_documentation_only(name) or name in FAST_ONLY_ANALYTICAL

def changed_files(base: str, head: str) -> list[str]:
    if not (base and head and len(base)==40 and len(head)==40):
        raise ValueError("Both full 40-digit base and head SHAs required")
    result=subprocess.run(["git","diff","--name-only","--diff-filter=ACMRTD",base,head],
        check=True,stdout=subprocess.PIPE,text=True)
    return [x for x in result.stdout.splitlines() if x]

def decide(paths: list[str], manual: bool=False) -> bool:
    if manual: return True
    if not paths: raise ValueError("Empty PR diff; refusing to skip checks")
    return any(not is_fast_only(p) for p in paths)

def main() -> None:
    if "--selftest" in sys.argv:
        assert decide(["04_KiCad/V2.4/a.kicad_sch"])
        assert decide([".github/workflows/test.yml"])
        assert decide(["03_Verifiche/V2.4/test.py"])
        assert not decide(["03_Verifiche/V2.7/verify_audio_load_envelope.py"])
        assert not decide(["03_Verifiche/V2.7/AUDIO_LOAD_ENVELOPE_LM386_6V.csv"])
        assert not decide(["03_Verifiche/V2.7/verify_audio_rail_current_graph_v27.py"])
        assert not decide(["03_Verifiche/V2.7/LM386_GRAPH_6V_RAIL_CURRENT_BRACKETS.csv"])
        assert not decide(["03_Verifiche/V2.7/verify_audio_load_envelope.py",
                           "03_Verifiche/V2.7/RAPPORTO_LM386_LM317_ENVELOPE_CARICO_AUDIO.md"])
        # Any mixed CAD, power netlist, ngspice or unknown file forces FULL.
        assert decide(["03_Verifiche/V2.7/verify_audio_load_envelope.py",
                       "04_KiCad/V2.7_DRAFT/AMP.kicad_sch"])
        assert decide(["03_Verifiche/V2.7/verify_audio_load_envelope.py",
                       "03_Verifiche/V2.7/verify_audio_rail_step_ngspice.py"])
        assert decide(["03_Verifiche/V2.7/verify_audio_load_envelope.py",
                       "ci/ci_scope.py"])
        assert decide(["03_Verifiche/V2.7/new_not_allowlisted.csv"])
        assert decide(["03_Verifiche/V2.7/new_not_allowlisted.py"])
        assert decide([".github/workflows/ci_optimized.yml"])
        assert decide(["ci/fast_regressions.py"])
        assert decide(["ci/full_regressions.py"])
        assert not decide(["00_Gestione_Progetto/WORK_STATO_CORRENTE.md"])
        assert not decide(["RIPRENDI_IN_UNA_NUOVA_CHAT.md","03_Verifiche/V2.4/report.md"])
        assert decide(["AGENTS.md",".github/workflows/f.yml"])
        assert decide(["AGENTS.md"],manual=True)
        try: decide([])
        except ValueError: pass
        else: raise AssertionError("Empty-diff skip accepted")
        print("PASS_CI_CHANGE_DETECTION_SELFTEST")
        return
    manual=os.getenv("GITHUB_EVENT_NAME")=="workflow_dispatch"
    paths=["manual full suite"] if manual else changed_files(
        os.environ["BASE_SHA"],os.environ["HEAD_SHA"])
    full=decide(paths,manual)
    output=Path(os.environ["GITHUB_OUTPUT"])
    with output.open("a",encoding="utf-8") as f:
        f.write("full="+("true" if full else "false")+"\n")
    print("CI_SCOPE",{"full":full,"files":paths},flush=True)

if __name__=="__main__":
    main()
