from z3 import *
from engine_factory import QuantifierEngineFactory
import pytest

@pytest.mark.parametrize("engine_type", ["mbqi", "e-matching"])
@pytest.mark.parametrize("file_path", [
    "AUFLIA/misc/arr2.smt2",
    # Add more files here
])
def test_run_quantifier_engine_on_file(file_path, engine_type):
    print(f"\nRunning {engine_type.upper()} on: {file_path}")

    try:
        with open(file_path, "r") as f:
            smt_text = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    try:
        formulas = parse_smt2_string(smt_text, decls={})
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return

    # Run original formula through Z3
    solver = Solver()
    for f in formulas:
        solver.add(f)

    result = solver.check()
    print(f"Z3 says: {result}")

    model = solver.model() if result == sat else None

    # Extract quantifiers
    quantifiers = []
    for f in formulas:
        if f.decl().kind() == Z3_OP_NOT and is_quantifier(f.arg(0)):
            quantifiers.append(f.arg(0))
        elif is_quantifier(f):
            quantifiers.append(f)

    # Run quantifier engine and check agreement
    for q in quantifiers:
        engine = QuantifierEngineFactory.create(engine_type, q, model)
        if not engine.is_applicable():
            print("  Quantifier not applicable.")
            continue

        insts = engine.find_instantiations()
        print(f"  Found {len(insts)} instantiation(s) for: {q}")

        for inst in insts:
            print(f"    → Instantiation: {inst}")

        # Now check whether the instantiations alone yield the same Z3 result
        inst_solver = Solver()
        inst_solver.add(*insts)
        inst_result = inst_solver.check()

        if inst_result == result:
            print("  ✔ Instantiations agree with original Z3 result.")
        else:
            print(f"  ✘ Instantiations do NOT agree: expected {result}, got {inst_result}")