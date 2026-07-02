const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error ?? 'The backend request failed.');
  }
  return data;
}

export function sendNotification(payload) {
  return request('/send/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getLogs() {
  const data = await request('/logs/');
  return data.logs;
}
