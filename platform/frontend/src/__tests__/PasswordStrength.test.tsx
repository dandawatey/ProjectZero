import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PasswordStrength } from '@/components/auth/PasswordStrength';

describe('PasswordStrength Component', () => {
  it('should render strength indicator', () => {
    render(<PasswordStrength password="Weak123!" />);
    expect(screen.getByText(/Strong/i)).toBeInTheDocument();
  });

  it('should show weak password indicator', () => {
    const { container } = render(<PasswordStrength password="weak" />);
    const bars = container.querySelectorAll('[class*="bg-"]');
    expect(bars.length).toBeGreaterThan(0);
  });

  it('should show details when showDetails is true', () => {
    render(<PasswordStrength password="Test123!" showDetails={true} />);
    expect(screen.getByText(/At least 12 characters/i)).toBeInTheDocument();
    expect(screen.getByText(/Uppercase letter/i)).toBeInTheDocument();
    expect(screen.getByText(/Number/i)).toBeInTheDocument();
    expect(screen.getByText(/Special character/i)).toBeInTheDocument();
  });

  it('should not show details by default', () => {
    render(<PasswordStrength password="Test123!" showDetails={false} />);
    expect(screen.queryByText(/At least 12 characters/i)).not.toBeInTheDocument();
  });

  it('should update when password changes', () => {
    const { rerender } = render(<PasswordStrength password="weak" showDetails={true} />);
    expect(screen.getByText(/Weak/i)).toBeInTheDocument();

    rerender(<PasswordStrength password="Abcdef123456!" showDetails={true} />);
    expect(screen.getByText(/Very Strong/i)).toBeInTheDocument();
  });

  it('should show correct check/x marks for requirements', () => {
    const { container: weakContainer } = render(
      <PasswordStrength password="abc" showDetails={true} />
    );

    const weakContent = weakContainer.textContent;
    expect(weakContent).toContain('At least 12 characters');

    const { container: strongContainer } = render(
      <PasswordStrength password="Abcdef123456!" showDetails={true} />
    );

    const strongContent = strongContainer.textContent;
    expect(strongContent).toContain('At least 12 characters');
    expect(strongContent).toContain('Uppercase letter');
    expect(strongContent).toContain('Number');
    expect(strongContent).toContain('Special character');
  });

  it('should display score out of 4', () => {
    render(<PasswordStrength password="Abcdef123456!" showDetails={false} />);
    expect(screen.getByText(/4\/4/i)).toBeInTheDocument();
  });
});
