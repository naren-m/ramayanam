.PHONY: help build clean

.DEFAULT: help
help:
	@echo "make test       run tests"
	@echo "make format     run yapf formatter"
	@echo "make build      genrate binary with pyinstaller"


test: clean
	pytest  tests

coverage: coverage-html coverage-xml

coverage-html:
	coverage html

clean-coverage:
	rm -rf htmlcov

clean-pyc: ## remove Python file artifacts
		find . -name '*.pyc' -exec rm -f {} +
		find . -name '*.pyo' -exec rm -f {} +
		find . -name '*~' -exec rm -f {} +
		find . -name '__pycache__' -exec rm -rf {} +

clean: clean-pyc clean-coverage
		find . -name '*.swp' -exec rm -rf {} +
		find . -name '*.bak' -exec rm -rf {} +
	    find . -name 'mprofile*.dat' -exec rm -rf {} +
		find . -name 'prof.*' -exec rm -rf {} +

format: clean
	yapf -r -i .

flake: clean
	autoflake -i -r --ignore-init-module-imports .

autopep: _autopep format

_autopep:
	autopep8 --in-place -r lib/

lint:
	pylint ramayanam/

profile: clean
	tools/pyflame -o prof.txt -x --threads -t pytest test/test_engine.py --fulltrace
	tools/flamegraph.pl prof.txt > prof.svg
