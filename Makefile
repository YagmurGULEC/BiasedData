export PYTHONPATH=.
SHELL=./make-venv


PHONY: install post-install run kill
install:
	python3 -m venv venv
	pip install --upgrade pip


post-install:
	pip install -r requirements.txt
kill:
	kill -9 `lsof -t -i:8000`

run: 
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

upload:
	python app/upload_file.py

data-analysis:
	python app/data_analyzer.py

test:
	pytest tests/ -v -s 



	
