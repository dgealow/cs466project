# util.py

import sys
from ete3 import Tree, faces, AttrFace, TextFace, TreeStyle

def read_matrix_from_file(input_file_name):
    # Create binary mutation matrix B from the input file
    with open(input_file_name, 'r') as f:
        line = f.readline()
        cells = int(line.split(' ')[0])  # Number of cells
        line = f.readline()
        mutations = int(line.split(' ')[0]) # Number of mutations

        B = []

        #print('Initial matrix:')

        for line in f:
            chars = line.rstrip().split(' ')
            row = [int(c) for c in chars]
            if len(row) != mutations:
                raise IOError('Error: incorrect number of mutations')
            B.append(row)
            #print(row)

        if len(B) != cells:
            raise IOError('Error: incorrect number of cells')
    # close input file
    return B, cells, mutations


def show_and_render_tree(tree, output_file_name, mut_order):
    # The following makes it show internal nodes
    def my_layout(node):
        if hasattr(node, 'has_face'):
            return
        if node.is_leaf():
            # If terminal node, draws its name
            name_face = AttrFace("name", fsize=12)
            node.add_face(name_face, column=0, position="branch-right")
        else:
            # If internal node, draws label with smaller font size
            if node.name == 'root':
                label = 'root'
            else:
                label = str(mut_order[int(node.name)])
            name_face = TextFace(label, fsize=10)
            node.add_face(name_face, column=0, position="branch-top")
        node.add_feature('has_face', True)
    # Adds the name face to the image at the preferred position
    #faces.add_face_to_node(name_face, node, column=0, position="branch-top")
    ts = TreeStyle()
    # Do not add leaf names automatically
    ts.show_leaf_name = False
    # Use my custom layout
    ts.layout_fn = my_layout
    tree.show(tree_style=ts)
    tree.render(output_file_name, tree_style=ts, dpi=180)
