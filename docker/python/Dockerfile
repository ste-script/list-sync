FROM python:3.13
ENV POETRY_HOME=/opt/poetry
RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install poetry==2.0.0 \
    && mkdir -p ~/.local/bin \
    && ln -s $POETRY_HOME/bin/poetry ~/.local/bin/poetry \
    && $POETRY_HOME/bin/poetry --version
ENV PATH="${PATH}:${POETRY_HOME}/bin"

WORKDIR /app