import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LoginForm } from '@/components/auth/LoginForm';
import { Layers } from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/app';

  const handleSuccess = async (sessionId: string) => {
    // Session established via API, proceed to navigation
    navigate(from, { replace: true });
  };

  const handleMFARequired = (sessionId: string) => {
    navigate('/mfa', { state: { sessionId } });
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-950">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[300px] bg-blue-600/8 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 mb-4 shadow-lg shadow-blue-500/20">
            <Layers size={22} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">ProjectZero</h1>
          <p className="text-sm text-gray-500 mt-1">Control Tower — Sign in</p>
        </div>

        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8 shadow-2xl">
          <LoginForm onSuccess={handleSuccess} onMFARequired={handleMFARequired} />
        </div>
      </div>
    </div>
  );
}
