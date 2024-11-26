from abc import ABC, abstractmethod

import pandas as pd


class BaseAgent(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def score(self, input: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
        pass
