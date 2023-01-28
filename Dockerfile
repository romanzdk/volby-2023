FROM python:3.10

ARG POETRY_VERSION=1.3.2
ENV POETRY_VERSION=$POETRY_VERSION
ENV POETRY_HOME=/usr/local
ENV POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml /usr/src/app/

RUN poetry install --no-root --without dev

COPY . /usr/src/app/

RUN chmod +x entrypoint.sh

ENV PYTHONPATH /usr/src/app

# because of Azure Web App
EXPOSE 8501

CMD ["./entrypoint.sh"]
