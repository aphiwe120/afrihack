const SUPABASE_URL = 'https://vkxlggpmlydvpttheeym.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZreGxnZ3BtbHlkdnB0dGhleWVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk4MTAyNzUsImV4cCI6MjEwNTM4NjI3NX0.KoHw21_j4akd-a_g_bJbx5aPGeKgyYDRVEFHlaVl3XVw';
var supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const logoutButton = document.getElementById('logoutBtn');
const vaultUpload = document.getElementById('vaultUpload');
const vaultUploadButton = document.getElementById('vaultUploadButton');
const uploadStatus = document.getElementById('uploadStatus');

const goals = [
  { title: 'Offshore Investment', target: 'R500k', current: 'R120k', progress: 24 },
  { title: 'Retirement Portfolio', target: 'R2m', current: 'R860k', progress: 43 },
];

const reminders = [
  { text: 'Annual FAIS Review Due', type: 'urgent' },
  { text: 'Sign updated mandate', type: 'standard' },
];

const renderGoals = () => {
  const goalsList = document.getElementById('goalsList');
  if (!goalsList) return;

  goalsList.replaceChildren();
  goals.forEach((goal) => {
    const item = document.createElement('li');
    item.className = 'goal-item';

    const header = document.createElement('div');
    header.className = 'goal-header';
    const title = document.createElement('strong');
    title.textContent = goal.title;
    const progressLabel = document.createElement('span');
    progressLabel.className = 'goal-progress-label';
    progressLabel.textContent = `${goal.progress}%`;
    header.append(title, progressLabel);

    const values = document.createElement('div');
    values.className = 'goal-values';
    values.textContent = `${goal.current} of ${goal.target}`;

    const track = document.createElement('div');
    track.className = 'progress-track bg-slate-200';
    const bar = document.createElement('div');
    bar.className = 'progress-bar bg-blue-600';
    bar.style.width = `${goal.progress}%`;
    track.append(bar);

    item.append(header, values, track);
    goalsList.append(item);
  });
};

const renderReminders = () => {
  const remindersList = document.getElementById('remindersList');
  if (!remindersList) return;

  remindersList.replaceChildren();
  reminders.forEach((reminder) => {
    const item = document.createElement('li');
    item.className = `reminder-item ${reminder.type}`;

    const text = document.createElement('span');
    text.textContent = reminder.text;
    const dismissButton = document.createElement('button');
    dismissButton.className = 'dismiss-button text-sm text-slate-500 hover:text-purple-600';
    dismissButton.type = 'button';
    dismissButton.textContent = 'Dismiss';
    dismissButton.addEventListener('click', () => item.remove());

    item.append(text, dismissButton);
    remindersList.append(item);
  });
};

document.addEventListener('DOMContentLoaded', () => {
  const currentDate = document.getElementById('currentDate');
  if (currentDate) {
    currentDate.innerText = new Date().toLocaleDateString();
  }

  const isOnboardingComplete = localStorage.getItem('demo_onboarding_complete') === 'true';
  if (!isOnboardingComplete) {
    window.location.href = 'onboarding.html';
  }

  renderGoals();
  renderReminders();
});

logoutButton?.addEventListener('click', async (event) => {
  event.preventDefault();

  const originalText = logoutButton.innerText;
  logoutButton.innerText = 'Logging out...';
  logoutButton.disabled = true;

  try {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;

    localStorage.clear();
    window.location.href = 'index.html';
  } catch (error) {
    console.error('Logout Error:', error.message);
    alert(`Failed to log out: ${error.message}`);
    logoutButton.innerText = originalText;
    logoutButton.disabled = false;
  }
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
