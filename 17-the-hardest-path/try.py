import csv

# each square is represented by its row index in the map.csv data
# illustration: [start, visit N, visit E, visit W, visitS, ...]
# full_list:    [  130,       8,      13,    111,      30, ...], # visited nodes
# back_index:    [  -1,       0,       0,      0,       0, ...], # index of full_list
# back_direction: [ '',     'N',     'E',    'W',     'S', ...],
full_list = [27267]
visited = set([27267]) # just a set representation of full_list
back_index = [-1]
back_direction = ['']
current_index = 0 # current node being explored, as index in full_list
d = ['N', 'E', 'W', 'S']

current = 27267 # starting point
answer = 10421 # the goal

result = [] # maze data, to be read from map.csv
mapping = dict() # a helping mapping to map from the hash to row index

with open('map.csv') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for row in r:
        result.append(row)
for i in range(0, len(result)):
    mapping[result[i][0]] = i

while True:
    current = full_list[current_index]
    for i in range(4):
        try_node = mapping[result[full_list[current_index]][2 + i]]
        if try_node == answer:
            s = d[i]
            next_index = current_index
            while next_index != 0:
                s = back_direction[next_index] + s
                next_index = back_index[next_index]
            print(s)
            exit()
        if try_node in visited:
            continue
        if len(result[try_node]) == 2:
            continue
        full_list.append(try_node)
        back_index.append(current_index)
        back_direction.append(d[i])
        visited.add(try_node)
    current_index += 1
