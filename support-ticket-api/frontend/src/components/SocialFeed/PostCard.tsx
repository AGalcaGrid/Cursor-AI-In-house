import { useState } from 'react';
import { Heart, MessageCircle, Share2, Bookmark, MoreHorizontal } from 'lucide-react';
import type { Post } from './types';
import UserAvatar from './UserAvatar';
import CommentSection from './CommentSection';

interface PostCardProps {
  post: Post;
  onLike: (postId: number) => void;
  onBookmark: (postId: number) => void;
  onShare: (postId: number) => void;
  onAddComment: (postId: number, content: string) => void;
  onLikeComment: (postId: number, commentId: number) => void;
}

export default function PostCard({ 
  post, 
  onLike, 
  onBookmark, 
  onShare, 
  onAddComment,
  onLikeComment 
}: PostCardProps) {
  const [showComments, setShowComments] = useState(false);
  const [imageIndex, setImageIndex] = useState(0);

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <article className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4">
        <UserAvatar 
          user={post.user} 
          showName 
          showUsername 
          timestamp={post.createdAt}
        />
        <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors">
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="px-4 pb-3">
        <p className="text-gray-900 whitespace-pre-wrap">{post.content}</p>
      </div>

      {/* Images */}
      {post.images && post.images.length > 0 && (
        <div className="relative">
          <div className="aspect-video bg-gray-100 overflow-hidden">
            <img
              src={post.images[imageIndex]}
              alt={`Post image ${imageIndex + 1}`}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src = `https://picsum.photos/seed/${post.id}/800/600`;
              }}
            />
          </div>
          {post.images.length > 1 && (
            <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
              {post.images.map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setImageIndex(idx)}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    idx === imageIndex ? 'bg-white' : 'bg-white/50'
                  }`}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Stats */}
      <div className="px-4 py-2 flex items-center justify-between text-sm text-gray-500 border-b border-gray-100">
        <div className="flex items-center gap-1">
          {post.likes > 0 && (
            <>
              <span className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center">
                <Heart className="w-3 h-3 text-white fill-white" />
              </span>
              <span>{formatNumber(post.likes)}</span>
            </>
          )}
        </div>
        <div className="flex items-center gap-4">
          {post.comments.length > 0 && (
            <button 
              onClick={() => setShowComments(!showComments)}
              className="hover:underline"
            >
              {post.comments.length} comments
            </button>
          )}
          {post.shares > 0 && (
            <span>{formatNumber(post.shares)} shares</span>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="px-2 py-1 flex items-center justify-between border-b border-gray-100">
        <button
          onClick={() => onLike(post.id)}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg transition-colors ${
            post.isLiked 
              ? 'text-red-500 hover:bg-red-50' 
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Heart className={`w-5 h-5 ${post.isLiked ? 'fill-current' : ''}`} />
          <span className="font-medium">Like</span>
        </button>
        
        <button
          onClick={() => setShowComments(!showComments)}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <MessageCircle className="w-5 h-5" />
          <span className="font-medium">Comment</span>
        </button>
        
        <button
          onClick={() => onShare(post.id)}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <Share2 className="w-5 h-5" />
          <span className="font-medium">Share</span>
        </button>
        
        <button
          onClick={() => onBookmark(post.id)}
          className={`p-2.5 rounded-lg transition-colors ${
            post.isBookmarked 
              ? 'text-blue-500 hover:bg-blue-50' 
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Bookmark className={`w-5 h-5 ${post.isBookmarked ? 'fill-current' : ''}`} />
        </button>
      </div>

      {/* Comments Section */}
      {showComments && (
        <div className="p-4 bg-gray-50">
          <CommentSection
            comments={post.comments}
            onAddComment={(content) => onAddComment(post.id, content)}
            onLikeComment={(commentId) => onLikeComment(post.id, commentId)}
          />
        </div>
      )}
    </article>
  );
}
