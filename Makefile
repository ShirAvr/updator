test:
	python3 -m unittest tests/*Tests.py

unit-test:
	python3 -m unittest tests/updatorUnitTests.py

integration-test:
	python3 -m unittest tests/updatorTests.py

only-test:
	python3 -m unittest tests.updatorUnitTests.ReplaceFuncParamsTests.test_update_all_function_instances_when_params_are_variables
# 	python3 -m unittest tests.updatorUnitTests.ChangeFuncReturnTests.test_change_func_return_from_value_to_list_of_vars
# 	python3 -m unittest tests.updatorUnitTests.RenameFunctionTests.test_apply_rule_change_function_inside_rule_inside_rule
