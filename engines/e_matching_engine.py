from z3 import *
from engines.quantifier_instantiation_engine import  QuantifierInstantiationEngine

class EMatchingEngine(QuantifierInstantiationEngine):
    def __init__(self, formula, model):
        super().__init__(formula, model)

    def is_applicable(self):
        return is_quantifier(self.formula) and self.formula.is_forall()

    def find_instantiations(self):
        # Placeholder: always returns empty
        return []

    def update_model(self, model):
        self.model = model