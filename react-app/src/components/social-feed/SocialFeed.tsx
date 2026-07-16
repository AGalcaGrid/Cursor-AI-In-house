import { useState, useEffect, useRef, useCallback } from 'react';
import type { Post, Comment, User } from './types';
import { PostCardMemo } from './PostCard';
import { PostCreationForm } from './PostCreationForm';
import { FeedErrorBoundary } from '../common';

const currentUser: User = {
  id: 'current',
  name: 'You',
  username: 'currentuser',
  avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face',
};

const sampleUsers: User[] = [
  { id: '1', name: 'Sarah Chen', username: 'sarahchen', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face', verified: true },
  { id: '2', name: 'Alex Rivera', username: 'alexrivera', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face' },
  { id: '3', name: 'Jordan Kim', username: 'jordankim', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face', verified: true },
  { id: '4', name: 'Taylor Morgan', username: 'taylormorgan', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face' },
  { id: '5', name: 'Casey Johnson', username: 'caseyjohnson', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face' },
];

const generateSamplePosts = (): Post[] => [
  {
    id: '1',
    user: sampleUsers[0],
    content: "Just shipped a major feature update! 🚀 Our team has been working on this for months and I couldn't be prouder of what we've accomplished together.\n\nThe new dashboard is live and already getting amazing feedback from users. Thank you to everyone who believed in us!",
    images: [
      'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop',
    ],
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    likes: 234,
    shares: 45,
    isLiked: false,
    isBookmarked: false,
    comments: [
      {
        id: 'c1',
        user: sampleUsers[1],
        content: 'Congratulations! This looks amazing 🎉',
        timestamp: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
        likes: 12,
        replies: [
          {
            id: 'c1r1',
            user: sampleUsers[0],
            content: 'Thank you so much! Your feedback during beta was invaluable.',
            timestamp: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
            likes: 5,
          },
        ],
      },
      {
        id: 'c2',
        user: sampleUsers[2],
        content: "The new UI is so clean! Can't wait to try it out.",
        timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
        likes: 8,
      },
    ],
  },
  {
    id: '2',
    user: sampleUsers[2],
    content: "Morning coffee and code ☕️💻\n\nThere's something magical about those early morning hours when the world is quiet and you can just focus on building something beautiful.",
    images: [
      'https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=800&h=600&fit=crop',
    ],
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    likes: 567,
    shares: 23,
    isLiked: true,
    isBookmarked: true,
    comments: [
      {
        id: 'c3',
        user: sampleUsers[3],
        content: 'Same! Early mornings are the best for deep work.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
        likes: 15,
      },
    ],
  },
  {
    id: '3',
    user: sampleUsers[1],
    content: "Hot take: TypeScript has made me a better JavaScript developer. The type safety isn't just about catching bugs - it's about thinking more clearly about your data structures and APIs.\n\nWhat's your experience been?",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    likes: 892,
    shares: 156,
    isLiked: false,
    isBookmarked: false,
    comments: [
      {
        id: 'c4',
        user: sampleUsers[4],
        content: "100% agree! The autocomplete alone is worth it. Plus, refactoring becomes so much safer.",
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
        likes: 45,
        replies: [
          {
            id: 'c4r1',
            user: sampleUsers[1],
            content: "Exactly! I used to be scared of large refactors. Now I just let the compiler guide me.",
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3.5).toISOString(),
            likes: 22,
          },
          {
            id: 'c4r2',
            user: sampleUsers[0],
            content: "The IDE integration is chef's kiss 👨‍🍳",
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
            likes: 18,
          },
        ],
      },
    ],
  },
  {
    id: '4',
    user: sampleUsers[3],
    content: "Just got back from an amazing hiking trip! Nature is the best way to recharge. 🏔️\n\nSometimes you need to disconnect to reconnect with yourself.",
    images: [
      'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&h=600&fit=crop',
    ],
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    likes: 1243,
    shares: 89,
    isLiked: false,
    isBookmarked: false,
    comments: [],
  },
  {
    id: '5',
    user: sampleUsers[4],
    content: "Pro tip: Use CSS Grid for layouts and Flexbox for components. They're not competing technologies - they complement each other perfectly! 🎨",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    likes: 456,
    shares: 78,
    isLiked: true,
    isBookmarked: false,
    comments: [
      {
        id: 'c5',
        user: sampleUsers[2],
        content: "This is such good advice! I used to try to do everything with Flexbox.",
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 47).toISOString(),
        likes: 23,
      },
    ],
  },
];

function LoadingSpinner() {
  return (
    <div className="flex justify-center py-8">
      <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

function PostSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 animate-pulse">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-full" />
        <div className="flex-1">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2" />
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-24" />
        </div>
      </div>
      <div className="space-y-2 mb-4">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
      </div>
      <div className="h-48 bg-gray-200 dark:bg-gray-700 rounded-lg mb-4" />
      <div className="flex gap-6">
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16" />
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16" />
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16" />
      </div>
    </div>
  );
}

interface SocialFeedProps {
  isDarkMode?: boolean;
}

export function SocialFeed({ isDarkMode = false }: SocialFeedProps) {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // Initial load
  useEffect(() => {
    const timer = setTimeout(() => {
      setPosts(generateSamplePosts());
      setIsLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  // Infinite scroll observer
  const handleObserver = useCallback((entries: IntersectionObserverEntry[]) => {
    const [entry] = entries;
    if (entry.isIntersecting && hasMore && !isLoadingMore) {
      loadMorePosts();
    }
  }, [hasMore, isLoadingMore]);

  useEffect(() => {
    observerRef.current = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: '100px',
      threshold: 0.1,
    });

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [handleObserver]);

  const loadMorePosts = () => {
    if (page >= 3) {
      setHasMore(false);
      return;
    }

    setIsLoadingMore(true);
    setTimeout(() => {
      const morePosts = generateSamplePosts().map((post) => ({
        ...post,
        id: `${post.id}-page${page + 1}`,
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * page * 2).toISOString(),
      }));
      setPosts((prev) => [...prev, ...morePosts]);
      setPage((prev) => prev + 1);
      setIsLoadingMore(false);
    }, 1500);
  };

  const handleLike = (postId: string) => {
    setPosts((prev) =>
      prev.map((post) =>
        post.id === postId
          ? { ...post, isLiked: !post.isLiked, likes: post.isLiked ? post.likes - 1 : post.likes + 1 }
          : post
      )
    );
  };

  const handleComment = (postId: string, content: string) => {
    const newComment: Comment = {
      id: `new-${Date.now()}`,
      user: currentUser,
      content,
      timestamp: new Date().toISOString(),
      likes: 0,
    };

    setPosts((prev) =>
      prev.map((post) =>
        post.id === postId
          ? { ...post, comments: [...post.comments, newComment] }
          : post
      )
    );
  };

  const handleShare = (postId: string) => {
    setPosts((prev) =>
      prev.map((post) =>
        post.id === postId ? { ...post, shares: post.shares + 1 } : post
      )
    );
  };

  const handleBookmark = (postId: string) => {
    setPosts((prev) =>
      prev.map((post) =>
        post.id === postId ? { ...post, isBookmarked: !post.isBookmarked } : post
      )
    );
  };

  const handleCreatePost = (content: string, images: string[]) => {
    const newPost: Post = {
      id: `new-${Date.now()}`,
      user: currentUser,
      content,
      images: images.length > 0 ? images : undefined,
      timestamp: new Date().toISOString(),
      likes: 0,
      comments: [],
      shares: 0,
      isLiked: false,
      isBookmarked: false,
    };

    setPosts((prev) => [newPost, ...prev]);
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'dark' : ''}`}>
      <div className="bg-gray-100 dark:bg-gray-900 min-h-screen">
        <div className="max-w-2xl mx-auto px-4 py-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Feed</h1>
            <p className="text-gray-500 dark:text-gray-400">See what's happening</p>
          </div>

          {/* Post Creation Form */}
          <div className="mb-6">
            <PostCreationForm currentUser={currentUser} onSubmit={handleCreatePost} />
          </div>

          {/* Posts */}
          {isLoading ? (
            <div className="space-y-6">
              <PostSkeleton />
              <PostSkeleton />
              <PostSkeleton />
            </div>
          ) : (
            <div className="space-y-6">
              {posts.map((post) => (
                <FeedErrorBoundary key={post.id}>
                  <PostCardMemo
                    post={post}
                    onLike={handleLike}
                    onComment={handleComment}
                    onShare={handleShare}
                    onBookmark={handleBookmark}
                    currentUser={currentUser}
                  />
                </FeedErrorBoundary>
              ))}

              {/* Infinite Scroll Trigger */}
              <div ref={loadMoreRef} className="py-4">
                {isLoadingMore && <LoadingSpinner />}
                {!hasMore && posts.length > 0 && (
                  <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                    You've reached the end! 🎉
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
