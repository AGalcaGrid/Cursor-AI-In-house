import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { CartIcon } from './CartIcon';
import { Store, Package, ShoppingBag } from 'lucide-react';

export const EcommerceLayout: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2 text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors">
              <Store className="w-6 h-6" />
              <span>E-Shop</span>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-6">
              <Link
                to="/shop"
                className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors font-medium"
              >
                <ShoppingBag className="w-5 h-5" />
                Shop
              </Link>
              <Link
                to="/orders"
                className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors font-medium"
              >
                <Package className="w-5 h-5" />
                Orders
              </Link>
              <Link
                to="/dashboard"
                className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors font-medium"
              >
                Dashboard
              </Link>
            </nav>

            {/* Cart Icon */}
            <div className="flex items-center gap-4">
              <CartIcon />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-bold text-gray-900 mb-3">About E-Shop</h3>
              <p className="text-gray-600 text-sm">
                Your one-stop shop for quality products at great prices.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-3">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/shop" className="text-gray-600 hover:text-blue-600">
                    Shop
                  </Link>
                </li>
                <li>
                  <Link to="/orders" className="text-gray-600 hover:text-blue-600">
                    My Orders
                  </Link>
                </li>
                <li>
                  <Link to="/cart" className="text-gray-600 hover:text-blue-600">
                    Shopping Cart
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-3">Customer Service</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>Email: support@eshop.com</li>
                <li>Phone: 1-800-ESHOP</li>
                <li>Hours: Mon-Fri 9AM-5PM EST</li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-gray-600">
            © 2026 E-Shop. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};
