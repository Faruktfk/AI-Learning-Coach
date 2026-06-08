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
    let detail = `HTTP ${response.status}`;
    try {
      const errorBody = await response.json();
      detail = errorBody.detail || detail;
    } catch {
      // Keep generic HTTP error.
    }
    throw new Error(detail);
  }

  return response.json();
}

export async function createSession() {
  return request('/sessions', {
    method: 'POST',
  });
}

export async function listSessions() {
  return request('/sessions');
}

export async function getSession(sessionId) {
  return request(`/sessions/${sessionId}`);
}

export async function deleteSession(sessionId) {
  return request(`/sessions/${sessionId}`, {
    method: 'DELETE',
  });
}

export async function stepSession(sessionId, payload = {}) {
  return request(`/sessions/${sessionId}/step`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
