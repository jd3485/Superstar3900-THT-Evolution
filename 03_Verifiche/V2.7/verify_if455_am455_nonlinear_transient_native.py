#!/usr/bin/env python3
"""Execute the nonlinear IF455/AM455 behavioral transient in native ngspice.
Only guards that a simulation actually ran and returned finite nonzero AF;
this is NOT an OEM diode qualification or acceptance of direct coupling.
"""
from pathlib import Path
import math
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "03_Verifiche/V2.7/spice/if455_am455_nonlinear_transient_generic.cir"

def main():
    content = DECK.read_text(encoding="utf-8")
    for required in (".model DGENERIC", "D1501 out envelope DGENERIC",
                     "C1602 tank 0 82p", "C1603 tank 0 30p",
                     "L1601 tank ltail 1m", "RCOIL ltail 0 16.5",
                     "C1604 tank out 10p", "R1602 out 0 100k",
                     "C1501 envelope 0 1n", "NO FAB/NO TX"):
        assert required in content, ("Deck contract changed", required)
    with tempfile.TemporaryDirectory(prefix="tht_if455_am455_nonlin_") as td:
        log_path = Path(td) / "native.log"
        proc = subprocess.run(["ngspice", "-b", "-o", str(log_path), str(DECK)],
                              cwd=td, text=True, capture_output=True)
        log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
        print("NGSPICE_STDERR", proc.stderr[-1000:], flush=True)
        print("NGSPICE_LOG", log[-2500:], flush=True)
        proc.check_returncode()
        assert "Error:" not in log and "fatal" not in log.lower(), "ngspice error"
    values = {}
    for label in ("coupled_max", "coupled_min", "direct_max", "direct_min", "rf_out_peak"):
        match = re.search(r"(?im)^\\s*" + label + r"\\s*=\\s*([+-]?(?:\\d+\\.?\\d*|\\.\\d+)(?:[eE][+-]?\\d+)?)", log)
        assert match, ("Missing measured native transient result", label)
        values[label] = float(match.group(1))
        assert math.isfinite(values[label]), label
    coupled_pp = values["coupled_max"] - values["coupled_min"]
    direct_pp = values["direct_max"] - values["direct_min"]
    assert coupled_pp > 0 and direct_pp > 0, ("No recovered 1kHz waveform", values)
    assert values["rf_out_peak"] > 0, ("No positive RF output peak", values)
    print("IF455_AM455_GENERIC_TRANSIENT_PP_VOLTAGES",
          {"coupled_af_pp_V": coupled_pp, "direct_reference_af_pp_V": direct_pp,
           "ratio_model_only": coupled_pp/direct_pp,
           "rf_out_positive_peak_V": values["rf_out_peak"]}, flush=True)
    print("PASS_NGSPICE_GENERIC_DIODE_TRANSIENT_NOT_OEM_NOT_HARDWARE_NO_FAB_NO_TX", flush=True)

if __name__ == "__main__":
    main()
