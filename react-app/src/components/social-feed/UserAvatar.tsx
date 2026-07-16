interface UserAvatarProps {
  src: string;
  alt: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  showRing?: boolean;
  isOnline?: boolean;
  className?: string;
}

const sizeClasses = {
  xs: 'w-6 h-6',
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16',
};

const ringClasses = {
  xs: 'ring-1',
  sm: 'ring-2',
  md: 'ring-2',
  lg: 'ring-2',
  xl: 'ring-4',
};

const onlineIndicatorClasses = {
  xs: 'w-1.5 h-1.5 border',
  sm: 'w-2 h-2 border',
  md: 'w-2.5 h-2.5 border-2',
  lg: 'w-3 h-3 border-2',
  xl: 'w-4 h-4 border-2',
};

export function UserAvatar({
  src,
  alt,
  size = 'md',
  showRing = false,
  isOnline,
  className = '',
}: UserAvatarProps) {
  return (
    <div className={`relative inline-block flex-shrink-0 ${className}`}>
      <img
        src={src}
        alt={alt}
        className={`${sizeClasses[size]} rounded-full object-cover ${
          showRing ? `${ringClasses[size]} ring-gray-100 dark:ring-gray-700` : ''
        }`}
      />
      {isOnline !== undefined && (
        <span
          className={`absolute bottom-0 right-0 ${onlineIndicatorClasses[size]} rounded-full border-white dark:border-gray-800 ${
            isOnline ? 'bg-green-500' : 'bg-gray-400'
          }`}
        />
      )}
    </div>
  );
}
