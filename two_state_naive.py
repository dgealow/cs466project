# two_state_naive.py

import sys
from ete3 import Tree, faces, AttrFace, TreeStyle

# Default input and output files
inputFileName = 'data/perfect_phylogeny/m25_n25_s1.txt'
outputFileName = 'tree.png'
# Get input and output files from command-line arguments
if (len(sys.argv) >= 2):
    inputFileName = sys.argv[1]
if (len(sys.argv) >= 3):
    outputFileName = sys.argv[2]

# Create binary mutation matrix B from the input file
with open(inputFileName, 'r') as f:
    line = f.readline()
    cells = int(line.split(' ')[0])  # Number of cells
    line = f.readline()
    mutations = int(line.split(' ')[0]) # Number of mutations

    B = []

    for line in f:
        chars = line.rstrip().split(' ')
        row = [int(c) for c in chars]
        if len(row) != mutations:
            raise IOError('Error: incorrect number of mutations')
        B.append(row)

    if len(B) != cells:
        raise IOError('Error: incorrect number of cells')
# close input file

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

# The following makes it show internal nodes
def my_layout(node):
    if node.is_leaf():
         # If terminal node, draws its name
         name_face = AttrFace("name", fsize=12)
         node.add_face(name_face, column=0, position="branch-right")
    else:
         # If internal node, draws label with smaller font size
         name_face = AttrFace("name", fsize=10)
         node.add_face(name_face, column=0, position="branch-top")
    # Adds the name face to the image at the preferred position
    #faces.add_face_to_node(name_face, node, column=0, position="branch-top")

ts = TreeStyle()
# Do not add leaf names automatically
ts.show_leaf_name = False
# Use my custom layout
ts.layout_fn = my_layout

T.show(tree_style=ts)
#T.render(outputFileName)
