import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PostCreationForm } from '../PostCreationForm';

const mockCurrentUser = {
  id: 'current',
  name: 'Test User',
  avatar: 'https://example.com/avatar.jpg',
};

describe('PostCreationForm', () => {
  it('renders the form with user avatar', () => {
    render(
      <PostCreationForm
        currentUser={mockCurrentUser}
        onSubmit={vi.fn()}
      />
    );

    const avatar = screen.getByAltText('Test User');
    expect(avatar).toBeInTheDocument();
  });

  it('renders textarea with placeholder', () => {
    render(
      <PostCreationForm
        currentUser={mockCurrentUser}
        onSubmit={vi.fn()}
      />
    );

    expect(screen.getByPlaceholderText("What's on your mind?")).toBeInTheDocument();
  });

  it('expands form when textarea is focused', async () => {
    const user = userEvent.setup();
    render(
      <PostCreationForm
        currentUser={mockCurrentUser}
        onSubmit={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText("What's on your mind?");
    await user.click(textarea);

    // Post button should appear after focus
    expect(screen.getByRole('button', { name: /post/i })).toBeInTheDocument();
  });

  it('disables post button when content is empty', async () => {
    const user = userEvent.setup();
    render(
      <PostCreationForm
        currentUser={mockCurrentUser}
        onSubmit={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText("What's on your mind?");
    await user.click(textarea);

    const postButton = screen.getByRole('button', { name: /^post$/i });
    expect(postButton).toBeDisabled();
  });

  it('enables post button when content is entered', async () => {
    const user = userEvent.setup();
    render(
      <PostCreationForm
        currentUser={mockCurrentUser}
        onSubmit={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText("What's on your mind?");
    await user.type(textarea, 'Hello world!');

    const postButton = screen.getByRole('button', { name: /^post$/i });
    expect(postButton).not.toBeDisabled();
  });

  it('calls onSubmit with content when form is submitted', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(
      <PostCreationForm
        currentUser={mockCurrentUser}
        onSubmit={onSubmit}
      />
    );

    const textarea = screen.getByPlaceholderText("What's on your mind?");
    await user.type(textarea, 'Test post content');

    const postButton = screen.getByRole('button', { name: /^post$/i });
    await user.click(postButton);

    expect(onSubmit).toHaveBeenCalledWith('Test post content', []);
  });

  it('clears form after successful submission', async () => {
    const user = userEvent.setup();
    render(
      <PostCreationForm
        currentUser={mockCurrentUser}
        onSubmit={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText("What's on your mind?") as HTMLTextAreaElement;
    await user.type(textarea, 'Test post content');
    
    const postButton = screen.getByRole('button', { name: /^post$/i });
    await user.click(postButton);

    expect(textarea.value).toBe('');
  });

  it('shows action buttons when expanded', async () => {
    const user = userEvent.setup();
    render(
      <PostCreationForm
        currentUser={mockCurrentUser}
        onSubmit={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText("What's on your mind?");
    await user.click(textarea);

    expect(screen.getByRole('button', { name: /add photo/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add gif/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add emoji/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create poll/i })).toBeInTheDocument();
  });

  it('adds demo image when demo image button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <PostCreationForm
        currentUser={mockCurrentUser}
        onSubmit={vi.fn()}
      />
    );

    const textarea = screen.getByPlaceholderText("What's on your mind?");
    await user.click(textarea);

    const addDemoButton = screen.getByRole('button', { name: /add demo image/i });
    await user.click(addDemoButton);

    // Should show an image preview
    const imagePreview = screen.getByAltText('Upload 1');
    expect(imagePreview).toBeInTheDocument();
  });
});
