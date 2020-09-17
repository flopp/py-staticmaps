.PHONY: setup
setup:
	python3 -m venv .env
	.env/bin/pip install --upgrade pip
	.env/bin/pip install -r requirements.txt

.PHONY: setup-dev
setup-dev: setup
	.env/bin/pip install -r requirements-dev.txt

.PHONY: install
install: setup
	.env/bin/pip install .

.PHONY: lint
lint:
	.env/bin/pylint \
	    setup.py staticmaps examples tests
	.env/bin/mypy \
	    setup.py staticmaps examples tests
	.env/bin/black \
	    --line-length 120 \
	    --check \
	    --diff \
	    setup.py staticmaps examples tests

.PHONY: format
format:
	.env/bin/black \
	    --line-length 120 \
	    setup.py staticmaps examples tests

.PHONY: run-examples
run-examples:
	PYTHONPATH=. .env/bin/python examples/zrh_swiss_destinations.py

.PHONY: test
test:
	PYTHONPATH=. .env/bin/python -m pytest tests
