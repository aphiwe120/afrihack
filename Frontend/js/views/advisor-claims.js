import { apiCall, hasSession } from '../api.js';

const STATUS_OPTIONS = [
  ['assessment_booked', 'Assessment booked'],
  ['repair_authorised', 'Repair authorised'],
  ['closed', 'Closed'],
];

function claimsPanel() {
  return [...document.querySelectorAll('#adviserView .panel')].find(panel => panel.querySelector('h3')?.textContent.trim() === 'Claims needing action');
}

function queueRow(claim) {
  const row = document.createElement('button');
  row.type = 'button';
  row.className = 'queue-row';
  row.dataset.claimId = claim.id;
  row.innerHTML = '<span><strong></strong><small></small></span><span class="status amber"></span>';
  row.querySelector('strong').textContent = claim.insurer_claim_number || claim.claim_number || `Claim ${claim.id}`;
  row.querySelector('small').textContent = claim.client_name || claim.incident_description || 'Claim requires advisor review';
  row.querySelector('.status').textContent = claim.status_label || 'Action needed';
  row.addEventListener('click', () => openClaimModal(claim.id));
  return row;
}

function closeClaimModal(modal) {
  modal.remove();
}

async function openClaimModal(claimId) {
  const modal = document.createElement('div');
  modal.className = 'modal-wrap open';
  modal.innerHTML = '<div class="modal"><div class="modal-head"><div><div class="breadcrumb">Advisor claim review</div><h2>Claim details</h2></div><button class="close" type="button" aria-label="Close claim details">×</button></div><div class="claim-detail"><p>Loading claim details...</p></div></div>';
  document.body.append(modal);
  modal.querySelector('.close').addEventListener('click', () => closeClaimModal(modal));
  modal.addEventListener('click', event => { if (event.target === modal) closeClaimModal(modal); });

  try {
    const claim = await apiCall(`/claims/${claimId}`);
    const detail = modal.querySelector('.claim-detail');
    detail.replaceChildren();
    const summary = document.createElement('p');
    summary.textContent = claim.incident_description || 'No incident description provided.';
    const form = document.createElement('form');
    form.className = 'view-form';
    form.innerHTML = '<label>Status<select name="status"></select></label><label>Provider update<textarea name="notes" required placeholder="Add the update for the provider timeline"></textarea></label><button class="primary" type="submit">Update claim</button>';
    const statusSelect = form.querySelector('select');
    STATUS_OPTIONS.forEach(([value, label]) => { const option = document.createElement('option'); option.value = value; option.textContent = label; option.selected = value === claim.status; statusSelect.append(option); });
    form.addEventListener('submit', async event => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(form));
      try {
        await apiCall(`/claims/${claimId}/timeline`, { method: 'POST', body: JSON.stringify(payload) });
        window.showToast?.('Claim status updated');
        closeClaimModal(modal);
        await hydrateAdvisorClaims({ role: 'advisor' });
      } catch (error) {
        window.showToast?.(`Claim update failed: ${error.message}`);
      }
    });
    detail.append(summary, form);
  } catch (error) {
    modal.querySelector('.claim-detail p').textContent = 'Claim details could not be loaded.';
    window.showToast?.(`Claim details unavailable: ${error.message}`);
  }
}

export async function hydrateAdvisorClaims(profile) {
  if (!hasSession() || !['advisor', 'adviser'].includes(profile?.role)) return;
  const panel = claimsPanel();
  if (!panel) return;
  try {
    const claims = await apiCall('/advisor/claims');
    panel.querySelectorAll('.queue-row').forEach(row => row.remove());
    claims.forEach(claim => panel.append(queueRow(claim)));
  } catch (error) {
    window.showToast?.(`Claims queue unavailable: ${error.message}`);
  }
}
