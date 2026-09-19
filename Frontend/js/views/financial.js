import { apiCall, hasSession } from '../api.js';

function renderAssets(assets) {
  const rows = document.querySelectorAll('.view-card');
  const balance = [...rows].find(card => card.querySelector('h3')?.textContent === 'Balance sheet');
  if (!balance) return;
  balance.querySelectorAll('.data-row').forEach(row => row.remove());
  assets.forEach(asset => {
    const row = document.createElement('div'); row.className = 'data-row';
    row.innerHTML = `<div><strong></strong><small></small></div><strong></strong>`;
    row.querySelector('strong').textContent = asset.product_category;
    row.querySelector('small').textContent = `${asset.provider_name} · ${asset.policy_number}`;
    row.lastElementChild.textContent = `R ${Number(asset.current_value).toLocaleString('en-ZA')}`;
    balance.append(row);
  });
}

export async function hydrateFinancialPosition() {
  if (!hasSession()) return;
  const assets = await apiCall('/assets');
  renderAssets(assets);
}

function addAssetForm() {
  const wrapper = document.createElement('div'); wrapper.className = 'view-card'; wrapper.innerHTML = '<h3>Add asset</h3><form class="view-form"><label>Provider<select name="provider_name"><option>Santam</option><option>Sanlam</option><option>Discovery</option><option>Old Mutual</option><option>Liberty</option><option>Momentum</option></select></label><label>Policy number<input name="policy_number" required></label><label>Product category<input name="product_category" required placeholder="Investment or insurance"></label><label>Current value<input name="current_value" required type="number" min="0" step="0.01"></label><label>Valuation renewal date<input name="valuation_renewal_date" type="date"></label><button class="primary" type="submit">Save asset</button></form>'; document.querySelector('.workspace-view')?.append(wrapper); wrapper.querySelector('form').addEventListener('submit', async event => { event.preventDefault(); const data = Object.fromEntries(new FormData(event.currentTarget)); if (!hasSession()) return window.showToast?.('Sign in before adding an asset.'); await apiCall('/assets', { method: 'POST', body: JSON.stringify({ ...data, current_value: Number(data.current_value) }) }); window.showToast?.('Asset added'); await hydrateFinancialPosition(); wrapper.remove(); }); }

window.addEventListener('click', event => { if (event.target.closest('[data-view="financial"]')) setTimeout(() => { hydrateFinancialPosition().catch(() => {}); const introButton = document.querySelector('.workspace-view .page-intro .primary'); if (introButton) { introButton.textContent = '+ Add asset'; introButton.onclick = addAssetForm; } }, 0); });
