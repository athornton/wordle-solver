all: wheel

.PHONY: init
init: .git/hooks/pre-commit
	pip install --editable .
	pip install --upgrade pip-tools pip setuptools
	rm -rf .tox
	pip install --upgrade tox pre-commit pytest
	pre-commit install

DATADIR=tests/static/
testdata=$(DATADIR)5x1000.txt     \
         $(DATADIR)5x1000.freq    \
         $(DATADIR)6x800.txt      \
         $(DATADIR)6x800.freq     \
         $(DATADIR)standard.freq  \
         $(DATADIR)flat.freq      \
         $(DATADIR)primel.txt     \
         $(DATADIR)mastermind.txt

$(testdata):
	scripts/generate_test_data

testdata: $(testdata)

.PHONY: test
test: $(testdata)
	pytest tests

wheel:
	pip wheel -e .

cleanup=tests/__pycache__                         \
        scripts/__pycache__                       \
        src/wordle_solver/__pycache__             \
        src/wordle_solver/wordle_solver.egg_info  \
        tests/static                              \
        build                                     \
        *.whl

.PHONY: clean
clean:
	-rm -rf $(cleanup)

