all: run

clean:
	rm -rf venv && rm -rf *.egg-info && rm -rf dist && rm -rf *.log*

venv:
	python3 -mvenv venv && venv/bin/python setup.py develop

run: venv
	FLASK_APP=captiveportal CAPTIVEPORTAL_SETTINGS=../settings.cfg venv/bin/flask run

test: venv
	CAPTIVEPORTAL_SETTINGS=../settings.cfg venv/bin/python -m unittest discover -s tests

sdist: venv test
	venv/bin/python setup.py sdist
