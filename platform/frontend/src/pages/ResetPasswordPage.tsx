import React, { useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ResetPasswordForm } from '@/components/auth/ResetPasswordForm';
import { Layers } from 'lucide-react';

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = useMemo(() => searchParams.get('token'), [searchParams]);

  if (!token) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-gray-950">
        <div className="text-center">
          <p className="text-red-400 mb-4">Invalid reset link. Please request new one.</p>
          <a href="/forgot-password" className="text-blue-500 hover:text-blue-400 font-medium">
            Request password reset
          </a>
        </div>
      </div>
    );
  }

  const handleSuccess = () => {
    navigate('/login');
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-950">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[300px] bg-teal-600/8 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-teal-500 to-blue-600 mb-4 shadow-lg shadow-teal-500/20">
            <Layers size={22} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">New Password</h1>
          <p className="text-sm text-gray-500 mt-1">Set your new password</p>
        </div>

        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8 shadow-2xl">
          <ResetPasswordForm token={token} onSuccess={handleSuccess} />
        </div>
      </div>
    </div>
  );
}
