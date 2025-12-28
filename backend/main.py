
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
import numpy as np
import os
from typing import List, Optional, Tuple, Union, Any

from polyhedron import Polyhedron

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PolyhedronModel(BaseModel):
    vertices: List[List[float]]
    faces: List[List[int]]
    edges: Optional[List[List[int]]] = None
    radius: Optional[float] = None
    history: Optional[List[str]] = []

class TransformationRequest(BaseModel):
    polyhedron: PolyhedronModel
    params: Optional[dict] = {}
    code: Optional[str] = None

def ingest_csv(filepath: str) -> Polyhedron:
    vertices = []
    faces = []
    
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            if not row: continue
            if row[0] == 'v':
                vertices.append([float(x) for x in row[1:4]])
            elif row[0] == 'f':
                faces.append([int(x) for x in row[1:]])
                
    # Recalculate edges from faces
    edges = set()
    for face in faces:
        for i in range(len(face)):
            v1 = face[i]
            v2 = face[(i+1)%len(face)]
            edges.add(tuple(sorted((v1, v2))))
            
    return Polyhedron(
        vertices=np.array(vertices), 
        faces=faces, 
        edges=np.array(sorted(list(edges))) if edges else np.zeros((0, 2)),
        radius=1.0 # Default
    )

def poly_to_model(poly: Polyhedron) -> PolyhedronModel:
    # Ensure faces is list of lists
    if isinstance(poly.faces, np.ndarray):
        faces_list = poly.faces.tolist()
    else:
        faces_list = poly.faces
        
    return PolyhedronModel(
        vertices=poly.vertices.tolist(),
        faces=faces_list,
        edges=poly.edges.tolist() if poly.edges is not None else [],
        radius=poly.radius,
        history=poly.history
    )


def model_to_poly(model: PolyhedronModel) -> Polyhedron:
    edges = model.edges
    if edges is None:
        edges = []
    p = Polyhedron(
        vertices=np.array(model.vertices),
        faces=model.faces,
        edges=np.array(edges) if len(edges) > 0 else np.zeros((0, 2)),
        radius=model.radius
    )
    if model.history:
        p.history = model.history
    return p

@app.get("/api/initialize/{preset_name}")
async def initialize_polyhedron(preset_name: str):
    filepath = os.path.join("presets", f"{preset_name}.csv")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Preset not found")
    
    poly = ingest_csv(filepath)
    poly.history.append(f"Initialized {preset_name}")
    return poly_to_model(poly)

@app.get("/api/presets")
async def list_presets():
    try:
        files = os.listdir("presets")
        presets = [f.split('.')[0] for f in files if f.endswith('.csv')]
        return {"presets": presets}
    except FileNotFoundError:
        return {"presets": []}

@app.post("/api/transform/dual")
async def transform_dual(req: TransformationRequest):
    poly = model_to_poly(req.polyhedron)
    if not poly.dual_subdivision():
         raise HTTPException(status_code=400, detail=poly.last_error)
    return poly_to_model(poly)

@app.post("/api/transform/geodesic")
async def transform_geodesic(req: TransformationRequest):
    poly = model_to_poly(req.polyhedron)
    if not poly.geodesic_subdivision():
         raise HTTPException(status_code=400, detail=poly.last_error)
    return poly_to_model(poly)

@app.post("/api/transform/triangulate")
async def transform_triangulate(req: TransformationRequest):
    poly = model_to_poly(req.polyhedron)
    if not poly.triangulate():
         raise HTTPException(status_code=400, detail=poly.last_error)
    return poly_to_model(poly)

@app.post("/api/transform/project_sphere")
async def transform_project_sphere(req: TransformationRequest):
    poly = model_to_poly(req.polyhedron)
    
    # Update radius if provided
    if req.params and 'radius' in req.params:
        try:
            target_radius = float(req.params['radius'])
            poly.radius = target_radius
        except ValueError:
            pass

    if not poly.project_sphere():
         raise HTTPException(status_code=400, detail=poly.last_error)
    return poly_to_model(poly)


@app.post("/api/transform/extrude")
async def transform_extrude(req: TransformationRequest):
    poly = model_to_poly(req.polyhedron)
    
    if req.code:
        # Dynamic execution of custom extrusion function
        # The user provides a function body for 'extrude(face)'
        # We need to wrap it appropriately
        try:
            # We expect the code to define a function named 'extrude'
            # example:
            # def extrude(face):
            #     return (1.5, 0.5)
            
            local_scope = {}
            exec(req.code, {}, local_scope)
            
            if 'extrude' not in local_scope:
                 raise HTTPException(status_code=400, detail="Custom code must define a function named 'extrude'.")
                 
            poly.extrusion_fn = local_scope['extrude']
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing custom code: {str(e)}")
    else:
        # Default behavior
        # Default behavior
        # Updated signature: (face, verts)
        def extrusion_logic(face, verts=None):
            length = 1.5
            scale = 0.5
            return (length, scale)
        poly.extrusion_fn = extrusion_logic
    
    if not poly.face_extrusion():
         raise HTTPException(status_code=400, detail=poly.last_error)
    return poly_to_model(poly)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
