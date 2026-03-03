/**
 * useAuth Hook
 * Custom hook for authentication state and operations
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/auth';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check authentication status on mount
  useEffect(() => {
    let mounted = true;

    const initializeAuth = async () => {
      setLoading(true);

      try {
        // Check if we have a stored token
        if (authService.isAuthenticated()) {
          // Get user from API to verify token is still valid
          const userData = await authService.getCurrentUser();

          if (mounted) {
            if (userData) {
              setIsAuthenticated(true);
              setUser(userData);
            } else {
              // Token was invalid, clear auth state
              setIsAuthenticated(false);
              setUser(null);
            }
          }
        } else {
          if (mounted) {
            setIsAuthenticated(false);
            setUser(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        if (mounted) {
          setIsAuthenticated(false);
          setUser(null);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };

    initializeAuth();

    return () => {
      mounted = false;
    };
  }, []);

  /**
   * Login with email and password
   */
  const login = useCallback(async (email, password) => {
    try {
      const { user: userData } = await authService.login(email, password);
      setUser(userData);
      setIsAuthenticated(true);
      return userData;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }, []);

  /**
   * Register a new user
   */
  const register = useCallback(async (email, password, name) => {
    try {
      const { user: userData } = await authService.register(email, password, name);
      setUser(userData);
      setIsAuthenticated(true);
      return userData;
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      await authService.logout();
      // The service will redirect to /login
    } catch (error) {
      console.error('Logout error:', error);
      // Force redirect on error
      window.location.href = '/login';
    }
  }, []);

  /**
   * Update user state
   */
  const updateUser = useCallback((userData) => {
    setUser(userData);
    authService.setUser(userData);
  }, []);

  /**
   * Refresh user data from API
   */
  const refreshUser = useCallback(async () => {
    try {
      const userData = await authService.getCurrentUser();
      if (userData) {
        setUser(userData);
      }
      return userData;
    } catch (error) {
      console.error('Refresh user error:', error);
      return null;
    }
  }, []);

  return {
    isAuthenticated,
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
    refreshUser,
  };
};

export default useAuth;
