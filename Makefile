.PHONY: test


PACKAGE_NAME=nameko_statsd


test: rst-lint flake8 pytest

rst-lint:
	rst-lint README.rst

flake8:
	flake8 $(PACKAGE_NAME) test

pytest:
	coverage run --concurrency=eventlet --source $(PACKAGE_NAME) --branch \
		-m pytest $(ARGS) test
	coverage report --show-missing --fail-under=100
