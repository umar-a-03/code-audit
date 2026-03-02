import { createBrowserRouter } from 'react-router-dom';
import Layout from '../layouts/Layout';
import Dashboard from '../pages/dashboard/Dashboard';
import Settings from '../pages/settings/Settings';
import Batch from '../pages/batch/Batch';
import BatchResults from '../pages/batch/BatchResults';
import ProtectedRoute from '../components/auth/ProtectedRoute';
import { LoginPage, OAuthCallback } from '../pages/auth';

// TODO: Create these pages
// import Projects from '../pages/projects/Projects';
// import ProjectDetail from '../pages/projects/ProjectDetail';
// import NewAudit from '../pages/audits/NewAudit';
// import AuditResults from '../pages/audits/AuditResults';

// Use existing pages temporarily
import Submit from '../pages/submit/Submit';
import Candidates from '../pages/candidates/Candidates';
import CandidateDetail from '../pages/candidate/CandidateDetail';
import ScoringResults from '../pages/scoring/ScoringResults';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/auth/callback',
    element: <OAuthCallback />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'audits/new',
        element: <Submit />, // Will be replaced with NewAudit
      },
      {
        path: 'batch',
        element: <Batch />,
      },
      {
        path: 'batch/:batchId/results',
        element: <BatchResults />,
      },
      {
        path: 'projects',
        element: <Candidates />, // Will be replaced with Projects
      },
      {
        path: 'projects/:id',
        element: <CandidateDetail />, // Will be replaced with ProjectDetail
      },
      {
        path: 'audits/:id',
        element: <ScoringResults />, // Will be replaced with AuditResults
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      // Legacy routes for compatibility
      {
        path: 'submit',
        element: <Submit />,
      },
      {
        path: 'candidates',
        element: <Candidates />,
      },
      {
        path: 'candidate/:id',
        element: <CandidateDetail />,
      },
      {
        path: 'scoring/:submissionId',
        element: <ScoringResults />,
      },
    ],
  },
]);

export default router;
