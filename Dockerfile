FROM python:3.12-alpine
RUN pip install poetry
COPY /src .
RUN poetry install

ENTRYPOINT ["poetry", "run", "python", " src/main.py"]