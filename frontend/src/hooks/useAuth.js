/**
 * useAuth Hook
 * Custom hook for authentication state and operations using Supabase
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/auth';
import { supabaseAuth } from '../supabase/client';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check authentication status on mount and set up listener
  useEffect(() => {
    let mounted = true;

    const initializeAuth = async () => {
      setLoading(true);

      try {
        // Check current Supabase session
        const session = await supabaseAuth.getSession();

        if (session && mounted) {
          const userData = await supabaseAuth.getUser();
          setIsAuthenticated(true);
          setUser(userData);
        } else {
          setIsAuthenticated(false);
          setUser(null);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        setIsAuthenticated(false);
        setUser(null);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    initializeAuth();

    // Set up Supabase auth state listener
    const { data: { subscription } } = supabaseAuth.onAuthStateChange((event, session) => {
      if (!mounted) return;

      if (event === 'SIGNED_IN' && session?.user) {
        setIsAuthenticated(true);
        setUser(session.user);
      } else if (event === 'SIGNED_OUT') {
        setIsAuthenticated(false);
        setUser(null);
      }
    });

    return () => {
      mounted = false;
      subscription?.unsubscribe();
    };
  }, []);

  /**
   * Login with Google via Supabase
   */
  const loginWithGoogle = useCallback(async () => {
    try {
      await authService.signInWithGoogle();
    // Supabase will redirect to Google OAuth, then back to /auth/callback
    } catch (error) {
      console.error('Google login error:', error);
      throw error;
    }
  }, []);

  /**
   * Login with GitHub via Supabase
   */
  const loginWithGithub = useCallback(async () => {
    try {
      await authService.signInWithGithub();
    // Supabase will redirect to GitHub OAuth, then back to /auth/callback
    } catch (error) {
      console.error('GitHub login error:', error);
      throw error;
    }
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      await authService.signOut();
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

  return {
    isAuthenticated,
    user,
    loading,
    loginWithGoogle,
    loginWithGithub,
    logout,
    updateUser,
  };
};

export default useAuth;
