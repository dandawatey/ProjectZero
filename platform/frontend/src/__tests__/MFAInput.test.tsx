import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MFAInput } from '@/components/auth/MFAInput';

describe('MFAInput Component', () => {
  it('should render 6 input fields', () => {
    render(<MFAInput onSubmit={vi.fn()} />);
    const inputs = screen.getAllByRole('textbox');
    expect(inputs).toHaveLength(6);
  });

  it('should only accept digits', async () => {
    const user = userEvent.setup();
    render(<MFAInput onSubmit={vi.fn()} />);

    const inputs = screen.getAllByRole('textbox');
    await user.type(inputs[0], 'a');

    expect((inputs[0] as HTMLInputElement).value).toBe('');
  });

  it('should accept digits', async () => {
    const user = userEvent.setup();
    render(<MFAInput onSubmit={vi.fn()} />);

    const inputs = screen.getAllByRole('textbox');
    await user.type(inputs[0], '5');

    expect((inputs[0] as HTMLInputElement).value).toBe('5');
  });

  it('should move to next field when digit entered', async () => {
    const user = userEvent.setup();
    render(<MFAInput onSubmit={vi.fn()} />);

    const inputs = screen.getAllByRole('textbox');
    await user.type(inputs[0], '1');

    expect(document.activeElement).toBe(inputs[1]);
  });

  it('should move back on backspace', async () => {
    const user = userEvent.setup();
    render(<MFAInput onSubmit={vi.fn()} />);

    const inputs = screen.getAllByRole('textbox');
    inputs[1].focus();

    await user.keyboard('{Backspace}');

    expect(document.activeElement).toBe(inputs[0]);
  });

  it('should not submit if not all digits filled', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<MFAInput onSubmit={onSubmit} />);

    const submitButton = screen.getByRole('button', { name: /Verify Code/i });
    expect(submitButton).toBeDisabled();
  });

  it('should submit when all 6 digits filled', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);

    render(<MFAInput onSubmit={onSubmit} />);

    const inputs = screen.getAllByRole('textbox');
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], String(i + 1));
    }

    const submitButton = screen.getByRole('button', { name: /Verify Code/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith('123456');
    });
  });

  it('should show loading state while submitting', async () => {
    const user = userEvent.setup();
    let resolveSubmit: () => void;
    const submitPromise = new Promise<void>(resolve => {
      resolveSubmit = resolve;
    });
    const onSubmit = vi.fn(() => submitPromise);

    render(<MFAInput onSubmit={onSubmit} isLoading={true} />);

    const inputs = screen.getAllByRole('textbox');
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], String(i + 1));
    }

    // With isLoading={true} prop, should show loading state
    expect(screen.getByText(/Verifying/i)).toBeInTheDocument();
  });

  it('should display error message', () => {
    render(<MFAInput onSubmit={vi.fn()} error="Invalid code" />);
    expect(screen.getByText('Invalid code')).toBeInTheDocument();
  });

  it('should show resend button when onResend provided', () => {
    render(<MFAInput onSubmit={vi.fn()} onResend={vi.fn()} />);
    expect(screen.getByRole('button', { name: /Resend code/i })).toBeInTheDocument();
  });

  it('should call onResend when clicked', async () => {
    const user = userEvent.setup();
    const onResend = vi.fn().mockResolvedValue(undefined);

    render(<MFAInput onSubmit={vi.fn()} onResend={onResend} />);

    const resendButton = screen.getByRole('button', { name: /Resend code/i });
    await user.click(resendButton);

    await waitFor(() => {
      expect(onResend).toHaveBeenCalled();
    });
  });

  it('should clear fields after resend', async () => {
    const user = userEvent.setup();
    const onResend = vi.fn().mockResolvedValue(undefined);

    render(<MFAInput onSubmit={vi.fn()} onResend={onResend} />);

    const inputs = screen.getAllByRole('textbox');
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], String(i + 1));
    }

    const resendButton = screen.getByRole('button', { name: /Resend code/i });
    await user.click(resendButton);

    await waitFor(() => {
      inputs.forEach(input => {
        expect((input as HTMLInputElement).value).toBe('');
      });
    });
  });

  it('should navigate with arrow keys', async () => {
    const user = userEvent.setup();
    render(<MFAInput onSubmit={vi.fn()} />);

    const inputs = screen.getAllByRole('textbox');
    inputs[2].focus();

    await user.keyboard('{ArrowLeft}');
    expect(document.activeElement).toBe(inputs[1]);

    await user.keyboard('{ArrowRight}');
    expect(document.activeElement).toBe(inputs[2]);
  });
});
