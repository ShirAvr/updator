test:
	python3 -m unittest tests/*Tests.py

unit-test:
	python3 -m unittest tests/updatorUnitTests.py

integration-test:
	python3 -m unittest tests/updatorTests.py