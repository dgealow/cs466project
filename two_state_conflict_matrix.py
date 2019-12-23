# two_state_conflict_matrix.py

import sys
from ete3 import Tree, faces, AttrFace, TreeStyle
import util

# Default input and output files
input_file_name = 'data/perfect_phylogeny/m25_n25_s1.txt'
output_file_name = 'tree.png'
method = 'maximum'
# Get input and output files from command-line arguments
if (len(sys.argv) >= 2):
    input_file_name = sys.argv[1]
if (len(sys.argv) >= 3):
    output_file_name = sys.argv[2]
if (len(sys.argv) >= 4):
    method = sys.argv[3]  # 'maximum' or 'sort'

# The 'sort' method is a related heuristic we came up with that may or may not
# run slightly faster than the default 'maximum' method. Briefly, it sorts the
# conflict matrix so that the characters with the most conflicts are first; then
# it removes the first row that has more conflicts than the one after it. Since
# the matrix is initially sorted, this should usually delete the row with the
# most conflicts and should usually find it after checking only the first few
# columns. We ignored it for our report since the 'maximum' method, which checks
# rigorously for the maximum, is easier to explain and to calculate the runtime.

if method != 'maximum' and method != 'sort':
    raise IOError(method + ' is not a valid method, input "sort" or "maximum"')

# Create binary mutation matrix B from the input file
B, cells, mutations = util.read_matrix_from_file(input_file_name)

conflicts = []
for i in range(mutations):
    conflicts.append([0] * mutations)

for m1 in range(mutations):
    for m2 in range(m1):
        has_11 = False
        has_10 = False
        has_01 = False
        for n in range(cells):
            if B[n][m1] and B[n][m2]:
                has_11 = True
            elif B[n][m1] and not B[n][m2]:
                has_10 = True
            elif not B[n][m1] and B[n][m2]:
                has_01 = True
        if has_11 and has_10 and has_01:
            conflicts[m1][m2] = 1
            conflicts[m2][m1] = 1

#print('\nConflict matrix:')
#for row in conflicts:
    #print(row)

if method == 'sort':
    def num_conflicts(m):
        return sum(conflicts[m])

    mut_order = sorted(range(mutations), key=num_conflicts, reverse=True)

    sorted_conflicts = []
    for i in range(mutations):
        sorted_conflicts.append([0] * mutations)

        for i in range(mutations):
            for j in range(mutations):
                sorted_conflicts[i][j] = conflicts[mut_order[i]][mut_order[j]]

    #print('\nSorted conflict matrix:')
    #for row in sorted_conflicts:
        #print(row)
    conflicts = sorted_conflicts
else:
    mut_order = list(range(mutations))


# count of the number of mutations removed/ignored
muts_removed = 0

while True:
    # Find the character i with the most conflicts
    # Faster method
    if method == 'sort':
        i = 0
        while i+1 < len(conflicts) and sum(conflicts[i]) <= sum(conflicts[i+1]):
            i += 1
    # Maximum method (sorting is unnecessary for this one)
    else:
        f = lambda x: sum(conflicts[x])
        i = max(range(len(conflicts)), key=f)
    # Exit loop if there aren't any conflicts
    if sum(conflicts[i]) == 0:
        break
    # Delete the character
    del conflicts[i]
    for row in conflicts:
        del row[i]
    del mut_order[i]
    if method == 'maximum':
        for row in B:
            del row[i]
    muts_removed += 1
    #print('Deleted mutation', i)

#print('\nTrimmed conflict matrix:')
#for row in conflicts:
    #print(row)

#print('Mutations removed:', muts_removed)

if method == 'sort':
    Bcf =[] # conflict-free matrix
    #print('\nConflict-free matrix:')
    for cell in range(cells):
        row = [B[cell][j] for j in mut_order]
        Bcf.append(row)
        #print(row)

    B = Bcf # replace matrix

mutations = len(mut_order)

# Function to get number of instances of each mutation
def taxa_with_mutation(m):
    count = 0
    for cell in range(cells):
        count = count + B[cell][m]
    return count

# Determine order the mutations should be in, most frequent first
mut_order_2 = sorted(range(mutations), key=taxa_with_mutation, reverse=True)

#print(mut_order_2)
#print('\nSorted matrix:')

# Create sorted binary mutation matrix
Bs = []
for row in B:
    Bs.append([row[mut_order_2[i]] for i in range(mutations)])
    #print(Bs[-1])

# T is the root of the (currently-empty) tree we're building.
T = Tree(name='root')

for cell in range(cells):
    node = T # start at root
    for m in range(mutations): # For each possible mutation
        # If the cell doesn't have the mutation, move on
        if not Bs[cell][m]:
            continue
        # If the cell does have the mutation:
        edge_exists = False
        for child in node.children: # Search through children of current node
            if not child.is_leaf() and m == child.name:
                # Find an internal node with a matching mutation
                node = child # Walk down the edge
                edge_exists = True
                break
        if not edge_exists:
            # If no matching mutation was found, create a new path:
            child = node.add_child(name=m)
            node = child

    # Once we've gotten through all the mutations,
    # add the leaf node for the cell
    node.add_child(name=('C' + str(cell)))

#print(T) # aaaand we're done! I hope.
if muts_removed == 0:
    print('Perfect phylogeny found!')
else:
    print('Conflicts present, removed', muts_removed,
          'mutations to construct phylogeny')
    #print(muts_removed)

util.show_and_render_tree(T, output_file_name)
