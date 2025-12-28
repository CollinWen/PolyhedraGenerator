"""
Core Polyhedron data structure and transformation utilities.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np

VertexArray = np.ndarray
EdgeArray = np.ndarray
Face = List[int]
FaceList = List[Face]


def _as_vertex_array(vertices: Optional[Sequence[Sequence[float]]]) -> VertexArray:
    if vertices is None:
        return np.zeros((0, 3), dtype=float)

    arr = np.asarray(vertices, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 3:
        raise ValueError("Vertices must be an (n, 3) array-like.")
    return arr


def _as_edge_array(edges: Optional[Sequence[Sequence[int]]]) -> EdgeArray:
    if edges is None:
        return np.zeros((0, 2), dtype=int)

    arr = np.asarray(edges, dtype=int)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError("Edges must be an (m, 2) array-like.")
    return arr


def _as_face_list(faces: Optional[Iterable[Sequence[int]]]) -> FaceList:
    if faces is None:
        return []
    
    # Handle numpy arrays specifically to avoid ambiguity
    if isinstance(faces, np.ndarray):
        if faces.size == 0:
            return []
    elif not faces:
        return []
        
    return [list(map(int, face)) for face in faces]


@dataclass
class Polyhedron:
    vertices: VertexArray
    edges: EdgeArray
    faces: Union[FaceList, np.ndarray, Iterable[Sequence[int]]]
    radius: Optional[float] = None
    radius: Optional[float] = None
    # Updated signature: Callable[[Face, np.ndarray], Tuple[float, float]]
    extrusion_fn: Optional[Callable[[Face, np.ndarray], Tuple[float, float]]] = None
    metadata: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, float] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    last_error: Optional[str] = None

    def __post_init__(self) -> None:
        self.vertices = _as_vertex_array(self.vertices)
        self.edges = _as_edge_array(self.edges)
        self.faces = _as_face_list(self.faces)


    def _set_state(
        self,
        vertices: Optional[VertexArray] = None,
        edges: Optional[Sequence[Sequence[int]]] = None,
        faces: Optional[Iterable[Sequence[int]]] = None,
    ) -> None:
        if vertices is not None:
            self.vertices = _as_vertex_array(vertices)

        if edges is not None:
            self.edges = _as_edge_array(edges)

        if faces is not None:
            self.faces = _as_face_list(faces)

    def _record_error(self, message: str) -> bool:
        self.last_error = message
        return False


    @property
    def vertex_count(self) -> int:
        return len(self.vertices)


    def dual_subdivision(self) -> bool:
        if not self.faces or self.vertex_count == 0:
            return self._record_error("Dual subdivision requires existing faces and vertices.")

        try:
            centroids = [
                np.mean(self.vertices[np.asarray(face, dtype=int)], axis=0)
                for face in self.faces
                if face
            ]
        except Exception as exc:  # pragma: no cover - defensive
            return self._record_error(f"Failed to compute face centroids: {exc}")

        if len(centroids) != len(self.faces):
            return self._record_error("Encountered empty face during centroid computation.")

        edge_to_faces: Dict[Tuple[int, int], List[int]] = {}
        for idx, face in enumerate(self.faces):
            face_len = len(face)
            for i in range(face_len):
                edge = tuple(sorted((face[i], face[(i + 1) % face_len])))
                edge_to_faces.setdefault(edge, []).append(idx)

        dual_edges_set = set()
        for face_indices in edge_to_faces.values():
            if len(face_indices) == 2:
                dual_edges_set.add(tuple(sorted(face_indices)))

        dual_edges = sorted(dual_edges_set)
        dual_faces: FaceList = []

        centroid_array = np.asarray(centroids, dtype=float)
        for v_idx in range(self.vertex_count):
            adjacent = [f_idx for f_idx, face in enumerate(self.faces) if v_idx in face]
            if len(adjacent) < 3:
                return self._record_error("Dual faces require a vertex adjacent to at least three faces.")

            local_center = centroid_array[np.asarray(adjacent)].mean(axis=0)

            # Sort adjacent faces to maintain consistent winding.
            # Improved sorting to handle chains (open or closed)
            ordered = [adjacent[0]]
            remaining = set(adjacent[1:])
            
            # Try to extend forward
            while remaining:
                last = ordered[-1]
                found = False
                for candidate in list(remaining):
                    edge_key = tuple(sorted((last, candidate)))
                    if edge_key in dual_edges_set:
                        ordered.append(candidate)
                        remaining.remove(candidate)
                        found = True
                        break
                if not found:
                    break
            
            # Try to extend backward if still remaining
            while remaining:
                first = ordered[0]
                found = False
                for candidate in list(remaining):
                    edge_key = tuple(sorted((first, candidate)))
                    if edge_key in dual_edges_set:
                        ordered.insert(0, candidate)
                        remaining.remove(candidate)
                        found = True
                        break
                if not found:
                    break
                    
            # If still have remaining, we have a disjoint set of faces incident to vertex.
            # This implies non-manifold or multiple fans. We just append them to be safe,
            # though the resulting face will be malformed.
            if remaining:
                 ordered.extend(list(remaining))

            # Ensure the orientation is consistent
            # We want the normal of the new face (dual face) to point outwards.
            # The new face lies around 'v_idx' of the original mesh.
            # So the normal should roughly align with the vector from the origin to that vertex
            # (assuming convex polyhedron centered at origin).
            if len(ordered) >= 3:
                # Calculate normal of the new face
                v0 = centroid_array[ordered[0]]
                v1 = centroid_array[ordered[1]]
                v2 = centroid_array[ordered[2]]
                
                # Normal of the potential face
                normal = np.cross(v1 - v0, v2 - v0)
                
                # Check against the original vertex position (which acts as a proxy for outward direction)
                original_vertex = self.vertices[v_idx]
                
                if np.dot(normal, original_vertex) < 0:
                     # If conflicting, reverse the order
                     ordered.reverse()

            dual_faces.append(ordered)
        
        self.history.append("Dual Subdivision")

        self._set_state(
            vertices=centroid_array,
            edges=dual_edges,
            faces=dual_faces,
        )
        return True

    def triangulate(self) -> bool:
        if not self.faces:
            return self._record_error("Triangulation requires existing faces.")

        new_vertices: List[np.ndarray] = []
        new_edges: List[Tuple[int, int]] = []
        new_faces: FaceList = []

        vertex_offset = self.vertex_count

        for face in self.faces:
            face_len = len(face)
            if face_len < 3:
                return self._record_error("Faces must contain at least three vertices.")

            if face_len == 3:
                new_faces.append(face[:])
                continue

            face_vertices = self.vertices[np.asarray(face, dtype=int)]
            centroid = face_vertices.mean(axis=0)
            new_vertices.append(centroid)
            centroid_idx = vertex_offset + len(new_vertices) - 1

            for i in range(face_len):
                v_current = face[i]
                v_next = face[(i + 1) % face_len]
                new_edges.append(tuple(sorted((v_current, centroid_idx))))
                new_faces.append([v_current, v_next, centroid_idx])

        if new_vertices:
            try:
                vertices = np.vstack((self.vertices, np.asarray(new_vertices, dtype=float)))
            except ValueError as exc:
                return self._record_error(f"Failed to append new vertices: {exc}")
        else:
            vertices = self.vertices.copy()

        if new_edges:
            unique_edges = sorted(set(new_edges))
            try:
                edges = np.vstack((self.edges, np.asarray(unique_edges, dtype=int)))
            except ValueError as exc:
                return self._record_error(f"Failed to append new edges: {exc}")
        else:
            edges = self.edges.copy()

        self.history.append("Triangulation")
        self._set_state(vertices=vertices, edges=edges, faces=new_faces)
        return True

    def geodesic_subdivision(self) -> bool:
        if not self.faces:
            return self._record_error("Geodesic subdivision requires existing faces.")

        midpoint_cache: Dict[Tuple[int, int], int] = {}
        new_vertices: List[np.ndarray] = []
        new_edges: List[Tuple[int, int]] = []
        new_faces: FaceList = []
        original_vertex_count = self.vertex_count

        for face in self.faces:
            if len(face) != 3:
                return self._record_error("Geodesic subdivision operates on triangular faces only.")

            face_midpoints: List[int] = []
            for i in range(3):
                v0 = face[i]
                v1 = face[(i + 1) % 3]
                edge_key = tuple(sorted((v0, v1)))

                if edge_key in midpoint_cache:
                    midpoint_idx = midpoint_cache[edge_key]
                else:
                    midpoint_coords = (self.vertices[v0] + self.vertices[v1]) / 2.0
                    midpoint_idx = original_vertex_count + len(new_vertices)
                    new_vertices.append(midpoint_coords)
                    midpoint_cache[edge_key] = midpoint_idx

                face_midpoints.append(midpoint_idx)
                new_edges.append(tuple(sorted((v0, midpoint_idx))))
                new_edges.append(tuple(sorted((v1, midpoint_idx))))

            # Connect midpoints together
            new_edges.extend(
                [
                    tuple(sorted((face_midpoints[0], face_midpoints[1]))),
                    tuple(sorted((face_midpoints[1], face_midpoints[2]))),
                    tuple(sorted((face_midpoints[2], face_midpoints[0]))),
                ]
            )

            new_faces.extend(
                [
                    [face_midpoints[0], face_midpoints[1], face_midpoints[2]],
                    [face[0], face_midpoints[0], face_midpoints[2]],
                    [face[1], face_midpoints[1], face_midpoints[0]],
                    [face[2], face_midpoints[2], face_midpoints[1]],
                ]
            )

        if new_vertices:
            try:
                vertices = np.vstack((self.vertices, np.asarray(new_vertices, dtype=float)))
            except ValueError as exc:
                return self._record_error(f"Failed to append geodesic vertices: {exc}")
        else:
            vertices = self.vertices.copy()

        if new_edges:
            unique_edges = sorted(set(new_edges))
            edges = np.asarray(unique_edges, dtype=int)
        else:
            edges = self.edges.copy()

        self.history.append("Geodesic Subdivision")
        self._set_state(vertices=vertices, edges=edges, faces=new_faces)
        return True

    def project_sphere(self) -> bool:
        target_radius = self.radius or self.metadata.get("radius") or 1.0
        if self.vertex_count == 0:
            return self._record_error("Sphere projection requires vertices.")

        norms = np.linalg.norm(self.vertices, axis=1, keepdims=True)
        if np.any(norms == 0):
            return self._record_error("Cannot project vertices lying at the origin.")

        self.vertices = (self.vertices / norms) * target_radius
        self.history.append(f"Sphere Projection (r={target_radius})")
        return True

    def face_extrusion(self) -> bool:
        extrude = self.extrusion_fn or self.metadata.get("extrusion_fn")
        if extrude is None:
            return self._record_error("No extrusion function configured on polyhedron.")

        new_vertices: List[np.ndarray] = []
        new_edges: List[Tuple[int, int]] = []
        new_faces: FaceList = []
        vertex_offset = self.vertex_count

        for face in self.faces:
            face_vertices = self.vertices[np.asarray(face, dtype=int)]
            if len(face) < 3:
                return self._record_error("Faces must contain at least three vertices.")

                return self._record_error("Faces must contain at least three vertices.")
            
            # PASS FACE VERTICES (and CENTROID context if desired) to the function
            # Updated signature: extrude(face_indices, face_vertices_coords) -> (length, scale)
            try:
                ext_len, ext_pct = extrude(face, face_vertices)
            except TypeError:
                 # Fallback for old signature: extrude(face_indices)
                 ext_len, ext_pct = extrude(face)

            centroid = face_vertices.mean(axis=0) * ext_len

            if np.isclose(ext_pct, 0.0):
                apex_idx = vertex_offset + len(new_vertices)
                new_vertices.append(centroid)
                for i, vid in enumerate(face):
                    next_vid = face[(i + 1) % len(face)]
                    new_edges.append(tuple(sorted((vid, apex_idx))))
                    new_faces.append([vid, next_vid, apex_idx])
                continue

            face_new_indices: List[int] = []
            for vid in face:
                vertex_coords = self.vertices[vid]
                # Fix: Interpret ext_pct as Scale Factor (1.0 = Prism, small = converging)
                # Formula: new = center + (old - center) * scale
                # Previous erroneous: old + (center - old) * scale  [This was Lerp(old, center, scale)]
                extruded = centroid + (vertex_coords - centroid) * ext_pct
                new_idx = vertex_offset + len(new_vertices)
                new_vertices.append(extruded)
                face_new_indices.append(new_idx)
                new_edges.append(tuple(sorted((vid, new_idx))))

            face_len = len(face_new_indices)
            for i in range(face_len):
                current = face_new_indices[i]
                nxt = face_new_indices[(i + 1) % face_len]
                new_edges.append(tuple(sorted((current, nxt))))
                new_faces.append([face[i], face[(i + 1) % len(face)], nxt, current])

            new_faces.append(face_new_indices)

        if new_vertices:
            try:
                vertices = np.vstack((self.vertices, np.asarray(new_vertices, dtype=float)))
            except ValueError as exc:
                return self._record_error(f"Failed to append extruded vertices: {exc}")
        else:
            vertices = self.vertices.copy()

        if new_edges:
            unique_edges = sorted(set(new_edges))
            edges = np.vstack((self.edges, np.asarray(unique_edges, dtype=int)))
        else:
            edges = self.edges.copy()

        faces = self.faces + new_faces
        self.history.append("Face Extrusion")
        self._set_state(vertices=vertices, edges=edges, faces=faces)
        return True
