test:
	python3 -m unittest tests/*Tests.py

unit-test:
	python3 -m unittest tests/updatorUnitTests.py

integration-test:
	python3 -m unittest tests/updatorTests.py

only-test:
	python3 -m unittest tests.updatorUnitTests.ReplaceFuncParamsTests.test_replace_params_positions_when_function_was_assigned