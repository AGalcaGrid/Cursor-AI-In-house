import React, { useState } from 'react';
import { useCart } from '../../contexts/CartContext';
import type { Product as EcommerceProduct } from '../../services/ecommerceApi';
import { ShoppingCart, Check } from 'lucide-react';

interface ProductCardWithCartProps {
  product: EcommerceProduct;
}

export const ProductCardWithCart: React.FC<ProductCardWithCartProps> = ({ product }) => {
  const { addToCart } = useCart();
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);

  const handleAddToCart = async () => {
    setAdding(true);
    try {
      await addToCart(product, 1);
      setAdded(true);
      setTimeout(() => setAdded(false), 2000);
    } catch (error) {
      console.error('Failed to add to cart:', error);
    } finally {
      setAdding(false);
    }
  };

  const discountPercentage = product.compare_at_price
    ? Math.round(((product.compare_at_price - product.price) / product.compare_at_price) * 100)
    : 0;

  return (
    <article className="group relative bg-white rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100">
      {/* Discount Badge */}
      {discountPercentage > 0 && (
        <div className="absolute top-3 left-3 z-10 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold shadow-lg">
          -{discountPercentage}%
        </div>
      )}

      {/* Stock Badge */}
      {!product.in_stock && (
        <div className="absolute top-3 right-3 z-10 bg-gray-800 text-white px-3 py-1 rounded-full text-sm font-medium">
          Out of Stock
        </div>
      )}
      {product.is_low_stock && product.in_stock && (
        <div className="absolute top-3 right-3 z-10 bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-medium">
          Low Stock
        </div>
      )}

      {/* Product Image */}
      <div className="relative h-64 overflow-hidden bg-gray-100">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <ShoppingCart className="w-16 h-16" />
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="p-5">
        {/* Brand */}
        {product.brand && (
          <p className="text-sm text-gray-500 font-medium mb-1">{product.brand}</p>
        )}

        {/* Product Name */}
        <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 min-h-[3.5rem]">
          {product.name}
        </h3>

        {/* Category */}
        {product.category && (
          <span className="inline-block px-2 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-md mb-3">
            {product.category}
          </span>
        )}

        {/* Description */}
        {product.description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">{product.description}</p>
        )}

        {/* Price */}
        <div className="flex items-baseline gap-2 mb-4">
          <span className="text-2xl font-bold text-gray-900">${product.price.toFixed(2)}</span>
          {product.compare_at_price && (
            <span className="text-lg text-gray-400 line-through">
              ${product.compare_at_price.toFixed(2)}
            </span>
          )}
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={handleAddToCart}
          disabled={!product.in_stock || adding || added}
          className={`w-full py-3 px-4 font-medium rounded-xl transition-all duration-200 ease-out
            focus:outline-none focus:ring-2 focus:ring-offset-2
            active:scale-[0.98]
            ${
              added
                ? 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500'
                : !product.in_stock
                ? 'bg-gray-300 cursor-not-allowed text-gray-500'
                : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-500/25 focus:ring-blue-500'
            }`}
          aria-label={`Add ${product.name} to cart`}
        >
          <span className="flex items-center justify-center gap-2">
            {adding ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Adding...
              </>
            ) : added ? (
              <>
                <Check className="w-5 h-5" />
                Added to Cart!
              </>
            ) : !product.in_stock ? (
              'Out of Stock'
            ) : (
              <>
                <ShoppingCart className="w-5 h-5" />
                Add to Cart
              </>
            )}
          </span>
        </button>

        {/* Stock Info */}
        {product.in_stock && product.stock_quantity <= 10 && (
          <p className="mt-2 text-xs text-orange-600 text-center">
            Only {product.stock_quantity} left in stock!
          </p>
        )}
      </div>
    </article>
  );
};
