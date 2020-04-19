test:
	python3 -m unittest tests/*Tests.py

unit-test:
	python3 -m unittest tests/updatorUnitTests.py

integration-test:
	python3 -m unittest tests/updatorTests.py

only-test:
	python3 -m unittest tests.updatorUnitTests.ChangeAttributeTests.test_rename_attr_inside_attr_as_assignment