FROM python:3.12-alpine

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY src ./src
COPY README.md .  
COPY .env .  

RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "src/main.py"]
