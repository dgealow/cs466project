# two_state_naive.py

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

# Create sorted binary mutation matrix
Bs = []
for row in B:
    Bs.append([row[mut_order[i]] for i in range(mutations)])

#print(Bs)

# T is the root of the (currently-empty) tree we're building.
T = Tree(name='root')

for cell in range(cells):
    node = T # start at root
    for m in range(mutations): # For each possible mutation
        if not Bs[cell][m]:  # If the cell doesn't have the mutation
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
            # If no matching mutation was found, create a new path:
            child = node.add_child(name=m)
            node = child

    # Once we've gotten through all the mutations,
    # add the leaf node for the cell
    node.add_child(name=('C' + str(cell)))

#print(T) # aaaand we're done! I hope.

util.show_and_render_tree(T, output_file_name, mut_order)
