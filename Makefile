PROJECT=staticmaps
SRC_CORE=staticmaps
SRC_TEST=tests
SRC_EXAMPLES=examples
SRC_COMPLETE=$(SRC_CORE) $(SRC_TEST) $(SRC_EXAMPLES) docs/gen_ref_pages.py
PYTHON=python3
PIP=$(PYTHON) -m pip

help: ## Print help for each target
	$(info Makefile low-level Python API.)
	$(info =============================)
	$(info )
	$(info Available commands:)
	$(info )
	@grep '^[[:alnum:]_-]*:.* ##' $(MAKEFILE_LIST) \
		| sort | awk 'BEGIN {FS=":.* ## "}; {printf "%-25s %s\n", $$1, $$2};'

clean: ## Cleanup
	@rm -f  ./*.pyc
	@rm -rf ./__pycache__
	@rm -f  $(SRC_CORE)/*.pyc
	@rm -rf $(SRC_CORE)/__pycache__
	@rm -f  $(SRC_TEST)/*.pyc
	@rm -rf $(SRC_TEST)/__pycache__
	@rm -f  $(SRC_EXAMPLES)/*.pyc
	@rm -rf $(SRC_EXAMPLES)/__pycache__
	@rm -rf $(SRC_EXAMPLES)/build
	@rm -rf ./.coverage
	@rm -rf ./coverage.xml
	@rm -rf ./.pytest_cache
	@rm -rf ./.mypy_cache
	@rm -rf ./site
	@rm -rf ./reports

.PHONY: setup
setup: ## Setup virtual environment
	$(PYTHON) -m venv .env
	.env/bin/pip install --upgrade pip wheel
	.env/bin/pip install --upgrade --requirement requirements.txt
	.env/bin/pip install --upgrade --requirement requirements-dev.txt
	.env/bin/pip install --upgrade --requirement requirements-examples.txt

.PHONY: install
install: setup ## install package
	.env/bin/pip install .

.PHONY: lint
lint: ## Lint the code
	.env/bin/pycodestyle \
		--max-line-length=120 \
		setup.py $(SRC_COMPLETE)
	.env/bin/isort \
		setup.py $(SRC_COMPLETE) \
		--check --diff
	.env/bin/black \
		--line-length 120 \
		--check \
		--diff \
		setup.py $(SRC_COMPLETE)
	.env/bin/pyflakes \
		setup.py $(SRC_COMPLETE)
	.env/bin/flake8 \
		setup.py $(SRC_COMPLETE)
	.env/bin/pylint \
		setup.py $(SRC_COMPLETE)
	.env/bin/mypy \
		setup.py $(SRC_COMPLETE)
	.env/bin/codespell  \
		README.md staticmaps/*.py tests/*.py examples/*.py

.PHONY: format
format: ## Format the code
	.env/bin/isort \
		setup.py $(SRC_COMPLETE)
	.env/bin/autopep8 \
		-i -r \
		setup.py $(SRC_COMPLETE)
	.env/bin/black \
		--line-length 120 \
		setup.py $(SRC_COMPLETE)

.PHONY: run-examples
run-examples: ## Generate example images
	(cd examples && PYTHONPATH=.. ../.env/bin/python custom_objects.py)
	(cd examples && PYTHONPATH=.. ../.env/bin/python draw_gpx.py running.gpx)
	(cd examples && PYTHONPATH=.. ../.env/bin/python frankfurt_newyork.py)
	(cd examples && PYTHONPATH=.. ../.env/bin/python freiburg_area.py)
	(cd examples && PYTHONPATH=.. ../.env/bin/python geodesic_circles.py)
	(cd examples && PYTHONPATH=.. ../.env/bin/python tile_providers.py)
	(cd examples && PYTHONPATH=.. ../.env/bin/python us_capitals.py)
	(cd examples && mkdir -p build)
	(cd examples && ls        *.svg 2>/dev/null && mv        *.svg build/.) || echo "no svg files found!"
	(cd examples && ls *pillow*.png 2>/dev/null && mv *pillow*.png build/.) || echo "no pillow png files found!"
	(cd examples && ls  *cairo*.png 2>/dev/null && mv  *cairo*.png build/.) || echo "no cairo png files found!"

.PHONY: test
test: ## Test the code
	PYTHONPATH=. .env/bin/python -m pytest tests

.PHONY: coverage
coverage: ## Generate coverage report for the code
	PYTHONPATH=. .env/bin/python -m pytest --cov=staticmaps --cov-branch --cov-report=term --cov-report=html tests

.PHONY: build-package
build-package: ## Build the package
	rm -rf dist
	PYTHONPATH=. .env/bin/python setup.py sdist
	PYTHONPATH=. .env/bin/twine check dist/*

.PHONY: upload-package-test
upload-package-test: ## Upload package test
	PYTHONPATH=. .env/bin/twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: upload-package
upload-package: ## Upload package
	PYTHONPATH=. .env/bin/twine upload --repository py-staticmaps dist/*

.PHONY: documentation
documentation: ## Generate documentation
	@if type mkdocs >/dev/null 2>&1 ; then .env/bin/python -m mkdocs build --clean --verbose ; \
	 else echo "SKIPPED. Run '$(PIP) install mkdocs' first." >&2 ; fi 

