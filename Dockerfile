FROM python:3.10

WORKDIR /pxls_auth

RUN pip install poetry==1.1.3
COPY poetry.lock pyproject.toml /pxls_auth/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-dev
COPY ./src /pxls_auth/src

CMD python -m src.main