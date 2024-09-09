APP_NAME=app.main:app
ENV_FILE=.env
SHELL=./make-venv

install:
	python -m venv venv
	pip install --upgrade pip


post-install:
	pip install -r requirements.txt

kill:
	kill -9 `lsof -t -i:8000`



	
