/**
 * API service for thesis check system
 */
import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthCheck = () => api.get('/health');

export const getProviders = () => api.get('/providers');

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const saveConfig = (config) => api.post('/config', config);

export const getConfig = (sessionId) => api.get(`/config/${sessionId}`);

export const startCheck = (data) => api.post('/check', data);

export const getCheckStatus = (checkId) => api.get(`/check/${checkId}/status`);

export const getCheckReport = (checkId) => api.get(`/check/${checkId}/report`);

export const deleteFile = (fileId) => api.delete(`/upload/${fileId}`);

export const downloadPdfReport = (checkId) =>
  api.get(`/check/${checkId}/report/pdf`, {
    responseType: 'blob',
    headers: {
      'Accept': 'application/pdf'
    }
  });

export default api;
