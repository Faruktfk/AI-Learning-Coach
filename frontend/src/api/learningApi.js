const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `API request failed with status ${response.status}`);
  }

  return response.json();
}

export async function createLearningSession() {
  return request('/sessions', {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export async function stepLearningSession(sessionId, payload = {}) {
  return request(`/sessions/${sessionId}/step`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function buildDownloadUrl(downloadUrl) {
  if (!downloadUrl) return null;

  if (
    downloadUrl.startsWith('http://') ||
    downloadUrl.startsWith('https://')
  ) {
    return downloadUrl;
  }

  const normalizedBaseUrl = API_BASE_URL.replace(/\/+$/, '');
  const normalizedPath = downloadUrl.startsWith('/')
    ? downloadUrl
    : `/${downloadUrl}`;

  return `${normalizedBaseUrl}${normalizedPath}`;
}

export async function generateLearningHandout(sessionId) {
  const normalizedBaseUrl = API_BASE_URL.replace(/\/+$/, '');

  const response = await fetch(`${normalizedBaseUrl}/sessions/${sessionId}/handout`, {
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || 'Handout konnte nicht generiert werden.');
  }

  return response.json();
}