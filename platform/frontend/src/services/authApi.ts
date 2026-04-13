/**
 * Raw auth API calls — PRJ0-29.
 * No token injection here — these are public/cookie-based calls.
 */

import type { TokenResponse, UserProfile } from '../types/auth';

const BASE = '/api/v1/auth';

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const r = await fetch(BASE + path, {
    credentials: 'include', // send httpOnly refresh cookie
    headers: { 'Content-Type': 'application/json', ...init.headers },
    ...init,
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(err.detail ?? r.statusText);
  }
  if (r.status === 204) return undefined as T;
  return r.json();
}

export const authApi = {
  register: (email: string, password: string, role = 'developer') =>
    request<UserProfile>('/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, role }),
    }),

  login: (email: string, password: string) =>
    request<TokenResponse>('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  logout: (token: string) =>
    request<void>('/logout', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    }),

  refresh: () => request<TokenResponse>('/refresh', { method: 'POST' }),

  me: (token: string) =>
    request<UserProfile>('/me', {
      headers: { Authorization: `Bearer ${token}` },
    }),
};
