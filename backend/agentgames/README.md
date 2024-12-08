# Agent Games Python API

Here's a sketch of how the python API design:
```python
### Agentgames general API
from agentgames.logging import FileLogger, PostgresLogger, CompositeLogger

from agentgames.models import (
    NuminaModel,
    OpenAIModel,
    LocalInferenceServer,
    RemoteInferenceServer,
    LocalTrainingServer,
    RemoteTrainingServer,
)

from agentgames.graph import (
    AgentGraph,
    RandomChoice,
    PromptGenerator,
    InferenceGenerator,
    CodeExecutor,
    Start,
    End,
)

from agentgames.train import (
    RecallBuffer,
    RLTrainer,
    ModelCheckpointer,
    Evaluator,
)

# AIMO specific
from agentgames.aimo.graph import AnswerExtractor, openai_prompt_template, numina_prompt_template

# From huggingface
from datasets import load_dataset


### Logging
# create a logger that you can attach to events in solver graph
file_logger = FileLogger(outpath=log_outpath)

# create a logger that writes to an external database for persistence
db_logger = PostgresLogger(**db_connection_params)

# combine loggers to pass to agents
logger = CompositeLogger([file_logger, db_logger])

# create a streaming dashboard to see events live
file_logger.stream()


### Models
# create a large language model specification to use for inference
numina_model = NuminaModel(**numina_model_config)

# can also interface with closed models running on a different server
openai_model = OpenAIModel(**gpt_model_config)

# create inference server which manages batching, optimizing and running inference generation
inference_server = RemoteInferenceServer(**remote_connection_params)  # send requests to run on a remote server
inference_server = LocalInferenceServer()  # or run locally
inference_server.register([
    ("numina", numina_model),
    ("openai", openai_model),
])

### Construct inference graph

# define agent graph for single inference
inference_agent_graph = AgentGraph(
    "inference_agent_graph",
    logger=logger,
)

# define graph nodes
# let's use two different prompt templates based on randomly selected model to demonstrate branching
model_picker = RandomChoice(p=[0.5, 0.5], choices=["openai", "numina"], output="model")
numina_prompt_generator = PromptGenerator(template=numina_prompt_template)
openai_prompt_generator = PromptGenerator(template=openai_prompt_template)
inferencer = InferenceGenerator(model=lambda state: state.get("model"), server=inference_server)
code_parser = CodeParser()
code_executer = CodeExecuter()
answer_extractor = AnswerExtractor()

# add nodes
inference_agent_graph.add_nodes([
    ("START", Start()),
    ("model_picker", model_picker),
    ("openai_prompt_generator", openai_prompt_generator),
    ("numina_prompt_generator", numina_prompt_generator),
    ("inferencer", inferencer),
    ("code_parser", code_parser),
    ("code_executer", code_executer),
    ("answer_extractor", answer_extractor),
    ("terminal_answer_extractor", answer_extractor),
    ("END", End()),
])

# connect edges
inference_agent_graph.add_edge("START", "model_picker")
inference_agent_graph.add_conditional_edge(
    source="model_picker",
    path=lambda state: state.get("model"),
    path_map={"openai": "openai_prompt_generator", "numina": "numina_prompt_generator"}
)
inference_agent_graph.add_edge("numina_prompt_generator", "inferencer")
inference_agent_graph.add_edge("openai_prompt_generator", "inferencer")
inference_agent_graph.add_edge("inference", "code_parser")
inference_agent_graph.add_conditional_edge(
    source="code_parser",
    path=lambda state: "code_executer" if state.get("code") else "answer_extractor",
)
inference_agent_graph.add_edge("code_executer", "answer_extractor")
inference_agent_graph.add_conditional_edge(
    source="answer_extractor",
    path=lambda state: "inferencer" if state.get("answer") else "END",
)
inference_agent_graph.add_edge("terminal_answer_extractor", "END")

# add global constraints on graph execution
inference_agent_graph.add_constraint(
    "max_inferencer_calls",
    MaxNodeVisits("inferencer", max_visits=3),
    path="terminal_answer_extractor",
)

# compile graph for safety checks and optimizations before running
inference_agent_graph.compile()

# visualize agent graph
inference_agent_graph.plot()
          
# run replications of inference for self-consistency
consensus_agent_graph = AgentGraph(
    "consensus_agent_graph",
    logger=logger,  
)

replicator = Replicator(node=inference_agent_graph, n=n_replications)
consensus_reducer = ConsensusReducer("consensus_reducer")

consensus_agent_graph.add_node("START", Start())
consensus_agent_graph.add_node("replicator", replicator)
consensus_agent_graph.add_node("reducer", consensus_reducer)
consensus_agent_graph.add_node("END", End())

consensus_agent_graph.add_edge("START", "replicator")
consensus_agent_graph.add_edge("replicator", "reducer")
consensus_agent_graph.add_edge("reducer", "END")

# compile graph for safety checks and optimizations before running
consensus_agent_graph.compile()

# visualize agent graph
consensus_agent_graph.plot()


### Load dataset
dataset = load_dataset(path="../solution/datasets/math-qsa-dataset/", data_files="train.csv", split="train")

# run graph on dataset
inference_results = dataset.map(
    lambda task: consensus_agent_graph(
        State(
            problem=task["problem"],
            # answer is not strictly required for inference
            # included for convenience in evaluating answers later
            answer=task["answer"],
        )
    ),
)


### Expected results (State) output object format
n_tasks_to_print = 3
n_replications_to_print = 3
for result in results[:n_tasks_to_print]:
    print(f"Solution to {result.problem=}:")
    print(f"{result.avg_accuracy=}")
    for replication in result.replications[:n_tasks_to_print]:
        print(f"{replication.gen_text=}")
        print(f"{replication.gen_answer=}")
        print(f"{replication.answer=}")


### Specify an RL training loop
n_epochs = 3                      # how many times to attempt the full dataset
new_batch_size = 1                # how many new problems to attempt in each training batch
n_attempts = 20                   # how many attempts per new problem
positive_recall_batch_size = 10   # how many old correct attempts to recall in training batch
negative_recall_batch_size = 10   # how many old incorrect attempts to recall in training batch 
max_buffer_size = 10_000          # how many past samples to keep in buffer (FIFO)
checkpointing_frequency = 1000    # after how many training steps to save model

trainable_model = ...
training_server.register([("trainable_model", trainable_model)])

recall_buffer = RecallBuffer(
    preload=inference_results,  # optinally preload recall buffer with previous inference results
    positive_recall_batch_size=positive_recall_batch_size,
    negative_recall_batch_size=negative_recall_batch_size,
)
checkpointer = ModelCheckpointer(outdir=checkpoint_dir, frequency=checkpointing_frequency)
evaluater = Evaluator(dataset=eval_dataset, metrics=metrics, frequency=eval_frequency)

trainer = RLTrainer(
    model="trainable_model",
    server=inference_server,
    recall_buffer=recall_buffer,
    callbacks=[checkpointer, evaluater],
    trainable_params=trainable_params,  # specify params to train
    **training_hyperparams,             # specify additional hyperparameters for training
)

for _ in range(n_epochs):
    inference_batches = dataset.map(
        lambda task: inference_agent_graph(
            State(problem=task["problem"], answer=task["answer"])
        ),
        batched=True,
        batch_size=new_batch_size,
    )
    for batch in inference_batches:
        recall_buffer.add(results_batch)
        trainer.step()


### Clean up to release resources
inference_server.close()
training_server.close()


### Serialize graphs so they can be loaded to / from file or string | Helpful for experiment logging and replication
graph_specification = consensus_agent_graph.serialize(output=graph_specification_file)
consensus_agent_graph = AgentGraph.from_file(graph_specification_file)
consensus_agent_graph = AgentGraph.from_string(graph_specification)


### TODO: Experiments management using Aim (https://aimstack.io/)
```
