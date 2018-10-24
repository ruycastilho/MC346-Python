import sys
import math
import numpy as np
from itertools import chain, permutations
from operator import itemgetter

def all_trips(lst):
    return chain(*map(lambda x: permutations(lst, x), range(2, len(lst)+1)))

# for subset in all_subsets(stuff):
#     print(subset)
    
def splitInput(x):
    index = 0
    while (x[index] != ['']):
        index += 1

    return x[:index], x[index+1:]

def floydMarshall(dist, w, n):
    for start in range(0, n):
        for end in range(0, n):
            dist[start][end] = w[start][end]

    for vertex in range(0, n):
       dist[vertex][vertex] = 0

    for k in range(0, n):
       for i in range(0, n):
          for j in range(0, n):
             if (dist[i][j] > dist[i][k] + dist[k][j] ):
                 dist[i][j] = dist[i][k] + dist[k][j]

    return dist

def check_valid(trip1, trip2, origin, destination, path):
    start1 = trip1[0]
    start2 = trip2[0]

    mid1 = None
    mid2 = None

    if (len(trip1) == 3):
        mid1 = trip1[2]

    if (len(trip2) == 3):
        mid2 = trip2[2]
    
    end1 = trip1[1]
    end2 = trip2[1]

    # if not the same trip
    if (trip1 != trip2):
        # origin and destination must be covered and start cant be the destination nor end be the origin
        if ((origin == start1 or origin == start2) and start1 != destination and start2 != destination):
            if ((destination == end1 or destination == end2) and end1 != origin and end2 != origin):

                # start, end and mid must be included in the path, also mid cant be the end and trips have to overlap
                if (start1 in path and end1 in path and start2 in path and end2 in path):
                    # trips have to overlap (must have path in common)
                    if (path.index(start1) <= path.index(end2) and path.index(start2) <= path.index(end1)):
                        if (not(mid1) and not(mid2)):
                            return True
                        else:
                            if ((mid1 and not(mid2) and mid1 in path and path.index(mid1) > path.index(start1) and mid1 != end and path.index(mid1) <= path.index(end2))
                            or (mid2 and not(mid1) and mid2 in path and path.index(mid2) > path.index(start2) and mid2 != end and path.index(mid2) <= path.index(end1))
                            or (mid1 and mid2 and mid1 in path and mid2 in path and path.index(mid2) > path.index(start2) and
                                    path.index(mid1) > path.index(start1) and mid1 != end and mid2 != end and path.index(mid1) <= path.index(end2) and path.index(mid2) <= path.index(end1) )):
                                return True
                    

    return False

def getInconvenience(trip1, trip2, path, times):
    inconvenience1 = 0
    inconvenience2 = 0
    
    start1_index = path.index(trip1[0])
    start2_index = path.index(trip2[0])

    mid1_index = None
    mid2_index = None

    end1_index = path.index(trip1[1])
    end2_index = path.index(trip2[1])

    if (len(trip1) == 3):
        mid1_index = path.index(trip1[0])
        for i in range(mid1_index, end1_index):
            inconvenience1 += times[path[i]][path[i+1]]
        base_time1 = times[trip1[2]][trip1[1]]
    else:
        for i in range(start1_index, end1_index):
            inconvenience1 += times[path[i]][path[i+1]]
        base_time1 = times[trip1[0]][trip1[1]]

    if (len(trip2) == 3):
        mid2_index = path.index(trip2[0])
        for i in range(mid2_index, end2_index):
            inconvenience2 += times[path[i]][path[i+1]]
        base_time2 = times[trip2[2]][trip2[1]]
    else :
        for i in range(start2_index, end2_index):
            inconvenience2 += times[path[i]][path[i+1]]
        base_time2 = times[trip2[0]][trip2[1]]

    base_time2 = times[trip2[0]][trip2[1]]

    inconvenience1 /= base_time1
    inconvenience2 /= base_time2

    return max(inconvenience1, inconvenience2)

# Main

raw = []

# Input and parsing
for line in sys.stdin:
    words =line.rstrip(" \n\r").split(' ')
    raw.append(words)

times, trips = splitInput(raw)

# Type convertion
times = list(map(lambda x : [int(x[0]), int(x[1]), float(x[2])], times))
trips = [[int(float(j)) for j in i] for i in trips]

passengers = {}
for i in range(0, len(trips)):
    passengers[str(trips[i])] = [trips[i][0], i]

# print(passengers)
# Set of vertices and its length

vertices = set([x[0] for x in times])
amount_of_vertices = len(vertices)

# Floyd-Marshall's arrays

travelTimes = np.full((amount_of_vertices,amount_of_vertices), math.inf)
weights = np.full((amount_of_vertices,amount_of_vertices), math.inf)

# Seting existing weights

for item in times:
    start = item[0]
    end = item[1]
    weight = item[2]
    weights[start][end] = weight

# Floyd Marshall

min_paths = floydMarshall(travelTimes, weights, amount_of_vertices)

# Calculating inconveniences
inconveniences = []

# Generates all possible paths, checks, for each path, which of passenges have trips that are valid for said path
# and calculates the corresponding inconvenience

for trip in all_trips(vertices):
    trip = list(trip)

    start = trip[0]
    end = trip[-1]

    # Checking valid pairs of passenges
    for trip1 in trips:
        for trip2 in trips:
            if(check_valid(trip1, trip2, start, end, trip)):
                # print(trip1, trip2, trip)
                inconvenience = getInconvenience(trip1, trip2, trip, travelTimes)
                inconveniences.append([trip1, trip2, inconvenience, trip])
            else:
                break

# select min inconvenience, remove all remaining trips that include either start or end from selected min inconvenience
sorted_inconveniences = sorted(inconveniences, key=itemgetter(2))

final_trips = []

while (len(passengers) and len(sorted_inconveniences)):
    minimum = sorted_inconveniences[0]

    # if (minimum[2] > 1.4):
    #     break

    passenger1 = minimum[0]
    passenger2 = minimum[1]
    trip = minimum[3]

    final_trips.append([passengers[str(passenger1)][1], passengers[str(passenger2)][1], trip])

    del passengers[str(passenger1)]
    del passengers[str(passenger2)]

    # print(passenger1, passenger2)
    sorted_inconveniences = list(filter(lambda x : x[0] != passenger1 and x[1] != passenger1 and x[0] != passenger2 and x[1] != passenger2, sorted_inconveniences))

# let the remaining passengers in individual trips
for item in passengers:
    final_trips.append([passengers[str(item)][1], item])

# [pass1, pass2, path] or [pass1, path]
print(final_trips)