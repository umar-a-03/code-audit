import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAudit } from '../../services/auditService';
import PDFToggleUpload from '../../components/batch/PDFToggleUpload';

const Submit = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    project_name: '',
    repo_url: '',
    branch: 'main',
    analysis_type: 'full',
    rules_text: '',
    project_structure_text: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await createAudit({
        repo_url: formData.repo_url,
        branch: formData.branch,
        analysis_type: formData.analysis_type,
        options: {
          project_name: formData.project_name,
          rules_text: formData.rules_text || null,
          project_structure_text: formData.project_structure_text || null,
        },
      });

      // Debug: log the result to understand structure
      console.log('Audit creation result:', result);

      // Validate that we have a valid ID before navigation
      if (!result.id || result.id === 'undefined' || result.id === 'null') {
        setError('Audit created but ID not returned. Please try again.');
        setLoading(false);
        return;
      }

      // Navigate to audit results page with audit/job ID
      navigate(`/audits/${result.id}`);
    } catch (err) {
      // Handle error: err.detail might be an array (Pydantic validation) or a string
      let errorMessage = 'Failed to submit. Please try again.';
      if (err.detail) {
        if (Array.isArray(err.detail)) {
          // Pydantic validation error - extract messages
          errorMessage = err.detail.map(e => e.msg || 'Validation error').join(', ');
        } else if (typeof err.detail === 'string') {
          errorMessage = err.detail;
        } else if (err.detail.message) {
          errorMessage = err.detail.message;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2 font-mono">
          <span className="text-primary">&gt;&gt;</span> NEW AUDIT
        </h1>
        <p className="text-gray-400 text-sm font-mono">
          Analyze a GitHub repository with AI-powered code quality assessment
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Project Info Section */}
        <div className="border border-white/10 p-6 relative">
          <div className="absolute -top-3 left-4 bg-background px-2">
            <span className="text-xs text-primary font-mono">PROJECT_INFO</span>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2 font-mono">
              PROJECT_NAME <span className="text-gray-600">(optional)</span>
            </label>
            <input
              type="text"
              name="project_name"
              value={formData.project_name}
              onChange={handleChange}
              placeholder="My Awesome Project"
              className="w-full bg-black/50 border border-white/20 px-4 py-3 text-white font-mono text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary/50 transition-colors"
            />
          </div>
        </div>

        {/* Repository Section */}
        <div className="border border-white/10 p-6 relative">
          <div className="absolute -top-3 left-4 bg-background px-2">
            <span className="text-xs text-neon-green font-mono">REPOSITORY</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2 font-mono">
                REPOSITORY_URL <span className="text-neon-red">*</span>
              </label>
              <input
                type="url"
                name="repo_url"
                value={formData.repo_url}
                onChange={handleChange}
                required
                placeholder="https://github.com/username/repository"
                className="w-full bg-black/50 border border-white/20 px-4 py-3 text-white font-mono text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary/50 transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2 font-mono">
                BRANCH
              </label>
              <input
                type="text"
                name="branch"
                value={formData.branch}
                onChange={handleChange}
                placeholder="main"
                className="w-full bg-black/50 border border-white/20 px-4 py-3 text-white font-mono text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary/50 transition-colors"
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm text-gray-400 mb-2 font-mono">
              ANALYSIS_TYPE
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="analysis_type"
                  value="full"
                  checked={formData.analysis_type === 'full'}
                  onChange={handleChange}
                  className="accent-primary"
                />
                <span className="text-sm text-gray-300 font-mono">FULL</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="analysis_type"
                  value="quick"
                  checked={formData.analysis_type === 'quick'}
                  onChange={handleChange}
                  className="accent-primary"
                />
                <span className="text-sm text-gray-300 font-mono">QUICK</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="analysis_type"
                  value="security"
                  checked={formData.analysis_type === 'security'}
                  onChange={handleChange}
                  className="accent-primary"
                />
                <span className="text-sm text-gray-300 font-mono">SECURITY</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="analysis_type"
                  value="custom"
                  checked={formData.analysis_type === 'custom'}
                  onChange={handleChange}
                  className="accent-primary"
                />
                <span className="text-sm text-gray-300 font-mono">CUSTOM</span>
              </label>
            </div>
          </div>
        </div>

        {/* Advanced Options Section */}
        <div className="border border-white/10 p-6 relative">
          <div className="absolute -top-3 left-4 bg-background px-2">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-xs text-primary font-mono hover:text-primary/80 transition-colors flex items-center gap-2"
            >
              <span>{showAdvanced ? '▼' : '▶'}</span>
              <span>ADVANCED OPTIONS</span>
              <span className="text-gray-600">(optional)</span>
            </button>
          </div>

          {showAdvanced && (
            <div className="mt-4 space-y-6">
              {/* Rules Section */}
              <PDFToggleUpload
                label="CUSTOM RULES"
                value={formData.rules_text}
                onChange={(value) => setFormData((prev) => ({ ...prev, rules_text: value }))}
                placeholder="Enter custom evaluation rules here...&#10;&#10;For example:&#10;- Use TypeScript for type safety&#10;- Follow React hooks best practices&#10;- Implement proper error handling&#10;- Write unit tests for all functions"
              />

              {/* Project Structure Section */}
              <PDFToggleUpload
                label="PROJECT STRUCTURE"
                value={formData.project_structure_text}
                onChange={(value) => setFormData((prev) => ({ ...prev, project_structure_text: value }))}
                placeholder="Describe expected project structure...&#10;&#10;For example:&#10;- /src - Source code&#10;- /components - React components&#10;- /api - API endpoints&#10;- /utils - Utility functions&#10;- /tests - Test files"
              />
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="border border-neon-red/50 bg-neon-red/10 px-4 py-3">
            <p className="text-neon-red text-sm font-mono">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-primary/20 border border-primary text-primary px-6 py-3 font-mono text-sm hover:bg-primary/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                PROCESSING...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <span>&gt;&gt;</span> START AUDIT
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => setFormData({
              project_name: '',
              repo_url: '',
              branch: 'main',
              analysis_type: 'full',
              rules_text: '',
              project_structure_text: '',
            })}
            className="px-6 py-3 border border-white/20 text-gray-400 font-mono text-sm hover:border-white/40 transition-colors"
          >
            CLEAR
          </button>
        </div>
      </form>

      {/* Info Box */}
      <div className="mt-8 border border-white/10 p-4">
        <p className="text-xs text-gray-500 font-mono">
          <span className="text-primary">INFO:</span> The audit process may take 1-3 minutes depending on repository size.
          The system will analyze code structure, quality metrics, security patterns, and generate an AI-powered report.
        </p>
      </div>
    </div>
  );
};

export default Submit;
