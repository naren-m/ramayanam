DOCKER_IMAGE_NAME := narenm/ramayanam
DOCKER_IMAGE_TAG := latest

.PHONY: help clean build push compose test format coverage coverage-html coverage-xml clean-coverage clean-pyc autopep _autopep lint profile portainer

.DEFAULT: help

help:
	@echo "Available targets:"
	@echo "  - build: Build the Docker image"
	@echo "  - push: Push the Docker image to Docker Hub"
	@echo "  - compose: Start the container via Docker Compose"
	@echo "  - test: Run tests"
	@echo "  - format: Run yapf formatter"
	@echo "  - coverage: Generate coverage reports"
	@echo "  - clean: Clean up project files"
	@echo "  - lint: Run pylint"
	@echo "  - profile: Profile the application"
	@echo "  - portainer: Start the container via Portainer (not implemented)"

build:
	@docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) .

push:
	@docker push $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)

compose:
	@docker-compose up --build

down:
	@docker-compose down


prod:
	@docker-compose -f docker-compose.prod.yml up

test: clean
	@pytest tests

format: clean
	@yapf -r -i .

coverage: clean coverage-html coverage-xml

coverage-html:
	@coverage html

clean-coverage:
	@rm -rf htmlcov

clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -rf {} +

clean: clean-pyc clean-coverage
	@find . -name '*.swp' -exec rm -rf {} +
	@find . -name '*.bak' -exec rm -rf {} +
	@find . -name 'mprofile*.dat' -exec rm -rf {} +
	@find . -name 'prof.*' -exec rm -rf {} +

lint:
	@pylint ramayanam/

profile: clean
	@tools/pyflame -o prof.txt -x --threads -t pytest test/test_engine.py --fulltrace
	@tools/flamegraph.pl prof.txt > prof.svg

portainer:
	@echo "Starting container via Portainer..."
	@echo "Please access Portainer via your web browser and follow the deployment steps."
