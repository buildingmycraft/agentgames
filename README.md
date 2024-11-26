# Agent Games

## Developer Notes

Project components:
- frontend [in progress]: specifies the front end of the application which allows interacting with agents
- backend [in progress]: specifies the backend container application which runs agent inference
- CDK app [not started]: using aws cloud development kit, specifies the infrastructure required to run the agent games application


### Local environment setup

To install and activate the development environment using conda:
```bash
conda env create -f backend/environment.yml --no-builds
conda activate agentgames
```

### Data download

#### Kaggle

We'll be downloading data from kaggle using the kaggle cli, installed already in the conda environment. However, we also need to set up our kaggle credentials, following the instructions [here](https://github.com/Kaggle/kaggle-api/blob/main/docs/README.md#api-credentials).

The kaggle dataset has already been committed to this repo for convenience, given it's small size. However, to (re)download the kaggle dataset using the kaggle api, you can run:

```bash
kaggle competitions download -c ai-mathematical-olympiad-progress-prize-2
unzip ai-mathematical-olympiad-progress-prize-2.zip -d kaggle
```

We'll also be using supplementary datasets on kaggle e.g. `awsaf49/math-qsa-dataset`, which you can download via:

```bash
kaggle datasets download awsaf49/math-qsa-dataset
mkdir backend/solution/datasets
unzip math-qsa-dataset.zip -d backend/solution/datasets/math-qsa-dataset
rm math-qsa-dataset.zip  # optionally, clean up redundant zip file
```