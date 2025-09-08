import os
import subprocess
from pathlib import Path

ANNOTATED_DATA_DIR = "annotated_data"
DATA_DIR = "data"

def main():
    smt2_files = os.listdir(DATA_DIR)
    for smt2_file in smt2_files:
        subprocess.run(f"python annotate_smt_for_unsat_cote.py {os.path.join(DATA_DIR, smt2_file)} -o {os.path.join(ANNOTATED_DATA_DIR, smt2_file)}", shell=True)
        subprocess.run(
            f"python get_trace_core_from_smt.py {os.path.join(ANNOTATED_DATA_DIR, smt2_file)}",
            shell=True)
        smt2_file_without_ext = Path(smt2_file).stem
        subprocess.run(
            f"python get_unsat_core_from_log.py {smt2_file_without_ext}_log",
            shell=True)
        subprocess.run(
            f"mv {smt2_file_without_ext}_log_unsat_core unsat_cores",
            shell=True)
        subprocess.run(
            f"rm {smt2_file_without_ext}_log",
            shell=True)



if __name__ == "__main__":
    main()