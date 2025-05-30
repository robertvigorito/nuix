
package=nuix

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

build: clean
	$(eval BUILD_LOCATION=./.build)
	pip install . -t $(BUILD_LOCATION) --upgrade

clean-build: ## remove build artifacts
	rm -fr out/
	rm -fr build/
	rm -fr .build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr .tox .ruff_cache .mypy_cache
	rm -fr cov.xml
	rm -fr coverage.xml
	rm -fr dump.rdb
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr tests/.pytest_cache

clean: clean-test clean-build clean-pyc

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/alfred.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ alfred
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

lint: 
	$(eval files=$(shell find ./ -type f -name "*.py"))
	@isort --check-only --color  $(files) --profile black || echo "isort failed" 
	@black --check $(files) || echo "black failed"
	pylint --exit-zero $(files)
	ruff check $(files)
	mypy --ignore-missing-imports $(files)

check:
	@mypy ./src

lint-check: lint check

install: clean
	pip install --upgrade .

poetry-install: clean
	poetry install 

test: ## run tests quickly with the default Python
	$(MAKE) poetry-install
	pytest --cov=$(package) --cov-report=term-missing --cov-fail-under=70 --cov-config=.coveragerc --cov-report=html ./tests

test-all: ## run tests on every Python version with tox
	tox

script:
	$(eval SCRIPTS=$(shell find ./scripts -type f -name "*"))
	@install -v -m 555 $(SCRIPTS) /software/scripts/

coverage: ## check code coverage quickly with the default Python
	wslview ./htmlcov/index.html