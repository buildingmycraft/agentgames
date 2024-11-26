import os
from abc import ABC

import pandas as pd


class BaseDataset(ABC):
    pass


class MathQSADataset(ABC):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def load(cls, directory: str | None = None) -> tuple[pd.DataFrame, ...]:
        if not directory:
            CURR_DIRECTORY = os.path.dirname(__file__)
            directory = os.path.join(CURR_DIRECTORY, "datasets/math-qsa-dataset") 
        train_data_path = os.path.join(directory, "test.csv")
        test_data_path = os.path.join(directory, "train.csv")

        train_df = pd.read_csv(train_data_path)
        test_df = pd.read_csv(test_data_path)

        return train_df, test_df