import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { cartApi } from '../services/ecommerceApi';
import type { Cart, Product } from '../services/ecommerceApi';

interface CartContextType {
  cart: Cart | null;
  loading: boolean;
  error: string | null;
  addToCart: (product: Product, quantity?: number) => Promise<void>;
  updateQuantity: (productId: number, quantity: number) => Promise<void>;
  removeFromCart: (productId: number) => Promise<void>;
  clearCart: () => Promise<void>;
  applyDiscount: (code: string) => Promise<void>;
  removeDiscount: () => Promise<void>;
  refreshCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

interface CartProviderProps {
  children: ReactNode;
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshCart = async () => {
    try {
      setLoading(true);
      setError(null);
      const cartData = await cartApi.getCart();
      setCart(cartData);
    } catch (err: any) {
      console.error('Failed to fetch cart:', err);
      // Don't set error on initial load - just use empty cart
      setCart({
        id: 0,
        total_items: 0,
        subtotal: 0,
        discount_amount: 0,
        total: 0,
        items: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (product: Product, quantity: number = 1) => {
    try {
      setLoading(true);
      setError(null);
      const updatedCart = await cartApi.addItem(product.id, quantity);
      setCart(updatedCart);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to add item to cart');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (productId: number, quantity: number) => {
    try {
      setLoading(true);
      setError(null);
      const updatedCart = await cartApi.updateItem(productId, quantity);
      setCart(updatedCart);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update quantity');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (productId: number) => {
    try {
      setLoading(true);
      setError(null);
      const updatedCart = await cartApi.removeItem(productId);
      setCart(updatedCart);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to remove item');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearCart = async () => {
    try {
      setLoading(true);
      setError(null);
      const updatedCart = await cartApi.clearCart();
      setCart(updatedCart);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to clear cart');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const applyDiscount = async (code: string) => {
    try {
      setLoading(true);
      setError(null);
      const updatedCart = await cartApi.applyDiscount(code);
      setCart(updatedCart);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to apply discount');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const removeDiscount = async () => {
    try {
      setLoading(true);
      setError(null);
      const updatedCart = await cartApi.removeDiscount();
      setCart(updatedCart);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to remove discount');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Load cart on mount
  useEffect(() => {
    refreshCart();
  }, []);

  const value: CartContextType = {
    cart,
    loading,
    error,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    applyDiscount,
    removeDiscount,
    refreshCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};
