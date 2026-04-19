export interface PasswordStrengthResult {
  score: number; // 0-4
  label: 'Weak' | 'Fair' | 'Good' | 'Strong' | 'Very Strong';
  passed: {
    minLength: boolean;
    hasUppercase: boolean;
    hasNumber: boolean;
    hasSymbol: boolean;
  };
}

const MIN_LENGTH = 12;
const UPPERCASE_REGEX = /[A-Z]/;
const NUMBER_REGEX = /[0-9]/;
const SYMBOL_REGEX = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/;

export function validatePasswordStrength(password: string): PasswordStrengthResult {
  const passed = {
    minLength: password.length >= MIN_LENGTH,
    hasUppercase: UPPERCASE_REGEX.test(password),
    hasNumber: NUMBER_REGEX.test(password),
    hasSymbol: SYMBOL_REGEX.test(password),
  };

  const score = Object.values(passed).filter(Boolean).length;

  const labelMap = {
    0: 'Weak' as const,
    1: 'Fair' as const,
    2: 'Good' as const,
    3: 'Strong' as const,
    4: 'Very Strong' as const,
  };

  return {
    score,
    label: labelMap[score as keyof typeof labelMap],
    passed,
  };
}

export function isStrongPassword(password: string): boolean {
  const result = validatePasswordStrength(password);
  return result.score === 4;
}
