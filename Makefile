.PHONY: setup
setup:
	python3 -m venv .env
	.env/bin/pip install --upgrade pip
	.env/bin/pip install --upgrade --requirement requirements.txt
	.env/bin/pip install --upgrade --requirement requirements-dev.txt
	.env/bin/pip install --upgrade --requirement requirements-examples.txt

.PHONY: install
install: setup
	.env/bin/pip install .

.PHONY: lint
lint:
	.env/bin/pylint \
	    setup.py staticmaps examples tests
	.env/bin/flake8 \
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
	(cd examples && PYTHONPATH=.. ../.env/bin/python draw_gpx.py running.gpx)
	(cd examples && PYTHONPATH=.. ../.env/bin/python frankfurt_newyork.py)
	(cd examples && PYTHONPATH=.. ../.env/bin/python freiburg_area.py)
	(cd examples && PYTHONPATH=.. ../.env/bin/python us_capitals.py)

.PHONY: test
test:
	PYTHONPATH=. .env/bin/python -m pytest tests

.PHONY: build-package
build-package:
	rm -rf dist
	PYTHONPATH=. .env/bin/python setup.py sdist
	PYTHONPATH=. .env/bin/twine check dist/*

.PHONY: upload-package-test
upload-package-test:
	PYTHONPATH=. .env/bin/twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: upload-package
upload-package:
	PYTHONPATH=. .env/bin/twine upload --repository py-staticmaps dist/*
