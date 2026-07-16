import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { UserAvatar } from '../UserAvatar';

describe('UserAvatar', () => {
  it('renders avatar image with correct src and alt', () => {
    render(
      <UserAvatar
        src="https://example.com/avatar.jpg"
        alt="Test User"
      />
    );

    const avatar = screen.getByAltText('Test User');
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute('src', 'https://example.com/avatar.jpg');
  });

  it('applies correct size class for xs', () => {
    render(
      <UserAvatar
        src="https://example.com/avatar.jpg"
        alt="Test User"
        size="xs"
      />
    );

    const avatar = screen.getByAltText('Test User');
    expect(avatar).toHaveClass('w-6', 'h-6');
  });

  it('applies correct size class for lg', () => {
    render(
      <UserAvatar
        src="https://example.com/avatar.jpg"
        alt="Test User"
        size="lg"
      />
    );

    const avatar = screen.getByAltText('Test User');
    expect(avatar).toHaveClass('w-12', 'h-12');
  });

  it('applies ring when showRing is true', () => {
    render(
      <UserAvatar
        src="https://example.com/avatar.jpg"
        alt="Test User"
        showRing={true}
      />
    );

    const avatar = screen.getByAltText('Test User');
    expect(avatar).toHaveClass('ring-2');
  });

  it('does not apply ring when showRing is false', () => {
    render(
      <UserAvatar
        src="https://example.com/avatar.jpg"
        alt="Test User"
        showRing={false}
      />
    );

    const avatar = screen.getByAltText('Test User');
    expect(avatar).not.toHaveClass('ring-2');
  });

  it('shows online indicator when isOnline is true', () => {
    const { container } = render(
      <UserAvatar
        src="https://example.com/avatar.jpg"
        alt="Test User"
        isOnline={true}
      />
    );

    const indicator = container.querySelector('.bg-green-500');
    expect(indicator).toBeInTheDocument();
  });

  it('shows offline indicator when isOnline is false', () => {
    const { container } = render(
      <UserAvatar
        src="https://example.com/avatar.jpg"
        alt="Test User"
        isOnline={false}
      />
    );

    const indicator = container.querySelector('.bg-gray-400');
    expect(indicator).toBeInTheDocument();
  });

  it('does not show indicator when isOnline is undefined', () => {
    const { container } = render(
      <UserAvatar
        src="https://example.com/avatar.jpg"
        alt="Test User"
      />
    );

    const greenIndicator = container.querySelector('.bg-green-500');
    const grayIndicator = container.querySelector('.bg-gray-400');
    expect(greenIndicator).not.toBeInTheDocument();
    expect(grayIndicator).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <UserAvatar
        src="https://example.com/avatar.jpg"
        alt="Test User"
        className="custom-class"
      />
    );

    const wrapper = container.firstChild;
    expect(wrapper).toHaveClass('custom-class');
  });
});
