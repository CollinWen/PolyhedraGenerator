
import React, { useState, useEffect } from 'react';
import { getPresets } from '../api';

const Controls = ({ onTransform, onReset, onUndo, canUndo, selectedPreset, onPresetChange, history }) => {
    const [presets, setPresets] = useState([]);
    const [params, setParams] = useState({ radius: 1.5 });
    const [customCode, setCustomCode] = useState(`def extrude(face):
    # Determines extrusion based on face properties
    # Return (length, scale_factor)
    import random
    return (1.0 + random.random(), 0.5)`);

    const [activePanel, setActivePanel] = useState(null); // 'project_sphere' | 'extrude' | null

    useEffect(() => {
        getPresets().then(setPresets);
    }, []);

    const isLocked = history && history.includes("Face Extrusion");

    const handleKeyDown = (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;
            const newValue = customCode.substring(0, start) + "    " + customCode.substring(end);
            setCustomCode(newValue);
            // Need to set cursor position after render, simplified here
        }
    };

    const transformations = [
        { id: 'dual', label: 'Dual Subdiv' },
        { id: 'geodesic', label: 'Geodesic' },
        { id: 'triangulate', label: 'Triangulate' },
        { id: 'project_sphere', label: 'Project Sphere', hasParams: true },
        { id: 'extrude', label: 'Extrude', hasParams: true },
    ];

    const handleClick = (t) => {
        if (t.hasParams) {
            if (activePanel === t.id) {
                setActivePanel(null); // Toggle off
            } else {
                setActivePanel(t.id);
            }
        } else {
            setActivePanel(null);
            onTransform(t.id);
        }
    };

    const handleApplyParam = (id) => {
        if (id === 'extrude') {
            onTransform(id, {}, customCode);
        } else {
            onTransform(id, params);
        }
    };

    return (
        <div style={{
            position: 'absolute',
            bottom: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '10px',
            zIndex: 10,
            width: '100%',
            maxWidth: '800px',
            pointerEvents: 'none' /* Let clicks pass through container area */
        }}>
            {/* Parameter Panels */}
            {activePanel === 'project_sphere' && (
                <div className="panel" style={{ pointerEvents: 'auto', marginBottom: '10px', width: '300px' }}>
                    <div style={{ marginBottom: '8px', fontSize: '0.8rem', color: 'var(--color-accent)' }}>TARGET RADIUS</div>
                    <input
                        type="range"
                        min="0.5"
                        max="5.0"
                        step="0.1"
                        value={params.radius}
                        onChange={(e) => setParams({ ...params, radius: parseFloat(e.target.value) })}
                        style={{ width: '100%' }}
                    />
                    <div style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{params.radius}</div>
                    <button onClick={() => handleApplyParam('project_sphere')} style={{ width: '100%', marginTop: '8px' }}>APPLY</button>
                </div>
            )}

            {activePanel === 'extrude' && (
                <div className="panel" style={{ pointerEvents: 'auto', marginBottom: '10px', width: '500px' }}>
                    <div style={{ marginBottom: '8px', fontSize: '0.8rem', color: 'var(--color-accent)' }}>CUSTOM EXTRUSION LOGIC (PYTHON)</div>
                    <textarea
                        value={customCode}
                        onChange={(e) => setCustomCode(e.target.value)}
                        style={{ width: '100%', height: '150px', background: '#050505', color: '#ccc', fontSize: '0.8rem', border: '1px solid #333' }}
                        spellCheck="false"
                        onKeyDown={handleKeyDown}
                    />
                    <button onClick={() => handleApplyParam('extrude')} style={{ width: '100%', marginTop: '8px' }}>EXECUTE</button>
                </div>
            )}

            {/* Main Bar */}
            <div className="panel" style={{
                pointerEvents: 'auto',
                display: 'flex',
                gap: '8px',
                padding: '12px',
                flexWrap: 'wrap',
                justifyContent: 'center',
                alignItems: 'center',
                border: '1px solid var(--color-text-secondary)',
                maxWidth: '95vw',
            }}>
                <select
                    value={selectedPreset}
                    onChange={(e) => onPresetChange(e.target.value)}
                    style={{ marginRight: '12px', textTransform: 'uppercase' }}
                >
                    {presets.map(p => <option key={p} value={p}>{p}</option>)}
                </select>

                <div style={{ width: '1px', background: '#333', margin: '0 8px' }}></div>

                {transformations.map(t => (
                    <button
                        key={t.id}
                        onClick={() => handleClick(t)}
                        disabled={isLocked && t.id !== 'extrude' && t.id !== 'project_sphere' ? true : (isLocked && t.id === 'extrude' ? true : false)}
                        style={activePanel === t.id ? { borderColor: 'var(--color-accent)', color: 'var(--color-accent)' } : {}}
                    >
                        {t.label} {t.hasParams && "..."}
                    </button>
                ))}

                <div style={{ width: '1px', background: '#333', margin: '0 8px' }}></div>

                <button
                    onClick={onUndo}
                    disabled={!canUndo}
                    style={{ color: canUndo ? '#fff' : '#555' }}
                >
                    UNDO
                </button>

                <button
                    onClick={onReset}
                    style={{ color: '#ff6b6b', borderColor: '#552222' }}
                >
                    RESET
                </button>
            </div>
        </div>
    );
};

export default Controls;
