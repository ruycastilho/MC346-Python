import sys
import math
import numpy as np
from itertools import chain, permutations
from operator import itemgetter

def splitInput(x):
    index = 0
    while (x[index] != []):
        index += 1

    return x[:index], x[index+1:]

def floydMarshall(dist, n):
    for k in range(0, n):
       for i in range(0, n):
          for j in range(0, n):
             if (dist[i][j] > dist[i][k] + dist[k][j] ):
                dist[i][j] = dist[i][k] + dist[k][j]

    return dist

def getInconvenience(trip1, trip2, times):
    inconveniences = [[0,0]]*4
    
    if (len(trip1) == 3):
        start1 = trip1[2]
        end1 = trip1[1]
    else:
        start1 = trip1[0]
        end1 = trip1[1]

    if (len(trip2) == 3):
        start2 = trip2[2]
        end2 = trip2[1]
    else:
        start2 = trip2[0]
        end2 = trip2[1]

    basetime1 = times[start1][end1]
    basetime2 = times[start2][end2]

    inconvenience1 = (times[start1][start2] + times[start2][end1])/basetime1
    inconvenience2 = (times[start2][end1] + times[end1][end2])/basetime2
    inconveniences[0] = [[start1, start2, end1, end2], max(inconvenience1, inconvenience2)]

    inconvenience1 = (times[start1][start2] + times[start2][end2] + times[end2][end1])/basetime1
    inconvenience2 = 1
    inconveniences[1] = [[start1,start2,end2,end1], max(inconvenience1, inconvenience2)]

    inconvenience1 = (times[start1][end2] + times[end2][end1])/basetime1
    inconvenience2 = (times[start2][start1] + times[start1][end2])/basetime2
    inconveniences[2] = [[start2,start1, end2, end1], max(inconvenience1, inconvenience2)]

    inconvenience1 = 1
    inconvenience2 = (times[start2][start1] + times[start1][end1]+ times[end1][end2])/basetime2
    inconveniences[3] = [[start2, start1, end1, end2], max(inconvenience1, inconvenience2)]

    sorted_inconveniences = sorted(inconveniences, key=itemgetter(1))
    minimum = sorted_inconveniences[0]
    min_path = minimum[0]
    inconvenience = minimum[1]

    if (inconvenience <= 1.4):
        return inconvenience, min_path

    return None, None

def print_result(results):
    for item in results:
        if (len(item) == 3):
            print('passageiros:', item[0]+1, 'e', item[1]+1, 'percurso:',*item[2], sep=' ')
        else:
            print('passageiro:', item[0]+1,  'percurso:', *item[1], sep=' ')

# Main

raw = []

# Input and parsing
for line in sys.stdin:
    line =line.strip(" \n\r").split()
    raw.append(line)

times, trips = splitInput(raw)

# Type convertion
times = list(map(lambda x : [int(x[0]), int(x[1]), float(x[2])], times))
trips = [[int(float(j)) for j in i] for i in trips]

amount_of_passengers = len(trips)
passengers = list(range(0, amount_of_passengers))

# Set of vertices and its length

vertices = set([x[0] for x in times])
amount_of_vertices = len(vertices)

# Floyd-Marshall's arrays

travelTimes = np.full((amount_of_vertices,amount_of_vertices), math.inf)

# Seting existing weights

for item in times:
    start = item[0]
    end = item[1]
    weight = item[2]
    travelTimes[start][end] = weight

# Floyd Marshall

min_times = floydMarshall(travelTimes, amount_of_vertices)

# Calculating inconveniences
inconveniences = []

# Generates all possible paths, checks, for each path, which of passenges have trips that are valid for said path
# and calculates the corresponding inconvenience

for i in range(0, amount_of_passengers):
    for j in range(i+1, amount_of_passengers):
        pass1 = trips[i]
        pass2 = trips[j]
        inconvenience, path = getInconvenience(pass1, pass2, min_times)
        if (inconvenience != None):
            inconveniences.append([i, j, inconvenience, path])

# select min inconvenience, remove all remaining trips that include either start or end from selected min inconvenience
sorted_inconveniences = sorted(inconveniences, key=itemgetter(2))

final_trips = []

while (amount_of_passengers and len(sorted_inconveniences)):
    minimum = sorted_inconveniences[0]

    passenger1 = minimum[0]
    passenger2 = minimum[1]
    trip = minimum[3]

    final_trips.append([passenger1,passenger2, trip])

    passengers.remove(passenger1)
    passengers.remove(passenger2)

    # print(passenger1, passenger2)
    sorted_inconveniences = list(filter(lambda x : x[0] != passenger1 and x[1] != passenger1 and x[0] != passenger2 and x[1] != passenger2, sorted_inconveniences))

# let the remaining passengers in individual trips
for item in passengers:
    if (len(trips[item]) == 2):
        final_trips.append([item, trips[item]])
    else:
        final_trips.append([item, [trips[item][2], trips[item][1]]])

# [pass1, pass2, path] or [pass1, path]
print_result(final_trips)