.PHONY: init
init:
	pip install --editable .
	pip install --upgrade pip-tools pip setuptools
	rm -rf .tox
	pip install --upgrade tox pre-commit
	pre-commit install

.PHONY: update
update: init
