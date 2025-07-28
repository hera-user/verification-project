from abc import ABC, abstractmethod
from typing import Any, List, Dict

class QuantifierInstantiationEngine(ABC):
    """
    Abstract base class for quantifier instantiation strategies,
    such as MBQI, E-matching, etc.
    """

    def __init__(self, formula: Any, model: Dict[str, Any]):
        """
        :param formula: A logical formula, e.g., in SMT-LIB-like structure
        :param model: A current candidate model (e.g., from a solver)
        """
        self.formula = formula
        self.model = model

    @abstractmethod
    def find_instantiations(self) -> List[Any]:
        """
        Returns a list of ground instances (substituted quantifiers)
        based on the specific instantiation strategy.
        """
        pass

    @abstractmethod
    def is_applicable(self) -> bool:
        """
        Check if this instantiation strategy can be applied to the formula.
        """
        pass

    def update_model(self, model: Dict[str, Any]) -> None:
        """
        Updates the model for future instantiations.
        """
        self.model = model
