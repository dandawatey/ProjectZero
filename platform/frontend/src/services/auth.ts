export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  organizationName: string;
  inviteCode?: string;
}

export interface MFAVerifyRequest {
  code: string;
  sessionId: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  newPassword: string;
}

export interface AuthResponse {
  success: boolean;
  message?: string;
  sessionId?: string;
  requiresMFA?: boolean;
}

export interface ResetLinkResponse {
  success: boolean;
  message: string;
}

const API_BASE = '/api/v1/auth';

async function handleResponse(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: `HTTP ${response.status}`,
    }));
    throw new Error(error.message || 'Request failed');
  }
  return response.json();
}

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    return handleResponse(response);
  },

  async signup(data: SignupRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async verifyMFA(data: MFAVerifyRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/mfa/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async requestPasswordReset(data: PasswordResetRequest): Promise<ResetLinkResponse> {
    const response = await fetch(`${API_BASE}/password/request-reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async confirmPasswordReset(data: PasswordResetConfirmRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/password/confirm-reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async logout(): Promise<void> {
    await fetch(`${API_BASE}/logout`, {
      method: 'POST',
    });
  },
};
