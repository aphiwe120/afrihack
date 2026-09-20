const verifyButton = document.getElementById('verifyBtn');
const idNumber = document.getElementById('idNumber');
const ficaStep = document.getElementById('step1Container');
const dhaLoading = document.getElementById('dhaLoading');
const consentStep = document.getElementById('step2Container');
const consentButton = document.getElementById('consentBtn');

verifyButton?.addEventListener('click', () => {
  verifyButton.style.display = 'none';
  idNumber.style.display = 'none';
  dhaLoading.style.display = 'flex';
  window.setTimeout(() => {
    ficaStep.style.display = 'none';
    consentStep.style.display = 'block';
  }, 2000);
});

consentButton?.addEventListener('click', () => {
  consentButton.innerText = 'Fetching financial summary...';
  consentButton.disabled = true;
  window.setTimeout(() => {
    window.location.href = 'dashboard.html';
  }, 2000);
});
