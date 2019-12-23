# two_state_fast.py

import sys
from ete3 import Tree
import util

# Default input and output files
input_file_name = 'data/perfect_phylogeny/m25_n25_s1.txt'
output_file_name = 'tree.png'
# Get input and output files from command-line arguments
if (len(sys.argv) >= 2):
    input_file_name = sys.argv[1]
if (len(sys.argv) >= 3):
    output_file_name = sys.argv[2]

# Create binary mutation matrix B from the input file
B, cells, mutations = util.read_matrix_from_file(input_file_name)

# Function to get number of instances of each mutation
def taxa_with_mutation(m):
    count = 0
    for cell in range(cells):
        count = count + B[cell][m]
    return count

# Determine order the mutations should be in, most frequent first
mut_order = sorted(range(mutations), key=taxa_with_mutation, reverse=True)

#print(mut_order)
#print('\nSorted matrix:')

# Create sorted binary mutation matrix
Bs = []
for row in B:
    Bs.append([row[mut_order[i]] for i in range(mutations)])
    #print(Bs[-1])

#print(Bs)

# T is the root of the (currently-empty) tree we're building.
T = Tree(name='root')

# Create an array of the nodes that each mutation occurs at
mut_node = [None] * mutations

# Create an array telling whether each mutation creates a conflict
conflicts = [False] * mutations

# And a flag for whether the given matrix permitted a perfect phylogeny
perfect = True

# And a count of the number of mutations removed/ignored
muts_removed = 0

for cell in range(cells):
    node = T # start at root
    for m in range(mutations): # For each possible mutation
        # If the cell doesn't have the mutation or it creates a conflict
        if not Bs[cell][m] or conflicts[m]:
            continue     # Move on
        # If the cell does have the mutation:
        edge_exists = False
        for child in node.children: # Search through children of current node
            if not child.is_leaf() and m == child.name:
                # Find an internal node with a matching mutation
                node = child # Walk down the edge
                edge_exists = True
                break
        if not edge_exists:
            # If the node for the mutation exists elsewhere, we have a conflict
            if mut_node[m] is not None:
                conflicts[m] = True
                perfect = False
                mut_node[m].delete()
                muts_removed += 1
                #print('Conflict found for mutation', m)
            else:
                # If no matching mutation was found, create a new path:
                child = node.add_child(name=m)
                node = child
                mut_node[m] = node

    # Once we've gotten through all the mutations,
    # add the leaf node for the cell
    node.add_child(name=('C' + str(cell)))

#print(T) # aaaand we're done! I hope.
if perfect:
    print('Perfect phylogeny found!')
else:
    print('Conflicts present, removed', muts_removed,
          'mutations to construct phylogeny')
    #print(muts_removed)

util.show_and_render_tree(T, output_file_name)
