import { apiCall, hasSession } from '../api.js';

export async function submitEncryptedFna(payload, encryptedPayload) {
  if (!hasSession()) throw new Error('Sign in before submitting an FNA.');
  return apiCall('/fna', { method: 'POST', body: JSON.stringify({ ...payload, encrypted_payload: encryptedPayload }) });
}

export function renderRiskTier(tier) {
  const card = document.createElement('div'); card.className = 'view-card'; card.dataset.riskProfile = 'true'; card.innerHTML = '<h3>Risk profile</h3><p></p>'; card.querySelector('p').textContent = `Your calculated tier is ${String(tier).toLowerCase()}.`; document.querySelector('#clientView')?.append(card); return card;
}

async function encryptPayload(payload, keyHex) {
  if (!/^[\da-f]{64}$/i.test(keyHex)) throw new Error('FNA encryption is not configured for this session.');
  const key = await crypto.subtle.importKey('raw', Uint8Array.from(keyHex.match(/.{2}/g), value => parseInt(value, 16)), 'AES-GCM', false, ['encrypt']);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, new TextEncoder().encode(JSON.stringify(payload)));
  return { ciphertext: btoa(String.fromCharCode(...new Uint8Array(ciphertext))), iv: [...iv].map(value => value.toString(16).padStart(2, '0')).join('') };
}

function renderFnaView() {
  const view = document.querySelector('.workspace-view'); if (!view) return;
  view.innerHTML = '<div class="page-intro"><div><h2>Financial Needs Analysis</h2><p>Complete the four planning steps securely with your adviser.</p></div></div><div class="view-card"><form id="fnaForm" class="view-form"><label>Monthly income<input name="income" type="number" min="0" required></label><label>Monthly expenses<input name="expenses" type="number" min="0" required></label><label>Dependents<input name="dependents" type="number" min="0" required></label><label>Medical history<textarea name="medical_history" required></textarea></label><label>Risk profile<select name="risk_tier"><option value="cautious">Cautious</option><option value="moderate">Moderate</option><option value="assertive">Assertive</option></select></label><button class="primary" type="submit">Save FNA securely</button></form></div>';
  view.classList.add('active');
  view.querySelector('#fnaForm').addEventListener('submit', async event => { event.preventDefault(); const payload = Object.fromEntries(new FormData(event.currentTarget)); try { const encrypted = await encryptPayload(payload, sessionStorage.getItem('rsf_media_key') || ''); await submitEncryptedFna({ steps: ['personal', 'assets_liabilities', 'income_expenditure', 'risk_profile'] }, encrypted); renderRiskTier(payload.risk_tier); window.showToast?.('FNA saved securely'); } catch (error) { window.showToast?.(error.message); } });
}

document.addEventListener('click', event => { if (!event.target.closest('[data-view="fna"]')) return; setTimeout(renderFnaView, 0); });
