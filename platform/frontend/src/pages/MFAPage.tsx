import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MFAInput } from '@/components/auth/MFAInput';
import { authService } from '@/services/auth';
import { Layers } from 'lucide-react';

export default function MFAPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const sessionId = (location.state as { sessionId?: string })?.sessionId;
  const [error, setError] = useState<string | null>(null);

  if (!sessionId) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-gray-950">
        <div className="text-center">
          <p className="text-red-400 mb-4">Invalid session. Please login again.</p>
          <a href="/login" className="text-blue-500 hover:text-blue-400 font-medium">
            Back to login
          </a>
        </div>
      </div>
    );
  }

  const handleSubmit = async (code: string) => {
    setError(null);
    try {
      const response = await authService.verifyMFA({
        code,
        sessionId,
      });

      if (response.success) {
        navigate('/app');
      } else {
        setError(response.message || 'Invalid code');
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Verification failed. Try again.');
      }
    }
  };

  const handleResend = async () => {
    try {
      // Call resend endpoint if available
      setError(null);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      }
    }
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-950">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[300px] bg-green-600/8 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-green-500 to-blue-600 mb-4 shadow-lg shadow-green-500/20">
            <Layers size={22} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Two-Factor Auth</h1>
          <p className="text-sm text-gray-500 mt-1">Enter code from authenticator</p>
        </div>

        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8 shadow-2xl">
          <MFAInput onSubmit={handleSubmit} onResend={handleResend} error={error} />
        </div>
      </div>
    </div>
  );
}
