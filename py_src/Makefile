SHELL := /bin/bash
build-SparseData build-LowDeltaT build-StuckTwoDay build-LongTermVariance:
	cp -r ./* $(ARTIFACTS_DIR)
	pip install --upgrade pip
	pip install pipenv
	pipenv run pip install -r <(pipenv requirements) -t $(ARTIFACTS_DIR)
