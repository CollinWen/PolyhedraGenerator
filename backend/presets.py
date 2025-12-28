
import csv
import numpy as np
import os
from polyhedron import Polyhedron

def save_preset(name, vertices, faces):
    os.makedirs('presets', exist_ok=True)
    with open(f'presets/{name}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['type', 'c1', 'c2', 'c3'])
        
        for v in vertices:
            writer.writerow(['v', v[0], v[1], v[2]])
            
        for face in faces:
            row = ['f'] + [str(idx) for idx in face]
            writer.writerow(row)
    print(f"Generated presets/{name}.csv")

def generate_cube():
    s = 1.0
    vertices = np.array([
        [s, s, s], [s, -s, s], [-s, -s, s], [-s, s, s],
        [s, s, -s], [s, -s, -s], [-s, -s, -s], [-s, s, -s]
    ])
    faces = [
        [3, 2, 1, 0], # Front
        [5, 6, 7, 4], # Back
        [4, 7, 3, 0], # Top
        [2, 6, 5, 1], # Bottom
        [1, 5, 4, 0], # Right
        [7, 6, 2, 3]  # Left
    ]
    save_preset('cube', vertices, faces)

def generate_tetrahedron():
    vertices = np.array([
        [1, 1, 1],
        [1, -1, -1],
        [-1, 1, -1],
        [-1, -1, 1]
    ])
    faces = [
        [0, 1, 2],
        [0, 3, 1],
        [0, 2, 3],
        [1, 3, 2]
    ]
    save_preset('tetrahedron', vertices, faces)

def generate_cylinder():
    segments = 16
    height = 2.0
    radius = 1.0
    vertices = []
    
    # Bottom circle
    for i in range(segments):
        theta = 2 * np.pi * i / segments
        vertices.append([radius * np.cos(theta), -height/2, radius * np.sin(theta)])
        
    # Top circle
    for i in range(segments):
        theta = 2 * np.pi * i / segments
        vertices.append([radius * np.cos(theta), height/2, radius * np.sin(theta)])
        
    faces = []
    # Side faces (quads)
    for i in range(segments):
        bottom1 = i
        bottom2 = (i + 1) % segments
        top1 = i + segments
        top2 = (i + 1) % segments + segments
        faces.append([bottom2, bottom1, top1, top2])
        
    # Top and Bottom caps (n-gons)
    faces.append(list(range(segments))[::-1]) # Bottom cap (reversed for outward normal)
    faces.append(list(range(segments, 2*segments))) # Top cap
    
    save_preset('cylinder', np.array(vertices), faces)

def generate_icosahedron():
    phi = (1 + np.sqrt(5)) / 2
    vertices = np.array([
        [-1,  phi, 0], [ 1,  phi, 0], [-1, -phi, 0], [ 1, -phi, 0],
        [0, -1,  phi], [0,  1,  phi], [0, -1, -phi], [0,  1, -phi],
        [ phi, 0, -1], [ phi, 0,  1], [-phi, 0, -1], [-phi, 0,  1]
    ])
    faces = [
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ]
    save_preset('icosahedron', vertices, faces)

if __name__ == "__main__":
    generate_cube()
    generate_tetrahedron()
    generate_cylinder()
    generate_icosahedron()
