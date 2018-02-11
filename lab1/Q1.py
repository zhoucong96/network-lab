import random
import math
from collections import deque
import numpy as np


lam = float(75)
rand_list = []

for i in range(0,1000):
    element = (-1/lam) * math.log(1 - random.random())  #inverse transform (-1/lam)*log(1-U)
    rand_list.append(element)


print('mean is '+str(np.mean(rand_list))+' and expected mean is 0.013333...')
print('variance is '+str(np.var(rand_list))+' and expected variance is 0.00018')
