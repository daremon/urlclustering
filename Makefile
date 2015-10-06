all: cleanup test

test:
	python -m unittest discover

cleanup:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

release-test:
	python setup.py register -r https://testpypi.python.org/pypi

release:
	python setup.py register -r https://pypi.python.org/pypi
	python setup.py sdist upload -r https://pypi.python.org/pypi
