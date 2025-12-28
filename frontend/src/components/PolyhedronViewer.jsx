
import React, { useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, ContactShadows, Stars, SpotLight } from '@react-three/drei';
import * as THREE from 'three';

// Utility to convert polyhedron data to Three.js geometry
const usePolyhedronGeometry = (data) => {
    return useMemo(() => {
        if (!data) return null;

        const { vertices, faces, edges } = data;

        // Vertices
        const floatVertices = new Float32Array(vertices.flat());

        // Faces (triangulate if needed)
        const indices = [];
        faces.forEach(face => {
            // Simple fan triangulation for convex polygons
            for (let i = 1; i < face.length - 1; i++) {
                indices.push(face[0], face[i], face[i + 1]);
            }
        });

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(floatVertices, 3));
        geometry.setIndex(indices);
        geometry.computeVertexNormals();

        // Edges for wireframe
        const edgeIndices = [];
        if (edges && edges.length > 0) {
            edges.forEach(edge => {
                edgeIndices.push(edge[0], edge[1]);
            });
        } else {
            // Derive edges from faces if not provided
            const distinctEdges = new Set();
            faces.forEach(face => {
                for (let i = 0; i < face.length; i++) {
                    const a = face[i];
                    const b = face[(i + 1) % face.length];
                    const key = a < b ? `${a},${b}` : `${b},${a}`;
                    distinctEdges.add(key);
                }
            });
            distinctEdges.forEach(edge => {
                const [a, b] = edge.split(',').map(Number);
                edgeIndices.push(a, b);
            });
        }

        const edgeGeometry = new THREE.BufferGeometry();
        edgeGeometry.setAttribute('position', new THREE.BufferAttribute(floatVertices, 3));
        edgeGeometry.setIndex(edgeIndices);

        return { meshGeometry: geometry, edgeGeometry };
    }, [data]);
};

function PolyhedronMesh({ data, onSelect }) {
    const geometries = usePolyhedronGeometry(data);
    const meshRef = useRef();

    useFrame((state) => {
        if (meshRef.current) {
            meshRef.current.rotation.y += 0.001;
        }
    });

    const handleClick = (e) => {
        e.stopPropagation();
        onSelect({
            type: 'FACE',
            index: e.faceIndex,
            point: e.point,
            distance: e.distance
        });
    };

    const handleVertexClick = (e) => {
        e.stopPropagation();
        onSelect({
            type: 'VERTEX',
            index: e.index,
            point: e.point,
            distance: e.distance
        });
    };

    if (!geometries) return null;

    return (
        <group ref={meshRef}>
            {/* Inner Mesh (Matter) - Darker, Glossier */}
            <mesh
                geometry={geometries.meshGeometry}
                onClick={handleClick}
                onPointerOver={() => document.body.style.cursor = 'crosshair'}
                onPointerOut={() => document.body.style.cursor = 'default'}
            >
                <meshStandardMaterial
                    color="#2a2a2a"
                    roughness={0.2}
                    metalness={0.6}
                    flatShading={true}
                    emissive="#111111"
                    emissiveIntensity={0.2}
                />
            </mesh>

            {/* Wireframe - Glowing Edges */}
            <lineSegments geometry={geometries.edgeGeometry}>
                <lineBasicMaterial color="#444" opacity={0.3} transparent linewidth={1} />
            </lineSegments>

            {/* Vertices - Sharp Points */}
            <points geometry={geometries.meshGeometry} onClick={handleVertexClick}>
                <pointsMaterial size={0.08} color="#ffffff" transparent opacity={0.6} sizeAttenuation={true} />
            </points>
        </group>
    );
}

const PolyhedronViewer = ({ data, onSelection }) => {
    return (
        <div style={{ width: '100%', height: '100%' }}>
            <Canvas dpr={[1, 2]} gl={{ antialias: true, toneMapping: THREE.ReinhardToneMapping, toneMappingExposure: 1.5 }}>
                <PerspectiveCamera makeDefault position={[0, 0, 8]} fov={50} />

                <color attach="background" args={['#050505']} />

                {/* Natural Industrial Lighting */}
                <ambientLight intensity={0.4} />
                <spotLight position={[10, 10, 5]} angle={0.3} penumbra={0.5} intensity={1.5} color="#eef" castShadow />
                <pointLight position={[-10, 5, -5]} intensity={1} color="#ffaa88" /> {/* Warm accents */}
                <pointLight position={[0, -8, 5]} intensity={0.5} color="#aaccff" /> {/* Cool fill */}
                <Environment preset="city" />

                <PolyhedronMesh data={data} onSelect={onSelection} />

                <OrbitControls enablePan={false} enableZoom={true} minDistance={3} maxDistance={20} />

                {/* Simple grid floor for spatial ref */}
                <gridHelper args={[50, 50, 0x222222, 0x111111]} position={[0, -5, 0]} />

                <Stars radius={100} depth={50} count={2000} factor={4} saturation={0} fade speed={1} />
            </Canvas>
        </div>
    );
};

export default PolyhedronViewer;
