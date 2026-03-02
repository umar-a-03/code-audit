// API Service Layer
// Axios instance with Supabase authentication

import axios from 'axios';
import { supabase } from '../supabase/client';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add Supabase auth token
api.interceptors.request.use(
  async (config) => {
    try {
      // Get Supabase session
      const { data: { session } } = await supabase.auth.getSession();

      if (session?.access_token) {
        // Add Supabase access token as Bearer token
        config.headers.Authorization = `Bearer ${session.access_token}`;
      }
    } catch (error) {
      // Session check failed, continue without auth
      console.warn('Failed to get Supabase session:', error);
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error);
  }
);

export default api;
