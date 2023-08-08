import numpy as np

from core.utils_math import random_choice_non_repetitive

x = [1, 2, 3]
a = [1.0, -1.0, 0.4]
r = random_choice_non_repetitive(x, p=np.absolute(a), size=10, take_less=True)
print(r)