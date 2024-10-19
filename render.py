"""
Rendering and user inteface for rendering polyhedrons.
"""

import open3d as o3d

def render_polyhedron(vertices, edges, faces):
    """
    Render a polyhedron with the given vertices, edges, and faces.
    """ 
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(faces)
    mesh.compute_vertex_normals()
    mesh.compute_triangle_normals()
    mesh.paint_uniform_color([0.5, 0.5, 0.5])
    o3d.visualization.draw_geometries([mesh])
    
    
def render_polyhedron_2(vertices, edges, faces):
    # Create an Open3D LineSet object
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(vertices)
    line_set.lines = o3d.utility.Vector2iVector(edges)

    # Optionally, set the color of each edge
    colors = [[0, 0, 1] for _ in range(len(edges))]  # Blue color for all edges
    line_set.colors = o3d.utility.Vector3dVector(colors)

    # Visualize the icosahedron's edges
    o3d.visualization.draw_geometries([line_set], window_name="Icosahedron Edges", width=1000, height=1000)