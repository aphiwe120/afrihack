const clients = [
  { id: 'c1', name: 'Sipho Ndlovu', status: 'pending', risk: 'Aggressive', date: '2026-09-20' },
  { id: 'c2', name: 'Aisha Patel', status: 'review', risk: 'Moderate', date: '2026-09-19' },
  { id: 'c3', name: 'Mandla Khumalo', status: 'approved', risk: 'Conservative', date: '2026-09-18' },
];

const columns = {
  pending: document.getElementById('col-pending'),
  review: document.getElementById('col-review'),
  approved: document.getElementById('col-approved'),
};

const showStatusToast = () => {
  const toast = document.createElement('div');
  toast.className = 'dashboard-toast advisor-toast show';
  toast.setAttribute('role', 'status');
  toast.textContent = 'Status updated securely.';
  document.body.append(toast);
  window.setTimeout(() => toast.remove(), 1800);
};

const addDragHandlers = (card) => {
  card.addEventListener('dragstart', (event) => {
    event.dataTransfer?.setData('text/plain', card.id);
    card.classList.add('is-dragging');
  });

  card.addEventListener('dragend', () => card.classList.remove('is-dragging'));
};

const renderClients = () => {
  Object.values(columns).forEach((column) => {
    column?.querySelectorAll('.client-card').forEach((card) => card.remove());
  });

  clients.forEach((client) => {
    const card = document.createElement('div');
    card.id = client.id;
    card.className = 'client-card bg-white p-4 rounded-lg shadow-sm border-l-4 border-blue-600 cursor-grab mb-4';
    card.draggable = true;

    const name = document.createElement('strong');
    name.textContent = client.name;
    const risk = document.createElement('span');
    risk.className = 'risk-badge bg-purple-100 text-purple-800';
    risk.textContent = client.risk;
    const date = document.createElement('small');
    date.textContent = client.date;

    card.append(name, risk, date);
    columns[client.status]?.append(card);
    addDragHandlers(card);
  });
};

Object.values(columns).forEach((column) => {
  column?.addEventListener('dragover', (event) => event.preventDefault());
  column?.addEventListener('drop', (event) => {
    event.preventDefault();
    const cardId = event.dataTransfer?.getData('text/plain');
    const card = cardId ? document.getElementById(cardId) : null;
    if (!card || !event.currentTarget) return;
    event.currentTarget.append(card);
    showStatusToast();
  });
});

renderClients();

const logoutButton = document.getElementById('logoutBtn');

logoutButton?.addEventListener('click', () => {
  localStorage.clear();
  window.location.href = 'index.html';
});
