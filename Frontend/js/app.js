import { hydrateDashboard, installRoleSwitch } from './views/dashboard.js';
import { hydrateAdvisorWorkspace } from './views/advisor.js';
import { hydrateAdvisorClients } from './views/advisor-clients.js';
import { hydrateAdvisorClaims } from './views/advisor-claims.js';
import { setServiceRequestProfile } from './views/requests.js';
import './views/claims.js';
import './views/financial.js';
import './views/compliance.js';
import './views/fna.js';

window.showToast = window.showToast || (() => {});
window.addEventListener('DOMContentLoaded', async () => {
  try {
    const profile = await hydrateDashboard();
    installRoleSwitch();
    setServiceRequestProfile(profile);
    await hydrateAdvisorWorkspace(profile);
    await hydrateAdvisorClients(profile);
    await hydrateAdvisorClaims(profile);
  } catch (error) {
    console.warn('Royal Square API hydration unavailable:', error.message);
  }
});
