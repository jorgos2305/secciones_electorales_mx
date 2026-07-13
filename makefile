.PHONY: setup api

setup:
	python -m etl.load_geography

api:
	uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload