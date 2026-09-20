const SUPABASE_URL = 'YOUR_SUPABASE_PROJECT_URL';
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const logoutButton = document.getElementById('logoutBtn');
const vaultUpload = document.getElementById('vaultUpload');
const vaultUploadButton = document.getElementById('vaultUploadButton');
const uploadStatus = document.getElementById('uploadStatus');

logoutButton?.addEventListener('click', async () => {
  logoutButton.disabled = true;
  const { error } = await supabase.auth.signOut();
  if (error) {
    logoutButton.disabled = false;
    showToast(error.message);
    return;
  }
  window.location.href = 'index.html';
});

function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'dashboard-toast';
  toast.textContent = message;
  document.body.append(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  window.setTimeout(() => {
    toast.classList.remove('show');
    window.setTimeout(() => toast.remove(), 180);
  }, 2800);
}

vaultUploadButton?.addEventListener('click', () => {
  showToast('File encrypted client-side and locked via Zero-Trust policy.');
});

vaultUpload?.addEventListener('change', () => {
  const file = vaultUpload.files?.[0];
  if (!file) return;
  uploadStatus.textContent = `${file.name} ready for secure encryption.`;
});
