// Scoring Service
// Legacy compatibility layer - re-exports from auditService
// This file is kept for backward compatibility but all
// functionality is now in auditService.js

export {
  // Audit operations
  getDashboardStats,
  listProjects,
  createProject,
  getProject,
  updateProject,
  deleteProject,

  // Audit/Scoring operations
  createAudit,
  listAudits,
  getAudit,
  cancelAudit,
  createBatch,
  getBatchStatus,

  // Report operations
  getReport,

  // API Keys
  listApiKeys,
  createApiKey,
  deleteApiKey,

  // Real-time updates
  subscribeToAuditProgress,
  pollAuditStatus,

  // Legacy compatibility functions
  submitForScoring,
  listSubmissions,
  getSubmissionStatus,
  getScoreReport,
  triggerScoring,
  subscribeToProgress,
  pollSubmissionStatus,
  downloadBulkTemplate,
  uploadBulkSubmissions,
  getBulkStatus,
  getQueueStats,
} from './auditService';

export default { subscribeToAuditProgress: import('./auditService').subscribeToAuditProgress };
