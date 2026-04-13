export type UserRole = 'admin' | 'developer' | 'viewer';

export interface UserProfile {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}
