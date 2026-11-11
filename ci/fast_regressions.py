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
