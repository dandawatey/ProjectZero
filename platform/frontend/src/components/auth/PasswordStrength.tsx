import React, { useMemo } from 'react';
import { validatePasswordStrength } from '@/services/password-strength';
import { Check, X } from 'lucide-react';

interface PasswordStrengthProps {
  password: string;
  showDetails?: boolean;
}

export function PasswordStrength({ password, showDetails = false }: PasswordStrengthProps) {
  const strength = useMemo(() => validatePasswordStrength(password), [password]);

  const scoreColors = {
    0: 'bg-red-500',
    1: 'bg-orange-500',
    2: 'bg-yellow-500',
    3: 'bg-blue-500',
    4: 'bg-green-500',
  };

  const scoreLabels = {
    0: 'Weak',
    1: 'Fair',
    2: 'Good',
    3: 'Strong',
    4: 'Very Strong',
  };

  return (
    <div className="space-y-2">
      <div className="flex gap-1">
        {[0, 1, 2, 3].map(i => (
          <div
            key={i}
            className={`flex-1 h-2 rounded ${i < strength.score ? scoreColors[strength.score as keyof typeof scoreColors] : 'bg-gray-200'}`}
          />
        ))}
      </div>

      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">
          {scoreLabels[strength.score as keyof typeof scoreLabels]}
        </span>
        <span className="text-xs text-gray-500">{strength.score}/4</span>
      </div>

      {showDetails && (
        <div className="mt-3 space-y-2 bg-gray-50 p-3 rounded text-sm">
          <div className={`flex items-center gap-2 ${strength.passed.minLength ? 'text-green-600' : 'text-gray-500'}`}>
            {strength.passed.minLength ? (
              <Check size={16} />
            ) : (
              <X size={16} />
            )}
            <span>At least 12 characters</span>
          </div>

          <div className={`flex items-center gap-2 ${strength.passed.hasUppercase ? 'text-green-600' : 'text-gray-500'}`}>
            {strength.passed.hasUppercase ? (
              <Check size={16} />
            ) : (
              <X size={16} />
            )}
            <span>Uppercase letter (A-Z)</span>
          </div>

          <div className={`flex items-center gap-2 ${strength.passed.hasNumber ? 'text-green-600' : 'text-gray-500'}`}>
            {strength.passed.hasNumber ? (
              <Check size={16} />
            ) : (
              <X size={16} />
            )}
            <span>Number (0-9)</span>
          </div>

          <div className={`flex items-center gap-2 ${strength.passed.hasSymbol ? 'text-green-600' : 'text-gray-500'}`}>
            {strength.passed.hasSymbol ? (
              <Check size={16} />
            ) : (
              <X size={16} />
            )}
            <span>Special character (!@#$%^&*)</span>
          </div>
        </div>
      )}
    </div>
  );
}
