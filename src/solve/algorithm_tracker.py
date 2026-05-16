from dataclasses import dataclass

@dataclass
class AlgorithmTracker:
    basic_operations: int=0
    start_time: float=0.0
    end_time: float=0.0
    solutions_tested: int=0