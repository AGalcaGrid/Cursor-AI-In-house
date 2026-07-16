import { useState, useRef } from 'react';

interface PostCreationFormProps {
  currentUser: { id: string; name: string; avatar: string };
  onSubmit: (content: string, images: string[]) => void;
}

export function PostCreationForm({ currentUser, onSubmit }: PostCreationFormProps) {
  const [content, setContent] = useState('');
  const [images, setImages] = useState<string[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (content.trim() || images.length > 0) {
      onSubmit(content.trim(), images);
      setContent('');
      setImages([]);
      setIsExpanded(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      // In a real app, you'd upload these to a server
      // For demo, we'll use placeholder images
      const newImages = Array.from(files).map(() => 
        `https://images.unsplash.com/photo-${1500000000000 + Math.random() * 100000000}?w=800&h=600&fit=crop`
      );
      setImages((prev) => [...prev, ...newImages].slice(0, 4));
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  const addDemoImage = () => {
    const demoImages = [
      'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=800&h=600&fit=crop',
      'https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=800&h=600&fit=crop',
    ];
    if (images.length < 4) {
      setImages((prev) => [...prev, demoImages[prev.length % demoImages.length]]);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <form onSubmit={handleSubmit}>
        <div className="flex gap-3">
          <img
            src={currentUser.avatar}
            alt={currentUser.name}
            className="w-12 h-12 rounded-full object-cover flex-shrink-0"
          />
          <div className="flex-1">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onFocus={() => setIsExpanded(true)}
              placeholder="What's on your mind?"
              rows={isExpanded ? 3 : 1}
              className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-700 rounded-2xl text-gray-900 dark:text-white
                placeholder-gray-500 dark:placeholder-gray-400 resize-none
                focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />

            {/* Image Preview */}
            {images.length > 0 && (
              <div className={`mt-3 grid gap-2 ${
                images.length === 1 ? 'grid-cols-1' :
                images.length === 2 ? 'grid-cols-2' :
                'grid-cols-2'
              }`}>
                {images.map((image, index) => (
                  <div key={index} className="relative group">
                    <img
                      src={image}
                      alt={`Upload ${index + 1}`}
                      className="w-full h-32 object-cover rounded-lg"
                    />
                    <button
                      type="button"
                      onClick={() => removeImage(index)}
                      className="absolute top-2 right-2 p-1.5 bg-black/50 rounded-full text-white
                        opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/70"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Action Buttons */}
            {isExpanded && (
              <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {/* Image Upload */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="p-2 rounded-full text-gray-500 hover:text-green-500 hover:bg-green-50 
                      dark:hover:bg-green-900/20 transition-colors"
                    title="Add photo"
                    aria-label="Add photo"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </button>

                  {/* Demo Image Button */}
                  <button
                    type="button"
                    onClick={addDemoImage}
                    disabled={images.length >= 4}
                    className="p-2 rounded-full text-gray-500 hover:text-blue-500 hover:bg-blue-50 
                      dark:hover:bg-blue-900/20 transition-colors disabled:opacity-50"
                    title="Add demo image"
                    aria-label="Add demo image"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </button>

                  {/* GIF */}
                  <button
                    type="button"
                    className="p-2 rounded-full text-gray-500 hover:text-purple-500 hover:bg-purple-50 
                      dark:hover:bg-purple-900/20 transition-colors"
                    title="Add GIF"
                    aria-label="Add GIF"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>

                  {/* Emoji */}
                  <button
                    type="button"
                    className="p-2 rounded-full text-gray-500 hover:text-yellow-500 hover:bg-yellow-50 
                      dark:hover:bg-yellow-900/20 transition-colors"
                    title="Add emoji"
                    aria-label="Add emoji"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>

                  {/* Poll */}
                  <button
                    type="button"
                    className="p-2 rounded-full text-gray-500 hover:text-orange-500 hover:bg-orange-50 
                      dark:hover:bg-orange-900/20 transition-colors"
                    title="Create poll"
                    aria-label="Create poll"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={!content.trim() && images.length === 0}
                  className="px-6 py-2 bg-blue-500 text-white font-semibold rounded-full
                    hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Post
                </button>
              </div>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}
