import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { CartProvider } from './contexts/CartContext';
import { ShopPage } from './pages/ShopPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import { OrderConfirmationPage } from './pages/OrderConfirmationPage';
import { OrdersPage } from './pages/OrdersPage';
import { EcommerceLayout } from './components/ecommerce/EcommerceLayout';
import { ErrorBoundary } from './components/ErrorBoundary';
import App from './App';

function AppWithRouter() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <CartProvider>
          <Routes>
            {/* E-Commerce Routes */}
            <Route path="/" element={<EcommerceLayout />}>
              <Route index element={<ShopPage />} />
              <Route path="shop" element={<ShopPage />} />
              <Route path="cart" element={<CartPage />} />
              <Route path="checkout" element={<CheckoutPage />} />
              <Route path="orders" element={<OrdersPage />} />
              <Route path="order-confirmation/:orderNumber" element={<OrderConfirmationPage />} />
            </Route>

            {/* Main Dashboard App */}
            <Route path="/dashboard" element={<App />} />

            {/* Redirect unknown routes */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </CartProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default AppWithRouter;
