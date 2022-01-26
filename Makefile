all: wheel

.PHONY: init
init: .git/hooks/pre-commit
	pip install --editable .
	pip install --upgrade pip-tools pip setuptools
	rm -rf .tox
	pip install --upgrade tox pre-commit pytest
	pre-commit install

.PHONY: test
test:
	pytest tests

wheel:
	pip wheel -e .
