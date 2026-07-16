export interface FeedUser {
  id: number;
  name: string;
  username: string;
  avatar?: string;
  verified?: boolean;
}

export interface Comment {
  id: number;
  user: FeedUser;
  content: string;
  createdAt: string;
  likes: number;
  isLiked: boolean;
}

export interface Post {
  id: number;
  user: FeedUser;
  content: string;
  images?: string[];
  createdAt: string;
  likes: number;
  comments: Comment[];
  shares: number;
  isLiked: boolean;
  isBookmarked: boolean;
}

export interface FeedState {
  posts: Post[];
  isLoading: boolean;
  hasMore: boolean;
  page: number;
}
