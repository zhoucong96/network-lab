import sys
import math
import random
from collections import deque

def takeSecond(element):
    return element[1]

def takeFirst(element):
    return element[0]

def getRand(param):
    return (-1/param) * math.log(1 - random.random())

def observe_event(event_time):
    global queue, DES, No, idle_counter, IDLE, DES, packet_num_list
    No += 1

    if IDLE == 1:
        idle_counter += 1   #increment idle_counter

    packet_num_list.append(len(queue))


def arrival_event(event_time):
    global queue, Na, DES, K, L, IDLE, DES, packet_num, idle_start_time, total_idle_time, packet_generated, loss, plus_idle

    Na += 1
    packet_generated += 1
    packet_index = packet_generated - 1

    #generate packet size and calculate the service time
    packet_size = getRand(1/L)
    service_time = packet_size / C

    if IDLE == 1:        #server is empty
        if plus_idle == 1:
            total_idle_time += (event_time - idle_start_time)
            plus_idle = 0
        IDLE = 0

        generate_departure(True, packet_index, service_time)

    elif IDLE == 0:     #server is busy
        if K is None or len(queue) < K: #when queue has space
            queue.appendleft(event_time)#the time when it goes in
            generate_departure(False, packet_index, service_time)#it will have departure_event
        else:#packet loss and no departure_event
            loss += 1

def departure_event(event_time):
    global queue, DES, Nd, idle_counter, IDLE, DES, total_idle_time, idle_start_time, plus_idle
    Nd += 1
    if len(queue) > 1:       #queue has packets
        queue.pop()
    elif len(queue) == 1:
        queue.pop()#when when the queue is empty
        idle_start_time = event_time#when when the queue is empty
        plus_idle = 1
        IDLE = 1
    else:                    #queue is empty
        IDLE = 1

def generate_departure(noDelay, packet_index, service_time):
    global C, DES, arrival_list, departure_list

    if noDelay: #calculate departure time without delay
        departure_element = arrival_list[packet_index] + service_time#calculate the departure time
        departure_list.append(departure_element)
        departure_list = sorted(departure_list)
        DES.append(('departure', departure_element))#the first departure event
        DES = sorted(DES,key=takeSecond, reverse=True)
    else: #calculate departure time with sojourn time
        departure_element = departure_list[-1] + service_time
        departure_list.append(departure_element)
        departure_list = sorted(departure_list)
        DES.append(('departure', departure_element))#the first departure event
        DES = sorted(DES,key=takeSecond, reverse=True)

def generate_events(LAM, L, ALP, T):
    global departure_list, DES, arrival_list

    #generate observer and arrival events
    observer_list = []
    arrival_list = []
    arrival_interval_list = []
    observer_interval_list = []
    arrival_element = 0 #the time for each arrival event
    observer_element = 0

    #generate observer event time, arrival event time and length
    for i in range(0,T):
        inter_observer = getRand(ALP)     #generate observer events with exponential distribution
        observer_interval_list.append(inter_observer)
        observer_element += inter_observer
        observer_list.append(observer_element)
        DES.append(('observer',observer_element))        #add observer event time into ES
        inter_arrival = getRand(LAM)                    #generate inter arrival time
        arrival_interval_list.append(inter_arrival)
        arrival_element += inter_arrival                #get the arrival event time
        arrival_list.append(arrival_element)#arrival with packet length
        DES.append(('arrival', arrival_element))

    DES = sorted(DES,key=takeSecond, reverse=True)

def print_ES_toCSV(ES):
    f = open("results/DES.csv", 'w')
    f.write("name,time")
    for i in range(len(ES)):
        f.write("\n{}, {}".format(takeFirst(ES[i]), takeSecond(ES[i])))
    f.close()

def execute_one_event():
    global DES

    #dequeue the event and call corresponding procedure
    event = DES.pop()
    event_name = takeFirst(event)
    event_time = takeSecond(event)
    if event_name == 'observer':
        observe_event(event_time)
    elif event_name == 'arrival':
        arrival_event(event_time)
    elif event_name == 'departure':
        departure_event(event_time)

def simulation_once(p, T, K, L):
    global queue, DES, C, Na, Nd, No, idle_counter, IDLE, DES, packet_num_list, total_idle_time, idle_start_time, packet_generated, loss, plus_idle, departure_list

    LAM = float(p * C / L)
    ALP = LAM
    queue = deque(maxlen=K)
    DES = []
    Na = 0
    Nd = 0
    No = 0
    idle_counter = 0
    IDLE = 1
    packet_generated = 0
    loss = 0
    packet_num_list = []
    departure_list = []
    total_idle_time = 0.0
    idle_start_time = 0.0
    EN = 0.0
    plus_idle = 1#avoid double counting

    generate_events(LAM, L, ALP, T)
    total_time = takeSecond(DES[0])
    #execute the ES
    for i in range(0, 100*T):
        #execute only when there are events
        if len(DES) > 0:
            if total_time < takeSecond(DES[0]):
                total_time = takeSecond(DES[0])
            execute_one_event()

    #print out the DES
    print_ES_toCSV(DES)

    #compute performance
    queue_average = float(sum(packet_num_list))/len(packet_num_list)
    idle_time_portion = total_idle_time/total_time
    loss_ratio = float(loss)/float(packet_generated)

    return queue_average, idle_time_portion, loss_ratio

#main

global K, C, L

P_idle = 0.0
P_loss = 0.0
EN = 0.0
M = 15
T = 5000
p = 0.4
K = 15
L = float(2000)#12kb
C = float(1000000)#1Mb/s

if K is None:
    f = open("results/mm1.csv", 'w')
else:
    f = open("results/mm1K.csv", 'w')

f.write("p,E[N],P_IDLE, P_LOSS")

for i in range(0, M):
    queue_average, idle_ratio, loss_ratio = simulation_once(p, T, K, L)
    EN = queue_average
    P_idle = idle_ratio
    P_loss = loss_ratio
    print('p = '+str(p)+': '+ 'EN = ' +str(EN)+' and Pidle = '+str(P_idle)+' and Ploss = '+str(P_loss))
    f.write("\n{},{},{},{}".format(p, EN, P_idle, P_loss))
    p += 0.1

f.close()
