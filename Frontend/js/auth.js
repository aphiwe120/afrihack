const isVerified = localStorage.getItem('demo_onboarding_complete');

if (isVerified === 'true') {
  window.location.href = 'dashboard.html';
} else {
  window.location.href = 'onboarding.html';
}

const SUPABASE_URL = 'https://vkxlggpmlydvpttheeym.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZreGxnZ3BtbHlkdnB0dGhlZXltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk4MTAyNzUsImV4cCI6MjEwNTM4NjI3NX0.KoHw21_j4akd-a_gJbx5aPGeKgyYDRVEFHlaVlV3XVw';
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

let isSignUpMode = false;

const authTitle = document.getElementById('authTitle');
const authForm = document.getElementById('authForm');
const emailInput = document.getElementById('emailInput');
const passwordInput = document.getElementById('passwordInput');
const submitBtn = document.getElementById('submitBtn');
const toggleBtn = document.getElementById('toggleBtn');
const errorMsg = document.getElementById('errorMsg');

function restoreSubmitButton() {
  submitBtn.disabled = false;
  submitBtn.innerText = isSignUpMode ? 'Sign Up' : 'Log In';
}

function showError(message) {
  errorMsg.innerText = message;
  errorMsg.style.display = 'block';
}

toggleBtn.addEventListener('click', event => {
  event.preventDefault();
  isSignUpMode = !isSignUpMode;
  authTitle.innerText = isSignUpMode ? 'Create Account' : 'Log In';
  submitBtn.innerText = isSignUpMode ? 'Sign Up' : 'Log In';
  toggleBtn.innerText = isSignUpMode
    ? 'Already have an account? Log in'
    : 'Need an account? Sign up';
  passwordInput.autocomplete = isSignUpMode ? 'new-password' : 'current-password';
  errorMsg.style.display = 'none';
});

async function routeAuthenticatedUser(user) {
  const { data: profile, error } = await supabaseClient
    .from('profiles')
    .select('onboarding_status')
    .eq('id', user.id)
    .single();

  if (error) throw error;
  window.location.href = profile?.onboarding_status === 'complete'
    ? 'dashboard.html'
    : 'onboarding.html';
}

authForm.addEventListener('submit', async event => {
  event.preventDefault();

  const email = emailInput.value.trim();
  const password = passwordInput.value;
  console.log('Submitting:', { isSignUpMode, email });

  errorMsg.style.display = 'none';
  submitBtn.disabled = true;
  submitBtn.innerText = 'Processing...';

  try {
    const authResult = isSignUpMode
      ? await supabaseClient.auth.signUp({ email, password })
      : await supabaseClient.auth.signInWithPassword({ email, password });

    if (authResult.error) throw authResult.error;

    if (isSignUpMode) {
      console.log('Signup successful');
      window.location.href = 'onboarding.html';
      return;
    }

    const { data: sessionData, error: sessionError } = await supabaseClient.auth.getSession();
    if (sessionError) throw sessionError;
    const user = sessionData.session?.user || authResult.data?.user;
    if (!user) throw new Error('Authentication succeeded but no user session was returned.');
    await routeAuthenticatedUser(user);
  } catch (error) {
    showError(error.message || 'Authentication failed. Please try again.');
    restoreSubmitButton();
  }
});
