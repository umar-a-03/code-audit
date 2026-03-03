/**
 * SignupPage Component
 * Email/password registration page
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const SignupPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  const validateForm = () => {
    if (!formData.email.trim()) {
      setError('Email is required');
      return false;
    }
    if (!formData.password) {
      setError('Password is required');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await register(
        formData.email,
        formData.password,
        formData.name.trim() || null
      );
      // Redirect to dashboard on successful registration
      navigate('/dashboard');
    } catch (err) {
      console.error('Registration failed:', err);
      setError(err.detail || err.message || 'Failed to create account. Please try again.');
    } finally {
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

        {/* Signup Card */}
        <div className="border border-white/10 bg-black/50 backdrop-blur-sm p-8 relative">
          {/* Corner decorations */}
          <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-primary" />
          <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-primary" />
          <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-primary" />
          <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-primary" />

          <h2 className="text-xl font-mono text-center mb-8">
            <span className="text-primary">&gt;&gt;</span> CREATE ACCOUNT
          </h2>

          {/* Error Display */}
          {error && (
            <div className="mb-4 p-3 border border-neon-red bg-neon-red/10 text-neon-red text-sm font-mono">
              <span className="material-symbols-outlined text-sm align-middle mr-2">error</span>
              {error}
            </div>
          )}

          {/* Signup Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name Input */}
            <div>
              <label htmlFor="name" className="block text-sm font-mono text-gray-400 mb-2">
                Name <span className="text-gray-600">(optional)</span>
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-4 py-3 bg-black/50 border border-white/20 text-white font-mono text-sm focus:outline-none focus:border-primary focus:shadow-neon transition-all duration-200 disabled:opacity-50"
                placeholder="Enter your name"
              />
            </div>

            {/* Email Input */}
            <div>
              <label htmlFor="email" className="block text-sm font-mono text-gray-400 mb-2">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={loading}
                className="w-full px-4 py-3 bg-black/50 border border-white/20 text-white font-mono text-sm focus:outline-none focus:border-primary focus:shadow-neon transition-all duration-200 disabled:opacity-50"
                placeholder="Enter your email"
              />
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password" className="block text-sm font-mono text-gray-400 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={loading}
                className="w-full px-4 py-3 bg-black/50 border border-white/20 text-white font-mono text-sm focus:outline-none focus:border-primary focus:shadow-neon transition-all duration-200 disabled:opacity-50"
                placeholder="Create a password (min 8 characters)"
              />
            </div>

            {/* Confirm Password Input */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-mono text-gray-400 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                disabled={loading}
                className="w-full px-4 py-3 bg-black/50 border border-white/20 text-white font-mono text-sm focus:outline-none focus:border-primary focus:shadow-neon transition-all duration-200 disabled:opacity-50"
                placeholder="Confirm your password"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-primary/20 border border-primary hover:bg-primary/30 hover:shadow-neon transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <span className="material-symbols-outlined animate-spin">progress_activity</span>
                  <span className="font-mono text-sm">Creating account...</span>
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined">person_add</span>
                  <span className="font-mono text-sm group-hover:text-primary transition-colors">
                    Create Account
                  </span>
                </>
              )}
            </button>
          </form>

          {/* Login link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-400 font-mono">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-primary hover:text-primary/80 transition-colors"
              >
                Sign in
              </Link>
            </p>
          </div>

          {/* Info text */}
          <div className="mt-6 pt-6 border-t border-white/10 text-center">
            <p className="text-xs text-gray-500 font-mono">
              By creating an account, you agree to our Terms of Service and Privacy Policy
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

export default SignupPage;
