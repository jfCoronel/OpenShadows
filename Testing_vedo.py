"""Manually build a mesh from points and faces"""
from vedo import Mesh, show, Line
# Define the vertices and faces that make up the mesh
verts = [(0,0,0), (10,0,0), (10,0,5), (0,0,5)]
cells = [(0,1,2,3)] # cells same as faces

# Build the polygonal Mesh object from the vertices and faces
mesh = Mesh([verts, cells])

# Set the backcolor of the mesh to violet
# and show edges with a linewidth of 2
mesh.backcolor('violet')

# Create the first line and color it black
l1 = Line(verts).c('black').linewidth(5)

# Create labels for all vertices in the mesh showing their ID
labs = mesh.labels2d('pointid')

# Print the points and faces of the mesh as numpy arrays
print('vertices:', mesh.vertices) # same as mesh.points or mesh.coordinates
print('faces   :', mesh.cells)

# Show the mesh, vertex labels, and docstring
show(mesh, l1, labs, __doc__, viewup='z', axes=1).close()