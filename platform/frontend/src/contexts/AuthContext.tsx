/**
 * AuthContext — PRJ0-29.
 *
 * Token lives in memory (useRef) only — never localStorage — prevents XSS theft.
 * On mount: try stored token → GET /me; on 401 → POST /refresh → retry /me.
 * Exposes setTokenGetter so api.ts injects Authorization without circular imports.
 * Refresh queue: concurrent 401s trigger exactly ONE refresh call.
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import { authApi } from '../services/authApi';
import { setTokenGetter } from '../services/api';
import type { UserProfile } from '../types/auth';

interface AuthContextType {
  user: UserProfile | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

// Shared refresh promise — prevents N concurrent refresh calls
let _refreshingPromise: Promise<string | null> | null = null;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const tokenRef = useRef<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const getToken = useCallback(() => tokenRef.current, []);

  // Called by api.ts on 401 — returns new token or null
  const refreshAccessToken = useCallback(async (): Promise<string | null> => {
    if (_refreshingPromise) return _refreshingPromise;
    _refreshingPromise = authApi
      .refresh()
      .then((res) => {
        tokenRef.current = res.access_token;
        setUser(res.user);
        return res.access_token;
      })
      .catch(() => {
        tokenRef.current = null;
        setUser(null);
        return null;
      })
      .finally(() => {
        _refreshingPromise = null;
      });
    return _refreshingPromise;
  }, []);

  // Rehydrate session on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await authApi.refresh();
        tokenRef.current = res.access_token;
        setUser(res.user);
      } catch {
        tokenRef.current = null;
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  // Inject token getter + refresh fn into api.ts (no circular import)
  useEffect(() => {
    setTokenGetter(getToken, refreshAccessToken);
  }, [getToken, refreshAccessToken]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await authApi.login(email, password);
    tokenRef.current = res.access_token;
    setUser(res.user);
  }, []);

  const logout = useCallback(async () => {
    if (tokenRef.current) {
      await authApi.logout(tokenRef.current).catch(() => {});
    }
    tokenRef.current = null;
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, getToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
