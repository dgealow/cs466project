# two_state_conflict_matrix.py

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

    print('Initial matrix:')

    for line in f:
        chars = line.rstrip().split(' ')
        row = [int(c) for c in chars]
        if len(row) != mutations:
            raise IOError('Error: incorrect number of mutations')
        B.append(row)
        print(row)

    if len(B) != cells:
        raise IOError('Error: incorrect number of cells')
# close input file

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

print('\nConflict matrix:')
for row in conflicts:
    print(row)

def num_conflicts(m):
    return sum(conflicts[m])

mut_order = sorted(range(mutations), key=num_conflicts, reverse=True)

sorted_conflicts = []
for i in range(mutations):
    sorted_conflicts.append([0] * mutations)

for i in range(mutations):
    for j in range(mutations):
        sorted_conflicts[i][j] = conflicts[mut_order[i]][mut_order[j]]

print('\nSorted conflict matrix:')
for row in sorted_conflicts:
    print(row)

conflicts = sorted_conflicts

# count of the number of mutations removed/ignored
muts_removed = 0

while True:
    # Find the character i with the most conflicts
    # Faster method
    #i = 0
    #while i+1 < len(conflicts) and sum(conflicts[i]) <= sum(conflicts[i+1]):
    #    i += 1
    # Accurate method (sorting is unnecessary for this one)
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
    muts_removed += 1

print('\nTrimmed conflict matrix:')
for row in sorted_conflicts:
    print(row)

print('Mutations removed:', muts_removed)


Bcf =[] # conflict-free matrix
print('\nConflict-free matrix:')
for cell in range(cells):
    row = [B[cell][j] for j in mut_order]
    Bcf.append(row)
    print(row)

B = Bcf # replace matrix

mutations = len(mut_order)

# Function to get number of instances of each mutation
def taxa_with_mutation(m):
    count = 0
    for cell in range(cells):
        count = count + B[cell][m]
    return count

# Determine order the mutations should be in, most frequent first
mut_order = sorted(range(mutations), key=taxa_with_mutation, reverse=True)

#print(mut_order)
print('\nSorted matrix:')

# Create sorted binary mutation matrix
Bs = []
for row in B:
    Bs.append([row[mut_order[i]] for i in range(mutations)])
    print(Bs[-1])

# T is the root of the (currently-empty) tree we're building.
T = Tree(name='root')

# Create an array of the nodes that each mutation occurs at
mut_node = [None] * mutations

# Create an array telling whether each mutation creates a conflict
conflicts = [False] * mutations


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
                print('Conflict found for mutation', m)
                print('Something has gone horribly wrong')
            else:
                # If no matching mutation was found, create a new path:
                child = node.add_child(name=m)
                node = child
                mut_node[m] = node

    # Once we've gotten through all the mutations,
    # add the leaf node for the cell
    node.add_child(name=('C' + str(cell)))

#print(T) # aaaand we're done! I hope.
if muts_removed == 0:
    print('Perfect phylogeny found!')
else:
    print('Conflicts present, removed', muts_removed,
          'mutations to construct phylogeny')

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
