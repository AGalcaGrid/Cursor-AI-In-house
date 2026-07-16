import { useState } from 'react';
import { Send } from 'lucide-react';
import type { Comment } from './types';
import UserAvatar from './UserAvatar';

interface CommentSectionProps {
  comments: Comment[];
  onAddComment: (content: string) => void;
  onLikeComment: (commentId: number) => void;
  maxVisible?: number;
}

export default function CommentSection({ 
  comments, 
  onAddComment, 
  onLikeComment,
  maxVisible = 3 
}: CommentSectionProps) {
  const [newComment, setNewComment] = useState('');
  const [showAll, setShowAll] = useState(false);

  const visibleComments = showAll ? comments : comments.slice(0, maxVisible);
  const hiddenCount = comments.length - maxVisible;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newComment.trim()) {
      onAddComment(newComment.trim());
      setNewComment('');
    }
  };

  const formatTimestamp = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    if (diffDays < 7) return `${diffDays}d`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="space-y-3">
      {comments.length > maxVisible && !showAll && (
        <button
          onClick={() => setShowAll(true)}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          View all {comments.length} comments
        </button>
      )}

      {visibleComments.map((comment) => (
        <div key={comment.id} className="flex gap-3">
          <UserAvatar user={comment.user} size="sm" />
          <div className="flex-1 min-w-0">
            <div className="bg-gray-100 rounded-2xl px-4 py-2">
              <span className="font-semibold text-sm text-gray-900">{comment.user.name}</span>
              <p className="text-sm text-gray-700">{comment.content}</p>
            </div>
            <div className="flex items-center gap-4 mt-1 px-2">
              <span className="text-xs text-gray-500">{formatTimestamp(comment.createdAt)}</span>
              <button
                onClick={() => onLikeComment(comment.id)}
                className={`text-xs font-medium ${comment.isLiked ? 'text-red-500' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Like {comment.likes > 0 && `(${comment.likes})`}
              </button>
              <button className="text-xs font-medium text-gray-500 hover:text-gray-700">
                Reply
              </button>
            </div>
          </div>
        </div>
      ))}

      {showAll && hiddenCount > 0 && (
        <button
          onClick={() => setShowAll(false)}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Show less
        </button>
      )}

      <form onSubmit={handleSubmit} className="flex items-center gap-3 mt-3">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-medium flex-shrink-0">
          Y
        </div>
        <div className="flex-1 relative">
          <input
            type="text"
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Write a comment..."
            className="w-full px-4 py-2 pr-10 bg-gray-100 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
          />
          <button
            type="submit"
            disabled={!newComment.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-blue-500 hover:text-blue-600 disabled:text-gray-300 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
