import type { UserProfile as UserProfileType } from '../../types/user';

interface UserProfileProps {
  user: UserProfileType;
  onFollow?: () => void;
  onMessage?: () => void;
  onEditProfile?: () => void;
}

function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
  }
  return num.toString();
}

export function UserProfile({
  user,
  onFollow,
  onMessage,
  onEditProfile,
}: UserProfileProps) {
  return (
    <article
      className="w-full bg-white rounded-2xl shadow-lg overflow-hidden"
      aria-label={`Profile of ${user.displayName}`}
    >
      {/* Cover/Header Area */}
      <div className="h-24 bg-gradient-to-r from-blue-500 to-purple-600" />

      {/* Profile Content */}
      <div className="relative px-6 pb-6">
        {/* Avatar */}
        <div className="relative -mt-12 mb-4">
          <img
            src={user.avatar}
            alt={`${user.displayName}'s avatar`}
            className="w-24 h-24 rounded-full border-4 border-white object-cover shadow-md"
          />
          {user.isOwnProfile && (
            <span className="sr-only">Your profile</span>
          )}
        </div>

        {/* User Info */}
        <header className="mb-4">
          <h1 className="text-xl font-bold text-gray-900">
            {user.displayName}
          </h1>
          <p className="text-sm text-gray-500">@{user.username}</p>
        </header>

        {/* Bio */}
        {user.bio && (
          <p className="text-gray-700 text-sm leading-relaxed mb-4">
            {user.bio}
          </p>
        )}

        {/* Stats */}
        <div
          className="flex justify-between py-4 border-y border-gray-100 mb-4"
          role="list"
          aria-label="Profile statistics"
        >
          <div className="text-center flex-1" role="listitem">
            <span className="block text-lg font-bold text-gray-900">
              {formatNumber(user.stats.posts)}
            </span>
            <span className="text-xs text-gray-500 uppercase tracking-wide">
              Posts
            </span>
          </div>
          <div className="text-center flex-1 border-x border-gray-100" role="listitem">
            <span className="block text-lg font-bold text-gray-900">
              {formatNumber(user.stats.followers)}
            </span>
            <span className="text-xs text-gray-500 uppercase tracking-wide">
              Followers
            </span>
          </div>
          <div className="text-center flex-1" role="listitem">
            <span className="block text-lg font-bold text-gray-900">
              {formatNumber(user.stats.following)}
            </span>
            <span className="text-xs text-gray-500 uppercase tracking-wide">
              Following
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          {user.isOwnProfile ? (
            <button
              onClick={onEditProfile}
              className="flex-1 px-4 py-2.5 bg-gray-100 text-gray-700 font-medium rounded-lg
                         hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-300
                         focus:ring-offset-2 transition-colors"
              aria-label="Edit your profile"
            >
              Edit Profile
            </button>
          ) : (
            <>
              <button
                onClick={onFollow}
                className={`flex-1 px-4 py-2.5 font-medium rounded-lg transition-colors
                           focus:outline-none focus:ring-2 focus:ring-offset-2
                           ${
                             user.isFollowing
                               ? 'bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-gray-300'
                               : 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-300'
                           }`}
                aria-pressed={user.isFollowing}
                aria-label={user.isFollowing ? `Unfollow ${user.displayName}` : `Follow ${user.displayName}`}
              >
                {user.isFollowing ? 'Following' : 'Follow'}
              </button>
              <button
                onClick={onMessage}
                className="flex-1 px-4 py-2.5 bg-gray-100 text-gray-700 font-medium rounded-lg
                           hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-300
                           focus:ring-offset-2 transition-colors"
                aria-label={`Send message to ${user.displayName}`}
              >
                Message
              </button>
            </>
          )}
        </div>
      </div>
    </article>
  );
}
