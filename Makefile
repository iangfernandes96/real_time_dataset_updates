.PHONY: start test

start:
	docker-compose up --build

stop:
	docker-compose down

test:
	# Create virtual environment if not exists
	test -d .venv || python -m venv .venv
	# Activate virtual environment and install requirements
	. .venv/bin/activate && pip install -r requirements.txt
	# Run pytest
	. .venv/bin/activate && python -m pytest
