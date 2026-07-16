import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../../contexts/CartContext';
import { ShoppingCart } from 'lucide-react';

export const CartIcon: React.FC = () => {
  const navigate = useNavigate();
  const { cart } = useCart();

  const itemCount = cart?.total_items || 0;

  return (
    <button
      onClick={() => navigate('/cart')}
      className="relative p-2 text-gray-700 hover:text-blue-600 transition-colors"
      aria-label={`Shopping cart with ${itemCount} items`}
    >
      <ShoppingCart className="w-6 h-6" />
      {itemCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
          {itemCount > 9 ? '9+' : itemCount}
        </span>
      )}
    </button>
  );
};
