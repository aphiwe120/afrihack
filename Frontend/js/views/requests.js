import { apiCall, hasSession } from '../api.js';

let currentProfile = null;
const REQUEST_STATUSES = [
  ['submitted', 'Submitted'],
  ['processing', 'Processing'],
  ['completed', 'Completed'],
];

function isAdvisor() {
  return ['advisor', 'adviser'].includes(currentProfile?.role);
}

function statusClass(status) {
  return String(status).toLowerCase() === 'submitted' ? 'status amber' : 'status';
}

function createRequestRow(request) {
  const row = document.createElement('div');
  row.className = 'data-row';
  const details = document.createElement('div');
  const title = document.createElement('strong');
  const metadata = document.createElement('small');
  const controls = document.createElement('div');
  const status = document.createElement('span');
  const update = document.createElement('button');

  title.textContent = request.request_type || 'Service request';
  metadata.textContent = `${request.client_name || request.user_name || 'Client'} · ${request.created_at ? new Date(request.created_at).toLocaleDateString('en-ZA') : 'Date unavailable'}`;
  status.className = statusClass(request.status);
  status.textContent = request.status || 'Submitted';
  update.type = 'button';
  update.className = 'secondary';
  update.textContent = 'Update';
  update.addEventListener('click', () => openUpdateModal(request));
  details.append(title, metadata);
  controls.className = 'request-actions';
  controls.append(status, update);
  row.append(details, controls);
  return row;
}

function openUpdateModal(request) {
  const modal = document.createElement('div');
  modal.className = 'modal-wrap open';
  modal.innerHTML = '<div class="modal"><div class="modal-head"><div><div class="breadcrumb">Advisor request queue</div><h2>Update service request</h2></div><button class="close" type="button" aria-label="Close request update">×</button></div><form class="view-form"><label>Status<select name="status"></select></label><button class="primary" type="submit">Save status</button></form></div>';
  document.body.append(modal);
  modal.querySelector('.close').addEventListener('click', () => modal.remove());
  modal.addEventListener('click', event => { if (event.target === modal) modal.remove(); });
  const select = modal.querySelector('select');
  REQUEST_STATUSES.forEach(([value, label]) => { const option = document.createElement('option'); option.value = value; option.textContent = label; option.selected = value === String(request.status).toLowerCase(); select.append(option); });
  modal.querySelector('form').addEventListener('submit', async event => {
    event.preventDefault();
    try {
      await apiCall(`/service-requests/${request.id}`, { method: 'PATCH', body: JSON.stringify({ status: select.value }) });
      modal.remove();
      window.showToast?.('Service request updated');
      await hydrateServiceRequests();
    } catch (error) {
      window.showToast?.(`Request update failed: ${error.message}`);
    }
  });
}

export async function hydrateServiceRequests(profile = currentProfile) {
  currentProfile = profile || currentProfile;
  if (!hasSession() || !isAdvisor()) return;
  const view = document.querySelector('.workspace-view');
  if (!view) return;
  try {
    const requests = await apiCall('/service-requests');
    view.innerHTML = '<div class="page-intro"><div><h2>Service requests</h2><p>Manage requests across your client portfolio.</p></div><span class="status amber"></span></div><div class="view-card"><div class="panel-head"><div><h3>Portfolio request queue</h3><p>Update submitted requests as they move through processing.</p></div></div><div class="request-list"></div></div>';
    view.querySelector('.status').textContent = `${requests.length} active`;
    const list = view.querySelector('.request-list');
    requests.forEach(request => list.append(createRequestRow(request)));
  } catch (error) {
    window.showToast?.(`Service requests unavailable: ${error.message}`);
  }
}

export function setServiceRequestProfile(profile) {
  currentProfile = profile;
}

document.addEventListener('click', event => {
  if (!event.target.closest('[data-view="requests"]') || !isAdvisor()) return;
  setTimeout(() => hydrateServiceRequests().catch(() => {}), 0);
});
