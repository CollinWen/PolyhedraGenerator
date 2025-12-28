
import React, { useState, useEffect } from 'react';
import PolyhedronViewer from './components/PolyhedronViewer';
import Controls from './components/Controls';
import { initializePolyhedron, transformPolyhedron } from './api';

function App() {
  const [data, setData] = useState(null);
  const [historyStack, setHistoryStack] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPreset, setSelectedPreset] = useState('icosahedron');
  const [selectionInfo, setSelectionInfo] = useState(null);

  const init = async (preset = selectedPreset) => {
    try {
      setLoading(true);
      setError(null);
      setData(null); // Clear for transition
      setHistoryStack([]);
      const poly = await initializePolyhedron(preset);
      setData(poly);
    } catch (err) {
      setError("Failed to initialize polyhedron system.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    init();
  }, [selectedPreset]);

  const handleTransform = async (type, params = {}, code = null) => {
    if (!data || loading) return;

    try {
      setLoading(true);
      // Push current state to history stack before transforming
      if (data) {
        setHistoryStack(prev => [...prev, data]);
      }

      const newData = await transformPolyhedron(type, data, params, code);
      setData(newData);
    } catch (err) {
      alert(`Transformation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUndo = () => {
    if (historyStack.length === 0 || loading) return;
    const prev = historyStack[historyStack.length - 1];
    setHistoryStack(prevStack => prevStack.slice(0, -1));
    setData(prev);
  };

  const handleReset = () => {
    init();
  };

  return (
    <>
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }}>
        {data && <PolyhedronViewer data={data} onSelection={setSelectionInfo} />}
      </div>

      {/* Top Left Header */}
      {/* Top Left Header */}
      <div style={{
        position: 'absolute',
        top: '30px',
        left: '30px',
        zIndex: 10,
        pointerEvents: 'none',
        // Removed border to be cleaner
      }}>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: '600',
          letterSpacing: '-1px',
          lineHeight: '1',
          marginBottom: '0.2rem',
          color: '#fff',
        }}>ICO<span style={{ color: 'var(--color-accent)', fontSize: '1rem', verticalAlign: 'top', marginLeft: '5px' }}>v1.0.0</span></h1>
      </div>

      {/* Top Right History Panel */}
      <div className="panel" style={{
        position: 'absolute',
        top: '30px',
        right: '30px',
        zIndex: 10,
        width: '250px',
        maxHeight: '300px',
        overflowY: 'auto',
        fontSize: '0.8rem',
        fontFamily: 'var(--font-mono)',
      }}>
        <div style={{ borderBottom: '1px solid #333', paddingBottom: '5px', marginBottom: '5px', color: 'var(--color-accent)' }}>
          OPERATION LOG
        </div>
        {data?.history && data.history.map((entry, idx) => (
          <div key={idx} style={{ padding: '2px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <span style={{ color: '#555', marginRight: '5px' }}>{idx.toString().padStart(2, '0')}</span>
            {entry}
          </div>
        ))}
        {(!data?.history || data.history.length === 0) && <div style={{ color: '#444' }}>No operations recorded.</div>}
      </div>

      {/* Bottom Right Details */}
      {selectionInfo && (
        <div className="panel" style={{
          position: 'absolute',
          bottom: '30px',
          right: '30px',
          zIndex: 10,
          width: '200px',
          fontSize: '0.7rem',
          fontFamily: 'var(--font-mono)',
        }}>
          <div style={{ color: 'var(--color-accent)', marginBottom: '5px', textTransform: 'uppercase' }}>SELECTION: {selectionInfo.type}</div>
          {selectionInfo.type === 'FACE' && <div>IDX: {selectionInfo.index}</div>}
          <div>DIST: {selectionInfo.distance.toFixed(4)}</div>
          <div>LOC: {selectionInfo.point.x.toFixed(2)}, {selectionInfo.point.y.toFixed(2)}, {selectionInfo.point.z.toFixed(2)}</div>
        </div>
      )}

      {/* Bottom Left Status */}
      <div style={{
        position: 'absolute',
        bottom: '30px',
        left: '30px',
        zIndex: 10,
        fontFamily: 'var(--font-mono)',
        fontSize: '0.7rem',
        color: 'var(--color-text-secondary)'
      }}>
        <div>VERTICES: {data?.vertices?.length || 0}</div>
        <div>FACES: {data?.faces?.length || 0}</div>
        <div>EDGES: {data?.edges?.length || 0}</div>
        <div>STATUS: <span style={{ color: loading ? 'var(--color-accent)' : '#0f0' }} className={loading ? 'blink' : ''}>{loading ? 'COMPUTING' : 'IDLE'}</span></div>
      </div>

      <Controls
        onTransform={handleTransform}
        onReset={handleReset}
        onUndo={handleUndo}
        canUndo={historyStack.length > 0}
        selectedPreset={selectedPreset}
        onPresetChange={setSelectedPreset}
        history={data?.history || []}
      />

      {error && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: 'var(--color-accent)',
          background: 'rgba(0,0,0,0.9)',
          padding: '2rem',
          border: '1px solid var(--color-accent)',
          zIndex: 30,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>ERROR</div>
          {error}
          <br />
          <div style={{ display: 'flex', gap: '10px', marginTop: '2rem' }}>
            <button onClick={() => setError(null)} style={{ width: '50%' }}>DISMISS</button>
            <button onClick={() => init()} style={{ width: '50%' }}>REBOOT</button>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
