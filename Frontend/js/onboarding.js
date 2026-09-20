const verifyButton = document.getElementById('verifyBtn');
const idNumber = document.getElementById('idNumber');
const ficaStep = document.getElementById('step1Container');
const dhaLoading = document.getElementById('dhaLoading');
const faisStep = document.getElementById('step2Container');
const consentButton = document.getElementById('consentBtn');
const saveProfileButton = document.getElementById('saveProfileBtn');
const legalStep = document.getElementById('step3Container');
const progressSteps = [document.getElementById('progressStep1'), document.getElementById('progressStep2'), document.getElementById('progressStep3')];
const legalConsent = document.getElementById('legalConsent');
const digitalSignature = document.getElementById('digitalSignature');
const finalizeButton = document.getElementById('finalizeBtn');
const transitionDelay = 1500;

const showStep = (stepNumber) => {
  [ficaStep, faisStep, legalStep].forEach((step, index) => {
    step.style.display = index + 1 === stepNumber ? 'block' : 'none';
  });
  progressSteps.forEach((step, index) => step.classList.toggle('active', index + 1 === stepNumber));
};

const showToast = (message) => {
  const toast = document.createElement('div');
  toast.className = 'dashboard-toast show';
  toast.setAttribute('role', 'status');
  toast.textContent = message;
  document.body.append(toast);
  window.setTimeout(() => toast.remove(), 2200);
};

const setButtonLoading = (button, message) => {
  button.disabled = true;
  button.innerHTML = '<span class="spinner" aria-hidden="true"></span> ' + message;
};

verifyButton?.addEventListener('click', () => {
  verifyButton.style.display = 'none';
  idNumber.style.display = 'none';
  dhaLoading.style.display = 'flex';
  window.setTimeout(() => {
    dhaLoading.style.display = 'none';
    showStep(2);
  }, transitionDelay);
});

consentButton?.addEventListener('click', () => {
  setButtonLoading(consentButton, 'Fetching assets & liabilities...');
  window.setTimeout(() => {
    consentButton.innerText = 'Banking details and financial situation connected';
    consentButton.disabled = false;
    showToast('Banking details and financial situation connected successfully.');
  }, transitionDelay);
});

saveProfileButton?.addEventListener('click', () => showStep(3));

const updateFinalizeState = () => {
  const isValid = legalConsent.checked && digitalSignature.value.length > 2;
  finalizeButton.disabled = !isValid;
  finalizeButton.classList.toggle('active', isValid);
};

legalConsent?.addEventListener('change', updateFinalizeState);
digitalSignature?.addEventListener('input', updateFinalizeState);

const updateSupabaseOnboardingStatus = async () => {
  const client = window.supabaseClient;
  if (!client?.from || !client.auth?.getUser) return;

  const { data: { user } = {} } = await client.auth.getUser();
  if (user) {
    await client.from('profiles').update({ onboarding_status: 'complete' }).eq('id', user.id);
  }
};

finalizeButton?.addEventListener('click', async () => {
  if (finalizeButton.disabled) return;
  setButtonLoading(finalizeButton, 'Generating FAIS Recommendation Record...');
  await new Promise((resolve) => window.setTimeout(resolve, transitionDelay));
  try {
    await updateSupabaseOnboardingStatus();
  } catch (error) {
    console.error('Unable to update Supabase onboarding status:', error);
  }
  localStorage.setItem('demo_onboarding_complete', 'true');
  window.location.href = 'dashboard.html';
});
