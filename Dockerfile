FROM python:3.10

ARG POETRY_VERSION=1.3.2
ENV POETRY_VERSION=$POETRY_VERSION
ENV POETRY_HOME=/usr/local
ENV POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml /usr/src/app/

RUN poetry install --no-root

COPY . /usr/src/app/

RUN chown -R nobody /usr/src/app/

RUN usermod --home /tmp nobody
USER nobody

ENV PYTHONPATH /usr/src/app

CMD ["streamlit", "run", "app/application.py"]
