from collections import defaultdict
from pwn import *
"""
......
..11..
..1...
..1..1
...12.
2....2
"""

def convert_path(path):
    """ convert list of coordinates [0, 1, 2, 3, 9, 15, ...., 0] to commands 'rrrdd.....u'
    """
    commands = ''

    for i,j in zip(path[:-1], path[1:]):

        if j - i == 1:
            commands += 'r'

        if j - i == -1:
            commands += 'l'

        if j - i == 6:
            commands += 'd'

        if j - i == -6:
            commands += 'u'

    return commands

def to_checking_array(path):
    """ get the checking array [4, 5, 6, 3, 6, ...] from commands 'rrrrddddllluuuu'
    """
    loc = 0
    res = [0] * 36

    for command in path:

        if command == 'l':
            res[loc] = 4
            loc -= 1
            
        elif command == 'r':
            res[loc] = 6
            loc += 1
            
        elif command == 'u':
            res[loc] = 3
            loc -= 6
            
        elif command == 'd':
            res[loc] = 5
            loc += 6
            
    return res

def FUN_00101479(checking_array):
    """ check "1" positions
    """
    needed_check = [8, 9, 14, 20, 23, 27]

    for i in range(6): # local_c

        for j in range(6): # local_10

            if i * 6 + j not in needed_check:
                continue

            bvar1 = checking_array[i*6+j]
            local_12 = j
            local_11 = i

            if bvar1 == 6: # r
                local_12 -= 1
            elif bvar1 == 5: # d
                local_11 -= 1
            elif bvar1 == 3: # u
                local_11 += 1
            elif bvar1 == 4: # l
                local_12 += 1

            if bvar1 != checking_array[local_11*6+local_12]:
                return 0

    return 1

def FUN_001011fa(checking_array):
    """ check "2" positions
    """
    arr = checking_array + [99] * 12   # dummy elements to avoid array out of bounds in python, their values won't affect the check
    needed_check = [28, 30, 35]

    for i in range(6): # local_c

        for j in range(6): # local_10
            
            coord = i * 6 + j
            if coord not in needed_check:
                continue

            bvar1 = arr[coord]
            local_12 = j
            local_11 = i

            if bvar1 == 6: # r
                local_12 += 1
            elif bvar1 == 5: # d
                local_11 += 1
            elif bvar1 == 3: # u
                local_11 -= 1
            elif bvar1 == 4: # l
                local_12 -= 1

            if bvar1 != arr[local_11*6+local_12]:
                return 0

            if bvar1 in [3, 5]:
                if (arr[coord+1] != 4 or arr[coord+2] != 4) and (arr[coord-1] != 6 or arr[coord-2] != 6):
                    return 0
            else:
                if (arr[coord+1*6] != 3 or arr[coord+2*6] != 3) and (arr[coord-1*6] != 5 or arr[coord-2*6] != 5):
                    return 0
    return 1

def check_path(path):
    """ check if the given path [0, 1, 2, 3, 9, ..., 0] satisfies the '1' and '2' checks
    """
    commands = convert_path(path)
    arr_check = to_checking_array(commands)
    if FUN_001011fa(arr_check) == 1 and FUN_00101479(arr_check) == 1:
        return True
    return False

# This class represents a directed graph
# using adjacency list representation
class Graph:
  
    def __init__(self, vertices):
        # No. of vertices
        self.V = vertices
         
        # default dictionary to store graph
        self.graph = defaultdict(list)
  
    # function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)
  
    '''A recursive function to print all paths from 'u' to 'd'.
    visited[] keeps track of vertices in current path.
    path[] stores actual vertices and path_index is current
    index in path[]'''
    def printAllPathsUtil(self, u, d, visited, path):
 
        # Mark the current node as visited and store in path
        ####################### not start the visited array from the starting point 0 #############################
        if u != 0:
            visited[u] = True
        path.append(u)
 
        # If current vertex is same as destination, then print
        # current path[]
        if u == d and len(path) > 1:
            ##################### add checking path here ##############################
            if check_path(path):
                all_paths.append(path[:])
                print(path)
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            for i in self.graph[u]:
                if not visited[i]:
                    self.printAllPathsUtil(i, d, visited, path)
                     
        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[u] = False
  
  
    # Prints all paths from 's' to 'd'
    def printAllPaths(self, s, d):
 
        # Mark all the vertices as not visited
        visited = [False] * (self.V)
 
        # Create an array to store paths
        path = []
 
        # Call the recursive helper function to print all paths
        self.printAllPathsUtil(s, d, visited, path)


if __name__ == '__main__':

    g = Graph(36)

    for i in range(36):

        if i % 6 in [0,1,2,3,4]:
            g.addEdge(i, i+1)

        if i % 6 in [1,2,3,4,5]:
            g.addEdge(i, i-1)

        if i // 6 in [1,2,3,4,5]:
            g.addEdge(i, i-6)

        if i // 6 in [0,1,2,3,4]:
            g.addEdge(i, i+6)


    s = 0
    d = 0
    print("Following are all different paths from %d to %d :" %(s, d))
    all_paths = []
    # there are 102 paths, assuming the same cell cannot be visited twice
    g.printAllPaths(s, d)

    results = []

    for path in all_paths:
        commands = convert_path(path)
        io = process('./ej')
        io.sendlineafter(b':/\n', commands.encode())
        res = io.recvall()
        io.close()
        results.append(res.strip().replace(b'correct! :)\n', b''))

    # wctf{ma5yu_puzz13s_4re_fUN!RL!1!}
    # [0, 1, 2, 3, 4, 10, 9, 8, 7, 13, 14, 15, 21, 20, 19, 25, 26, 27, 28, 22, 16, 17, 23, 29, 35, 34, 33, 32, 31, 30, 24, 18, 12, 6, 0]
    # rrrrdllldrrdlldrrruurdddllllluuuuu
    # length: 35, meaning it's a 34-step commands
    correct_path = all_paths[10]
    print(correct_path, convert_path(correct_path), results[10], 'length:', len(correct_path))