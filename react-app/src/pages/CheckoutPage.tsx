import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { checkoutApi } from '../services/ecommerceApi';
import type { CheckoutData } from '../services/ecommerceApi';
import { CreditCard, Truck, Lock } from 'lucide-react';

export const CheckoutPage: React.FC = () => {
  const navigate = useNavigate();
  const { cart } = useCart();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<CheckoutData>({
    shipping_first_name: '',
    shipping_last_name: '',
    shipping_email: '',
    shipping_phone: '',
    shipping_street_address: '',
    shipping_apartment: '',
    shipping_city: '',
    shipping_state: '',
    shipping_postal_code: '',
    shipping_country: 'US',
    billing_same_as_shipping: true,
    payment_method: 'card',
    notes: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const order = await checkoutApi.completeCheckout(formData);
      navigate(`/order-confirmation/${order.order_number}`);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to complete checkout. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!cart || cart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900">Your cart is empty</h2>
            <button
              onClick={() => navigate('/')}
              className="mt-4 inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Continue Shopping
            </button>
          </div>
        </div>
      </div>
    );
  }

  const tax = cart.subtotal * 0.08; // 8% tax
  const shipping = 0; // Free shipping
  const total = cart.total + tax + shipping;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Checkout</h1>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-400">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Checkout Form */}
            <div className="lg:col-span-2 space-y-6">
              {/* Shipping Information */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Truck className="w-5 h-5 text-blue-600" />
                  <h2 className="text-xl font-bold text-gray-900">Shipping Information</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      First Name *
                    </label>
                    <input
                      type="text"
                      name="shipping_first_name"
                      value={formData.shipping_first_name}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      name="shipping_last_name"
                      value={formData.shipping_last_name}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email *
                    </label>
                    <input
                      type="email"
                      name="shipping_email"
                      value={formData.shipping_email}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone
                    </label>
                    <input
                      type="tel"
                      name="shipping_phone"
                      value={formData.shipping_phone}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Street Address *
                    </label>
                    <input
                      type="text"
                      name="shipping_street_address"
                      value={formData.shipping_street_address}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Apartment, Suite, etc.
                    </label>
                    <input
                      type="text"
                      name="shipping_apartment"
                      value={formData.shipping_apartment}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      City *
                    </label>
                    <input
                      type="text"
                      name="shipping_city"
                      value={formData.shipping_city}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      State *
                    </label>
                    <input
                      type="text"
                      name="shipping_state"
                      value={formData.shipping_state}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Postal Code *
                    </label>
                    <input
                      type="text"
                      name="shipping_postal_code"
                      value={formData.shipping_postal_code}
                      onChange={handleChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              {/* Payment Method */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <CreditCard className="w-5 h-5 text-blue-600" />
                  <h2 className="text-xl font-bold text-gray-900">Payment Method</h2>
                </div>

                <div className="space-y-3">
                  <label className="flex items-center gap-3 p-4 border-2 border-blue-600 rounded-lg cursor-pointer">
                    <input
                      type="radio"
                      name="payment_method"
                      value="card"
                      checked={formData.payment_method === 'card'}
                      onChange={handleChange}
                      className="w-4 h-4 text-blue-600"
                    />
                    <CreditCard className="w-5 h-5 text-gray-600" />
                    <span className="font-medium">Credit/Debit Card</span>
                  </label>

                  <div className="flex items-center gap-2 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <Lock className="w-4 h-4 text-blue-600" />
                    <p className="text-sm text-blue-900">
                      Your payment information is secure and encrypted
                    </p>
                  </div>
                </div>
              </div>

              {/* Order Notes */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Order Notes (Optional)</h2>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={4}
                  placeholder="Special instructions for your order..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6 sticky top-4">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>

                {/* Items */}
                <div className="space-y-3 mb-4 pb-4 border-b">
                  {cart.items.map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <span className="text-gray-600">
                        {item.product.name} × {item.quantity}
                      </span>
                      <span className="font-medium">${item.total_price.toFixed(2)}</span>
                    </div>
                  ))}
                </div>

                {/* Price Breakdown */}
                <div className="space-y-2 mb-4 pb-4 border-b">
                  <div className="flex justify-between text-gray-600">
                    <span>Subtotal</span>
                    <span>${cart.subtotal.toFixed(2)}</span>
                  </div>
                  {cart.discount_amount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount</span>
                      <span>-${cart.discount_amount.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-gray-600">
                    <span>Shipping</span>
                    <span>{shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`}</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>Tax (8%)</span>
                    <span>${tax.toFixed(2)}</span>
                  </div>
                </div>

                {/* Total */}
                <div className="flex justify-between text-xl font-bold text-gray-900 mb-6">
                  <span>Total</span>
                  <span>${total.toFixed(2)}</span>
                </div>

                {/* Place Order Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Processing...' : 'Place Order'}
                </button>

                <button
                  type="button"
                  onClick={() => navigate('/cart')}
                  className="w-full mt-3 py-3 px-4 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
                >
                  Back to Cart
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
