import { apiCall, hasSession } from '../api.js';

function requiresImmediateAction(client) {
  return Boolean(
    client.requires_immediate_action
    ?? client.requires_action
    ?? client.action_required
    ?? client.status === 'action_needed'
  );
}

function renderClientRow(client) {
  const row = document.createElement('tr');
  const clientCell = document.createElement('td');
  const name = document.createElement('strong');
  const reference = document.createElement('span');
  const portfolioCell = document.createElement('td');
  const activityCell = document.createElement('td');
  const statusCell = document.createElement('td');
  const status = document.createElement('span');

  name.textContent = `${client.first_name || ''} ${client.last_name || ''}`.trim() || 'Unnamed client';
  reference.textContent = client.id || client.reference || 'No reference';
  reference.style.color = 'var(--muted)';
  clientCell.append(name, document.createElement('br'), reference);

  const portfolioValue = client.portfolio_value ?? client.net_worth ?? client.assets_under_advice ?? 0;
  portfolioCell.textContent = `R ${Number(portfolioValue).toLocaleString('en-ZA')}`;
  activityCell.textContent = client.recent_activity || client.activity || client.next_review || 'No recent activity';

  const actionRequired = requiresImmediateAction(client);
  status.className = actionRequired ? 'status amber' : 'status';
  status.textContent = actionRequired ? 'Action needed' : (client.status_label || 'On track');
  statusCell.append(status);
  row.append(clientCell, portfolioCell, activityCell, statusCell);
  return row;
}

export async function hydrateAdvisorClients(profile) {
  if (!hasSession() || !['advisor', 'adviser'].includes(profile?.role)) return;
  const tableBody = document.querySelector('#adviserView .table tbody');
  if (!tableBody) return;

  try {
    const clients = await apiCall('/advisor/clients');
    tableBody.replaceChildren(...clients.map(renderClientRow));
  } catch (error) {
    window.showToast?.(`Client directory unavailable: ${error.message}`);
  }
}
