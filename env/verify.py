from pycaret.classification import *
from pycaret.datasets import get_data

data = get_data("juice")

exp = setup(data=data, target="Purchase", html=False, verbose=False)

best = compare_models()

print(best)