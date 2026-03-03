/**
 * Authentication service for traditional email/password authentication
 * Handles login, register, and token management
 */

import api from './api';

const TOKEN_KEY = 'access_token';
const USER_KEY = 'user';

export const authService = {
  /**
   * Register a new user
   * @param {string} email - User email
   * @param {string} password - User password
   * @param {string} [name] - Optional user name
   * @returns {Promise<{user: object, token: string}>}
   */
  register: async (email, password, name = null) => {
    const payload = { email, password };
    if (name) payload.name = name;

    const response = await api.post('/auth/register', payload);
    const { access_token, user } = response;

    // Store token and user
    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));

    return { user, token: access_token };
  },

  /**
   * Login with email and password
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<{user: object, token: string}>}
   */
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, user } = response;

    // Store token and user
    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));

    return { user, token: access_token };
  },

  /**
   * Logout user
   */
  logout: async () => {
    try {
      // Call logout endpoint (optional, for server-side cleanup)
      await api.post('/auth/logout');
    } catch (error) {
      // Ignore logout API errors
      console.warn('Logout API call failed:', error);
    }

    // Clear local storage
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);

    // Redirect to login page
    window.location.href = '/login';
  },

  /**
   * Get current user from API
   * @returns {Promise<object|null>}
   */
  getCurrentUser: async () => {
    try {
      const user = await api.get('/auth/me');
      // Update stored user data
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      return user;
    } catch (error) {
      // Token might be expired or invalid
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      return null;
    }
  },

  /**
   * Get stored token
   * @returns {string|null}
   */
  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },

  /**
   * Get stored user data
   * @returns {object|null}
   */
  getUser: () => {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Check if user is authenticated (has valid token)
   * @returns {boolean}
   */
  isAuthenticated: () => {
    return !!localStorage.getItem(TOKEN_KEY);
  },

  /**
   * Update stored user data
   * @param {object} user - User data to store
   */
  setUser: (user) => {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  },

  /**
   * Clear all auth data
   */
  clearAuth: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

export default authService;
