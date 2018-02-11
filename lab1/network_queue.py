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
    global queue, Na, Nd, No, idle_counter, IDLE, DES, packet_num_list
    No += 1

    if IDLE == 1:
        idle_counter += 1   #increment idle_counter

    packet_num_list.append(len(queue))

def arrival_event(event_time):
    global queue, Na, Nd, No, idle_counter, IDLE, DES, packet_num, idle_start_time, total_idle_time, plus_idle
    Na += 1
    if IDLE == 1:        #server is empty
        if plus_idle == 1:
            total_idle_time += (event_time - idle_start_time)
            plus_idle = 0
        IDLE = 0
    elif IDLE == 0:
        queue.appendleft(event_time)#the time when it goes in

def departure_event(event_time):
    global queue, Na, Nd, No, idle_counter, IDLE, DES, total_idle_time, idle_start_time, plus_idle
    Nd += 1
    if len(queue) > 1:       #queue has packets
        queue.pop()
    elif len(queue) == 1:
        queue.pop()
        idle_start_time = event_time#when when the queue is empty
        plus_idle = 1
        IDLE = 1
    else:                    #queue is empty
        IDLE = 1

def generate_events(LAM, L, ALP, C, T):
    observer_list = []
    arrival_list = []
    arrival_interval_list = []
    observer_interval_list = []
    departure_list = []
    service_list = []
    length_list = []
    ES = []
    arrival_element = 0 #the time for each arrival event
    observer_element = 0

    #generate observer event time, arrival event time and length
    for i in range(0,T):
        inter_observer = getRand(ALP)     #generate observer events with exponential distribution
        observer_interval_list.append(inter_observer)
        observer_element += inter_observer
        observer_list.append(observer_element)
        ES.append(('observer',observer_element))        #add observer event time into ES
        length_element = getRand(1/L)
        length_list.append(length_element)                #length of packets with exponential distribution
        inter_arrival = getRand(LAM)                    #generate inter arrival time
        arrival_interval_list.append(inter_arrival)
        arrival_element += inter_arrival                #get the arrival event time
        arrival_list.append(arrival_element)#arrival with packet length
        ES.append(('arrival', arrival_element))

    #length_list = sorted(length_list)#exponential
    #calculate first departure time
    service_time_element = length_list[0]/C
    service_list.append(service_time_element)  #get the service time
    departure_element = arrival_list[0] + service_time_element#calculate the departure time
    departure_list.append(departure_element)#the first departure = arrival+service
    ES.append(('departure', departure_element))#the first departure event

    #calculate the rest departure time
    for i in range(1,T):
        arrival_time_element = arrival_list[i]
        service_time_element = length_list[i]/C
        service_list.append(service_time_element)
        if arrival_time_element >= departure_list[i-1]:   #arrive after departure
            departure_time_element = arrival_time_element + service_time_element
            departure_list.append(departure_time_element)
            ES.append(('departure', departure_time_element))
        elif arrival_time_element < departure_list[i-1]:  #server is busy
            departure_time_element = departure_list[i-1] + service_time_element
            departure_list.append(departure_time_element)
            ES.append(('departure', departure_time_element))

    detail_print(observer_list, arrival_list, departure_list, C, service_list, arrival_interval_list, length_list, observer_interval_list)

    return sorted(ES,key=takeSecond, reverse=True)

def detail_print(observer_list, arrival_list, departure_list, C,service_list, arrival_interval_list, length_list, observer_interval_list):
    f = open("noK_result/observer.csv", 'w')
    #print('observer event')
    for i in range(len(observer_list)):
    #    print('observer time: ' + str(observer_list[i]))
        f.write("\n{}".format(observer_list[i]))
    f.close()

    f = open("noK_result/service_time.csv", 'w')
    for i in range(len(service_list)):
        f.write("\n{}".format(service_list[i]))
    f.close()

    f = open("noK_result/inter_arrival.csv", 'w')
    for i in range(len(arrival_interval_list)):
        f.write("\n{}".format(arrival_interval_list[i]))
    f.close()

    f = open("noK_result/inter_observer.csv", 'w')
    for i in range(len(observer_interval_list)):
        f.write("\n{}".format(observer_interval_list[i]))
    f.close()

    f = open("noK_result/arrivalanddeparture.csv", 'w')
    f.write("arrival,departure,length")
    #print('arrival and departure:')
    for i in range(len(arrival_list)):
    #    print('arrival time: ' + str(takeFirst(arrival_list[i])) + '  length: ' + str(takeSecond(arrival_list[i])) + ' bits' + '    service time: ' + str(takeSecond(arrival_list[i])/C) + ' departure time: ' + str(departure_list[i]))
        f.write("\n{},{},{}".format(arrival_list[i], departure_list[i], length_list[i]))
    f.close()

def print_ES_toCSV(ES):
    f = open("noK_result/DES.csv", 'w')
    f.write("name,time")
    for i in range(len(ES)):
        f.write("\n{}, {}".format(takeFirst(ES[i]), takeSecond(ES[i])))
    f.close()

def simulate_start(ES):
    #dequeue the event and call corresponding procedure
    for i in range(len(ES)):
        event = ES.pop()
        event_name = takeFirst(event)
        event_time = takeSecond(event)
        if event_name == 'observer':
            observe_event(event_time)
        elif event_name == 'arrival':
            arrival_event(event_time)
        elif event_name == 'departure':
            departure_event(event_time)

def simulation_once(p, T, K, L, C):
    global queue, Na, Nd, No, idle_counter, IDLE, DES, packet_num_list, total_idle_time, idle_start_time, plus_idle

    LAM = float(p * C / L)
    ALP = LAM
    queue = deque(maxlen=K)
    Na = 0
    Nd = 0
    No = 0
    idle_counter = 0
    IDLE = 1
    packet_num_list = []
    total_idle_time = 0.0
    idle_start_time = 0.0
    EN = 0.0
    plus_idle = 1#avoid double couting

    DES = generate_events(LAM, L, ALP, C, T)
    print_ES_toCSV(DES)

    total_time = takeSecond(DES[0])
    simulate_start(DES)

    #compute performance
    queue_average = float(sum(packet_num_list))/len(packet_num_list)
    idle_time_portion = total_idle_time/total_time

    return queue_average, idle_time_portion

#main
P_idle = 0.0
EN = 0.0
M = 10
T = 10000
p = 0.25
K = None
L = float(2000)#12kb
C = float(1000000)#1Mb/s

f = open("noK_result/mm1.csv", 'w')
f.write("p,E[N],P_IDLE")

for i in range(2, M):
    queue_average, idle_ratio = simulation_once(p, T, K, L, C)
    EN = queue_average
    P_idle = idle_ratio
    print('p = '+str(p)+': '+ 'EN = ' +str(EN)+' and Pidle = '+str(P_idle))
    f.write("\n{},{},{}".format(p, EN, P_idle))
    p += 0.1

f.close()
