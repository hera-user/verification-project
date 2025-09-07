#!/usr/bin/env python3
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    arg = Path(sys.argv[1])
    if arg.suffix.lower() == ".smt2":
        smt_path = arg
        name = smt_path.stem
    else:
        smt_path = arg.with_suffix(".smt2")
        name = arg.name

    smt_path = smt_path.resolve()
    if not smt_path.exists():
        print(f"Error: SMT file not found: {smt_path}")
        sys.exit(2)

    z3 = shutil.which("z3") or shutil.which("z3.exe")
    if not z3:
        print("Error: z3 executable not found on PATH.")
        sys.exit(2)

    trace_name = f"{name}_log"
    cmd = [z3, "trace=true", "proof=true", f"trace_file_name={trace_name}", str(smt_path)]

    try:
        proc = subprocess.run(cmd)
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Error running z3: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()