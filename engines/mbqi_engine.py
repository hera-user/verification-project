from z3 import *
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from engines.quantifier_instantiation_engine import  QuantifierInstantiationEngine
import itertools

class MBQIInstantiator(QuantifierInstantiationEngine):
    """
    Implements Model-Based Quantifier Instantiation for Z3.
    """

    def __init__(self, formula, model, max_iterations: int = 100, verbose: bool = False):
        super().__init__(formula, model)
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.solver = z3.Solver()
        self.quantifiers = []
        self.ground_formulas = []
        self.instantiated_terms = set()

        # Preprocess formula (if it's a list, add all)
        if isinstance(formula, list):
            for f in formula:
                self.add_formula(f)
        else:
            self.add_formula(formula)

    def add_formula(self, formula):
        if self._is_quantifier(formula):
            self.quantifiers.append(formula)
        else:
            self.ground_formulas.append(formula)
            self.solver.add(formula)

    def _is_quantifier(self, formula) -> bool:
        return z3.is_quantifier(formula)

    def _get_model(self) -> Optional[z3.ModelRef]:
        if self.solver.check() == z3.sat:
            return self.solver.model()
        return None

    def _get_universe_values(self, model: z3.ModelRef, sort: z3.SortRef) -> List:
        universe = []
        for decl in model.decls():
            if decl.range() == sort:
                universe.append(model.get_interp(decl))

        if sort.is_int():
            universe.extend([z3.IntVal(i) for i in range(-5, 6)])
        elif sort.is_real():
            universe.extend([z3.RealVal(i) for i in range(-5, 6)])
            universe.extend([z3.RealVal(i)/2 for i in range(-5, 6)])
        elif sort.is_bool():
            universe.extend([z3.BoolVal(True), z3.BoolVal(False)])

        return list(set(map(str, universe)))

    def _instantiate_quantifier(self, quantifier, model: z3.ModelRef) -> List[z3.ExprRef]:
        num_vars = quantifier.num_vars()
        var_sorts = [quantifier.var_sort(i) for i in range(num_vars)]
        var_names = [quantifier.var_name(i) for i in range(num_vars)]
        body = quantifier.body()
        universe_values = [self._get_universe_values(model, sort) for sort in var_sorts]

        instantiations = []
        for values in itertools.product(*universe_values):
            if tuple(values) in self.instantiated_terms:
                continue
            self.instantiated_terms.add(tuple(values))
            subst = []

            for name, sort, value in zip(var_names, var_sorts, values):
                if sort.is_int():
                    val = z3.IntVal(int(value))
                elif sort.is_real():
                    if '/' in value:
                        num, denom = value.split('/')
                        val = z3.RealVal(int(num)) / z3.RealVal(int(denom))
                    else:
                        val = z3.RealVal(float(value))
                elif sort.is_bool():
                    val = z3.BoolVal(value == 'True')
                else:
                    val = None
                    for decl in model.decls():
                        if str(model.get_interp(decl)) == value:
                            val = model.get_interp(decl)
                            break
                    if val is None:
                        continue
                const = z3.Const(name, sort)
                subst.append((const, val))

            instance = z3.substitute(body, subst)
            if self.verbose:
                print(f"Generated instance: {instance}")
            instantiations.append(instance)

        return instantiations

    def find_instantiations(self) -> List[Any]:
        model = self._get_model()
        if not model:
            return []

        all_instances = []
        for q in self.quantifiers:
            instances = self._instantiate_quantifier(q, model)
            all_instances.extend(instances)
        return all_instances

    def is_applicable(self) -> bool:
        return len(self.quantifiers) > 0

    def solve(self) -> Tuple[z3.CheckSatResult, Optional[z3.ModelRef]]:
        iteration = 0
        while iteration < self.max_iterations:
            if self.verbose:
                print(f"MBQI Iteration {iteration}")

            check_result = self.solver.check()
            if check_result != z3.sat:
                return check_result, None

            model = self.solver.model()
            all_satisfied = True
            new_instances = []

            for quantifier in self.quantifiers:
                is_universal = z3.is_quantifier(quantifier) and not quantifier.is_exists()
                instances = self._instantiate_quantifier(quantifier, model)

                for instance in instances:
                    value = model.eval(instance, model_completion=True)
                    if (is_universal and value == z3.BoolVal(False)) or \
                       (not is_universal and value == z3.BoolVal(True)):
                        if is_universal:
                            new_instances.append(instance)
                            all_satisfied = False

            if all_satisfied:
                return z3.sat, model

            for instance in new_instances:
                self.solver.add(instance)

            iteration += 1

        return z3.unknown, None

    def check_sat(self) -> z3.CheckSatResult:
        result, _ = self.solve()
        return result

    def get_model(self) -> Optional[z3.ModelRef]:
        result, model = self.solve()
        return model if result == z3.sat else None


def mbqi_solve(formulas, max_iterations=100, verbose=False) -> Tuple[z3.CheckSatResult, Optional[z3.ModelRef]]:
    mbqi = MBQIInstantiator(formulas, {}, max_iterations=max_iterations, verbose=verbose)
    return mbqi.solve()
