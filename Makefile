test:
	python3 -m unittest tests/*Tests.py

unit-test:
	python3 -m unittest tests/updatorUnitTests.py

integration-test:
	python3 -m unittest tests/updatorTests.py

only-test:
# 	python3 -m unittest tests.updatorUnitTests.CombinationTypeTests.test_change_compound_funtion_use_to_attr_use
	python3 -m unittest tests.updatorUnitTests.ReplaceFuncParamsTests.test_change_param_value
# 	python3 -m unittest tests.updatorUnitTests.ReplaceFuncParamsTests.test_update_all_function_instances_when_params_are_variables
