import argparse
import subprocess
import sys
import shutil
import os
from pathlib import Path

TRACER_PATH = r"/home/itamaben/verification/qifac/submodules/smt2utils/target/release/z3tracer"

def main():
    parser = argparse.ArgumentParser(description="Run Z3 tracer on an SMT file.")
    parser.add_argument("name", help="Path to the input SMT file (<NAME>).")
    args = parser.parse_args()

    inp = Path(args.name).resolve()
    if not inp.exists():
        print(f"Input file not found: {inp}", file=sys.stderr)
        sys.exit(2)

    # Derive <NAME_UNSAT_CORE> as <stem>_unsat_core (no extension)
    unsat_core = inp.with_name(f"{inp.stem}_unsat_core")

    tracer = TRACER_PATH
    cmd = [tracer, "--flat-instantiations", str(unsat_core), "--skip-z3-version-check", str(inp)]

    try:
        proc = subprocess.run(cmd, check=False)
        sys.exit(proc.returncode)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(127)
    except Exception as e:
        print(f"Failed to run z3tracer: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()