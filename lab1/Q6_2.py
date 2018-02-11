import queue_simulation

pmin = [0.4, 2, 5]
pmax = [1.9, 4.8, 9.8]
step = [0.1, 0.2, 0.4]
L = float(12000)
C = float(1000000)
K = [5, 10, 40]

for k in K:
    for i in range(len(pmin)):
        p_min = pmin[i]
        p_max = pmax[i]
        step_size = step[i]
        queue_simulation.main([p_min, p_max, step_size, L, C,'Q6_2', k])
