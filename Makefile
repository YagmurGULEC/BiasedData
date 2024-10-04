export PYTHONPATH=.
SHELL=./make-venv


PHONY: run install post-install create-data
install:
	python3 -m venv venv
	pip install --upgrade pip


post-install:
	pip install -r requirements.txt
kill:
	kill -9 `lsof -t -i:8000`

create-data:
	python app/create_data.py



	
