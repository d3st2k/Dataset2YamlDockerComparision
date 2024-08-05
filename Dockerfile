FROM openjdk:11 AS base

ARG PYTHON_VERSION='3.10'
ARG INPUT_FOLDER="Input CSV Metadata"

WORKDIR /app

COPY ${INPUT_FOLDER}/20240101_metadata.csv /app/
COPY ${INPUT_FOLDER}/syntheticDataset.csv /app/
COPY ${INPUT_FOLDER}/syntheticDataset10K.csv /app/
COPY ${INPUT_FOLDER}/syntheticDataset100K.csv /app/
COPY requirements.txt /app/
COPY Generators/PySparkParallelGeneratorSpeed.ipynb /app/

# --- Set environment variables
ENV HOME=/app
ENV PYENV_ROOT=$HOME/.pyenv
ENV PYTHON_VERSION=$PYTHON_VERSION
ENV PATH=$PYENV_ROOT/shims:$PATH:$PYENV_ROOT/bin
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# --- Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    git

# --- Install pyenv
RUN curl https://pyenv.run | bash

# --- Set up pyenv environment
ENV PATH="$PYENV_ROOT/bin:$PATH"
RUN pyenv install $PYTHON_VERSION
RUN pyenv global $PYTHON_VERSION
RUN pyenv rehash

# ---- Install the needed packages and jupyter to run the notebooks
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install jupyter

# --- Expose the port Jupyter Notebook will run on
EXPOSE 8888

# --- Run the notebook and start the Jupyter Notebook server
CMD /bin/bash -c "\
    jupyter nbconvert --to notebook --execute /app/PySparkParallelGeneratorSpeed.ipynb --output /app/PySparkParallelGeneratorSpeed_output.ipynb && \
    jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root"