import { useState, useEffect } from 'react';
import {
  SettingsSection,
  ApiKeyInput,
  TemperatureSlider,
  StatusBadge,
} from '../../components/settings';
import { listApiKeys, createApiKey, deleteApiKey } from '../../services/auditService';
import authService from '../../services/auth';

const Settings = () => {
  const user = authService.getUser();

  // API Keys state
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form state for new API key
  const [newKeyForm, setNewKeyForm] = useState({
    provider: 'openai',
    key_name: '',
    key_value: '',
  });
  const [showAddKey, setShowAddKey] = useState(false);

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      setLoading(true);
      const keys = await listApiKeys();
      setApiKeys(keys.data || keys || []);
    } catch (error) {
      console.error('Failed to fetch API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddApiKey = async () => {
    try {
      await createApiKey({
        provider: newKeyForm.provider,
        key: newKeyForm.key_value,
        key_name: newKeyForm.key_name || `${newKeyForm.provider} Key`,
      });

      // Reset form and refresh
      setNewKeyForm({ provider: 'openai', key_name: '', key_value: '' });
      setShowAddKey(false);
      fetchApiKeys();
    } catch (error) {
      console.error('Failed to add API key:', error);
      alert('Failed to add API key. Please check the format and try again.');
    }
  };

  const handleDeleteApiKey = async (id) => {
    if (!confirm('Are you sure you want to delete this API key?')) return;

    try {
      await deleteApiKey(id);
      fetchApiKeys();
    } catch (error) {
      console.error('Failed to delete API key:', error);
    }
  };

  const getProviderIcon = (provider) => {
    const icons = {
      openai: 'smart_toy',
      anthropic: 'psychology',
      claude: 'chat',
      gemini: 'auto_awesome',
      github: 'github',
    };
    return icons[provider] || 'key';
  };

  const getProviderLabel = (provider) => {
    const labels = {
      openai: 'OpenAI',
      anthropic: 'Anthropic',
      claude: 'Claude',
      gemini: 'Google Gemini',
      github: 'GitHub',
    };
    return labels[provider] || provider;
  };

  return (
    <div className="flex flex-col gap-8">
      {/* User Info Section */}
      <SettingsSection
        title="ACCOUNT"
        subtitle="Your account information"
        icon="person"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 border border-primary/50 overflow-hidden">
            <img
              src={user?.avatar || 'https://via.placeholder.com/64'}
              alt="Avatar"
              className="w-full h-full object-cover grayscale"
            />
          </div>
          <div>
            <p className="text-white font-mono">{user?.name || 'User'}</p>
            <p className="text-sm text-gray-400">{user?.email || ''}</p>
            <p className="text-xs text-primary font-mono mt-1">
              Provider: {user?.oauth_provider || 'Unknown'}
            </p>
          </div>
        </div>
      </SettingsSection>

      {/* AI Provider Configuration */}
      <SettingsSection
        title="AI_PROVIDERS"
        subtitle="Manage your AI provider API keys for code analysis"
        icon="psychology"
        gradient
      >
        {/* Existing API Keys */}
        <div className="space-y-3 mb-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-mono text-gray-400">YOUR_API_KEYS</h3>
            <button
              onClick={() => setShowAddKey(!showAddKey)}
              className="text-xs bg-primary/20 border border-primary text-primary px-3 py-1 hover:bg-primary/30 transition-colors font-mono flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-[14px]">add</span>
              {showAddKey ? 'CANCEL' : 'ADD_NEW_KEY'}
            </button>
          </div>

          {loading ? (
            <p className="text-gray-500 text-sm font-mono">Loading...</p>
          ) : apiKeys.length === 0 ? (
            <p className="text-gray-500 text-sm font-mono py-4 border border-dashed border-gray-700 text-center">
              No API keys configured. Add your first key to get started.
            </p>
          ) : (
            apiKeys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-3 border border-white/10 bg-black/50 hover:border-primary/30 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-primary text-[20px]">
                    {getProviderIcon(key.provider)}
                  </span>
                  <div>
                    <p className="text-white text-sm font-mono">{key.key_name}</p>
                    <p className="text-xs text-gray-500 font-mono">
                      {getProviderLabel(key.provider)} • {key.is_active ? 'Active' : 'Inactive'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {key.last_used_at && (
                    <p className="text-[10px] text-gray-600 font-mono">
                      Last used: {new Date(key.last_used_at).toLocaleDateString()}
                    </p>
                  )}
                  <button
                    onClick={() => handleDeleteApiKey(key.id)}
                    className="text-gray-500 hover:text-neon-red transition-colors p-1"
                  >
                    <span className="material-symbols-outlined text-[18px]">delete</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Add New Key Form */}
        {showAddKey && (
          <div className="border border-primary/50 bg-primary/5 p-4 space-y-4">
            <h3 className="text-xs font-mono text-primary mb-4">ADD_NEW_API_KEY</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Provider Selection */}
              <div>
                <label className="block text-xs font-mono text-gray-400 mb-2 uppercase">
                  AI Provider
                </label>
                <select
                  value={newKeyForm.provider}
                  onChange={(e) => setNewKeyForm({ ...newKeyForm, provider: e.target.value })}
                  className="w-full bg-black border border-gray-800 text-white font-mono text-sm py-2 px-3 focus:border-primary focus:outline-none transition-all"
                >
                  <option value="openai">OpenAI (GPT-4, GPT-3.5)</option>
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="gemini">Google Gemini</option>
                </select>
              </div>

              {/* Key Name */}
              <div>
                <label className="block text-xs font-mono text-gray-400 mb-2 uppercase">
                  Key Name (Optional)
                </label>
                <input
                  type="text"
                  value={newKeyForm.key_name}
                  onChange={(e) => setNewKeyForm({ ...newKeyForm, key_name: e.target.value })}
                  placeholder="My API Key"
                  className="w-full bg-black border border-gray-800 text-white font-mono text-sm py-2 px-3 focus:border-primary focus:outline-none transition-all"
                />
              </div>
            </div>

            {/* API Key Value */}
            <div>
              <label className="block text-xs font-mono text-gray-400 mb-2 uppercase">
                API Key
              </label>
              <input
                type="password"
                value={newKeyForm.key_value}
                onChange={(e) => setNewKeyForm({ ...newKeyForm, key_value: e.target.value })}
                placeholder="sk-..."
                className="w-full bg-black border border-gray-800 text-white font-mono text-sm py-2 px-3 focus:border-primary focus:outline-none transition-all"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowAddKey(false);
                  setNewKeyForm({ provider: 'openai', key_name: '', key_value: '' });
                }}
                className="px-4 py-2 border border-white/20 text-gray-400 font-mono text-xs hover:border-white/40 transition-colors"
              >
                CANCEL
              </button>
              <button
                onClick={handleAddApiKey}
                disabled={!newKeyForm.key_value}
                className="px-4 py-2 bg-primary text-black font-mono font-bold text-xs hover:bg-white transition-colors shadow-neon-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-[14px]">save</span>
                SAVE_KEY
              </button>
            </div>
          </div>
        )}

        {/* Info Box */}
        <div className="border border-white/10 p-3 bg-black/30">
          <p className="text-xs text-gray-500 font-mono">
            <span className="text-primary">INFO:</span> Your API keys are encrypted and stored securely.
            Keys are used only for analyzing your repositories and are never shared.
          </p>
        </div>
      </SettingsSection>

      {/* Analysis Preferences */}
      <SettingsSection
        title="ANALYSIS_PREFERENCES"
        subtitle="Default settings for code analysis"
        icon="tune"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Analysis Type */}
            <div>
              <label className="block text-xs font-mono text-gray-400 mb-2 uppercase">
                Default Analysis Type
              </label>
              <select
                defaultValue="full"
                className="w-full bg-black border border-gray-800 text-white font-mono text-sm py-2 px-3 focus:border-primary focus:outline-none transition-all"
              >
                <option value="full">Full Analysis</option>
                <option value="quick">Quick Scan</option>
                <option value="security">Security Only</option>
                <option value="custom">Custom Rules Only</option>
              </select>
            </div>

            {/* Default Branch */}
            <div>
              <label className="block text-xs font-mono text-gray-400 mb-2 uppercase">
                Default Branch
              </label>
              <input
                type="text"
                defaultValue="main"
                className="w-full bg-black border border-gray-800 text-white font-mono text-sm py-2 px-3 focus:border-primary focus:outline-none transition-all"
              />
            </div>
          </div>

          {/* Temperature/Analysis Depth */}
          <TemperatureSlider
            label="Analysis Depth"
            value={0.7}
            minLabel="Quick"
            maxLabel="Thorough"
          />
        </div>
      </SettingsSection>
    </div>
  );
};

export default Settings;
