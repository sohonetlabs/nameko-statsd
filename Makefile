test: flake8 pytest

flake8:
	flake8 nameko_statsd test

pytest:
	coverage run --concurrency=eventlet --source nameko_statsd --branch -m pytest test
	coverage report --show-missing --fail-under=100
