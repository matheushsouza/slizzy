dist:
	python3 setup.py sdist bdist_wheel

install:
	pip install --user .

upload:
	twine upload dist/*

clean:
	rm -r dist/
