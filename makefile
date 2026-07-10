setup:
	python -m etl.load_geography

apii:
	uvicorn api.server:app --reload