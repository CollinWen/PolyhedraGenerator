
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const getPresets = async () => {
    try {
        const response = await axios.get(`${API_BASE}/presets`);
        return response.data.presets;
    } catch (error) {
        console.error("Error fetching presets:", error);
        return [];
    }
};

export const initializePolyhedron = async (presetName) => {
    try {
        const response = await axios.get(`${API_BASE}/initialize/${presetName}`);
        return response.data;
    } catch (error) {
        console.error("Error initializing polyhedron:", error);
        throw error;
    }
};

export const transformPolyhedron = async (type, currentPolyhedron, params = {}, code = null) => {
    try {
        const payload = {
            polyhedron: currentPolyhedron,
            params: params,
            code: code
        };
        const response = await axios.post(`${API_BASE}/transform/${type}`, payload);
        return response.data;
    } catch (error) {
        console.error(`Error applying transformation ${type}:`, error);
        throw error;
    }
};
