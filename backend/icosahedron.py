"""
Generating icosahedrons and performing transformations on them.
"""


import numpy as np
# import open3d as o3d
from polyhedron import Polyhedron
# from render import *

def generate_icosahedron_vertices(radius):
    # The golden ratio
    phi = (1 + np.sqrt(5)) / 2

    # Define the 12 vertices of an icosahedron
    vertices = np.array([
        [-1,  phi, 0],
        [ 1,  phi, 0],
        [-1, -phi, 0],
        [ 1, -phi, 0],
        [0, -1,  phi],
        [0,  1,  phi],
        [0, -1, -phi],
        [0,  1, -phi],
        [ phi, 0, -1],
        [ phi, 0,  1],
        [-phi, 0, -1],
        [-phi, 0,  1]
    ])
    vertices *= radius

    # Define the 20 triangular faces of the icosahedron using vertex indices
    faces = np.array([
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ])

    # Collect all edges from the faces
    edges = set()
    for face in faces:
        edges.add(tuple(sorted([face[0], face[1]])))
        edges.add(tuple(sorted([face[1], face[2]])))
        edges.add(tuple(sorted([face[2], face[0]])))

    # Convert the set to a sorted list of edges
    edges = np.array(sorted(edges))

    return Polyhedron(vertices=vertices, edges=edges, faces=faces, radius=radius, metadata={"radius": radius})


def generate_cube(side_length):
    vertices = np.array([
        [side_length/2.0, side_length/2.0, side_length/2.0],                # 0
        [side_length/2.0, -1*side_length/2.0, side_length/2.0],             # 1
        [-1*side_length/2.0, -1*side_length/2.0, side_length/2.0],          # 2
        [-1*side_length/2.0, side_length/2.0, side_length/2.0],             # 3
        [side_length/2.0, side_length/2.0, -1*side_length/2.0],             # 4
        [side_length/2.0, -1*side_length/2.0, -1*side_length/2.0],          # 5
        [-1*side_length/2.0, -1*side_length/2.0, -1*side_length/2.0],       # 6
        [-1*side_length/2.0, side_length/2.0, -1*side_length/2.0],          # 7
    ])

    edges = np.array([
        [0, 1],
        [0, 3],
        [0, 4],
        [1, 2],
        [1, 5],
        [2, 6],
        [2, 3],
        [3, 7],
        [4, 5],
        [4, 7],
        [5, 6],
        [6, 7],
    ])

    faces: list[list[int]] = []

    return Polyhedron(vertices=vertices, edges=edges, faces=faces, metadata={"side_length": side_length})


def main():
    icosahedron = generate_icosahedron_vertices(5.0)

# render_polyhedron_3(icosahedron["vertices"], icosahedron["edges"], icosahedron["faces"])

    if not icosahedron.geodesic_subdivision():
        raise RuntimeError(icosahedron.last_error)

    # render_polyhedron_3(icosahedron["vertices"], icosahedron["edges"], icosahedron["faces"])

    # icosahedron = geodesic_subdivision(icosahedron["vertices"], icosahedron["edges"], icosahedron["faces"])

    icosahedron.radius = 10.0
    if not icosahedron.project_sphere():
        raise RuntimeError(icosahedron.last_error)

    # render_polyhedron_3(icosahedron["vertices"], icosahedron["edges"], icosahedron["faces"])

    if not icosahedron.dual_subdivision():
        raise RuntimeError(icosahedron.last_error)

    # render_polyhedron_3(icosahedron["vertices"], icosahedron["edges"], icosahedron["faces"])

    # icosahedron = triangulate(icosahedron["vertices"], icosahedron["edges"], icosahedron["faces"])

    # render_polyhedron_3(icosahedron["vertices"], icosahedron["edges"], icosahedron["faces"])

    # icosahedron = face_extrusion(icosahedron["vertices"], icosahedron["edges"], icosahedron["faces"], lambda x: (1.5, 0.75) if len(x) == 5 else (2, 0.8))
    
    # icosahedron["vertices"] = project_sphere(icosahedron["vertices"], radius=10.0)

    icosahedron.extrusion_fn = lambda x: (1.5, 0.75) if len(x) == 5 else (2, 0.8)
    if not icosahedron.face_extrusion():
        raise RuntimeError(icosahedron.last_error)

    if not icosahedron.triangulate():
        raise RuntimeError(icosahedron.last_error)

    print(icosahedron.vertices)
    print(icosahedron.edges)
    print(icosahedron.faces)

    render_polyhedron_3(icosahedron.vertices, icosahedron.edges, np.asarray(icosahedron.faces, dtype=int))

if __name__ == "__main__":
    main()
