import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SignupForm } from '@/components/auth/SignupForm';
import { Layers } from 'lucide-react';

export default function SignupPage() {
  const navigate = useNavigate();

  const handleSuccess = () => {
    navigate('/login', { state: { message: 'Account created. Please sign in.' } });
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-950">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[300px] bg-purple-600/8 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-600 mb-4 shadow-lg shadow-purple-500/20">
            <Layers size={22} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">ProjectZero</h1>
          <p className="text-sm text-gray-500 mt-1">Control Tower — Create account</p>
        </div>

        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8 shadow-2xl">
          <SignupForm onSuccess={handleSuccess} />
          <div className="text-center text-sm mt-6 pt-6 border-t border-gray-800">
            Already have account?{' '}
            <a href="/login" className="text-blue-500 hover:text-blue-400 font-medium">
              Sign in
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
