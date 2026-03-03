// Scoring Service
// API calls for submission scoring with WebSocket support
// Maps to backend's audit endpoints

import api from './api';

// WebSocket connection manager
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
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = apiUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${wsHost}/api/v1/audits/${auditId}/events`;
  }

  /**
   * Connect to WebSocket server
   */
  connect(auditId) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = this.getWebSocketUrl(auditId);
    console.log('[WebSocket] Connecting to', wsUrl);

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('[WebSocket] Connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('[WebSocket] Received:', data);

        // Notify subscribers
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
    };

    this.ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
    };
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

/**
 * Submit a GitHub URL for scoring (creates audit)
 * @param {Object} data - Submission data
 * @param {string} data.github_url - GitHub repository URL
 * @param {string} [data.branch] - Git branch
 * @param {string} [data.analysis_type] - Analysis type
 * @param {Object} [data.options] - Additional options
 * @returns {Promise<Object>} Audit response with ID
 */
export const submitForScoring = async (data) => {
  return api.post('/audits', {
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
 * Get audit status
 * @param {string} submissionId - Audit ID
 * @returns {Promise<Object>} Audit details
 */
export const getSubmissionStatus = async (submissionId) => {
  return api.get(`/audits/${submissionId}`);
};

/**
 * Get full audit report
 * @param {string} submissionId - Audit ID
 * @returns {Promise<Object>} Complete audit report
 */
export const getScoreReport = async (submissionId) => {
  return api.get(`/audits/${submissionId}`);
};

/**
 * List all audits (submissions)
 * @param {Object} params - Query parameters
 * @param {number} [params.skip=0] - Number to skip
 * @param {number} [params.limit=20] - Max results
 * @param {string} [params.status] - Filter by status
 * @returns {Promise<Array>} List of audits
 */
export const listSubmissions = async (params = {}) => {
  const queryParams = new URLSearchParams();
  if (params.skip) queryParams.append('skip', params.skip);
  if (params.limit) queryParams.append('limit', params.limit);
  if (params.status) queryParams.append('status', params.status);

  return api.get(`/audits?${queryParams.toString()}`);
};

/**
 * Trigger scoring for an audit (not supported)
 * @param {string} submissionId - Audit ID
 * @returns {Promise<Object>} Updated audit
 * @deprecated Audits start immediately on creation
 */
export const triggerScoring = async (submissionId) => {
  console.warn('triggerScoring is deprecated - audits start immediately');
  return getSubmissionStatus(submissionId);
};

/**
 * Get dashboard statistics
 * @returns {Promise<Object>} Dashboard stats with counts and recent audits
 */
export const getDashboardStats = async () => {
  return api.get('/dashboard/stats');
};

/**
 * Subscribe to real-time progress updates for an audit
 * @param {string} submissionId - Audit ID
 * @param {function} onProgress - Callback for progress updates
 * @returns {function} Unsubscribe function
 */
export const subscribeToProgress = (submissionId, onProgress) => {
  return wsManager.subscribeToAuditProgress(submissionId, onProgress);
};

/**
 * Poll audit status until complete (fallback if WebSocket unavailable)
 * @param {string} submissionId - Audit ID
 * @param {function} onProgress - Progress callback
 * @param {number} intervalMs - Polling interval in ms
 * @returns {Promise<Object>} Final audit result
 */
export const pollSubmissionStatus = async (submissionId, onProgress, intervalMs = 2000) => {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const response = await getSubmissionStatus(submissionId);
        const audit = response.data || response;

        onProgress?.({
          submission_id: submissionId,
          stage: audit.status,
          progress: audit.status === 'completed' ? 100 : 50,
          message: `Status: ${audit.status}`,
        });

        if (audit.status === 'completed') {
          resolve(audit);
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
// Bulk Upload Functions (not supported by backend)
// ===========================================

/**
 * Download bulk submission Excel template
 * @returns {Promise<Blob>} Excel template file
 * @deprecated Not supported by backend
 */
export const downloadBulkTemplate = async () => {
  console.warn('Bulk template download is not supported');
  throw new Error('Bulk template download is not supported');
};

/**
 * Upload bulk submissions Excel file
 * @param {File} file - Excel file with submissions
 * @returns {Promise<Object>} Upload result with batch_id
 * @deprecated Not supported by backend - use batch audits instead
 */
export const uploadBulkSubmissions = async (file) => {
  console.warn('Bulk upload is not supported - use batch audits instead');
  throw new Error('Bulk upload is not supported - use batch audits instead');
};

/**
 * Get bulk upload status
 * @param {string} batchId - Batch ID from upload
 * @returns {Promise<Object>} Status with counts
 * @deprecated Not supported by backend
 */
export const getBulkStatus = async (batchId) => {
  console.warn('Bulk status is not supported');
  throw new Error('Bulk status is not supported');
};

/**
 * Get Redis Queue statistics
 * @returns {Promise<Object>} Queue stats
 * @deprecated Not supported by backend
 */
export const getQueueStats = async () => {
  console.warn('Queue stats is not supported');
  throw new Error('Queue stats is not supported');
};

export default api;
