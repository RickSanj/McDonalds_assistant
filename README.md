This project is a command-line AI assistant that takes natural language food orders and processes them using an LLM, following McDonald's-style menu and business logic.

Prerequisites:
- Python 3.12+
- Poetry
- Docker + Docker Compose

How to run:
Locally:
```
poetry run python src/main.py
```
In docker:
```
docker-compose run --rm --service-ports mcdonalds-app
```


I would like one McChicken burger without Mayo and Apple Juice

The smallest you have 

yes

yes, BBQ sauce

Chocolate Chip Cookie