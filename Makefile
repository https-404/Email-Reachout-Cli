.PHONY: install install-dev test build release-check clean

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

build: test
	rm -rf dist build *.egg-info jobreach.egg-info
	python -m build

release-check: build
	twine check dist/*

clean:
	rm -rf dist build *.egg-info jobreach.egg-info .pytest_cache
