import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '@/components/auth/LoginForm';
import * as authModule from '@/services/auth';

vi.mock('@/services/auth');

describe('LoginForm Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render email and password fields', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  });

  it('should render sign in button', () => {
    render(<LoginForm />);
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
  });

  it('should validate email format', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const submitButton = screen.getByRole('button', { name: /Sign In/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid email/i)).toBeInTheDocument();
    });
  });

  it('should require password', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/Email/i) as HTMLInputElement;
    await user.type(emailInput, 'test@example.com');

    const submitButton = screen.getByRole('button', { name: /Sign In/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Password is required/i)).toBeInTheDocument();
    });
  });

  it('should submit valid form data', async () => {
    const user = userEvent.setup();
    const mockLogin = vi.fn().mockResolvedValue({ success: true, sessionId: 'test-id' });
    vi.mocked(authModule.authService.login).mockImplementation(mockLogin);

    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/Email/i);
    const passwordInput = screen.getByLabelText(/Password/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password');

    const submitButton = screen.getByRole('button', { name: /Sign In/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
      });
    });
  });

  it('should show loading state while submitting', async () => {
    const user = userEvent.setup();
    let resolveLogin: () => void;
    const loginPromise = new Promise<{ success: boolean; sessionId: string }>(resolve => {
      resolveLogin = resolve;
    });
    vi.mocked(authModule.authService.login).mockReturnValue(loginPromise);

    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/Email/i);
    const passwordInput = screen.getByLabelText(/Password/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password');

    const submitButton = screen.getByRole('button', { name: /Sign In/i });
    await user.click(submitButton);

    expect(screen.getByText(/Signing in/i)).toBeInTheDocument();
    resolveLogin!({ success: true, sessionId: 'test-id' });
  });

  it('should display forgot password link', () => {
    render(<LoginForm />);
    const forgotLink = screen.getByRole('link', { name: /Forgot password/i });
    expect(forgotLink).toHaveAttribute('href', '/forgot-password');
  });

  it('should call onSuccess callback on successful login', async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    vi.mocked(authModule.authService.login).mockResolvedValue({ success: true, sessionId: 'test-id' });

    render(<LoginForm onSuccess={onSuccess} />);

    const emailInput = screen.getByLabelText(/Email/i);
    const passwordInput = screen.getByLabelText(/Password/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password');

    const submitButton = screen.getByRole('button', { name: /Sign In/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith('test-id');
    });
  });

  it('should handle network errors', async () => {
    const user = userEvent.setup();
    vi.mocked(authModule.authService.login).mockRejectedValue(new Error('Network error'));

    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/Email/i);
    const passwordInput = screen.getByLabelText(/Password/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password');

    const submitButton = screen.getByRole('button', { name: /Sign In/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Network error/i)).toBeInTheDocument();
    });
  });

  it('should have accessible form elements', () => {
    render(<LoginForm />);

    const emailLabel = screen.getByText(/Email/);
    const passwordLabel = screen.getByText(/Password/);

    expect(emailLabel).toBeInTheDocument();
    expect(passwordLabel).toBeInTheDocument();
  });

  it('should disable form during submission', async () => {
    const user = userEvent.setup();
    let resolveLogin: () => void;
    const loginPromise = new Promise<{ success: boolean; sessionId: string }>(resolve => {
      resolveLogin = resolve;
    });
    vi.mocked(authModule.authService.login).mockReturnValue(loginPromise);

    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/Email/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/Password/i) as HTMLInputElement;

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password');

    const submitButton = screen.getByRole('button', { name: /Sign In/i }) as HTMLButtonElement;
    await user.click(submitButton);

    expect(submitButton.disabled).toBe(true);
    expect(emailInput.disabled).toBe(true);
    expect(passwordInput.disabled).toBe(true);
    resolveLogin!({ success: true, sessionId: 'test-id' });
  });
});
