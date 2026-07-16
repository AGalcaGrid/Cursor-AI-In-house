import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PostCard } from '../PostCard';
import type { Post } from '../types';

const mockCurrentUser = {
  id: 'current',
  name: 'Test User',
  avatar: 'https://example.com/avatar.jpg',
};

const mockPost: Post = {
  id: '1',
  user: {
    id: '2',
    name: 'John Doe',
    username: 'johndoe',
    avatar: 'https://example.com/john.jpg',
    verified: true,
  },
  content: 'This is a test post content',
  images: ['https://example.com/image1.jpg'],
  timestamp: new Date().toISOString(),
  likes: 42,
  comments: [
    {
      id: 'c1',
      user: {
        id: '3',
        name: 'Jane Doe',
        username: 'janedoe',
        avatar: 'https://example.com/jane.jpg',
      },
      content: 'Great post!',
      timestamp: new Date().toISOString(),
      likes: 5,
    },
  ],
  shares: 10,
  isLiked: false,
  isBookmarked: false,
};

describe('PostCard', () => {
  it('renders post content correctly', () => {
    render(
      <PostCard
        post={mockPost}
        onLike={vi.fn()}
        onComment={vi.fn()}
        onShare={vi.fn()}
        onBookmark={vi.fn()}
        currentUser={mockCurrentUser}
      />
    );

    expect(screen.getByText('This is a test post content')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('@johndoe')).toBeInTheDocument();
  });

  it('displays verified badge for verified users', () => {
    render(
      <PostCard
        post={mockPost}
        onLike={vi.fn()}
        onComment={vi.fn()}
        onShare={vi.fn()}
        onBookmark={vi.fn()}
        currentUser={mockCurrentUser}
      />
    );

    // Verified badge is an SVG, check for the path element
    const verifiedBadge = document.querySelector('svg.text-blue-500');
    expect(verifiedBadge).toBeInTheDocument();
  });

  it('calls onLike when like button is clicked', () => {
    const onLike = vi.fn();
    render(
      <PostCard
        post={mockPost}
        onLike={onLike}
        onComment={vi.fn()}
        onShare={vi.fn()}
        onBookmark={vi.fn()}
        currentUser={mockCurrentUser}
      />
    );

    const likeButton = screen.getByRole('button', { name: /like post/i });
    fireEvent.click(likeButton);

    expect(onLike).toHaveBeenCalledWith('1');
  });

  it('calls onShare when share button is clicked', () => {
    const onShare = vi.fn();
    render(
      <PostCard
        post={mockPost}
        onLike={vi.fn()}
        onComment={vi.fn()}
        onShare={onShare}
        onBookmark={vi.fn()}
        currentUser={mockCurrentUser}
      />
    );

    const shareButton = screen.getByRole('button', { name: /share post/i });
    fireEvent.click(shareButton);

    expect(onShare).toHaveBeenCalledWith('1');
  });

  it('calls onBookmark when bookmark button is clicked', () => {
    const onBookmark = vi.fn();
    render(
      <PostCard
        post={mockPost}
        onLike={vi.fn()}
        onComment={vi.fn()}
        onShare={vi.fn()}
        onBookmark={onBookmark}
        currentUser={mockCurrentUser}
      />
    );

    const bookmarkButton = screen.getByRole('button', { name: /bookmark post/i });
    fireEvent.click(bookmarkButton);

    expect(onBookmark).toHaveBeenCalledWith('1');
  });

  it('toggles comments section when comment button is clicked', () => {
    render(
      <PostCard
        post={mockPost}
        onLike={vi.fn()}
        onComment={vi.fn()}
        onShare={vi.fn()}
        onBookmark={vi.fn()}
        currentUser={mockCurrentUser}
      />
    );

    // Comments should not be visible initially
    expect(screen.queryByPlaceholderText('Write a comment...')).not.toBeInTheDocument();

    // Click comment button
    const commentButton = screen.getByRole('button', { name: /show comments/i });
    fireEvent.click(commentButton);

    // Comments should now be visible
    expect(screen.getByPlaceholderText('Write a comment...')).toBeInTheDocument();
  });

  it('displays correct like count', () => {
    render(
      <PostCard
        post={mockPost}
        onLike={vi.fn()}
        onComment={vi.fn()}
        onShare={vi.fn()}
        onBookmark={vi.fn()}
        currentUser={mockCurrentUser}
      />
    );

    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('displays liked state correctly', () => {
    const likedPost = { ...mockPost, isLiked: true };
    render(
      <PostCard
        post={likedPost}
        onLike={vi.fn()}
        onComment={vi.fn()}
        onShare={vi.fn()}
        onBookmark={vi.fn()}
        currentUser={mockCurrentUser}
      />
    );

    const unlikeButton = screen.getByRole('button', { name: /unlike post/i });
    expect(unlikeButton).toBeInTheDocument();
  });

  it('renders images when provided', () => {
    render(
      <PostCard
        post={mockPost}
        onLike={vi.fn()}
        onComment={vi.fn()}
        onShare={vi.fn()}
        onBookmark={vi.fn()}
        currentUser={mockCurrentUser}
      />
    );

    const image = screen.getByAltText('Post image 1');
    expect(image).toBeInTheDocument();
  });
});
