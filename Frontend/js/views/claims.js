import { apiCall, hasSession } from '../api.js';
import { decryptBlob, encryptFile } from '../crypto.js';

const DB_NAME = 'royal-square-offline';
const STORE_NAME = 'claim-drafts';

function openDrafts() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    request.onupgradeneeded = () => request.result.createObjectStore(STORE_NAME, { keyPath: 'requestId' });
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function saveDraft(draft) {
  const db = await openDrafts();
  await new Promise((resolve, reject) => { const request = db.transaction(STORE_NAME, 'readwrite').objectStore(STORE_NAME).put(draft); request.onsuccess = resolve; request.onerror = () => reject(request.error); });
}

export async function queueClaimDraft(payload, media = []) {
  await saveDraft({ requestId: crypto.randomUUID(), payload, media, createdAt: new Date().toISOString() });
}

export async function flushClaimDrafts() {
  if (!hasSession() || !navigator.onLine) return;
  const db = await openDrafts();
  const drafts = await new Promise((resolve, reject) => { const request = db.transaction(STORE_NAME).objectStore(STORE_NAME).getAll(); request.onsuccess = () => resolve(request.result); request.onerror = () => reject(request.error); });
  for (const draft of drafts) {
    const claim = await apiCall('/claims', { method: 'POST', headers: { 'Idempotency-Key': draft.requestId }, body: JSON.stringify(draft.payload) });
    if (claim?.id) for (const evidence of draft.media || []) { const body = new FormData(); body.append('file', evidence.blob, evidence.fileName); body.append('encryption_iv', evidence.encryptionIv); await apiCall(`/claims/${claim.id}/media`, { method: 'POST', body }); }
    const transaction = db.transaction(STORE_NAME, 'readwrite'); transaction.objectStore(STORE_NAME).delete(draft.requestId);
  }
}

export async function prepareEncryptedEvidence(files, masterKeyHex) {
  return Promise.all([...files].map(async file => { const encrypted = await encryptFile(file, masterKeyHex); return { fileName: file.name, fileType: file.type, blob: encrypted.blob, encryptionIv: encrypted.ivHex }; }));
}

export async function retrieveEvidence(claimId, evidenceId, masterKeyHex, ivHex, mediaType = 'image/*') {
  const signed = await apiCall(`/claims/${claimId}/media/${evidenceId}`);
  const response = await fetch(signed.url || signed);
  const decrypted = await decryptBlob(await response.blob(), masterKeyHex, ivHex, mediaType);
  const objectUrl = URL.createObjectURL(decrypted);
  return { objectUrl, revoke: () => URL.revokeObjectURL(objectUrl) };
}

window.addEventListener('online', () => flushClaimDrafts().catch(() => {}));

function fieldValue(label) {
  const field = [...document.querySelectorAll('#claimModal .form-step.active label')].find(item => item.firstChild?.textContent?.trim() === label);
  return field?.querySelector('input, select, textarea')?.value || '';
}

function claimPayload() {
  const steps = [...document.querySelectorAll('#claimModal .form-step')];
  const values = [...steps[1].querySelectorAll('input, select, textarea')].map(input => input.value);
  return {
    claim_type: values[0],
    incident_timestamp: values[1],
    incident_location: values[3],
    incident_description: values[10] || values[15],
    police_case_number: values[5] || null,
    driver_type: values[6],
    third_party_info: { vehicle_registration: values[11], insurer: values[12], policy_number: values[13] },
  };
}

document.addEventListener('click', async event => {
  if (event.target.id !== 'nextBtn' || document.querySelectorAll('#claimModal .form-step.active').length === 0) return;
  const activeStep = document.querySelector('#claimModal .form-step.active');
  const allSteps = document.querySelectorAll('#claimModal .form-step');
  if (activeStep !== allSteps[allSteps.length - 1]) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  const payload = claimPayload();
  const selectedFiles = [...(window.rsfSelectedEvidence || [])];
  try {
    const mediaKey = sessionStorage.getItem('rsf_media_key');
    if (selectedFiles.length && !mediaKey) throw new Error('Evidence encryption is not configured for this session.');
    const media = mediaKey ? await prepareEncryptedEvidence(selectedFiles, mediaKey) : [];
    if (!navigator.onLine || !hasSession()) {
      await queueClaimDraft(payload, media);
      window.showToast?.('Claim saved securely for sync when you are online');
      document.getElementById('claimModal').classList.remove('open');
      return;
    }
    const claim = await apiCall('/claims', { method: 'POST', headers: { 'Idempotency-Key': crypto.randomUUID() }, body: JSON.stringify(payload) });
    if (claim?.id) for (const evidence of media) { const body = new FormData(); body.append('file', evidence.blob, evidence.fileName); body.append('encryption_iv', evidence.encryptionIv); await apiCall(`/claims/${claim.id}/media`, { method: 'POST', body }); }
    window.showToast?.('Claim submitted securely');
    document.getElementById('claimModal').classList.remove('open');
  } catch (error) {
    window.showToast?.(error.message);
  }
}, true);
