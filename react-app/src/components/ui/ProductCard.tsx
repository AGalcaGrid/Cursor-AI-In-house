import type { Product } from '../../types/product';

interface ProductCardProps {
  product: Product;
  onAddToCart?: (product: Product) => void;
}

function StarRating({ rating, reviewCount }: { rating: number; reviewCount: number }) {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

  return (
    <div className="flex items-center gap-1.5" role="img" aria-label={`Rating: ${rating} out of 5 stars`}>
      <div className="flex" aria-hidden="true">
        {[...Array(fullStars)].map((_, i) => (
          <svg key={`full-${i}`} className="w-4 h-4 text-yellow-400 fill-current" viewBox="0 0 20 20">
            <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
          </svg>
        ))}
        {hasHalfStar && (
          <svg className="w-4 h-4 text-yellow-400" viewBox="0 0 20 20">
            <defs>
              <linearGradient id="halfGradient">
                <stop offset="50%" stopColor="currentColor" />
                <stop offset="50%" stopColor="#D1D5DB" />
              </linearGradient>
            </defs>
            <path fill="url(#halfGradient)" d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
          </svg>
        )}
        {[...Array(emptyStars)].map((_, i) => (
          <svg key={`empty-${i}`} className="w-4 h-4 text-gray-300 fill-current" viewBox="0 0 20 20">
            <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
          </svg>
        ))}
      </div>
      <span className="text-sm text-gray-500">({reviewCount})</span>
    </div>
  );
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(price);
}

export function ProductCard({ product, onAddToCart }: ProductCardProps) {
  const discountPercentage = product.originalPrice
    ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)
    : 0;

  return (
    <article
      className="group relative flex flex-col bg-white rounded-2xl shadow-md overflow-hidden
                 transition-all duration-300 ease-out
                 hover:shadow-xl hover:-translate-y-1"
      aria-label={`Product: ${product.title}`}
    >
      {/* Discount Badge */}
      {discountPercentage > 0 && (
        <span
          className="absolute top-3 left-3 z-10 px-2.5 py-1 bg-red-500 text-white text-xs font-bold rounded-full"
          aria-label={`${discountPercentage}% discount`}
        >
          -{discountPercentage}%
        </span>
      )}

      {/* Out of Stock Overlay */}
      {!product.inStock && (
        <div className="absolute inset-0 z-20 bg-white/80 flex items-center justify-center">
          <span className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg">
            Out of Stock
          </span>
        </div>
      )}

      {/* Product Image */}
      <div className="relative aspect-square overflow-hidden bg-gray-100">
        <img
          src={product.image}
          alt={product.title}
          className="w-full h-full object-cover transition-transform duration-500 ease-out
                     group-hover:scale-110"
          loading="lazy"
        />
      </div>

      {/* Product Details */}
      <div className="flex flex-col flex-1 p-4">
        {/* Category */}
        {product.category && (
          <span className="text-xs font-medium text-blue-600 uppercase tracking-wide mb-1">
            {product.category}
          </span>
        )}

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 mb-1">
          {product.title}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-500 line-clamp-2 mb-3 flex-1">
          {product.description}
        </p>

        {/* Rating */}
        <div className="mb-3">
          <StarRating rating={product.rating} reviewCount={product.reviewCount} />
        </div>

        {/* Price */}
        <div className="flex items-baseline gap-2 mb-4">
          <span className="text-xl font-bold text-gray-900">
            {formatPrice(product.price)}
          </span>
          {product.originalPrice && (
            <span className="text-sm text-gray-400 line-through">
              {formatPrice(product.originalPrice)}
            </span>
          )}
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={() => onAddToCart?.(product)}
          disabled={!product.inStock}
          className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-xl
                     transition-all duration-200 ease-out
                     hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-500/25
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                     active:scale-[0.98]
                     disabled:bg-gray-300 disabled:cursor-not-allowed disabled:hover:shadow-none"
          aria-label={`Add ${product.title} to cart`}
        >
          <span className="flex items-center justify-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Add to Cart
          </span>
        </button>
      </div>
    </article>
  );
}
