#!/usr/bin/env python3
"""IF455 Touchstone 2-port measurement ingest and termination mathematics.

No OEM data is embedded or fabricated. In selftest a synthetic passive series
resistor network checks real/imag S-parameter indexing, impedance conversion,
and loaded Vout/Vsource against independent circuit algebra. Real datasets
must be traceable to an instrument and sample; validation != qualification.
"""
from __future__ import annotations
import argparse
import cmath
import math
from pathlib import Path
import tempfile

MULTIPLIERS={"HZ":1,"KHZ":1e3,"MHZ":1e6,"GHZ":1e9}

def parse_s2p(path:Path):
    """Touchstone v1 2-port, RI/MA/DB; standard order S11,S21,S12,S22."""
    unit="GHZ"
    representation="MA"
    ref=50.0
    records=[]
    pending=[]
    for raw in path.read_text(encoding="utf-8").splitlines():
        line=raw.split("!",1)[0].strip()
        if not line:
            continue
        if line.startswith("["):
            raise ValueError("Touchstone v2 keywords require explicit converter")
        if line.startswith("#"):
            assert not records and not pending
            tokens=line[1:].upper().split()
            assert len(tokens)>=3 and tokens[1]=="S",tokens
            unit,representation=tokens[:1][0],tokens[2]
            assert unit in MULTIPLIERS and representation in ("RI","MA","DB")
            if "R" in tokens:
                ref=float(tokens[tokens.index("R")+1])
            assert math.isfinite(ref) and ref>0
            continue
        pending.extend(float(x) for x in line.split())
        while len(pending)>=9:
            nums=pending[:9]
            pending=pending[9:]
            assert all(math.isfinite(x) for x in nums)
            freq=nums[0]*MULTIPLIERS[unit]
            assert freq>0 and (not records or freq>records[-1][0])
            def value(a,b):
                if representation=="RI":
                    return complex(a,b)
                magnitude=10**(a/20) if representation=="DB" else a
                assert magnitude>=0 and math.isfinite(magnitude)
                return cmath.rect(magnitude,math.radians(b))
            # Explicit touchstone v1 2-port network ordering.
            s11=value(nums[1],nums[2])
            s21=value(nums[3],nums[4])
            s12=value(nums[5],nums[6])
            s22=value(nums[7],nums[8])
            records.append((freq,s11,s21,s12,s22))
    assert not pending,"Truncated S2P record"
    assert records,"No S2P data"
    return ref,records

def terminated_port(row,z0,zload):
    """Source is matched to z0; load arbitrary passive complex impedance."""
    f,s11,s21,s12,s22=row
    assert z0>0 and zload.real>0
    gamma=(zload-z0)/(zload+z0)
    denominator=1-s22*gamma
    assert abs(denominator)>1e-9
    gin=s11+s12*s21*gamma/denominator
    assert abs(1-gin)>1e-9
    zin=z0*(1+gin)/(1-gin)
    # a1=Vs/(2*sqrt(z0)), a2=gamma*b2, b2=S21*a1/(1-S22*gamma).
    # Vload/Vs = S21*(1+gamma)/(2*(1-S22*gamma)).
    transfer=s21*(1+gamma)/(2*denominator)
    return zin,transfer

def synthetic_series_twoport(r,z0,f):
    # Series-only reciprocal two-port, reference z0 on BOTH ports.
    return (f,complex(r/(2*z0+r)),complex(2*z0/(2*z0+r)),
            complex(2*z0/(2*z0+r)),complex(r/(2*z0+r)))

def fmt(x):
    return f"{x.real:.12e} {x.imag:.12e}"

def selftest():
    samples=0
    with tempfile.TemporaryDirectory(prefix="if455_s2p_fixture_") as td:
        root=Path(td)
        for encoding in ("RI","MA","DB"):
            lines=[f"# kHz S {encoding} R 2000"]
            for f in (445000,455000,465000):
                _,a,b,c,d=synthetic_series_twoport(100,2000,f)
                def pack(z):
                    if encoding=="RI": return fmt(z)
                    deg=math.degrees(cmath.phase(z))
                    magnitude=abs(z) if encoding=="MA" else 20*math.log10(abs(z))
                    return f"{magnitude:.14g} {deg:.14g}"
                lines.append(f"{f/1000} {pack(a)} {pack(b)} {pack(c)} {pack(d)}")
            path=root/f"fixture_{encoding}.s2p"
            path.write_text("\n".join(lines)+"\n",encoding="utf-8")
            z0,rows=parse_s2p(path)
            assert z0==2000 and len(rows)==3
            for row in rows:
                for load in (1500+0j,2000+0j,2000-350j):
                    zin,transfer=terminated_port(row,z0,load)
                    # Independent Kirchhoff series-resistor reference:
                    # Zin = Rseries+ZL, Vload/Vs = ZL/(Z0+Rseries+ZL).
                    expected_zin=100+load
                    expected_transfer=load/(z0+100+load)
                    assert abs(zin-expected_zin)<1e-6,(encoding,zin,expected_zin)
                    assert abs(transfer-expected_transfer)<1e-9,(
                        encoding,transfer,expected_transfer)
                    samples+=1
        bad=root/"truncated.s2p"
        bad.write_text("# Hz S RI R 2000\n455000 0 0 1 0 1\n",encoding="utf-8")
        try:
            parse_s2p(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("Incomplete measurement accepted")
    assert samples==27
    print("PASS_IF455_TOUCHSTONE_TWO_PORT_27_ANALYTICAL_TERMINATION_TESTS_NO_OEM_NO_FAB_NO_TX",
          {"analytical_crosschecks":samples,"synthetic_only":True},flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--measurement",type=Path,help="External calibrated .s2p; never treated as OEM qualified automatically")
    p.add_argument("--load-real-ohm",type=float,default=2000)
    p.add_argument("--load-imag-ohm",type=float,default=0)
    args=p.parse_args()
    selftest()
    if args.measurement:
        z0,records=parse_s2p(args.measurement)
        assert 100e3<=records[0][0]<=records[-1][0]<=10e6
        assert len(records)>=3,"Need multiple measured frequency points"
        load=complex(args.load_real_ohm,args.load_imag_ohm)
        for row in records:
            zin,gain=terminated_port(row,z0,load)
            assert math.isfinite(zin.real) and math.isfinite(zin.imag)
            print("IF455_EXTERNAL_UNQUALIFIED_S2P_TERMINATED",{
                "frequency_Hz":row[0],"Zin_real_ohm":zin.real,
                "Zin_imag_ohm":zin.imag,"loaded_gain_mag":abs(gain),
                "loaded_gain_phase_deg":math.degrees(cmath.phase(gain)),
                "requires_sample_calibration_oem_review":True},flush=True)

if __name__=="__main__":
    main()
