FROM tiangolo/uvicorn-gunicorn:python3.11

WORKDIR /wetin_dey_sup_backend

COPY pyproject.toml poetry.lock /wetin_dey_sup_backend/
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . /wetin_dey_sup_backend