import { useState, useEffect } from 'react'
import { UserProfile, ProductCard } from './components/ui'
import { Sidebar, TopBar } from './components/layout'
import { DashboardPageWithAuth } from './pages/DashboardPageWithAuth'
import { SupportTicketsPage } from './pages/SupportTicketsPage'
import { TaskFlowDashboard } from './pages/TaskFlowDashboard'
import { AnalyticsDashboard } from './components/analytics'
import { TeamDashboardWithContext } from './components/team-dashboard'
import { SocialFeed } from './components/social-feed'
import { useAuth } from './contexts/AuthContext'
import type { UserProfile as UserProfileType } from './types/user'
import type { Product } from './types/product'
import type { NavItem } from './types/navigation'

const navItems: NavItem[] = [
  { label: 'Home', href: '#home' },
  { label: 'E-Commerce Shop', href: '#shop' },
  { label: 'Products', href: '#products' },
  { label: 'Profiles', href: '#profiles' },
  { label: 'Task Flow', href: '#taskflow' },
  { label: 'Team', href: '#team' },
  { label: 'Analytics', href: '#analytics' },
  { label: 'Feed', href: '#feed' },
  { label: 'About', href: '#about' },
]

const currentUser = {
  name: 'John Doe',
  email: 'john@example.com',
  avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
}

const sampleUsers: UserProfileType[] = [
  {
    id: '1',
    username: 'johndoe',
    displayName: 'John Doe',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
    bio: 'Software developer passionate about building great user experiences. Open source enthusiast.',
    stats: { followers: 12500, following: 890, posts: 234 },
    isFollowing: false,
    isOwnProfile: true,
  },
  {
    id: '2',
    username: 'sarahdesigner',
    displayName: 'Sarah Chen',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face',
    bio: 'UI/UX Designer | Creating beautiful digital experiences | Coffee addict ☕',
    stats: { followers: 45200, following: 1200, posts: 567 },
    isFollowing: true,
    isOwnProfile: false,
  },
  {
    id: '3',
    username: 'mikephoto',
    displayName: 'Mike Anderson',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face',
    bio: 'Professional photographer capturing moments around the world 📸 | Travel enthusiast | Available for bookings',
    stats: { followers: 89300, following: 456, posts: 1823 },
    isFollowing: false,
    isOwnProfile: false,
  },
  {
    id: '4',
    username: 'emilywriter',
    displayName: 'Emily Rodriguez',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
    bio: 'Content creator & storyteller ✍️ | Published author | Sharing life lessons and creative inspiration',
    stats: { followers: 34700, following: 678, posts: 892 },
    isFollowing: true,
    isOwnProfile: false,
  },
  {
    id: '5',
    username: 'alexfitness',
    displayName: 'Alex Martinez',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
    bio: 'Certified personal trainer 💪 | Nutrition coach | Helping you achieve your fitness goals | DM for coaching',
    stats: { followers: 56800, following: 234, posts: 1456 },
    isFollowing: false,
    isOwnProfile: false,
  },
  {
    id: '6',
    username: 'lisachef',
    displayName: 'Lisa Thompson',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face',
    bio: 'Chef & food blogger 🍳 | Sharing easy recipes for busy people | Cookbook coming soon!',
    stats: { followers: 128000, following: 890, posts: 2341 },
    isFollowing: true,
    isOwnProfile: false,
  },
  {
    id: '7',
    username: 'davidtech',
    displayName: 'David Kim',
    avatar: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face',
    bio: 'Tech entrepreneur | AI & blockchain enthusiast | Building the future one startup at a time 🚀',
    stats: { followers: 67500, following: 1234, posts: 456 },
    isFollowing: false,
    isOwnProfile: false,
  },
  {
    id: '8',
    username: 'jessicaart',
    displayName: 'Jessica Williams',
    avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&h=150&fit=crop&crop=face',
    bio: 'Digital artist & illustrator 🎨 | Commission work available | Bringing imagination to life through art',
    stats: { followers: 92400, following: 567, posts: 1678 },
    isFollowing: true,
    isOwnProfile: false,
  },
]

const sampleProducts: Product[] = [
  {
    id: '1',
    title: 'Wireless Noise-Canceling Headphones',
    description: 'Premium over-ear headphones with active noise cancellation and 30-hour battery life.',
    price: 249.99,
    originalPrice: 349.99,
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
    rating: 4.5,
    reviewCount: 2847,
    inStock: true,
    category: 'Electronics',
  },
  {
    id: '2',
    title: 'Minimalist Leather Watch',
    description: 'Elegant timepiece with genuine leather strap and sapphire crystal glass.',
    price: 189.00,
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
    rating: 4.8,
    reviewCount: 1256,
    inStock: true,
    category: 'Accessories',
  },
  {
    id: '3',
    title: 'Smart Fitness Tracker',
    description: 'Track your health metrics, sleep patterns, and workouts with this advanced wearable.',
    price: 79.99,
    originalPrice: 129.99,
    image: 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400&h=400&fit=crop',
    rating: 4.2,
    reviewCount: 3421,
    inStock: true,
    category: 'Fitness',
  },
  {
    id: '4',
    title: 'Portable Bluetooth Speaker',
    description: 'Waterproof speaker with 360° sound and 20-hour playtime. Perfect for outdoor adventures.',
    price: 59.99,
    image: 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop',
    rating: 4.0,
    reviewCount: 892,
    inStock: false,
    category: 'Electronics',
  },
  {
    id: '5',
    title: 'Mechanical Gaming Keyboard',
    description: 'RGB backlit mechanical keyboard with customizable keys and ultra-responsive switches.',
    price: 129.99,
    originalPrice: 179.99,
    image: 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=400&fit=crop',
    rating: 4.7,
    reviewCount: 1543,
    inStock: true,
    category: 'Electronics',
  },
  {
    id: '6',
    title: 'Leather Laptop Bag',
    description: 'Professional leather messenger bag with padded laptop compartment and multiple pockets.',
    price: 149.00,
    image: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop',
    rating: 4.6,
    reviewCount: 876,
    inStock: true,
    category: 'Accessories',
  },
  {
    id: '7',
    title: 'Wireless Gaming Mouse',
    description: 'High-precision wireless mouse with customizable DPI and programmable buttons.',
    price: 79.99,
    image: 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=400&h=400&fit=crop',
    rating: 4.4,
    reviewCount: 2156,
    inStock: true,
    category: 'Electronics',
  },
  {
    id: '8',
    title: 'Stainless Steel Water Bottle',
    description: 'Insulated water bottle keeps drinks cold for 24 hours or hot for 12 hours.',
    price: 34.99,
    originalPrice: 49.99,
    image: 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop',
    rating: 4.9,
    reviewCount: 3287,
    inStock: true,
    category: 'Fitness',
  },
  {
    id: '9',
    title: 'Yoga Mat with Carrying Strap',
    description: 'Non-slip exercise mat with extra cushioning for comfort during workouts.',
    price: 39.99,
    image: 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&h=400&fit=crop',
    rating: 4.3,
    reviewCount: 1654,
    inStock: true,
    category: 'Fitness',
  },
  {
    id: '10',
    title: 'Wireless Earbuds Pro',
    description: 'True wireless earbuds with active noise cancellation and 8-hour battery life.',
    price: 199.99,
    originalPrice: 249.99,
    image: 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&h=400&fit=crop',
    rating: 4.6,
    reviewCount: 4521,
    inStock: true,
    category: 'Electronics',
  },
  {
    id: '11',
    title: 'Smart Watch Series 5',
    description: 'Advanced smartwatch with health tracking, GPS, and customizable watch faces.',
    price: 299.99,
    image: 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&h=400&fit=crop',
    rating: 4.8,
    reviewCount: 5632,
    inStock: false,
    category: 'Electronics',
  },
  {
    id: '12',
    title: 'Polarized Sunglasses',
    description: 'UV protection sunglasses with polarized lenses and durable metal frame.',
    price: 89.99,
    originalPrice: 129.99,
    image: 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&h=400&fit=crop',
    rating: 4.5,
    reviewCount: 987,
    inStock: true,
    category: 'Accessories',
  },
]

function App() {
  const { isAuthenticated, logout: authLogout } = useAuth()
  const [users, setUsers] = useState<UserProfileType[]>(sampleUsers)
  const [cartCount, setCartCount] = useState(0)
  const [isLoggedIn, setIsLoggedIn] = useState(true)
  const [showDashboard, setShowDashboard] = useState(false)
  const [showSupportTickets, setShowSupportTickets] = useState(false)
  const [showTaskFlow, setShowTaskFlow] = useState(false)
  const [showAnalytics, setShowAnalytics] = useState(false)
  const [showTeamDashboard, setShowTeamDashboard] = useState(false)
  const [showSocialFeed, setShowSocialFeed] = useState(false)
  const [analyticsDarkMode, setAnalyticsDarkMode] = useState(false)
  const [activeSection, setActiveSection] = useState('#home')
  const [isDarkMode, setIsDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('darkMode')
      if (saved !== null) {
        return saved === 'true'
      }
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return false
  })

  const handleFollow = (userId: string) => {
    setUsers((prev) =>
      prev.map((user) =>
        user.id === userId
          ? {
              ...user,
              isFollowing: !user.isFollowing,
              stats: {
                ...user.stats,
                followers: user.isFollowing
                  ? user.stats.followers - 1
                  : user.stats.followers + 1,
              },
            }
          : user
      )
    )
  }

  const handleMessage = (displayName: string) => {
    alert(`Opening chat with ${displayName}`)
  }

  const handleEditProfile = () => {
    alert('Opening profile editor')
  }

  const handleAddToCart = (product: Product) => {
    setCartCount((prev) => prev + 1)
    alert(`Added "${product.title}" to cart!`)
  }

  const handleSearch = (query: string) => {
    alert(`Searching for: ${query}`)
  }

  const handleLogout = () => {
    console.log('🔴 Main app logout clicked');
    authLogout();
    setIsLoggedIn(false);
  }

  const handleProfile = () => {
    alert('Opening profile...')
  }

  const handleSettings = () => {
    alert('Opening settings...')
  }

  const handleNavClick = (href: string) => {
    setActiveSection(href)
    if (href.startsWith('#')) {
      const element = document.getElementById(href.slice(1))
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    } else if (href.startsWith('/')) {
      // Handle route navigation
      window.location.href = href
    }
  }

  const handleToggleDarkMode = () => {
    setIsDarkMode(!isDarkMode)
  }

  // Apply dark mode to document and persist to localStorage
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('darkMode', String(isDarkMode))
  }, [isDarkMode])

  // Show Task Flow as full page
  if (showTaskFlow) {
    return <TaskFlowDashboard onBack={() => setShowTaskFlow(false)} />;
  }

  // Show Support Tickets as full page
  if (showSupportTickets) {
    return <SupportTicketsPage onBack={() => setShowSupportTickets(false)} />;
  }

  // Show Dashboard as full page
  if (showDashboard) {
    return (
      <div className="relative">
        {isAuthenticated && (
          <button
            onClick={() => setShowDashboard(false)}
            className="fixed top-20 right-4 z-50 px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 
                       rounded-lg shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Demo
          </button>
        )}
        <DashboardPageWithAuth />
      </div>
    );
  }

  // Show Analytics Dashboard as full page
  if (showAnalytics) {
    return (
      <div className="relative">
        <button
          onClick={() => setShowAnalytics(false)}
          className="fixed top-4 right-4 z-50 px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 
                     rounded-lg shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Demo
        </button>
        <AnalyticsDashboard 
          isDarkMode={analyticsDarkMode} 
          onToggleDarkMode={() => setAnalyticsDarkMode(!analyticsDarkMode)} 
        />
      </div>
    );
  }

  // Show Team Dashboard as full page
  if (showTeamDashboard) {
    return <TeamDashboardWithContext onBack={() => setShowTeamDashboard(false)} />;
  }

  // Show Social Feed as full page
  if (showSocialFeed) {
    return (
      <div className="relative">
        <button
          onClick={() => setShowSocialFeed(false)}
          className="fixed top-4 right-4 z-50 px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 
                     rounded-lg shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Demo
        </button>
        <SocialFeed />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-950 transition-colors duration-300">
      {/* Sidebar Navigation */}
      <Sidebar
        navItems={navItems}
        activeSection={activeSection}
        onNavClick={handleNavClick}
      />

      {/* Top Bar */}
      <TopBar
        onSearch={handleSearch}
        title="Component Showcase"
        user={isLoggedIn ? currentUser : null}
        cartCount={cartCount}
        onProfile={handleProfile}
        onSettings={handleSettings}
        onLogout={handleLogout}
        isDarkMode={isDarkMode}
        onToggleDarkMode={handleToggleDarkMode}
      />

      {/* Main Content - with padding for sidebar and top bar */}
      <div className="md:ml-64 pt-16 pb-12 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Home Section */}
          <section id="home" className="mb-20 pt-4">
            <header className="text-center mb-12">
              <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
                Welcome to ShopDemo
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                Explore our collection of premium products and connect with amazing people.
                Scroll down to see our components in action.
              </p>
            </header>

            {/* E-Commerce Shop Banner */}
            <div id="shop" className="scroll-mt-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-2xl p-8 mb-12 text-white">
              <div className="max-w-3xl mx-auto text-center">
                <div className="inline-block bg-white/20 backdrop-blur-sm px-4 py-1 rounded-full text-sm font-medium mb-4">
                  🎉 NEW FEATURE
                </div>
                <h2 className="text-4xl font-bold mb-4">
                  Full E-Commerce Shop Now Live!
                </h2>
                <p className="text-xl mb-6 text-blue-100">
                  Browse products, add to cart, apply discounts, and complete checkout with our fully integrated shopping experience.
                </p>
                <div className="flex flex-wrap gap-4 justify-center">
                  <a
                    href="/shop"
                    className="px-8 py-4 bg-white text-blue-600 font-bold rounded-xl hover:bg-blue-50 transition-all transform hover:scale-105 shadow-lg"
                  >
                    🛍️ Start Shopping
                  </a>
                  <a
                    href="/orders"
                    className="px-8 py-4 bg-blue-500/30 backdrop-blur-sm text-white font-bold rounded-xl hover:bg-blue-500/40 transition-all border-2 border-white/30"
                  >
                    📦 View Orders
                  </a>
                </div>
                <div className="mt-6 flex flex-wrap gap-6 justify-center text-sm">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Shopping Cart</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Discount Codes</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Order Tracking</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Product Cards Section */}
          <section id="products" className="mb-20 pt-4">
            <header className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                Product Card Component
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                E-commerce product cards with ratings, prices, and hover effects
              </p>
            </header>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {sampleProducts.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onAddToCart={handleAddToCart}
                />
              ))}
            </div>
          </section>

          {/* User Profiles Section */}
          <section id="profiles" className="mb-20 pt-4">
            <header className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                User Profile Component
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Social media user profiles with various states
              </p>
            </header>

            <div className="flex flex-col gap-6 max-w-4xl mx-auto">
              {users.map((user) => (
                <div key={user.id} className="flex flex-col">
                  <span className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 px-1">
                    {user.isOwnProfile
                      ? '👤 Own Profile'
                      : user.isFollowing
                      ? '✓ Following'
                      : '○ Not Following'}
                  </span>
                  <UserProfile
                    user={user}
                    onFollow={() => handleFollow(user.id)}
                    onMessage={() => handleMessage(user.displayName)}
                    onEditProfile={handleEditProfile}
                  />
                </div>
              ))}
            </div>
          </section>

          {/* Task Flow Section - FEATURED */}
          <section id="taskflow" className="mb-20 pt-4">
            <header className="text-center mb-12">
              <div className="inline-block px-4 py-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-semibold rounded-full mb-4">
                ⭐ FEATURED
              </div>
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                Task Flow Dashboard
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Unified dashboard with Task Management, Support Tickets, and Validation Tests
              </p>
            </header>

            <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl shadow-lg p-8 mb-6 border-2 border-blue-200 dark:border-blue-800">
              <div className="grid md:grid-cols-3 gap-6 mb-6">
                <div className="text-center">
                  <div className="text-3xl mb-2">📋</div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Task Management</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">CRUD operations, statistics, status tracking</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl mb-2">🎫</div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Support Tickets</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Full ticket system with SLA tracking</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl mb-2">✅</div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Validation Tests</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Interactive validation testing suite</p>
                </div>
              </div>
              <div className="flex justify-center">
                <button
                  onClick={() => setShowTaskFlow(true)}
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold text-lg rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
                >
                  Open Task Flow Dashboard →
                </button>
              </div>
            </div>
          </section>

          {/* Team Dashboard Section */}
          <section id="team" className="mb-20 pt-4">
            <header className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                Team Collaboration Dashboard
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Project overview, team members, progress charts, and activity feed
              </p>
            </header>

            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-6">
              <p className="text-center text-gray-600 dark:text-gray-300 mb-4">
                Click the button below to view the team collaboration dashboard
              </p>
              <div className="flex justify-center">
                <button
                  onClick={() => setShowTeamDashboard(true)}
                  className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Open Team Dashboard
                </button>
              </div>
            </div>
          </section>

          {/* Analytics Section */}
          <section id="analytics" className="mb-20 pt-4">
            <header className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                Analytics Dashboard
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Data analytics with KPIs, charts, tables, and filters
              </p>
            </header>

            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-6">
              <p className="text-center text-gray-600 dark:text-gray-300 mb-4">
                Click the button below to view the analytics dashboard
              </p>
              <div className="flex justify-center">
                <button
                  onClick={() => setShowAnalytics(true)}
                  className="px-6 py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors"
                >
                  Open Analytics
                </button>
              </div>
            </div>
          </section>

          {/* Social Feed Section */}
          <section id="feed" className="mb-20 pt-4">
            <header className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                Social Media Feed
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Posts, comments, likes, shares, and infinite scroll
              </p>
            </header>

            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-6">
              <p className="text-center text-gray-600 dark:text-gray-300 mb-4">
                Click the button below to view the social feed
              </p>
              <div className="flex justify-center">
                <button
                  onClick={() => setShowSocialFeed(true)}
                  className="px-6 py-3 bg-pink-600 text-white font-medium rounded-lg hover:bg-pink-700 transition-colors"
                >
                  Open Social Feed
                </button>
              </div>
            </div>
          </section>

          {/* About Section */}
          <section id="about" className="pt-4">
            <header className="text-center mb-8">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                About This Demo
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                A showcase of React components built with TypeScript and Tailwind CSS
              </p>
            </header>

            <div className="max-w-2xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <p>
                  This demo showcases several reusable React components including:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong className="text-gray-900 dark:text-white">NavBar</strong> - Responsive navigation with search, user dropdown, and mobile menu</li>
                  <li><strong className="text-gray-900 dark:text-white">ProductCard</strong> - E-commerce cards with ratings, prices, and animations</li>
                  <li><strong className="text-gray-900 dark:text-white">UserProfile</strong> - Social media profile cards with follow/message actions</li>
                  <li><strong className="text-gray-900 dark:text-white">Dashboard</strong> - Task management with sidebar, statistics, and dark mode</li>
                  <li><strong className="text-gray-900 dark:text-white">Team Dashboard</strong> - Project overview, team avatars, progress charts, activity feed</li>
                  <li><strong className="text-gray-900 dark:text-white">Analytics</strong> - Data dashboard with KPIs, charts, tables, and filters</li>
                  <li><strong className="text-gray-900 dark:text-white">Social Feed</strong> - Posts, comments, likes, shares, and infinite scroll</li>
                </ul>
                <p className="pt-4">
                  Built with React, TypeScript, Vite, and Tailwind CSS v4.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default App
