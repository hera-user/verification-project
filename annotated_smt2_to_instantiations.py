import subprocess
import argparse

PATH_TO_Z3_TRACER = "/root/verfication/qifac/submodules/smt2utils/target/release/z3tracer"

def run_z3_with_trace(smt_path: str, log_path: str):
    """
    Run Z3 with trace logging enabled.
    """
    subprocess.run(["z3", "trace=true", f"trace_file_name={log_path}", smt_path]
    )
    print(f"Z3 trace written to {log_path}")



def run_z3tracer(trace_path: str, out_path: str):
    """
    Run z3tracer to process the trace log.
    """
    subprocess.run(
        [PATH_TO_Z3_TRACER,  "--skip-z3-version-check", "--detailed-instantiation", out_path, trace_path],
        )
    print(f"Instantiations extracted to {out_path}")


def main(smt2_path: str = "inner2.smt2", output_path: str = "instantiations"):

    run_z3_with_trace(smt2_path, "temp")
    run_z3tracer("temp", output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Z3 with tracing and process with z3tracer.")
    parser.add_argument("smt2_path", nargs="?", default="inner2.smt2", help="Path to the SMT2 file")
    parser.add_argument("output_path", nargs="?", default="instantiations", help="Output path for instantiations")
    args = parser.parse_args()
    main(args.smt2_path, args.output_path)

