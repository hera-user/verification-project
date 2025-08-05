import sys
from z3 import *
from partial_substitute import SubBoundVars

class Z3PartialInstantiator:
    def __init__(self, filename, inst_str):
        self.filename = filename
        self.inst_str = inst_str

    def run_z3(self, formulas):
        s = Solver()
        for f in formulas:
            s.add(f)
        res = s.check()
        return res == sat

    def create_label(self):
        print(f"Running Z3 on original file: {self.filename}")
        original_formulas = parse_smt2_file(self.filename)
        is_sat = self.run_z3(original_formulas)
        print(f"Original result: {is_sat}")

        print("\nApplying partial instantiation:", self.inst_str)
        new_formulas = SubBoundVars.substitute_bound_vars(self.filename, self.inst_str)

        print("\nRunning Z3 on partially instantiated formulas")
        is_sat_new = self.run_z3(new_formulas)
        print(f"After instantiation result: {is_sat_new}")
        label = 1 if (not is_sat and not is_sat_new) else 0
        return label

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 partial_instantiate_and_run.py input.smt2 var1=val1,var2=val2,...")
        exit()

    filename = sys.argv[1]
    inst_str = sys.argv[2]

    runner = Z3PartialInstantiator(filename, inst_str)
    runner.create_label()