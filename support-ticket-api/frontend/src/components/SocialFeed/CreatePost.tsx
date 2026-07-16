import { useState, useRef } from 'react';
import { Image, Smile, MapPin, Users, X } from 'lucide-react';

interface CreatePostProps {
  onSubmit: (content: string, images?: string[]) => void;
  userAvatar?: string;
  userName?: string;
}

export default function CreatePost({ onSubmit, userName = 'You' }: CreatePostProps) {
  const [content, setContent] = useState('');
  const [images, setImages] = useState<string[]>([]);
  const [isFocused, setIsFocused] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (content.trim() || images.length > 0) {
      onSubmit(content.trim(), images.length > 0 ? images : undefined);
      setContent('');
      setImages([]);
      setIsFocused(false);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      Array.from(files).forEach((file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          if (e.target?.result) {
            setImages((prev) => [...prev, e.target!.result as string]);
          }
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const removeImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  const initials = userName
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <form onSubmit={handleSubmit}>
        <div className="flex gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium flex-shrink-0">
            {initials}
          </div>
          <div className="flex-1">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onFocus={() => setIsFocused(true)}
              placeholder={`What's on your mind, ${userName.split(' ')[0]}?`}
              className="w-full resize-none border-0 focus:ring-0 text-gray-900 placeholder-gray-500 text-lg bg-transparent"
              rows={isFocused ? 3 : 1}
            />
          </div>
        </div>

        {/* Image Previews */}
        {images.length > 0 && (
          <div className="mt-3 grid grid-cols-2 gap-2">
            {images.map((img, idx) => (
              <div key={idx} className="relative aspect-video rounded-lg overflow-hidden bg-gray-100">
                <img src={img} alt={`Upload ${idx + 1}`} className="w-full h-full object-cover" />
                <button
                  type="button"
                  onClick={() => removeImage(idx)}
                  className="absolute top-2 right-2 p-1 bg-black/50 rounded-full text-white hover:bg-black/70 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Divider */}
        <div className="border-t border-gray-200 mt-4 pt-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1">
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
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Image className="w-5 h-5 text-green-500" />
                <span className="text-sm font-medium hidden sm:inline">Photo</span>
              </button>
              <button
                type="button"
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Smile className="w-5 h-5 text-yellow-500" />
                <span className="text-sm font-medium hidden sm:inline">Feeling</span>
              </button>
              <button
                type="button"
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <MapPin className="w-5 h-5 text-red-500" />
                <span className="text-sm font-medium hidden sm:inline">Location</span>
              </button>
              <button
                type="button"
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Users className="w-5 h-5 text-blue-500" />
                <span className="text-sm font-medium hidden sm:inline">Tag</span>
              </button>
            </div>

            <button
              type="submit"
              disabled={!content.trim() && images.length === 0}
              className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Post
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
