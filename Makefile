init:
	pip install -r requirements.txt
	git config core.hooksPath .githooks
	git config --bool flake8.strict true


