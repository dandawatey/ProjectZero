import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { signupSchema, type SignupFormData } from '@/services/validation-schemas';
import { authService } from '@/services/auth';
import { PasswordStrength } from './PasswordStrength';
import { Loader2, AlertCircle } from 'lucide-react';

interface SignupFormProps {
  onSuccess?: () => void;
}

export function SignupForm({ onSuccess }: SignupFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  });

  const password = watch('password');

  const onSubmit = async (data: SignupFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.signup({
        email: data.email,
        password: data.password,
        organizationName: data.organizationName,
        inviteCode: data.inviteCode,
      });

      if (response.success) {
        onSuccess?.();
      } else {
        setError(response.message || 'Signup failed');
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

      <div>
        <label htmlFor="organizationName" className="block text-sm font-medium text-gray-700 mb-1">
          Organization Name
        </label>
        <input
          {...register('organizationName')}
          id="organizationName"
          type="text"
          placeholder="Your company"
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.organizationName ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
          }`}
          disabled={isLoading}
          aria-label="Organization name"
        />
        {errors.organizationName && (
          <p className="text-red-600 text-sm mt-1">{errors.organizationName.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
          Password
        </label>
        <input
          {...register('password')}
          id="password"
          type="password"
          placeholder="••••••••"
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 mb-3 ${
            errors.password ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
          }`}
          disabled={isLoading}
          aria-label="Password"
        />
        {password && <PasswordStrength password={password} showDetails={true} />}
        {errors.password && <p className="text-red-600 text-sm mt-1">{errors.password.message}</p>}
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
          Confirm Password
        </label>
        <input
          {...register('confirmPassword')}
          id="confirmPassword"
          type="password"
          placeholder="••••••••"
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
            errors.confirmPassword ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
          }`}
          disabled={isLoading}
          aria-label="Confirm password"
        />
        {errors.confirmPassword && (
          <p className="text-red-600 text-sm mt-1">{errors.confirmPassword.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="inviteCode" className="block text-sm font-medium text-gray-700 mb-1">
          Invite Code (Optional)
        </label>
        <input
          {...register('inviteCode')}
          id="inviteCode"
          type="text"
          placeholder="Leave blank if not invited"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
          aria-label="Invite code"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        aria-busy={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Creating account...
          </>
        ) : (
          'Sign Up'
        )}
      </button>
    </form>
  );
}
