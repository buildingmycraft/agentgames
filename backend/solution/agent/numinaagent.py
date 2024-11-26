import os
from dataclasses import dataclass

import pandas as pd
import torch
from vllm import LLM, SamplingParams

from .base import BaseAgent


@dataclass
class Config:
    model_id: str

    num_samples: int
    num_generations: int

    restart_on_fail: bool

    temperature: float
    max_new_tokens: int

    validation_set: str
    is_submission: bool = bool(os.getenv("KAGGLE_IS_COMPETITION_RERUN"))


class NuminaAgent(BaseAgent):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config
        self._model = self.build_vllm(config)

    @staticmethod
    def build_vllm(config: Config) -> LLM:
        num_gpus = torch.cuda.device_count()
        if "awq" in config.model_id.lower():
            quantization = "AWQ"
        elif "gptq" in config.model_id.lower():
            quantization = "gptq"
        else:
            quantization = None
        
        vllm = LLM(
            model=config.model_id,
            tensor_parallel_size=num_gpus,
            quantization=quantization,
            swap_space=0,
        )
        return vllm
    
    @staticmethod
    def apply_template(data, template, tokenizer):
        return 
    
    def generate(self, prompts: list[str]) -> list[str]:
        sampling_params = SamplingParams(
            temperature=self._config.temperature,
            max_tokens=self._config.max_new_tokens,
            stop=["```output\n"],
            include_stop_str_in_output=True,
        )

        outputs = self._model.generate(
            prompts=prompts,
            sampling_params=sampling_params,
            use_tqdm=True
        )
        generations = [o.prompt + o.outputs[0].text for o in outputs]
        
        return generations

    def score(self, input: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
        assert "answer" in input.columns
        assert "problem" in input.columns

        _input = input.copy()
        _input["generations"] = self.generate(prompts=_input["problem"].to_list())
        _input["predictions"] = 0
        _input["score"] = _input["answer"] == _input["predictions"]
        return _input