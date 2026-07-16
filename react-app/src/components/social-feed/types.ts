export interface User {
  id: string;
  name: string;
  username: string;
  avatar: string;
  verified?: boolean;
}

export interface Comment {
  id: string;
  user: User;
  content: string;
  timestamp: string;
  likes: number;
  isLiked?: boolean;
  replies?: Comment[];
}

export interface Post {
  id: string;
  user: User;
  content: string;
  images?: string[];
  timestamp: string;
  likes: number;
  comments: Comment[];
  shares: number;
  isLiked?: boolean;
  isBookmarked?: boolean;
}
