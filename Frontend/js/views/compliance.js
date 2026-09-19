import { apiCall, hasSession } from '../api.js';

export async function submitSignature({ agreementType, signatureBase64 }) {
  if (!hasSession()) return { demo: true, agreement_type: agreementType, signature_token: signatureBase64 };
  return apiCall('/agreements/sign', { method: 'POST', body: JSON.stringify({ agreement_type: agreementType, signature_token: signatureBase64, signed_at: new Date().toISOString() }) });
}

export async function loadComplianceReport() {
  return hasSession() ? apiCall('/compliance/report') : [];
}

function renderComplianceView() {
  const view = document.querySelector('.workspace-view'); if (!view) return;
  view.innerHTML = '<div class="page-intro"><div><h2>Compliance consent</h2><p>Sign the FAIS and POPIA consent record securely.</p></div></div><div class="view-card"><canvas id="signatureCanvas" width="600" height="180" style="border:1px solid var(--line);max-width:100%"></canvas><div class="request-actions"><button class="secondary" id="clearSignature" type="button">Clear</button><button class="primary" id="submitSignature" type="button">Submit signature</button></div></div>';
  view.classList.add('active');
  const canvas = view.querySelector('#signatureCanvas'); const context = canvas.getContext('2d'); let drawing = false;
  const point = event => { const box = canvas.getBoundingClientRect(); return { x: (event.clientX - box.left) * canvas.width / box.width, y: (event.clientY - box.top) * canvas.height / box.height }; };
  canvas.addEventListener('pointerdown', event => { drawing = true; context.beginPath(); const position = point(event); context.moveTo(position.x, position.y); });
  canvas.addEventListener('pointermove', event => { if (!drawing) return; const position = point(event); context.lineTo(position.x, position.y); context.stroke(); });
  canvas.addEventListener('pointerup', () => { drawing = false; });
  view.querySelector('#clearSignature').onclick = () => context.clearRect(0, 0, canvas.width, canvas.height);
  view.querySelector('#submitSignature').onclick = async () => { try { const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data; const signed = [...pixels].some((value, index) => index % 4 === 3 && value > 0); if (!signed) throw new Error('Add your signature before submitting.'); await submitSignature({ agreementType: 'popia_consent', signatureBase64: canvas.toDataURL('image/png') }); window.showToast?.(hasSession() ? 'Consent signature submitted' : 'Consent signature saved in demo mode'); context.clearRect(0, 0, canvas.width, canvas.height); const submitButton = view.querySelector('#submitSignature'); submitButton.textContent = 'Submit signature'; submitButton.disabled = false; } catch (error) { window.showToast?.(error.message); } };
}

document.addEventListener('click', event => { if (event.target.closest('[data-view="compliance"]')) setTimeout(renderComplianceView, 0); });
