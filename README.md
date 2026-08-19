To install new packages run `poetry add [package name]` instead of using `pip`

Export the `poetry.lock` use `poetry export --format requirements.txt --output requirements.txt`

To set up the virtual environment, make sure you're using python 3.10, and then run
1. `py -m pip install --upgrade pip`
2. `pip install -r requirements.txt`