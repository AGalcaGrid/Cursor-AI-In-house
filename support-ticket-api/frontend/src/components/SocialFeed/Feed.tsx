import { useState, useEffect, useCallback, useRef } from 'react';
import { Loader2 } from 'lucide-react';
import type { Post, Comment, FeedUser } from './types';
import PostCard from './PostCard';
import CreatePost from './CreatePost';

const MOCK_USERS: FeedUser[] = [
  { id: 1, name: 'Sarah Johnson', username: 'sarahj', verified: true },
  { id: 2, name: 'Michael Chen', username: 'mchen', verified: false },
  { id: 3, name: 'Emily Davis', username: 'emilyd', verified: true },
  { id: 4, name: 'James Wilson', username: 'jwilson', verified: false },
  { id: 5, name: 'Lisa Anderson', username: 'lisaa', verified: true },
];

const generateMockPosts = (page: number): Post[] => {
  const baseId = (page - 1) * 5;
  return [
    {
      id: baseId + 1,
      user: MOCK_USERS[0],
      content: "Just finished an amazing hike! The views were absolutely breathtaking. Nature really has a way of putting things into perspective. 🏔️ #hiking #nature #adventure",
      images: [`https://picsum.photos/seed/${baseId + 1}/800/600`],
      createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      likes: 142,
      shares: 12,
      isLiked: false,
      isBookmarked: false,
      comments: [
        {
          id: 1,
          user: MOCK_USERS[1],
          content: "Wow, that looks incredible! Where is this?",
          createdAt: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
          likes: 5,
          isLiked: false,
        },
        {
          id: 2,
          user: MOCK_USERS[2],
          content: "I need to visit this place! Adding to my bucket list 📝",
          createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
          likes: 3,
          isLiked: false,
        },
      ],
    },
    {
      id: baseId + 2,
      user: MOCK_USERS[1],
      content: "Excited to announce that I've just joined an amazing new team! Can't wait to start this new chapter. Thanks to everyone who supported me along the way. 🚀",
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
      likes: 89,
      shares: 5,
      isLiked: true,
      isBookmarked: false,
      comments: [
        {
          id: 3,
          user: MOCK_USERS[3],
          content: "Congratulations! 🎉",
          createdAt: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
          likes: 2,
          isLiked: false,
        },
      ],
    },
    {
      id: baseId + 3,
      user: MOCK_USERS[2],
      content: "Coffee and code - the perfect combination for a productive morning. ☕💻\n\nWhat's your go-to productivity hack?",
      images: [`https://picsum.photos/seed/${baseId + 3}/800/600`],
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
      likes: 234,
      shares: 18,
      isLiked: false,
      isBookmarked: true,
      comments: [],
    },
    {
      id: baseId + 4,
      user: MOCK_USERS[3],
      content: "Just watched the most mind-blowing documentary about space exploration. We're living in such an exciting time for science! 🌌✨",
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
      likes: 67,
      shares: 8,
      isLiked: false,
      isBookmarked: false,
      comments: [
        {
          id: 4,
          user: MOCK_USERS[4],
          content: "Which documentary? I'd love to watch it!",
          createdAt: new Date(Date.now() - 1000 * 60 * 60 * 7).toISOString(),
          likes: 1,
          isLiked: false,
        },
        {
          id: 5,
          user: MOCK_USERS[0],
          content: "Space documentaries are the best! 🚀",
          createdAt: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
          likes: 4,
          isLiked: true,
        },
        {
          id: 6,
          user: MOCK_USERS[1],
          content: "I've been meaning to watch more science content",
          createdAt: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
          likes: 0,
          isLiked: false,
        },
        {
          id: 7,
          user: MOCK_USERS[2],
          content: "The universe is truly fascinating",
          createdAt: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
          likes: 2,
          isLiked: false,
        },
      ],
    },
    {
      id: baseId + 5,
      user: MOCK_USERS[4],
      content: "Weekend vibes 🎵 Nothing beats good music and great company!",
      images: [
        `https://picsum.photos/seed/${baseId + 5}a/800/600`,
        `https://picsum.photos/seed/${baseId + 5}b/800/600`,
      ],
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
      likes: 312,
      shares: 24,
      isLiked: false,
      isBookmarked: false,
      comments: [],
    },
  ];
};

const STORAGE_KEY = 'social-feed-posts';

export default function Feed() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const loaderRef = useRef<HTMLDivElement>(null);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        setPosts(JSON.parse(saved));
      } catch {
        setPosts(generateMockPosts(1));
      }
    } else {
      setPosts(generateMockPosts(1));
    }
  }, []);

  // Save to localStorage on changes
  useEffect(() => {
    if (posts.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(posts));
    }
  }, [posts]);

  // Infinite scroll placeholder
  const loadMore = useCallback(async () => {
    if (isLoading || !hasMore) return;
    
    setIsLoading(true);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const newPosts = generateMockPosts(page + 1);
    setPosts(prev => [...prev, ...newPosts]);
    setPage(prev => prev + 1);
    
    // Stop after 5 pages for demo
    if (page >= 4) {
      setHasMore(false);
    }
    
    setIsLoading(false);
  }, [isLoading, hasMore, page]);

  // Intersection Observer for infinite scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isLoading) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (loaderRef.current) {
      observer.observe(loaderRef.current);
    }

    return () => observer.disconnect();
  }, [loadMore, hasMore, isLoading]);

  const handleCreatePost = (content: string, images?: string[]) => {
    const newPost: Post = {
      id: Date.now(),
      user: { id: 0, name: 'You', username: 'you', verified: false },
      content,
      images,
      createdAt: new Date().toISOString(),
      likes: 0,
      shares: 0,
      isLiked: false,
      isBookmarked: false,
      comments: [],
    };
    setPosts(prev => [newPost, ...prev]);
  };

  const handleLike = (postId: number) => {
    setPosts(prev => prev.map(post => {
      if (post.id !== postId) return post;
      return {
        ...post,
        isLiked: !post.isLiked,
        likes: post.isLiked ? post.likes - 1 : post.likes + 1,
      };
    }));
  };

  const handleBookmark = (postId: number) => {
    setPosts(prev => prev.map(post => {
      if (post.id !== postId) return post;
      return { ...post, isBookmarked: !post.isBookmarked };
    }));
  };

  const handleShare = (postId: number) => {
    // Placeholder for share functionality
    const post = posts.find(p => p.id === postId);
    if (post) {
      // Copy link to clipboard placeholder
      navigator.clipboard?.writeText(`https://example.com/post/${postId}`);
      alert('Link copied to clipboard!');
      setPosts(prev => prev.map(p => 
        p.id === postId ? { ...p, shares: p.shares + 1 } : p
      ));
    }
  };

  const handleAddComment = (postId: number, content: string) => {
    const newComment: Comment = {
      id: Date.now(),
      user: { id: 0, name: 'You', username: 'you', verified: false },
      content,
      createdAt: new Date().toISOString(),
      likes: 0,
      isLiked: false,
    };
    
    setPosts(prev => prev.map(post => {
      if (post.id !== postId) return post;
      return { ...post, comments: [...post.comments, newComment] };
    }));
  };

  const handleLikeComment = (postId: number, commentId: number) => {
    setPosts(prev => prev.map(post => {
      if (post.id !== postId) return post;
      return {
        ...post,
        comments: post.comments.map(comment => {
          if (comment.id !== commentId) return comment;
          return {
            ...comment,
            isLiked: !comment.isLiked,
            likes: comment.isLiked ? comment.likes - 1 : comment.likes + 1,
          };
        }),
      };
    }));
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Social Feed</h1>
          <p className="text-gray-500 mt-1">See what's happening in your network</p>
        </div>
      </div>

      <CreatePost onSubmit={handleCreatePost} userName="You" />

      <div className="space-y-4">
        {posts.map(post => (
          <PostCard
            key={post.id}
            post={post}
            onLike={handleLike}
            onBookmark={handleBookmark}
            onShare={handleShare}
            onAddComment={handleAddComment}
            onLikeComment={handleLikeComment}
          />
        ))}
      </div>

      {/* Infinite Scroll Loader */}
      <div ref={loaderRef} className="py-8 flex justify-center">
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Loading more posts...</span>
          </div>
        )}
        {!hasMore && posts.length > 0 && (
          <p className="text-gray-500 text-center">
            You've reached the end! 🎉
          </p>
        )}
      </div>
    </div>
  );
}
