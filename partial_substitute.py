import sys
from z3 import *
from utils import parse_inst
from itertools import product

class SubBoundVars:

    @staticmethod
    def _substitute_bound_vars_in_quant(quant, subst_map):
        """
        Substitute bound variables by name inside a quantifier.
        Returns a new quantifier or formula.
        """
        assert is_quantifier(quant)

        num_vars = quant.num_vars()
        var_names = [(quant.var_name(i), quant.var_sort(i)) for i in range(num_vars)]
        # var_sorts = [quant.var_sort(i) for i in range(num_vars)]

        subs = []
        remaining_vars = []

        # De Bruijn indices go from innermost=0 to outermost=num_vars-1,
        # but quant.var_name(i) enumerates from outermost=0 to innermost=num_vars-1,
        # so we reverse the index to get correct Var index.
        for i, (name, sort) in enumerate(var_names):
            idx = num_vars - 1 - i
            if name in subst_map:
                subs.append((Var(idx, sort), subst_map[name]))
            else:
                remaining_vars.append((name, sort))

        new_body = substitute(quant.body(), *subs)
        new_body = SubBoundVars._substitute_bound_vars_rec(new_body, subst_map)  # recurse inside body

        if quant.is_forall():
            if remaining_vars:
                syms = [Const(name, sort) for name, sort in remaining_vars]
                return ForAll(syms, new_body)
            else:
                return new_body
        elif quant.is_exists():
            if remaining_vars:
                syms = [Const(name, sort) for name, sort in remaining_vars]
                return Exists(syms, new_body)
            else:
                return new_body
        else:
            raise Exception("Unsupported quantifier type")

    @staticmethod
    def _substitute_bound_vars_rec(expr, subst_map):
        """
        Recursively traverse expr, substituting bound variables in quantifiers.
        """
        if is_quantifier(expr):
            num_vars = expr.num_vars()
            var_names = [expr.var_name(i) for i in range(num_vars)]
            items_to_iterate = [[(var_name, value) for value in subst_map[var_name]] for var_name in var_names]
            sats_to_concat = list()
            for item in product(*items_to_iterate):
                new_subst_map = subst_map.copy()
                for var_list in item:
                    new_subst_map[var_list[0]] = var_list[1]
                sats_to_concat.append(SubBoundVars._substitute_bound_vars_in_quant(expr, new_subst_map))

            quantifier_to_return = And(*sats_to_concat) if expr.is_forall() else Or(*sats_to_concat)
            return quantifier_to_return

        if expr.num_args() == 0:
            # leaf node
            return expr

        new_args = [SubBoundVars._substitute_bound_vars_rec(expr.arg(i), subst_map) for i in range(expr.num_args())]

        return expr.decl()(*new_args)

    @staticmethod
    def substitute_bound_vars(filename, inst_str):

        # Parse substitution string like "X=3,Y=d"
        subst_map = parse_inst(inst_str)

        formulas = parse_smt2_file(filename)

        new_formulas = [SubBoundVars._substitute_bound_vars_rec(f, subst_map) for f in formulas]

        return new_formulas

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 partial_instantiate_smt2.py input.smt2 var1=val1,var2=val2,...")
        exit()

    filename = sys.argv[1]
    inst_str = sys.argv[2]
    SubBoundVars.substitute_bound_vars(filename, inst_str)
