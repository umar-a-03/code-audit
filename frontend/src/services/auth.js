/**
 * Authentication service using Supabase
 * Handles Google OAuth authentication via Supabase
 */

import { supabase, supabaseAuth } from '../supabase/client';

const USER_KEY = 'user';

export const authService = {
  /**
   * Sign in with Google OAuth via Supabase
   */
  signInWithGoogle: async () => {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent',
        },
      },
    });
    if (error) throw error;
    return data;
  },

  /**
   * Sign in with GitHub OAuth via Supabase
   */
  signInWithGithub: async () => {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'github',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    if (error) throw error;
    return data;
  },

  /**
   * Sign out user
   */
  signOut: async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;

    // Clear local user data
    localStorage.removeItem(USER_KEY);

    // Redirect to login page
    window.location.href = '/login';
  },

  /**
   * Get current user from Supabase
   */
  getUser: async () => {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
  },

  /**
   * Get current session from Supabase
   */
  getSession: async () => {
    const { data: { session } } = await supabase.auth.getSession();
    return session;
  },

  /**
   * Set user in localStorage (for quick access)
   */
  setUser: (user) => {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  },

  /**
   * Clear user from localStorage
   */
  clearUser: () => {
    localStorage.removeItem(USER_KEY);
  },

  /**
   * Check if user is authenticated
   * Checks both Supabase session and localStorage
   */
  isAuthenticated: async () => {
    try {
      const session = await supabase.auth.getSession();
      return !!session?.session;
    } catch {
      return false;
    }
  },

  /**
   * Initialize auth state listener
   * Calls the callback when auth state changes
   */
  onAuthStateChange: (callback) => {
    return supabase.auth.onAuthStateChange((event, session) => {
      // Update localStorage when session changes
      if (event === 'SIGNED_IN' && session?.user) {
        authService.setUser(session.user);
      } else if (event === 'SIGNED_OUT') {
        authService.clearUser();
      }
      callback(event, session);
    });
  },

  /**
   * Legacy method for compatibility - delegates to getSession
   */
  getToken: async () => {
    const session = await supabaseAuth.getSession();
    return session?.session?.access_token || null;
  },

  /**
   * Legacy method - get user from both Supabase and localStorage
   */
  getUserData: async () => {
    try {
      // First try Supabase
      const { data: { user } } = await supabase.auth.getUser();
      if (user) return user;

      // Fallback to localStorage
      const userStr = localStorage.getItem(USER_KEY);
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      // Fallback to localStorage only
      const userStr = localStorage.getItem(USER_KEY);
      return userStr ? JSON.parse(userStr) : null;
    }
  },
};

export default authService;
