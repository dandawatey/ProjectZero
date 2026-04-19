import React, { useRef, useState } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';

interface MFAInputProps {
  onSubmit: (code: string) => Promise<void>;
  onResend?: () => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

export function MFAInput({ onSubmit, onResend, isLoading = false, error = null }: MFAInputProps) {
  const inputRefs = useRef<(HTMLInputElement | null)[]>(Array(6).fill(null));
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [isResending, setIsResending] = useState(false);

  const handleChange = (value: string, index: number) => {
    if (!/^\d?$/.test(value)) return;

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);

    // Move to next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === 'Backspace') {
      if (!code[index] && index > 0) {
        inputRefs.current[index - 1]?.focus();
      }
      const newCode = [...code];
      newCode[index] = '';
      setCode(newCode);
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const fullCode = code.join('');
    if (fullCode.length === 6) {
      await onSubmit(fullCode);
    }
  };

  const handleResend = async () => {
    if (!onResend) return;
    setIsResending(true);
    try {
      await onResend();
      setCode(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setIsResending(false);
    }
  };

  const isFilled = code.every(digit => digit !== '');

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Enter 6-digit code
        </label>

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm mb-3">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <div className="flex gap-2 justify-center">
          {code.map((digit, index) => (
            <input
              key={index}
              ref={el => (inputRefs.current[index] = el)}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={e => handleChange(e.target.value, index)}
              onKeyDown={e => handleKeyDown(e, index)}
              disabled={isLoading}
              className={`w-12 h-12 text-center text-2xl font-bold border-2 rounded-lg focus:outline-none focus:ring-2 ${
                error ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-blue-500'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              aria-label={`Digit ${index + 1}`}
            />
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={!isFilled || isLoading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        aria-busy={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Verifying...
          </>
        ) : (
          'Verify Code'
        )}
      </button>

      {onResend && (
        <div className="text-center">
          <button
            type="button"
            onClick={handleResend}
            disabled={isResending || isLoading}
            className="text-blue-600 hover:text-blue-700 font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isResending ? 'Resending...' : 'Resend code'}
          </button>
        </div>
      )}
    </form>
  );
}
