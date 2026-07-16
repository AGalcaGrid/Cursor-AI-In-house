# 🚀 Quick Start - E-Commerce System

## Prerequisites Installed ✅

- ✅ `react-router-dom` - Routing
- ✅ `axios` - API calls
- ✅ `lucide-react` - Icons

---

## Start the System

### 1. Start Backend (Docker)

```bash
# From project root
docker compose up -d ecommerce-api

# Verify it's running
docker compose ps ecommerce-api
curl http://localhost:5004/api/products
```

**Backend URL:** `http://localhost:5004`

---

### 2. Start Frontend (React)

```bash
cd react-app
npm run dev
```

**Frontend URL:** `http://localhost:3000`

---

## 🎯 Test the Complete Flow

### Step 1: Browse Products
- Open `http://localhost:3000`
- You'll see the Shop page
- Products will load from the API

### Step 2: Add to Cart
- Click "Add to Cart" on any product
- See the cart badge update in the header
- Button shows "Added to Cart!" confirmation

### Step 3: View Cart
- Click the cart icon (🛒) in the header
- See all items in your cart
- Try updating quantities with +/- buttons
- Try removing items

### Step 4: Apply Discount (Optional)
- In the cart, enter discount code: `SAVE20`
- Click "Apply"
- See discount applied to total

### Step 5: Checkout
- Click "Proceed to Checkout"
- Fill in shipping information:
  - First Name: John
  - Last Name: Doe
  - Email: john@example.com
  - Phone: 555-1234
  - Street: 123 Main St
  - City: New York
  - State: NY
  - Postal Code: 10001
- Click "Place Order"

### Step 6: Order Confirmation
- See order confirmation page
- Note your order number
- See order details and shipping info

### Step 7: View Orders
- Click "Orders" in the navigation
- See your order history
- Click any order to view details

---

## 🔧 Troubleshooting

### Backend Not Running

```bash
# Check if container is up
docker compose ps ecommerce-api

# If not running, start it
docker compose up -d ecommerce-api

# Check logs
docker compose logs -f ecommerce-api
```

### Frontend Errors

```bash
# Make sure dependencies are installed
cd react-app
npm install

# Restart dev server
npm run dev
```

### CORS Errors

The backend is configured to accept requests from `http://localhost:3000`. If you're running on a different port, update the backend's CORS settings in `docker-compose.yml`.

### API Connection Failed

1. Verify backend is running: `curl http://localhost:5004/api/products`
2. Check browser console for errors
3. Verify API URL in `src/services/ecommerceApi.ts` is `http://localhost:5004/api`

---

## 📊 Available Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | Shop | Product listing (home) |
| `/shop` | Shop | Product listing |
| `/cart` | Cart | Shopping cart |
| `/checkout` | Checkout | Checkout form |
| `/orders` | Orders | Order history |
| `/order-confirmation/:orderNumber` | Confirmation | Order success |

---

## 🎨 Features to Try

### Product Search
- Use the search bar on the Shop page
- Search by product name, brand, or description

### Category Filter
- Use the category dropdown
- Filter products by category

### Discount Codes
- Try these codes in the cart:
  - `SAVE20` - 20% off
  - `SAVE10` - 10% off
  - (Add more in backend if needed)

### Quantity Management
- Add multiple items to cart
- Update quantities
- Remove items
- Clear cart

---

## 🗄️ Sample Data

### Create Sample Products (Optional)

You can add products via the API:

```bash
curl -X POST http://localhost:5004/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PROD-001",
    "name": "Wireless Headphones",
    "description": "Premium wireless headphones with noise cancellation",
    "price": 199.99,
    "compare_at_price": 299.99,
    "category": "Electronics",
    "brand": "AudioTech",
    "stock_quantity": 50
  }'
```

---

## 🎯 Success Indicators

**Everything is working if you can:**

1. ✅ See products on the home page
2. ✅ Add products to cart
3. ✅ See cart badge update
4. ✅ View cart with items
5. ✅ Apply discount codes
6. ✅ Complete checkout
7. ✅ See order confirmation
8. ✅ View order history

---

## 📝 Notes

- **Authentication:** Currently optional for browsing/cart
- **Payment:** Using mock Stripe keys (development mode)
- **Email:** Using mock SendGrid keys (won't send real emails)
- **Database:** SQLite in Docker volume (persists data)

---

## 🎉 You're Ready!

Your complete e-commerce system is running:

- ✅ **Backend API** on port 5004
- ✅ **Frontend UI** on port 3000
- ✅ **Database** in Docker
- ✅ **Full checkout flow**

**Happy shopping!** 🛒
