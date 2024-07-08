SHELL := /bin/bash
build-PythonTemplate build-LowDeltaT build-LongTermVariance:
	cp -r ./* $(ARTIFACTS_DIR)
	pip install --upgrade pip
	pip install pipenv
	pipenv run pip install -r <(pipenv requirements) -t $(ARTIFACTS_DIR)