import logging
import sys

from .agent import NuminaAgent, Config
from .data import MathQSADataset


stdout_handler = logging.StreamHandler(stream=sys.stdout)
logging.basicConfig(
    level=logging.INFO,
    handlers=[stdout_handler],
)
logger = logging.getLogger("Agent")


if __name__ == "__main__":
    train_df, test_df = MathQSADataset.load()
    logger.info(f"Loaded training data with {len(train_df)} rows and test data {len(test_df)}")    
    
    config = Config(
        model_id = "AI-MO/NuminaMath-7B-TIR-GPTQ",
        num_samples=48,
        num_generations=4,
        restart_on_fail=True,
        temperature=0.8,
        max_new_tokens=2048,
        validation_set="AI-MO/aimo-validation-amc",
    )

    agent = NuminaAgent(config=config)
    output = agent.score(test_df.sample(5))
    logger.info(f"Produced {len(output)} predictions with an average score of {sum(output["score"]) / len(output["score"])}")

    for o in output["generations"]:
        print(o)
        print()