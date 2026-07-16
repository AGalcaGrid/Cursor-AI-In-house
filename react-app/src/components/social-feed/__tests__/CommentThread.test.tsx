import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CommentThread } from '../CommentThread';
import type { Comment } from '../types';

const mockComments: Comment[] = [
  {
    id: 'c1',
    user: {
      id: '1',
      name: 'John Doe',
      username: 'johndoe',
      avatar: 'https://example.com/john.jpg',
      verified: true,
    },
    content: 'This is a great post!',
    timestamp: new Date().toISOString(),
    likes: 5,
    isLiked: false,
    replies: [
      {
        id: 'c1r1',
        user: {
          id: '2',
          name: 'Jane Doe',
          username: 'janedoe',
          avatar: 'https://example.com/jane.jpg',
        },
        content: 'I agree!',
        timestamp: new Date().toISOString(),
        likes: 2,
      },
    ],
  },
  {
    id: 'c2',
    user: {
      id: '3',
      name: 'Bob Smith',
      username: 'bobsmith',
      avatar: 'https://example.com/bob.jpg',
    },
    content: 'Nice work!',
    timestamp: new Date().toISOString(),
    likes: 0,
  },
];

describe('CommentThread', () => {
  it('renders all comments', () => {
    render(<CommentThread comments={mockComments} />);

    expect(screen.getByText('This is a great post!')).toBeInTheDocument();
    expect(screen.getByText('Nice work!')).toBeInTheDocument();
  });

  it('displays user names correctly', () => {
    render(<CommentThread comments={mockComments} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Bob Smith')).toBeInTheDocument();
  });

  it('shows verified badge for verified users', () => {
    render(<CommentThread comments={mockComments} />);

    // John Doe is verified, should have a badge
    const verifiedBadges = document.querySelectorAll('svg.text-blue-500');
    expect(verifiedBadges.length).toBeGreaterThan(0);
  });

  it('displays like count correctly', () => {
    render(<CommentThread comments={mockComments} />);

    expect(screen.getByText('5 Likes')).toBeInTheDocument();
  });

  it('shows "Like" text when likes is 0', () => {
    render(<CommentThread comments={mockComments} />);

    expect(screen.getByText('Like')).toBeInTheDocument();
  });

  it('toggles like state when like button is clicked', () => {
    render(<CommentThread comments={mockComments} />);

    const likeButtons = screen.getAllByRole('button', { name: /like comment/i });
    fireEvent.click(likeButtons[0]);

    // After clicking, it should show "Unlike comment"
    expect(screen.getByRole('button', { name: /unlike comment/i })).toBeInTheDocument();
  });

  it('shows reply button for comments', () => {
    render(<CommentThread comments={mockComments} />);

    const replyButtons = screen.getAllByRole('button', { name: /reply to comment/i });
    expect(replyButtons.length).toBeGreaterThan(0);
  });

  it('shows reply input when reply button is clicked', () => {
    render(<CommentThread comments={mockComments} />);

    const replyButtons = screen.getAllByRole('button', { name: /reply to comment/i });
    fireEvent.click(replyButtons[0]);

    expect(screen.getByPlaceholderText(/reply to john doe/i)).toBeInTheDocument();
  });

  it('renders nested replies', () => {
    render(<CommentThread comments={mockComments} />);

    // The reply "I agree!" should be visible (depth < 2)
    expect(screen.getByText('I agree!')).toBeInTheDocument();
  });
});
