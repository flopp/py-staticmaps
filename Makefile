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
	    airports
	.env/bin/mypy \
	    airports
	.env/bin/black \
	    --line-length 120 \
	    --check \
	    --diff \
	    airports

.PHONY: format
format:
	.env/bin/black \
	    --line-length 120 \
	    airports

.PHONY: run
run: setup
	PYTHONPATH=. .env/bin/python airports/cli.py \
		--config config-example.py \
		--verbose
