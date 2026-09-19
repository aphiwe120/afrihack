const API_BASE_URL = window.RSF_API_BASE_URL || '';

export async function apiCall(endpoint, options = {}) {
  const token = sessionStorage.getItem('rsf_jwt');
  const headers = new Headers(options.headers || {});
  headers.set('Accept', 'application/json');
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
    if (response.status === 401) {
      sessionStorage.removeItem('rsf_jwt');
      window.dispatchEvent(new CustomEvent('rsf:session-expired'));
      throw new Error('Your session has expired. Please sign in again.');
    }
    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json') ? await response.json() : await response.text();
    if (!response.ok) throw new Error(payload?.detail || payload || `Request failed (${response.status})`);
    return payload;
  } catch (error) {
    window.showToast?.(error.message || 'Request failed');
    throw error;
  }
}

export function hasSession() {
  return Boolean(sessionStorage.getItem('rsf_jwt'));
}
