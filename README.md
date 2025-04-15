# Parts API with data scrapper
The purpose of this API is to expose alle the data that were available to scrape from https://www.urparts.com/index.cfm/page/catalogue/.

## Dependency management
We're using `uv` to manage our dependencies.

## How to use
There is a Make file with a couple of handy recipes. Let's go through them:
1. `make format` reformats whole codebase using `ruff`;
2. `make check` does static code analysis using `ruff` & `mypy`;
3. `make test` runs test suite for whole application;
4. `make build` builds a Docker image for the application;
5. `make migrate` applies `alembic` migrations to the database;
6. `make scrape` runs the data scraping process;
7. `make up` runs the API;
8. `make down` puts down all Docker containers.

## Scraper
### Solution
We're using `aiohttp` for requesting all the pages in parts catalogue, 
then we use `BeautifulSoup4` to parse the data of interest.  
Everything is being run in an asynchronous context, although not every possible aspect is parallelized.  
Each manufacturer is parsed imperatively (one by one), and then, the categories, models & parts are parsed
in parallel.

There is a semaphore used to prevent abusing the website too much (it was raising Timeouts when).

### Performance
Between 6 - 7 minutes for 4.4M parts (and much fewer manufacturers, categories & models) on 2021 M1 Pro.

### Resources
The task is CPU-bound as of now, so it will consume a lot of CPU. 
Because of the parallelism it's not so IO-bound anymore.

## API
### OpenAPI specification
The OpenAPI specification can be found here: http://localhost:8080/docs after starting the application.

### Structure
Overall structure of the repository & API is based on domains. Each domain has its own category & directory.

For the simplicity of the solution - `service`/`controller` layer wasn't introduced.

### Tests
For demonstration purposes, there's just one test written.  
It won't work if you have any category in the database (there's no schema separation). 