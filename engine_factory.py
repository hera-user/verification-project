from engines.mbqi_engine import MBQIEngine
from engines.e_matching_engine import EMatchingEngine


class QuantifierEngineFactory:
    @staticmethod
    def create(engine_type: str, formula, model):
        engine_type = engine_type.lower()
        if engine_type == "mbqi":
            return MBQIEngine(formula, model)
        elif engine_type == "e-matching":
            return EMatchingEngine(formula, model)
        else:
            raise ValueError(f"Unknown engine type: '{engine_type}'")

    @staticmethod
    def available_engines():
        return ["mbqi", "e-matching"]