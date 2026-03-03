/**
 * Audit Service
 * API calls for code audit functionality with WebSocket support
 */

import api from './api';

// WebSocket connection manager for real-time audit progress
class WebSocketManager {
  constructor() {
    this.ws = null;
    this.subscribers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  /**
   * Get WebSocket URL from API base URL
   */
  getWebSocketUrl(auditId) {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = apiUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${wsHost}/api/v1/audits/${auditId}/events`;
  }

  /**
   * Connect to WebSocket server for audit updates
   */
  connect(auditId) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = this.getWebSocketUrl(auditId);
    console.log('[WebSocket] Connecting to', wsUrl);

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('[WebSocket] Connected to audit updates');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('[WebSocket] Received:', data);

        // Notify all subscribers for this audit
        const callbacks = this.subscribers.get(auditId);
        if (callbacks) {
          callbacks.forEach((cb) => cb(data));
        }
      } catch (err) {
        console.error('[WebSocket] Parse error:', err);
      }
    };

    this.ws.onclose = () => {
      console.log('[WebSocket] Disconnected');
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
    };
  }

  /**
   * Attempt to reconnect
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WebSocket] Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * this.reconnectAttempts;
    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      // We need the auditId to reconnect, which we don't have here
      // This is handled by re-subscribing from the component
    }, delay);
  }

  /**
   * Subscribe to audit progress updates
   */
  subscribeToAuditProgress(auditId, callback) {
    this.connect(auditId);

    if (!this.subscribers.has(auditId)) {
      this.subscribers.set(auditId, new Set());
    }
    this.subscribers.get(auditId).add(callback);

    return () => {
      const callbacks = this.subscribers.get(auditId);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.subscribers.delete(auditId);
          if (this.subscribers.size === 0) {
            this.disconnect();
          }
        }
      }
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.subscribers.clear();
  }
}

// Singleton instance
const wsManager = new WebSocketManager();

// ===========================================
// Dashboard API
// ===========================================

/**
 * Get dashboard statistics
 * @returns {Promise<Object>} Dashboard stats
 */
export const getDashboardStats = async () => {
  return api.get('/dashboard/stats');
};

// ===========================================
// Projects API
// ===========================================

/**
 * List all projects
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Projects list
 */
export const listProjects = async (params = {}) => {
  return api.get('/projects', { params });
};

/**
 * Create a new project
 * @param {Object} data - Project data
 * @returns {Promise<Object>} Created project
 */
export const createProject = async (data) => {
  return api.post('/projects', data);
};

/**
 * Get project by ID
 * @param {string} id - Project ID
 * @returns {Promise<Object>} Project details
 */
export const getProject = async (id) => {
  return api.get(`/projects/${id}`);
};

/**
 * Update project
 * @param {string} id - Project ID
 * @param {Object} data - Update data
 * @returns {Promise<Object>} Updated project
 */
export const updateProject = async (id, data) => {
  return api.put(`/projects/${id}`, data);
};

/**
 * Delete project
 * @param {string} id - Project ID
 * @returns {Promise<void>}
 */
export const deleteProject = async (id) => {
  return api.delete(`/projects/${id}`);
};

// ===========================================
// Audits API
// ===========================================

/**
 * Create a new audit
 * @param {Object} data - Audit data
 * @param {string} data.project_id - Project ID (optional)
 * @param {string} data.repo_url - Repository URL
 * @param {string} [data.branch] - Git branch
 * @param {string} [data.analysis_type] - Analysis type
 * @param {Object} [data.options] - Additional options
 * @returns {Promise<Object>} Created audit job
 */
export const createAudit = async (data) => {
  return api.post('/audits', data);
};

/**
 * List all audits
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Audits list
 */
export const listAudits = async (params = {}) => {
  return api.get('/audits', { params });
};

/**
 * Get audit by ID
 * @param {string} id - Audit ID
 * @returns {Promise<Object>} Audit details
 */
export const getAudit = async (id) => {
  return api.get(`/audits/${id}`);
};

/**
 * Cancel an audit
 * @param {string} id - Audit ID
 * @returns {Promise<Object>} Cancelled audit
 */
export const cancelAudit = async (id) => {
  return api.delete(`/audits/${id}`);
};

// ===========================================
// Batch Audits API
// ===========================================

/**
 * Create a batch audit
 * @param {Object} data - Batch data
 * @param {Array<string>} data.repo_urls - List of repository URLs
 * @param {string} [data.name] - Batch name
 * @returns {Promise<Object>} Created batch job
 */
export const createBatch = async (data) => {
  return api.post('/audits/batch', data);
};

/**
 * Get batch status
 * @param {string} batchId - Batch ID
 * @returns {Promise<Object>} Batch status
 */
export const getBatchStatus = async (batchId) => {
  return api.get(`/audits/batch/${batchId}`);
};

// ===========================================
// Reports API
// ===========================================

/**
 * Get audit report
 * @param {string} jobId - Job ID (audit ID)
 * @param {string} [format='json'] - Format (json, html, pdf)
 * @returns {Promise<Object>} Report data
 */
export const getReport = async (jobId, format = 'json') => {
  return api.get(`/audits/${jobId}/report`, {
    params: { format },
    responseType: format === 'pdf' ? 'blob' : 'json'
  });
};

// ===========================================
// API Keys Management
// ===========================================

/**
 * List all API keys for current user
 * @returns {Promise<Array>} API keys
 */
export const listApiKeys = async () => {
  return api.get('/api-keys');
};

/**
 * Store a new API key
 * @param {Object} data - API key data
 * @param {string} data.provider - Provider (openai, anthropic, etc.)
 * @param {string} data.key - API key
 * @param {string} [data.key_name] - Display name
 * @returns {Promise<Object>} Created API key
 */
export const createApiKey = async (data) => {
  return api.post('/api-keys', data);
};

/**
 * Delete an API key
 * @param {string} id - API key ID
 * @returns {Promise<void>}
 */
export const deleteApiKey = async (id) => {
  return api.delete(`/api-keys/${id}`);
};

// ===========================================
// Real-time Updates
// ===========================================

/**
 * Subscribe to real-time audit progress updates
 * @param {string} auditId - Audit ID
 * @param {function} onProgress - Progress callback
 * @returns {function} Unsubscribe function
 *
 * @example
 * const unsubscribe = subscribeToAuditProgress('audit_123', (data) => {
 *   console.log(`Progress: ${data.progress}% - ${data.message}`);
 *   if (data.status === 'completed') {
 *     console.log('Audit complete!', data.result);
 *   }
 * });
 *
 * // Later: unsubscribe();
 */
export const subscribeToAuditProgress = (auditId, onProgress) => {
  return wsManager.subscribeToAuditProgress(auditId, onProgress);
};

/**
 * Poll audit status until complete (fallback if WebSocket unavailable)
 * @param {string} auditId - Audit ID
 * @param {function} onProgress - Progress callback
 * @param {number} intervalMs - Polling interval in ms
 * @returns {Promise<Object>} Final audit result
 */
export const pollAuditStatus = async (auditId, onProgress, intervalMs = 2000) => {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const response = await getAudit(auditId);
        const audit = response.data || response;

        onProgress?.({
          audit_id: auditId,
          status: audit.status,
          progress: audit.status === 'completed' ? 100 : audit.status === 'running' ? 50 : 0,
          message: audit.error_message || `Status: ${audit.status}`,
        });

        if (audit.status === 'completed') {
          const report = await getReport(audit.id);
          resolve(report.data || report);
        } else if (audit.status === 'failed') {
          reject(new Error(audit.error_message || 'Audit failed'));
        } else {
          setTimeout(poll, intervalMs);
        }
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
};

// ===========================================
// Legacy compatibility (rename from scoringService)
// ===========================================

/**
 * @deprecated Use createAudit instead
 * Submit a repository for audit (legacy name from scoringService)
 */
export const submitForScoring = async (data) => {
  return createAudit({
    repo_url: data.github_url,
    branch: data.branch || 'main',
    analysis_type: data.analysis_type || 'full',
    options: {
      rules_text: data.rules_text || null,
      project_structure_text: data.project_structure_text || null,
    },
  });
};

/**
 * @deprecated Use listAudits instead
 */
export const listSubmissions = listAudits;

/**
 * @deprecated Use getAudit instead
 */
export const getSubmissionStatus = getAudit;

/**
 * @deprecated Use getReport instead
 */
export const getScoreReport = getReport;

/**
 * @deprecated Use subscribeToAuditProgress instead
 */
export const subscribeToProgress = subscribeToAuditProgress;

/**
 * @deprecated Use createAudit instead
 * Trigger scoring (legacy name)
 */
export const triggerScoring = submitForScoring;

/**
 * @deprecated Use pollAuditStatus instead
 * Poll submission status (legacy name)
 */
export const pollSubmissionStatus = pollAuditStatus;

/**
 * @deprecated Use downloadBulkTemplate if available
 * Download bulk template (placeholder)
 */
export const downloadBulkTemplate = async () => {
  throw new Error('downloadBulkTemplate not implemented');
};

/**
 * @deprecated Use uploadBulkSubmissions if available
 * Upload bulk submissions (placeholder)
 */
export const uploadBulkSubmissions = async () => {
  throw new Error('uploadBulkSubmissions not implemented');
};

/**
 * @deprecated Use getBatchStatus instead
 * Get bulk status (legacy name)
 */
export const getBulkStatus = getBatchStatus;

/**
 * @deprecated Use getDashboardStats for queue stats
 * Get queue stats (placeholder)
 */
export const getQueueStats = getDashboardStats;

export default api;
