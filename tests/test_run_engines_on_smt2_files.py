from z3 import *
from engine_factory import QuantifierEngineFactory
import pytest

@pytest.mark.parametrize("engine_type", ["mbqi", "e-matching"])
@pytest.mark.parametrize("file_path", [
    "AUFLIA/misc/arr2.smt2",
    # Add more files here
])
def test_run_quantifier_engine_on_file(file_path, engine_type):
    print(f"Running {engine_type.upper()} on: {file_path}")
    with open(file_path, "r") as f:
        smt_text = f.read()

    try:
        formulas = parse_smt2_string(smt_text, decls={})

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    solver = Solver()
    for f in formulas:
        solver.add(f)

    result = solver.check()
    model = solver.model()
    print(f"Z3 says: {result}")

    quantifiers = []
    for f in formulas:
        if f.decl().kind() == Z3_OP_NOT and is_quantifier(f.arg(0)):
            quantifiers.append(f.arg(0))
        elif is_quantifier(f):
            quantifiers.append(f)

    for q in quantifiers:
        engine = QuantifierEngineFactory.create(engine_type, q, model)
        if engine.is_applicable():
            insts = engine.find_instantiations()
            print(f"  Found {len(insts)} counterexample(s) for: {q}")
            for inst in insts:
                print(f"    → Instantiation: {inst}")
        else:
            print("  Quantifier not applicable.")
