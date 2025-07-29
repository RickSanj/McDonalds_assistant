To-do list:

- parse menu 
- validate state of the order
- testing 

- async
- REST API 

if it doesn't pass the validation, the system should ask the user to specify the order again, and discard the LLM output.

run:
poetry run python src/main.py

poetry run python -m unittest discover -s tests
