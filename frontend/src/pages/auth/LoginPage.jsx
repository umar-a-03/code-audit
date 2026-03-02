/**
 * LoginPage Component
 * Google OAuth login page via Supabase
 */

import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';

const LoginPage = () => {
  const { loginWithGoogle, loginWithGithub } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Initiating Google login...');
      await loginWithGoogle();
    } catch (err) {
      console.error('Google login failed:', err);
      setError(err.message || 'Failed to login with Google');
      setLoading(false);
    }
  };

  const handleGithubLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Initiating GitHub login...');
      await loginWithGithub();
    } catch (err) {
      console.error('GitHub login failed:', err);
      setError(err.message || 'Failed to login with GitHub');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-oled-black text-white flex items-center justify-center relative overflow-hidden">
      {/* Scanlines overlay */}
      <div className="scanlines absolute inset-0 pointer-events-none" />

      {/* Grid background */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.1] grid-bg" />

      {/* Main content */}
      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo/Branding */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="flex items-center justify-center w-16 h-16 text-primary border-2 border-primary shadow-neon bg-black/50">
              <span className="material-symbols-outlined text-4xl">terminal</span>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2 font-mono tracking-tight">
            Code<span className="text-primary">Audit</span>
          </h1>
          <p className="text-gray-400 text-sm font-mono">
            AI-Powered Code Analysis Platform
          </p>
        </div>

        {/* Login Card */}
        <div className="border border-white/10 bg-black/50 backdrop-blur-sm p-8 relative">
          {/* Corner decorations */}
          <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-primary" />
          <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-primary" />
          <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-primary" />
          <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-primary" />

          <h2 className="text-xl font-mono text-center mb-8">
            <span className="text-primary">&gt;&gt;</span> SIGN IN
          </h2>

          {/* Error Display */}
          {error && (
            <div className="mb-4 p-3 border border-neon-red bg-neon-red/10 text-neon-red text-sm font-mono">
              <span className="material-symbols-outlined text-sm align-middle mr-2">error</span>
              {error}
            </div>
          )}

          {/* OAuth Buttons */}
          <div className="space-y-4">
            {/* GitHub Login */}
            <button
              onClick={handleGithubLogin}
              disabled={loading}
              className="w-full flex items-center justify-center gap-3 px-6 py-4 border border-white/20 hover:border-primary hover:bg-primary/10 hover:shadow-neon transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="material-symbols-outlined animate-spin">progress_activity</span>
              ) : (
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A12.02 12.02 0 0024 12c0-6.627-5.373-12-12-12z" />
                </svg>
              )}
              <span className="font-mono text-sm group-hover:text-primary transition-colors">
                {loading ? 'Connecting...' : 'Continue with GitHub'}
              </span>
            </button>

            {/* Google Login */}
            <button
              onClick={handleGoogleLogin}
              disabled={loading}
              className="w-full flex items-center justify-center gap-3 px-6 py-4 border border-white/20 hover:border-primary hover:bg-primary/10 hover:shadow-neon transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="material-symbols-outlined animate-spin">progress_activity</span>
              ) : (
                <svg className="w-6 h-6" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
              )}
              <span className="font-mono text-sm group-hover:text-primary transition-colors">
                {loading ? 'Connecting...' : 'Continue with Google'}
              </span>
            </button>
          </div>

          {/* Info text */}
          <div className="mt-8 pt-6 border-t border-white/10 text-center">
            <p className="text-xs text-gray-500 font-mono">
              By continuing, you agree to our Terms of Service and Privacy Policy
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-[10px] text-gray-600 font-mono">
            System Status: <span className="text-neon-green">ONLINE</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
