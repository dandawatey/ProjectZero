import { describe, it, expect } from 'vitest';
import { validatePasswordStrength, isStrongPassword } from '@/services/password-strength';

describe('Password Strength Validation', () => {
  describe('validatePasswordStrength', () => {
    it('should return weak score for empty password', () => {
      const result = validatePasswordStrength('');
      expect(result.score).toBe(0);
      expect(result.label).toBe('Weak');
      expect(result.passed.minLength).toBe(false);
    });

    it('should check minimum length requirement (12 chars)', () => {
      const result11 = validatePasswordStrength('Abcdef1!@#1');
      expect(result11.passed.minLength).toBe(false);

      const result12 = validatePasswordStrength('Abcdef1!@#$2');
      expect(result12.passed.minLength).toBe(true);
    });

    it('should check uppercase requirement', () => {
      const result = validatePasswordStrength('abcdef123456');
      expect(result.passed.hasUppercase).toBe(false);

      const result2 = validatePasswordStrength('Abcdef123456');
      expect(result2.passed.hasUppercase).toBe(true);
    });

    it('should check number requirement', () => {
      const result = validatePasswordStrength('Abcdefghijkl!');
      expect(result.passed.hasNumber).toBe(false);

      const result2 = validatePasswordStrength('Abcdefghijkl1!');
      expect(result2.passed.hasNumber).toBe(true);
    });

    it('should check symbol requirement', () => {
      const result = validatePasswordStrength('Abcdef123456');
      expect(result.passed.hasSymbol).toBe(false);

      const result2 = validatePasswordStrength('Abcdef123456!');
      expect(result2.passed.hasSymbol).toBe(true);
    });

    it('should return score based on requirements met', () => {
      const weak = validatePasswordStrength('abc');
      expect(weak.score).toBe(0); // fails all requirements

      const fair = validatePasswordStrength('Abcdef1!');
      expect(fair.score).toBe(3); // minLength fails, but has uppercase + number + symbol

      const good = validatePasswordStrength('Abcdef123456');
      expect(good.score).toBe(3); // minLength + uppercase + number (no symbol)

      const veryStrong = validatePasswordStrength('Abcdef123456!');
      expect(veryStrong.score).toBe(4); // all requirements
    });

    it('should assign correct labels for each score', () => {
      const passwords = [
        { pwd: '', expectedLabel: 'Weak' },
        { pwd: 'a', expectedLabel: 'Weak' },
        { pwd: 'A', expectedLabel: 'Fair' },
        { pwd: 'A1', expectedLabel: 'Good' },
        { pwd: 'A1!', expectedLabel: 'Strong' },
        { pwd: 'Abcdef123456!', expectedLabel: 'Very Strong' },
      ];

      passwords.forEach(({ pwd, expectedLabel }) => {
        const result = validatePasswordStrength(pwd);
        expect(result.label).toBe(expectedLabel);
      });
    });
  });

  describe('isStrongPassword', () => {
    it('should return true only for very strong passwords', () => {
      expect(isStrongPassword('Abcdef123456!')).toBe(true);
      expect(isStrongPassword('MyP@ssw0rd123')).toBe(true);
      expect(isStrongPassword('Test!Pass123456')).toBe(true);
    });

    it('should return false for weak/fair/good/strong passwords', () => {
      expect(isStrongPassword('')).toBe(false);
      expect(isStrongPassword('weak')).toBe(false);
      expect(isStrongPassword('Weak')).toBe(false);
      expect(isStrongPassword('Weak123')).toBe(false);
      expect(isStrongPassword('Weak123!')).toBe(false); // missing minLength
    });
  });
});
