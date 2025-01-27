FROM python:3.13
ENV POETRY_HOME=/opt/poetry
RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install poetry==2.0.0 \
    && mkdir -p ~/.local/bin \
    && ln -s $POETRY_HOME/bin/poetry ~/.local/bin/poetry \
    && $POETRY_HOME/bin/poetry --version
RUN apt-get update && apt-get install -y iproute2 iputils-ping
ENV PATH="${PATH}:${POETRY_HOME}/bin"
RUN rm -rf /var/lib/apt/lists/*
WORKDIR /app