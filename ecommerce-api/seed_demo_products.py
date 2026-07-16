#!/usr/bin/env python3
"""
Seed demo products from main page into E-Commerce database
"""
from app import create_app, db
from app.models import Product

demo_products = [
    {
        'name': 'Wireless Noise-Canceling Headphones',
        'description': 'Premium over-ear headphones with active noise cancellation and 30-hour battery life.',
        'price': 249.99,
        'compare_at_price': 349.99,
        'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
        'category': 'Electronics',
        'brand': 'AudioTech',
        'stock_quantity': 45
    },
    {
        'name': 'Minimalist Leather Watch',
        'description': 'Elegant timepiece with genuine leather strap and sapphire crystal glass.',
        'price': 189.00,
        'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
        'category': 'Accessories',
        'brand': 'TimeStyle',
        'stock_quantity': 32
    },
    {
        'name': 'Smart Fitness Tracker',
        'description': 'Track your health metrics, sleep patterns, and workouts with this advanced wearable.',
        'price': 79.99,
        'compare_at_price': 129.99,
        'image_url': 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400&h=400&fit=crop',
        'category': 'Fitness',
        'brand': 'FitPro',
        'stock_quantity': 67
    },
    {
        'name': 'Portable Bluetooth Speaker',
        'description': 'Waterproof speaker with 360° sound and 20-hour playtime. Perfect for outdoor adventures.',
        'price': 59.99,
        'image_url': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop',
        'category': 'Electronics',
        'brand': 'SoundWave',
        'stock_quantity': 0
    },
    {
        'name': 'Mechanical Gaming Keyboard',
        'description': 'RGB backlit mechanical keyboard with customizable keys and ultra-responsive switches.',
        'price': 129.99,
        'compare_at_price': 179.99,
        'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=400&fit=crop',
        'category': 'Electronics',
        'brand': 'GameGear',
        'stock_quantity': 28
    },
    {
        'name': 'Leather Laptop Bag',
        'description': 'Professional leather messenger bag with padded laptop compartment and multiple pockets.',
        'price': 149.00,
        'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop',
        'category': 'Accessories',
        'brand': 'UrbanCarry',
        'stock_quantity': 19
    },
    {
        'name': 'Wireless Gaming Mouse',
        'description': 'High-precision wireless mouse with customizable DPI and programmable buttons.',
        'price': 79.99,
        'image_url': 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=400&h=400&fit=crop',
        'category': 'Electronics',
        'brand': 'GameGear',
        'stock_quantity': 54
    },
    {
        'name': 'Stainless Steel Water Bottle',
        'description': 'Insulated water bottle keeps drinks cold for 24 hours or hot for 12 hours.',
        'price': 34.99,
        'compare_at_price': 49.99,
        'image_url': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop',
        'category': 'Fitness',
        'brand': 'HydroLife',
        'stock_quantity': 89
    },
    {
        'name': 'Yoga Mat with Carrying Strap',
        'description': 'Non-slip exercise mat with extra cushioning for comfort during workouts.',
        'price': 39.99,
        'image_url': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&h=400&fit=crop',
        'category': 'Fitness',
        'brand': 'YogaEssentials',
        'stock_quantity': 76
    },
    {
        'name': 'Wireless Earbuds Pro',
        'description': 'True wireless earbuds with active noise cancellation and 8-hour battery life.',
        'price': 199.99,
        'compare_at_price': 249.99,
        'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&h=400&fit=crop',
        'category': 'Electronics',
        'brand': 'AudioTech',
        'stock_quantity': 41
    },
    {
        'name': 'Smart Watch Series 5',
        'description': 'Advanced smartwatch with health tracking, GPS, and customizable watch faces.',
        'price': 299.99,
        'image_url': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&h=400&fit=crop',
        'category': 'Electronics',
        'brand': 'TechWear',
        'stock_quantity': 0
    },
    {
        'name': 'Polarized Sunglasses',
        'description': 'UV protection sunglasses with polarized lenses and durable metal frame.',
        'price': 89.99,
        'compare_at_price': 129.99,
        'image_url': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&h=400&fit=crop',
        'category': 'Accessories',
        'brand': 'SunShield',
        'stock_quantity': 63
    }
]

def seed_products():
    app = create_app()
    
    with app.app_context():
        print("🌱 Seeding demo products...")
        
        # Check if products already exist
        existing_count = Product.query.count()
        print(f"📊 Current product count: {existing_count}")
        
        added_count = 0
        for idx, product_data in enumerate(demo_products, start=101):
            # Check if product with this name already exists
            existing = Product.query.filter_by(name=product_data['name']).first()
            if existing:
                print(f"⏭️  Skipping '{product_data['name']}' (already exists)")
                continue
            
            # Generate SKU
            category_prefix = product_data['category'][:3].upper()
            product_data['sku'] = f"{category_prefix}-DEMO-{idx:04d}"
            
            product = Product(**product_data)
            db.session.add(product)
            added_count += 1
            print(f"✅ Added: {product_data['name']} (SKU: {product_data['sku']})")
        
        db.session.commit()
        print(f"\n🎉 Successfully added {added_count} products!")
        print(f"📊 Total products in database: {Product.query.count()}")

if __name__ == '__main__':
    seed_products()
