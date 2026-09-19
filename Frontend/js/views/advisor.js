import { apiCall, hasSession } from '../api.js';

function updateMetric(label, value) {
  const metric = [...document.querySelectorAll('#adviserView .metric')].find(card => card.querySelector('.eyebrow')?.textContent.trim() === label);
  const valueElement = metric?.querySelector('strong');
  if (valueElement && value !== undefined && value !== null) valueElement.textContent = Number.isFinite(Number(value)) ? Number(value).toLocaleString('en-ZA') : String(value);
}

export async function hydrateAdvisorWorkspace(profile) {
  if (!hasSession() || !['advisor', 'adviser'].includes(profile?.role)) return;
  try {
    const summary = await apiCall('/advisor/dashboard');
    updateMetric('Active clients', summary.total_clients);
    updateMetric('Open claims', summary.active_claims);
    updateMetric('Reviews this week', summary.reviews_this_week ?? summary.reviews_due_this_week ?? summary.upcoming_reviews);
    updateMetric('Pending requests', summary.pending_requests ?? summary.open_service_requests);

  } catch (error) {
    window.showToast?.(`Advisor dashboard unavailable: ${error.message}`);
  }
}
