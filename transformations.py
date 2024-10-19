import numpy as np


def dual_subdivision(vertices, edges, faces):
    """
    Converts polyhedron into its dual, center of faces become vertices.
    """

    centroids = []

    for face in faces:
        centroids.append(np.mean([vertices[f] for f in face], axis=0, keepdims=False))
        
    edge_to_face = {}

    for idx, face in enumerate(faces):
        for i in range(len(face)):
            edge = tuple(sorted((face[i], face[(i + 1) % len(face)])))
            if edge in edge_to_face:
                edge_to_face[edge].append(idx)
            else:
                edge_to_face[edge] = [idx]

    dual_edges = []
    for edge, face_list in edge_to_face.items():
        if len(face_list) == 2:
            dual_edges.append(sorted((face_list[0], face_list[1])))

    dual_faces = []
    for v_idx in range(len(vertices)):
        adjacent_faces = [f_idx for f_idx, face in enumerate(faces) if v_idx in face]
        dual_faces.append(adjacent_faces)

    return {
        "vertices": np.array(centroids),
        "edges": np.array(dual_edges),
        "faces": np.array(dual_faces)
    }
    

def triangulate(vertices, edges, faces):
    """
    Converts all non triangular faces into triangles.
    """

    new_vertices = []
    new_faces = []
    new_edges = []

    for face in faces:
        if len(face) > 3:
            centroid = np.mean([vertices[f] for f in face], axis=0, keepdims=False)
            new_vertices.append(centroid)
            centroid_idx = len(vertices) + len(new_vertices) - 1
            for i in range(len(face)):
                new_edges.append([face[i], centroid_idx])
                new_faces.append([face[i], face[(i + 1) % len(face)], centroid_idx])

    return {
        "vertices": np.vstack((np.array(vertices), np.array(new_vertices))), 
        "edges": np.vstack((np.array(edges), np.array(new_edges))), 
        "faces": np.array(new_faces)
    }


def geodesic_subdivision(vertices, edges, faces):
    """
    Divides all triangular faces into 4 subfaces by connecting the midpoints of each edge.
    """
    
    new_vertices = []
    new_edges = []
    new_faces = []

    num_faces = len(faces)
    for i in range(num_faces):
        face = faces[i]
        if len(face) == 3: # triangular face
            mid_points = []

            for i in range(len(face)):
                edge = (face[i], face[(i+1)%3])

                mp = tuple((vertices[edge[0]] + vertices[edge[1]])/2.0)
                if mp in new_vertices:
                    mid_points.append(len(vertices) + new_vertices.index(mp))
                else:
                    new_vertices.append(mp)
                    mid_points.append(len(vertices) + len(new_vertices) - 1)

                new_edges.append([edge[0], mid_points[-1]])
                new_edges.append([edge[1], mid_points[-1]])
            
            new_edges.append(sorted([mid_points[0], mid_points[1]]))
            new_edges.append(sorted([mid_points[1], mid_points[2]]))
            new_edges.append(sorted([mid_points[2], mid_points[0]]))

            new_faces.append((mid_points[0], mid_points[1], mid_points[2]))
            new_faces.append((face[0], mid_points[0], mid_points[2]))
            new_faces.append((face[1], mid_points[1], mid_points[0]))
            new_faces.append((face[2], mid_points[2], mid_points[1]))

    return {
        "vertices": np.vstack((vertices, np.array(new_vertices))), 
        "edges": np.array(new_edges), 
        "faces": np.array(new_faces)
    }
            

def project_sphere(vertices, radius=1.0):
    """
    Projects the vertices onto a unit sphere centered at origin.
    """
    
    v = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)
    v *= radius

    return v

