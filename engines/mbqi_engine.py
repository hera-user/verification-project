from z3 import *
from typing import List
from engines.quantifier_instantiation_engine import  QuantifierInstantiationEngine

class MBQIEngine(QuantifierInstantiationEngine):
    def is_applicable(self) -> bool:
        return is_quantifier(self.formula) and self.formula.is_forall()

    def find_instantiations(self) -> List[ExprRef]:
        quant = self.formula

        # Get variables and body
        num_vars = quant.num_vars()
        vars = [Const(quant.var_name(i), quant.var_sort(i)) for i in range(num_vars)]
        body = quant.body()

        # Reverse vars to match De Bruijn indexing
        subst_body = substitute_vars(body, *reversed(vars))

        # Evaluate body under model with current variable values
        instantiation = []
        substitutions = []

        for v in vars:
            val = self.model.eval(v, model_completion=True)
            substitutions.append(val)

        # Plug in model values into the formula
        ground = substitute_vars(body, *reversed(substitutions))

        s = Solver()
        s.add(Not(ground))  # Check if body fails under model

        if s.check() == sat:
            # Counterexample found — return the instantiation
            instantiated = substitute_vars(body, *reversed(substitutions))
            return [substitute_vars(quant, *reversed(substitutions))]
        else:
            return []