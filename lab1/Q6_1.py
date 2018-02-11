import queue_simulation

pmin = 0.5
pmax = 1.5
step = 0.1
L = float(12000)
C = float(1000000)
K = [5, 10, 40]

for k in K:
    queue_simulation.main([pmin, pmax, step, L, C,'Q6_1', k])
