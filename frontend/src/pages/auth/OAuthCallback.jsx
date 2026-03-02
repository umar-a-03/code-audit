/**
 * OAuthCallback Component for Supabase
 * Handles OAuth redirect callbacks from Google via Supabase
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../../supabase/client';

const OAuthCallback = () => {
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Supabase handles the OAuth callback automatically
        // We just need to get the session and redirect
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();

        if (sessionError) {
          throw sessionError;
        }

        if (session?.user) {
          // Successfully authenticated
          navigate('/dashboard', { replace: true });
        } else {
          // No session - might be handling the redirect
          // Wait a moment and check again
          setTimeout(async () => {
            const { data: { session: retrySession } } = await supabase.auth.getSession();
            if (retrySession?.user) {
              navigate('/dashboard', { replace: true });
            } else {
              setError('Authentication failed. No session found.');
            }
          }, 1000);
        }
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError(err.message || 'Authentication failed. Please try again.');
      }
    };

    handleCallback();
  }, [navigate]);

  if (error) {
    return (
      <div className="min-h-screen bg-oled-black text-white flex items-center justify-center">
        <div className="text-center">
          <span className="material-symbols-outlined text-neon-red text-6xl">error</span>
          <h1 className="text-2xl font-mono mt-4 text-white">Authentication Failed</h1>
          <p className="text-gray-400 mt-2">{error}</p>
          <button
            onClick={() => navigate('/login')}
            className="mt-6 px-6 py-2 border border-primary text-primary hover:bg-primary/10 transition-colors font-mono text-sm"
          >
            &lt;&lt; BACK TO LOGIN
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-oled-black text-white flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block">
          <span className="material-symbols-outlined text-primary text-6xl animate-spin">progress_activity</span>
        </div>
        <p className="text-gray-400 mt-4 font-mono">Authenticating...</p>
      </div>
    </div>
  );
};

export default OAuthCallback;
