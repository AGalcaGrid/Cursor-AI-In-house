-- Add demo products from main page to E-Commerce shop
-- These products will be available in the /shop page

INSERT INTO products (name, description, price, compare_at_price, image_url, category, brand, in_stock, stock_quantity) VALUES
('Wireless Noise-Canceling Headphones', 'Premium over-ear headphones with active noise cancellation and 30-hour battery life.', 249.99, 349.99, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop', 'Electronics', 'AudioTech', true, 45),
('Minimalist Leather Watch', 'Elegant timepiece with genuine leather strap and sapphire crystal glass.', 189.00, NULL, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop', 'Accessories', 'TimeStyle', true, 32),
('Smart Fitness Tracker', 'Track your health metrics, sleep patterns, and workouts with this advanced wearable.', 79.99, 129.99, 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400&h=400&fit=crop', 'Fitness', 'FitPro', true, 67),
('Portable Bluetooth Speaker', 'Waterproof speaker with 360° sound and 20-hour playtime. Perfect for outdoor adventures.', 59.99, NULL, 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop', 'Electronics', 'SoundWave', false, 0),
('Mechanical Gaming Keyboard', 'RGB backlit mechanical keyboard with customizable keys and ultra-responsive switches.', 129.99, 179.99, 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=400&fit=crop', 'Electronics', 'GameGear', true, 28),
('Leather Laptop Bag', 'Professional leather messenger bag with padded laptop compartment and multiple pockets.', 149.00, NULL, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop', 'Accessories', 'UrbanCarry', true, 19),
('Wireless Gaming Mouse', 'High-precision wireless mouse with customizable DPI and programmable buttons.', 79.99, NULL, 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=400&h=400&fit=crop', 'Electronics', 'GameGear', true, 54),
('Stainless Steel Water Bottle', 'Insulated water bottle keeps drinks cold for 24 hours or hot for 12 hours.', 34.99, 49.99, 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop', 'Fitness', 'HydroLife', true, 89),
('Yoga Mat with Carrying Strap', 'Non-slip exercise mat with extra cushioning for comfort during workouts.', 39.99, NULL, 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&h=400&fit=crop', 'Fitness', 'YogaEssentials', true, 76),
('Wireless Earbuds Pro', 'True wireless earbuds with active noise cancellation and 8-hour battery life.', 199.99, 249.99, 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&h=400&fit=crop', 'Electronics', 'AudioTech', true, 41),
('Smart Watch Series 5', 'Advanced smartwatch with health tracking, GPS, and customizable watch faces.', 299.99, NULL, 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&h=400&fit=crop', 'Electronics', 'TechWear', false, 0),
('Polarized Sunglasses', 'UV protection sunglasses with polarized lenses and durable metal frame.', 89.99, 129.99, 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&h=400&fit=crop', 'Accessories', 'SunShield', true, 63)
ON CONFLICT DO NOTHING;
