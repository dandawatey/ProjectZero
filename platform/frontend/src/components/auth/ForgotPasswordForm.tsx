import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { forgotPasswordSchema, type ForgotPasswordFormData } from '@/services/validation-schemas';
import { authService } from '@/services/auth';
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';

interface ForgotPasswordFormProps {
  onSuccess?: () => void;
}

export function ForgotPasswordForm({ onSuccess }: ForgotPasswordFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.requestPasswordReset(data);

      if (response.success) {
        setSubmitted(true);
        onSuccess?.();
      } else {
        setError(response.message || 'Failed to send reset link');
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Network error. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="space-y-4 text-center">
        <CheckCircle size={48} className="text-green-600 mx-auto" />
        <h3 className="text-lg font-semibold text-gray-900">Check your email</h3>
        <p className="text-gray-600 text-sm">
          We've sent password reset instructions to your email address. Check your inbox and follow
          the link to reset your password.
        </p>
        <a href="/login" className="inline-block text-blue-600 hover:text-blue-700 font-medium">
          Back to login
        </a>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <input
          {...register('email')}
          id="email"
          type="email"
          placeholder="you@example.com"
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.email ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
          }`}
          disabled={isLoading}
          aria-label="Email address"
        />
        {errors.email && <p className="text-red-600 text-sm mt-1">{errors.email.message}</p>}
      </div>

      <p className="text-sm text-gray-600">
        Enter the email address associated with your account and we'll send you a link to reset your
        password.
      </p>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        aria-busy={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Sending...
          </>
        ) : (
          'Send Reset Link'
        )}
      </button>

      <div className="text-center text-sm">
        <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">
          Back to login
        </a>
      </div>
    </form>
  );
}
