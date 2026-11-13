#!/usr/bin/env python3
"""Cheap but real legacy Python regressions for every PR (including documents)."""
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSIONS=("V0.1","V0.2","V0.3","V0.4","V0.5","V0.6","V0.7","V0.8","V0.9","V1.0")
for version in VERSIONS:
    path=ROOT/"03_Verifiche"/version
    assert path.is_dir(), f"Missing required regression: {path}"
    print("START_FAST_REGRESSION",version,flush=True)
    subprocess.run([sys.executable,"-B","-m","unittest","discover","-s",str(path),
                    "-p","test_*.py","-v"],cwd=ROOT,check=True)
print("PASS_FAST_LEGACY_UNITTESTS_ALL_TEN_VERSION_SUITES",flush=True)

# Every PR also guards the 138-reference THT lifecycle inventory against CAD drift.
subprocess.run([sys.executable,"-B",str(ROOT/"03_Verifiche/V2.6/verify_mpn_inventory_v26.py")],cwd=ROOT,check=True)

# Pure numerical audio load scenarios run even on docs-only PRs. This is not
# SPICE nor a power-supply certification; it catches inconsistent assumptions
# about speaker impedance, required swing and regulator thermal envelope.
subprocess.run([sys.executable,"-B",str(ROOT/"03_Verifiche/V2.7/verify_audio_load_envelope.py")],
               cwd=ROOT,check=True)
