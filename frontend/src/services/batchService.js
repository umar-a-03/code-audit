// Batch Service
// API calls for batch submission management
// Maps to backend's audit/batch endpoints

import api from './api';

// Legacy: createBatch is now an alias for backend's batch audit creation
/**
 * Create a new batch audit
 * @param {Object} data - Batch data
 * @param {string} data.name - Batch name
 * @param {Array<string>} data.repo_urls - List of repository URLs
 * @param {Object} [data.options] - Optional analysis options
 * @returns {Promise<Object>} Created batch job
 */
export const createBatch = async (data) => {
  return api.post('/audits/batch', {
    name: data.name,
    repo_urls: data.repo_urls || [],
    options: data.options || {},
  });
};

/**
 * List all audits (equivalent to batches)
 * @param {Object} params - Query parameters
 * @param {number} [params.skip] - Number to skip
 * @param {number} [params.limit] - Max results
 * @param {string} [params.status] - Filter by status
 * @returns {Promise<Array>} List of audits
 */
export const listBatches = async (params = {}) => {
  const queryParams = new URLSearchParams();
  if (params.skip) queryParams.append('skip', params.skip);
  if (params.limit) queryParams.append('limit', params.limit);
  if (params.status) queryParams.append('status', params.status);

  return api.get(`/audits?${queryParams.toString()}`);
};

// Alias for listBatches for compatibility
export const listSubmissions = listBatches;

/**
 * Get batch audit status
 * @param {string} batchId - Batch ID
 * @returns {Promise<Object>} Batch status details
 */
export const getBatch = async (batchId) => {
  return api.get(`/audits/batch/${batchId}`);
};

/**
 * Update batch details (not supported by backend yet)
 * @param {string} batchId - Batch ID
 * @param {Object} data - Update data
 * @returns {Promise<Object>} Updated batch
 * @deprecated Backend does not support batch updates
 */
export const updateBatch = async (batchId, data) => {
  console.warn('updateBatch is not supported by the backend');
  return getBatch(batchId);
};

// Legacy: addSubmission maps to creating individual audits
/**
 * Add a submission to a batch (creates individual audit)
 * @param {string} batchId - Batch ID (not used, creates separate audit)
 * @param {Object} data - Submission data
 * @param {string} data.github_url - GitHub URL
 * @param {string} [data.branch] - Git branch
 * @returns {Promise<Object>} Created audit
 */
export const addSubmission = async (batchId, data) => {
  return api.post('/audits', {
    repo_url: data.github_url,
    branch: data.branch || 'main',
    analysis_type: 'full',
    options: {},
  });
};

/**
 * Add multiple submissions to a batch (creates multiple audits)
 * @param {string} batchId - Batch ID (not used, creates separate audits)
 * @param {Array<Object>} submissions - Array of submission data
 * @returns {Promise<Array>} Created audits
 */
export const addMultipleSubmissions = async (batchId, submissions) => {
  return Promise.all(
    submissions.map((data) => addSubmission(batchId, data))
  );
};

/**
 * Import submissions from CSV file (not supported by backend)
 * @param {string} batchId - Batch ID
 * @param {File} file - CSV file
 * @returns {Promise<Object>} Import result
 * @deprecated Backend does not support CSV import
 */
export const importCSV = async (batchId, file) => {
  console.warn('CSV import is not supported by the backend');
  throw new Error('CSV import is not supported');
};

/**
 * Start processing a batch (not supported by backend)
 * @param {string} batchId - Batch ID
 * @returns {Promise<Object>} Updated batch
 * @deprecated Backend starts processing immediately on batch creation
 */
export const startBatch = async (batchId) => {
  console.warn('startBatch is not supported - processing starts immediately');
  return getBatch(batchId);
};

/**
 * Get batch results with all submissions (uses batch status endpoint)
 * @param {string} batchId - Batch ID
 * @returns {Promise<Object>} Batch results with submissions and stats
 */
export const getBatchResults = async (batchId) => {
  return api.get(`/audits/batch/${batchId}`);
};

/**
 * Export batch results as CSV (not supported by backend)
 * @param {string} batchId - Batch ID
 * @returns {Promise<Blob>} CSV file blob
 * @deprecated Backend does not support CSV export
 */
export const exportBatchResults = async (batchId) => {
  console.warn('CSV export is not supported by the backend');
  throw new Error('CSV export is not supported');
};

/**
 * Delete a batch (not supported by backend)
 * @param {string} batchId - Batch ID
 * @returns {Promise<void>}
 * @deprecated Backend does not support batch deletion
 */
export const deleteBatch = async (batchId) => {
  console.warn('Batch deletion is not supported by the backend');
  throw new Error('Batch deletion is not supported');
};
