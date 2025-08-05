from z3 import *
from typing import Dict, List, Any


def parse_inst(s) -> Dict[str, List[Any]]:
    mapping = {}
    pairs = s.split(",")
    for p in pairs:
        var, val = p.split("=")
        var = var.strip()
        val = val.strip()
        if var not in mapping:
            mapping[var] = list()
        if val.lstrip("-").isdigit():
            mapping[var].append(IntVal(int(val)))
        else:
            mapping[var].append(Int(val))
    return mapping