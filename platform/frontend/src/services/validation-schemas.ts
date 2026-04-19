import { z } from 'zod';
import { isStrongPassword } from './password-strength';

const email = z.string().email('Invalid email address');

const strongPassword = z
  .string()
  .min(12, 'Password must be at least 12 characters')
  .refine(pwd => /[A-Z]/.test(pwd), 'Password must contain uppercase letter')
  .refine(pwd => /[0-9]/.test(pwd), 'Password must contain number')
  .refine(pwd => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd), 'Password must contain symbol')
  .refine(pwd => isStrongPassword(pwd), 'Password does not meet strength requirements');

export const loginSchema = z.object({
  email,
  password: z.string().min(1, 'Password is required'),
});

export const signupSchema = z
  .object({
    email,
    password: strongPassword,
    confirmPassword: z.string(),
    organizationName: z.string().min(1, 'Organization name is required'),
    inviteCode: z.string().optional(),
  })
  .refine(data => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export const mfaSchema = z.object({
  code: z
    .string()
    .min(6, 'OTP must be 6 digits')
    .max(6, 'OTP must be 6 digits')
    .regex(/^\d+$/, 'OTP must contain only digits'),
});

export const forgotPasswordSchema = z.object({
  email,
});

export const resetPasswordSchema = z
  .object({
    password: strongPassword,
    confirmPassword: z.string(),
  })
  .refine(data => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export type LoginFormData = z.infer<typeof loginSchema>;
export type SignupFormData = z.infer<typeof signupSchema>;
export type MFAFormData = z.infer<typeof mfaSchema>;
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
