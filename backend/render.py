"""
Rendering and user inteface for rendering polyhedrons.
"""

import open3d as o3d
import matplotlib.pyplot as plt
import numpy as np

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


def render_polyhedron_3(vertices, edges, faces):
    # Close previous figures to avoid conflicts
    plt.close('all')

    # Create an Open3D PointCloud for the vertices
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(vertices)

    # Create a mesh to visualize the faces
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(faces)
    mesh.compute_vertex_normals()

    # Create a LineSet to visualize the edges
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(vertices)
    line_set.lines = o3d.utility.Vector2iVector(edges)

    # Create a visualizer
    vis = o3d.visualization.Visualizer()
    vis.create_window()

    # Add geometries to the visualizer
    vis.add_geometry(point_cloud)
    vis.add_geometry(mesh)
    vis.add_geometry(line_set)

    # Render the scene and capture the camera position
    vis.run()
    vis.destroy_window()

    # To show vertex and face labels, we'll use matplotlib for 2D annotations

    # Visualize vertices and labels using matplotlib
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot vertices
    ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], c='r', s=100)
    
    # Add labels for vertices
    for i, vertex in enumerate(vertices):
        ax.text(vertex[0], vertex[1], vertex[2], f'V{i}', color='blue', fontsize=12)

    # Plot the faces (as lines)
    for face in faces:
        # Close the loop for each face by connecting back to the first vertex
        face_loop = np.append(face, face[0])
        ax.plot(vertices[face_loop, 0], vertices[face_loop, 1], vertices[face_loop, 2], color='k')

    # Show the plot with labels
    plt.show()
