import { apiCall, hasSession } from '../api.js';

function initials(profile) {
  return `${profile.first_name?.[0] || ''}${profile.last_name?.[0] || ''}`.toUpperCase();
}

function setMetric(card, value, label) {
  const amount = card.querySelector('strong');
  const trend = card.querySelector('.trend');
  if (amount && value !== undefined) amount.textContent = `R ${Number(value).toLocaleString('en-ZA')}`;
  if (trend && label) trend.textContent = label;
}

let advisorMarkup = '';

function removeAdvisorView() {
  const advisorView = document.getElementById('adviserView');
  if (advisorView && !advisorMarkup) advisorMarkup = advisorView.outerHTML.replace(' adviser-only', '');
  advisorView?.remove();
}

function mountAdvisorView() {
  if (!advisorMarkup || document.getElementById('adviserView')) return document.getElementById('adviserView');
  const container = document.querySelector('.main');
  const template = document.createElement('template');
  template.innerHTML = advisorMarkup;
  const advisorView = template.content.firstElementChild;
  container.append(advisorView);
  document.getElementById('clientView').style.display = 'none';
  advisorView.style.display = 'block';
  return advisorView;
}

export function redirectUnauthorizedAdvisorAccess() {
  removeAdvisorView();
  document.getElementById('clientView').style.display = '';
  document.getElementById('crumb').textContent = 'Overview';
  document.querySelector('[data-view="dashboard"]')?.click();
}

export function installRoleSwitch() {
  const toggle = document.getElementById('roleToggle');
  if (!toggle) return;
  const authenticated = hasSession();
  const authenticatedAdvisor = document.getElementById('adviserView');
  toggle.textContent = authenticatedAdvisor?.style.display === 'block' ? 'View as client' : 'View as adviser';
  toggle.addEventListener('click', () => {
    let advisorView = document.getElementById('adviserView');
    const clientView = document.getElementById('clientView');
    if (!advisorView) {
      if (authenticated) {
        window.showToast?.('Advisor access requires an authenticated advisor account.');
        return;
      }
      advisorView = mountAdvisorView();
    }
    const showingAdvisor = advisorView.style.display === 'block';
    advisorView.style.display = showingAdvisor ? 'none' : 'block';
    clientView.style.display = showingAdvisor ? '' : 'none';
    document.getElementById('roleLabel').textContent = showingAdvisor ? 'Client view' : 'Advisor';
    document.getElementById('welcome').textContent = showingAdvisor ? 'Good morning, John' : 'Good morning, Sarah';
    document.getElementById('crumb').textContent = 'Overview';
    toggle.textContent = showingAdvisor ? 'View as adviser' : 'View as client';
    window.showToast?.(showingAdvisor ? 'Client interface loaded' : 'Advisor interface loaded');
  });
}

export async function hydrateDashboard() {
  removeAdvisorView();
  if (!hasSession()) return null;
  const [profile, summary] = await Promise.all([apiCall('/users/me'), apiCall('/dashboard/summary')]);
  const isAdvisor = profile.role === 'advisor' || profile.role === 'adviser';
  const displayName = `${profile.first_name || ''} ${profile.last_name || ''}`.trim();
  document.getElementById('welcome').textContent = `Good morning, ${profile.first_name || 'there'}`;
  document.getElementById('roleName').textContent = displayName;
  document.getElementById('roleLabel').textContent = isAdvisor ? 'Advisor' : 'Client';
  document.querySelector('.avatar').textContent = initials(profile);
  profile.role = isAdvisor ? 'advisor' : 'client';
  if (isAdvisor) mountAdvisorView();
  const cards = [...document.querySelectorAll('#clientView .metric')];
  setMetric(cards[0], summary.net_worth, 'Live from your plan');
  setMetric(cards[1], summary.total_assets, 'Linked products');
  setMetric(cards[2], summary.total_assets - summary.net_worth, 'Current protection');
  const claims = cards[3]?.querySelector('strong');
  if (claims) claims.textContent = summary.quick_action_count ?? 0;
  return profile;
}

window.addEventListener('hashchange', () => {
  if (window.location.hash === '#advisor' && !document.getElementById('adviserView')) {
    window.location.hash = '';
    redirectUnauthorizedAdvisorAccess();
  }
});

document.addEventListener('click', event => {
  const navigation = event.target.closest('[data-view]');
  if (!navigation) return;
  const advisorView = document.getElementById('adviserView');
  if (!advisorView) return;
  const isDashboard = navigation.dataset.view === 'dashboard';
  advisorView.style.display = isDashboard ? 'block' : 'none';
  document.getElementById('clientView').style.display = isDashboard ? 'none' : 'none';
});

