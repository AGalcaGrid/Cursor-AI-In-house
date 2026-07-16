export interface UserStats {
  followers: number;
  following: number;
  posts: number;
}

export interface UserProfile {
  id: string;
  username: string;
  displayName: string;
  avatar: string;
  bio: string;
  stats: UserStats;
  isFollowing: boolean;
  isOwnProfile: boolean;
}
