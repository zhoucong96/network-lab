import queue_simulation

pmin = 0.25
pmax = 0.95
step = 0.1
L = float(12000)
C = float(1000000)

queue_simulation.main([pmin, pmax, step, L, C, 'Q3'])
