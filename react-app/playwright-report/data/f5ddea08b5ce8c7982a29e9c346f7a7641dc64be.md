# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tasks.spec.ts >> Task Management >> should show delete confirmation
- Location: e2e/tests/tasks.spec.ts:64:3

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: /open dashboard/i })

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - navigation "Main navigation" [ref=e4]:
    - link "Demo App" [ref=e6] [cursor=pointer]:
      - /url: /
      - img [ref=e7]
      - generic [ref=e9]: Demo App
    - navigation [ref=e10]:
      - link "Home" [ref=e11] [cursor=pointer]:
        - /url: "#home"
        - generic [ref=e12]: Home
      - link "Products" [ref=e14] [cursor=pointer]:
        - /url: "#products"
        - generic [ref=e15]: Products
      - link "Profiles" [ref=e16] [cursor=pointer]:
        - /url: "#profiles"
        - generic [ref=e17]: Profiles
      - link "Task Flow" [ref=e18] [cursor=pointer]:
        - /url: "#taskflow"
        - generic [ref=e19]: Task Flow
      - link "Team" [ref=e20] [cursor=pointer]:
        - /url: "#team"
        - generic [ref=e21]: Team
      - link "Analytics" [ref=e22] [cursor=pointer]:
        - /url: "#analytics"
        - generic [ref=e23]: Analytics
      - link "Feed" [ref=e24] [cursor=pointer]:
        - /url: "#feed"
        - generic [ref=e25]: Feed
      - link "About" [ref=e26] [cursor=pointer]:
        - /url: "#about"
        - generic [ref=e27]: About
  - banner [ref=e28]:
    - generic [ref=e29]:
      - heading "Component Showcase" [level=1] [ref=e30]
      - generic [ref=e33]:
        - img [ref=e34]
        - searchbox "Search" [ref=e37]
      - generic [ref=e38]:
        - button "Switch to dark mode" [ref=e39]:
          - img [ref=e40]
        - button "Notifications" [ref=e42]:
          - img [ref=e43]
        - button "John Doe John Doe" [ref=e48]:
          - img "John Doe" [ref=e49]
          - paragraph [ref=e51]: John Doe
          - img [ref=e52]
  - generic [ref=e55]:
    - generic [ref=e57]:
      - heading "Welcome to ShopDemo" [level=1] [ref=e58]
      - paragraph [ref=e59]: Explore our collection of premium products and connect with amazing people. Scroll down to see our components in action.
    - generic [ref=e60]:
      - generic [ref=e61]:
        - heading "Product Card Component" [level=2] [ref=e62]
        - paragraph [ref=e63]: E-commerce product cards with ratings, prices, and hover effects
      - generic [ref=e64]:
        - 'article "Product: Wireless Noise-Canceling Headphones" [ref=e65]':
          - generic "29% discount" [ref=e66]: "-29%"
          - img "Wireless Noise-Canceling Headphones" [ref=e68]
          - generic [ref=e69]:
            - generic [ref=e70]: Electronics
            - heading "Wireless Noise-Canceling Headphones" [level=3] [ref=e71]
            - paragraph [ref=e72]: Premium over-ear headphones with active noise cancellation and 30-hour battery life.
            - 'img "Rating: 4.5 out of 5 stars" [ref=e74]':
              - generic [ref=e75]:
                - img [ref=e76]
                - img [ref=e78]
                - img [ref=e80]
                - img [ref=e82]
                - img [ref=e84]
              - generic [ref=e86]: (2847)
            - generic [ref=e87]:
              - generic [ref=e88]: $249.99
              - generic [ref=e89]: $349.99
            - button "Add Wireless Noise-Canceling Headphones to cart" [ref=e90]:
              - generic [ref=e91]:
                - img [ref=e92]
                - text: Add to Cart
        - 'article "Product: Minimalist Leather Watch" [ref=e94]':
          - img "Minimalist Leather Watch" [ref=e96]
          - generic [ref=e97]:
            - generic [ref=e98]: Accessories
            - heading "Minimalist Leather Watch" [level=3] [ref=e99]
            - paragraph [ref=e100]: Elegant timepiece with genuine leather strap and sapphire crystal glass.
            - 'img "Rating: 4.8 out of 5 stars" [ref=e102]':
              - generic [ref=e103]:
                - img [ref=e104]
                - img [ref=e106]
                - img [ref=e108]
                - img [ref=e110]
                - img [ref=e112]
              - generic [ref=e114]: (1256)
            - generic [ref=e116]: $189.00
            - button "Add Minimalist Leather Watch to cart" [ref=e117]:
              - generic [ref=e118]:
                - img [ref=e119]
                - text: Add to Cart
        - 'article "Product: Smart Fitness Tracker" [ref=e121]':
          - generic "38% discount" [ref=e122]: "-38%"
          - img "Smart Fitness Tracker" [ref=e124]
          - generic [ref=e125]:
            - generic [ref=e126]: Fitness
            - heading "Smart Fitness Tracker" [level=3] [ref=e127]
            - paragraph [ref=e128]: Track your health metrics, sleep patterns, and workouts with this advanced wearable.
            - 'img "Rating: 4.2 out of 5 stars" [ref=e130]':
              - generic [ref=e131]:
                - img [ref=e132]
                - img [ref=e134]
                - img [ref=e136]
                - img [ref=e138]
                - img [ref=e140]
              - generic [ref=e142]: (3421)
            - generic [ref=e143]:
              - generic [ref=e144]: $79.99
              - generic [ref=e145]: $129.99
            - button "Add Smart Fitness Tracker to cart" [ref=e146]:
              - generic [ref=e147]:
                - img [ref=e148]
                - text: Add to Cart
        - 'article "Product: Portable Bluetooth Speaker" [ref=e150]':
          - generic [ref=e152]: Out of Stock
          - img "Portable Bluetooth Speaker" [ref=e154]
          - generic [ref=e155]:
            - generic [ref=e156]: Electronics
            - heading "Portable Bluetooth Speaker" [level=3] [ref=e157]
            - paragraph [ref=e158]: Waterproof speaker with 360° sound and 20-hour playtime. Perfect for outdoor adventures.
            - 'img "Rating: 4 out of 5 stars" [ref=e160]':
              - generic [ref=e161]:
                - img [ref=e162]
                - img [ref=e164]
                - img [ref=e166]
                - img [ref=e168]
                - img [ref=e170]
              - generic [ref=e172]: (892)
            - generic [ref=e174]: $59.99
            - button "Add Portable Bluetooth Speaker to cart" [disabled] [ref=e175]:
              - generic [ref=e176]:
                - img [ref=e177]
                - text: Add to Cart
        - 'article "Product: Mechanical Gaming Keyboard" [ref=e179]':
          - generic "28% discount" [ref=e180]: "-28%"
          - img "Mechanical Gaming Keyboard" [ref=e182]
          - generic [ref=e183]:
            - generic [ref=e184]: Electronics
            - heading "Mechanical Gaming Keyboard" [level=3] [ref=e185]
            - paragraph [ref=e186]: RGB backlit mechanical keyboard with customizable keys and ultra-responsive switches.
            - 'img "Rating: 4.7 out of 5 stars" [ref=e188]':
              - generic [ref=e189]:
                - img [ref=e190]
                - img [ref=e192]
                - img [ref=e194]
                - img [ref=e196]
                - img [ref=e198]
              - generic [ref=e200]: (1543)
            - generic [ref=e201]:
              - generic [ref=e202]: $129.99
              - generic [ref=e203]: $179.99
            - button "Add Mechanical Gaming Keyboard to cart" [ref=e204]:
              - generic [ref=e205]:
                - img [ref=e206]
                - text: Add to Cart
        - 'article "Product: Leather Laptop Bag" [ref=e208]':
          - img "Leather Laptop Bag" [ref=e210]
          - generic [ref=e211]:
            - generic [ref=e212]: Accessories
            - heading "Leather Laptop Bag" [level=3] [ref=e213]
            - paragraph [ref=e214]: Professional leather messenger bag with padded laptop compartment and multiple pockets.
            - 'img "Rating: 4.6 out of 5 stars" [ref=e216]':
              - generic [ref=e217]:
                - img [ref=e218]
                - img [ref=e220]
                - img [ref=e222]
                - img [ref=e224]
                - img [ref=e226]
              - generic [ref=e228]: (876)
            - generic [ref=e230]: $149.00
            - button "Add Leather Laptop Bag to cart" [ref=e231]:
              - generic [ref=e232]:
                - img [ref=e233]
                - text: Add to Cart
        - 'article "Product: Wireless Gaming Mouse" [ref=e235]':
          - img "Wireless Gaming Mouse" [ref=e237]
          - generic [ref=e238]:
            - generic [ref=e239]: Electronics
            - heading "Wireless Gaming Mouse" [level=3] [ref=e240]
            - paragraph [ref=e241]: High-precision wireless mouse with customizable DPI and programmable buttons.
            - 'img "Rating: 4.4 out of 5 stars" [ref=e243]':
              - generic [ref=e244]:
                - img [ref=e245]
                - img [ref=e247]
                - img [ref=e249]
                - img [ref=e251]
                - img [ref=e253]
              - generic [ref=e255]: (2156)
            - generic [ref=e257]: $79.99
            - button "Add Wireless Gaming Mouse to cart" [ref=e258]:
              - generic [ref=e259]:
                - img [ref=e260]
                - text: Add to Cart
        - 'article "Product: Stainless Steel Water Bottle" [ref=e262]':
          - generic "30% discount" [ref=e263]: "-30%"
          - img "Stainless Steel Water Bottle" [ref=e265]
          - generic [ref=e266]:
            - generic [ref=e267]: Fitness
            - heading "Stainless Steel Water Bottle" [level=3] [ref=e268]
            - paragraph [ref=e269]: Insulated water bottle keeps drinks cold for 24 hours or hot for 12 hours.
            - 'img "Rating: 4.9 out of 5 stars" [ref=e271]':
              - generic [ref=e272]:
                - img [ref=e273]
                - img [ref=e275]
                - img [ref=e277]
                - img [ref=e279]
                - img [ref=e281]
              - generic [ref=e283]: (3287)
            - generic [ref=e284]:
              - generic [ref=e285]: $34.99
              - generic [ref=e286]: $49.99
            - button "Add Stainless Steel Water Bottle to cart" [ref=e287]:
              - generic [ref=e288]:
                - img [ref=e289]
                - text: Add to Cart
        - 'article "Product: Yoga Mat with Carrying Strap" [ref=e291]':
          - img "Yoga Mat with Carrying Strap" [ref=e293]
          - generic [ref=e294]:
            - generic [ref=e295]: Fitness
            - heading "Yoga Mat with Carrying Strap" [level=3] [ref=e296]
            - paragraph [ref=e297]: Non-slip exercise mat with extra cushioning for comfort during workouts.
            - 'img "Rating: 4.3 out of 5 stars" [ref=e299]':
              - generic [ref=e300]:
                - img [ref=e301]
                - img [ref=e303]
                - img [ref=e305]
                - img [ref=e307]
                - img [ref=e309]
              - generic [ref=e311]: (1654)
            - generic [ref=e313]: $39.99
            - button "Add Yoga Mat with Carrying Strap to cart" [ref=e314]:
              - generic [ref=e315]:
                - img [ref=e316]
                - text: Add to Cart
        - 'article "Product: Wireless Earbuds Pro" [ref=e318]':
          - generic "20% discount" [ref=e319]: "-20%"
          - img "Wireless Earbuds Pro" [ref=e321]
          - generic [ref=e322]:
            - generic [ref=e323]: Electronics
            - heading "Wireless Earbuds Pro" [level=3] [ref=e324]
            - paragraph [ref=e325]: True wireless earbuds with active noise cancellation and 8-hour battery life.
            - 'img "Rating: 4.6 out of 5 stars" [ref=e327]':
              - generic [ref=e328]:
                - img [ref=e329]
                - img [ref=e331]
                - img [ref=e333]
                - img [ref=e335]
                - img [ref=e337]
              - generic [ref=e339]: (4521)
            - generic [ref=e340]:
              - generic [ref=e341]: $199.99
              - generic [ref=e342]: $249.99
            - button "Add Wireless Earbuds Pro to cart" [ref=e343]:
              - generic [ref=e344]:
                - img [ref=e345]
                - text: Add to Cart
        - 'article "Product: Smart Watch Series 5" [ref=e347]':
          - generic [ref=e349]: Out of Stock
          - img "Smart Watch Series 5" [ref=e351]
          - generic [ref=e352]:
            - generic [ref=e353]: Electronics
            - heading "Smart Watch Series 5" [level=3] [ref=e354]
            - paragraph [ref=e355]: Advanced smartwatch with health tracking, GPS, and customizable watch faces.
            - 'img "Rating: 4.8 out of 5 stars" [ref=e357]':
              - generic [ref=e358]:
                - img [ref=e359]
                - img [ref=e361]
                - img [ref=e363]
                - img [ref=e365]
                - img [ref=e367]
              - generic [ref=e369]: (5632)
            - generic [ref=e371]: $299.99
            - button "Add Smart Watch Series 5 to cart" [disabled] [ref=e372]:
              - generic [ref=e373]:
                - img [ref=e374]
                - text: Add to Cart
        - 'article "Product: Polarized Sunglasses" [ref=e376]':
          - generic "31% discount" [ref=e377]: "-31%"
          - img "Polarized Sunglasses" [ref=e379]
          - generic [ref=e380]:
            - generic [ref=e381]: Accessories
            - heading "Polarized Sunglasses" [level=3] [ref=e382]
            - paragraph [ref=e383]: UV protection sunglasses with polarized lenses and durable metal frame.
            - 'img "Rating: 4.5 out of 5 stars" [ref=e385]':
              - generic [ref=e386]:
                - img [ref=e387]
                - img [ref=e389]
                - img [ref=e391]
                - img [ref=e393]
                - img [ref=e395]
              - generic [ref=e397]: (987)
            - generic [ref=e398]:
              - generic [ref=e399]: $89.99
              - generic [ref=e400]: $129.99
            - button "Add Polarized Sunglasses to cart" [ref=e401]:
              - generic [ref=e402]:
                - img [ref=e403]
                - text: Add to Cart
    - generic [ref=e405]:
      - generic [ref=e406]:
        - heading "User Profile Component" [level=2] [ref=e407]
        - paragraph [ref=e408]: Social media user profiles with various states
      - generic [ref=e409]:
        - generic [ref=e410]:
          - generic [ref=e411]: 👤 Own Profile
          - article "Profile of John Doe" [ref=e412]:
            - generic [ref=e414]:
              - generic [ref=e415]:
                - img "John Doe's avatar" [ref=e416]
                - generic [ref=e417]: Your profile
              - generic [ref=e418]:
                - heading "John Doe" [level=1] [ref=e419]
                - paragraph [ref=e420]: "@johndoe"
              - paragraph [ref=e421]: Software developer passionate about building great user experiences. Open source enthusiast.
              - list "Profile statistics" [ref=e422]:
                - listitem [ref=e423]:
                  - generic [ref=e424]: "234"
                  - text: Posts
                - listitem [ref=e425]:
                  - generic [ref=e426]: 12.5K
                  - text: Followers
                - listitem [ref=e427]:
                  - generic [ref=e428]: "890"
                  - text: Following
              - button "Edit your profile" [ref=e430]: Edit Profile
        - generic [ref=e431]:
          - generic [ref=e432]: ✓ Following
          - article "Profile of Sarah Chen" [ref=e433]:
            - generic [ref=e435]:
              - img "Sarah Chen's avatar" [ref=e437]
              - generic [ref=e438]:
                - heading "Sarah Chen" [level=1] [ref=e439]
                - paragraph [ref=e440]: "@sarahdesigner"
              - paragraph [ref=e441]: UI/UX Designer | Creating beautiful digital experiences | Coffee addict ☕
              - list "Profile statistics" [ref=e442]:
                - listitem [ref=e443]:
                  - generic [ref=e444]: "567"
                  - text: Posts
                - listitem [ref=e445]:
                  - generic [ref=e446]: 45.2K
                  - text: Followers
                - listitem [ref=e447]:
                  - generic [ref=e448]: 1.2K
                  - text: Following
              - generic [ref=e449]:
                - button "Unfollow Sarah Chen" [pressed] [ref=e450]: Following
                - button "Send message to Sarah Chen" [ref=e451]: Message
        - generic [ref=e452]:
          - generic [ref=e453]: ○ Not Following
          - article "Profile of Mike Anderson" [ref=e454]:
            - generic [ref=e456]:
              - img "Mike Anderson's avatar" [ref=e458]
              - generic [ref=e459]:
                - heading "Mike Anderson" [level=1] [ref=e460]
                - paragraph [ref=e461]: "@mikephoto"
              - paragraph [ref=e462]: Professional photographer capturing moments around the world 📸 | Travel enthusiast | Available for bookings
              - list "Profile statistics" [ref=e463]:
                - listitem [ref=e464]:
                  - generic [ref=e465]: 1.8K
                  - text: Posts
                - listitem [ref=e466]:
                  - generic [ref=e467]: 89.3K
                  - text: Followers
                - listitem [ref=e468]:
                  - generic [ref=e469]: "456"
                  - text: Following
              - generic [ref=e470]:
                - button "Follow Mike Anderson" [ref=e471]: Follow
                - button "Send message to Mike Anderson" [ref=e472]: Message
        - generic [ref=e473]:
          - generic [ref=e474]: ✓ Following
          - article "Profile of Emily Rodriguez" [ref=e475]:
            - generic [ref=e477]:
              - img "Emily Rodriguez's avatar" [ref=e479]
              - generic [ref=e480]:
                - heading "Emily Rodriguez" [level=1] [ref=e481]
                - paragraph [ref=e482]: "@emilywriter"
              - paragraph [ref=e483]: Content creator & storyteller ✍️ | Published author | Sharing life lessons and creative inspiration
              - list "Profile statistics" [ref=e484]:
                - listitem [ref=e485]:
                  - generic [ref=e486]: "892"
                  - text: Posts
                - listitem [ref=e487]:
                  - generic [ref=e488]: 34.7K
                  - text: Followers
                - listitem [ref=e489]:
                  - generic [ref=e490]: "678"
                  - text: Following
              - generic [ref=e491]:
                - button "Unfollow Emily Rodriguez" [pressed] [ref=e492]: Following
                - button "Send message to Emily Rodriguez" [ref=e493]: Message
        - generic [ref=e494]:
          - generic [ref=e495]: ○ Not Following
          - article "Profile of Alex Martinez" [ref=e496]:
            - generic [ref=e498]:
              - img "Alex Martinez's avatar" [ref=e500]
              - generic [ref=e501]:
                - heading "Alex Martinez" [level=1] [ref=e502]
                - paragraph [ref=e503]: "@alexfitness"
              - paragraph [ref=e504]: Certified personal trainer 💪 | Nutrition coach | Helping you achieve your fitness goals | DM for coaching
              - list "Profile statistics" [ref=e505]:
                - listitem [ref=e506]:
                  - generic [ref=e507]: 1.5K
                  - text: Posts
                - listitem [ref=e508]:
                  - generic [ref=e509]: 56.8K
                  - text: Followers
                - listitem [ref=e510]:
                  - generic [ref=e511]: "234"
                  - text: Following
              - generic [ref=e512]:
                - button "Follow Alex Martinez" [ref=e513]: Follow
                - button "Send message to Alex Martinez" [ref=e514]: Message
        - generic [ref=e515]:
          - generic [ref=e516]: ✓ Following
          - article "Profile of Lisa Thompson" [ref=e517]:
            - generic [ref=e519]:
              - img "Lisa Thompson's avatar" [ref=e521]
              - generic [ref=e522]:
                - heading "Lisa Thompson" [level=1] [ref=e523]
                - paragraph [ref=e524]: "@lisachef"
              - paragraph [ref=e525]: Chef & food blogger 🍳 | Sharing easy recipes for busy people | Cookbook coming soon!
              - list "Profile statistics" [ref=e526]:
                - listitem [ref=e527]:
                  - generic [ref=e528]: 2.3K
                  - text: Posts
                - listitem [ref=e529]:
                  - generic [ref=e530]: 128K
                  - text: Followers
                - listitem [ref=e531]:
                  - generic [ref=e532]: "890"
                  - text: Following
              - generic [ref=e533]:
                - button "Unfollow Lisa Thompson" [pressed] [ref=e534]: Following
                - button "Send message to Lisa Thompson" [ref=e535]: Message
        - generic [ref=e536]:
          - generic [ref=e537]: ○ Not Following
          - article "Profile of David Kim" [ref=e538]:
            - generic [ref=e540]:
              - img "David Kim's avatar" [ref=e542]
              - generic [ref=e543]:
                - heading "David Kim" [level=1] [ref=e544]
                - paragraph [ref=e545]: "@davidtech"
              - paragraph [ref=e546]: Tech entrepreneur | AI & blockchain enthusiast | Building the future one startup at a time 🚀
              - list "Profile statistics" [ref=e547]:
                - listitem [ref=e548]:
                  - generic [ref=e549]: "456"
                  - text: Posts
                - listitem [ref=e550]:
                  - generic [ref=e551]: 67.5K
                  - text: Followers
                - listitem [ref=e552]:
                  - generic [ref=e553]: 1.2K
                  - text: Following
              - generic [ref=e554]:
                - button "Follow David Kim" [ref=e555]: Follow
                - button "Send message to David Kim" [ref=e556]: Message
        - generic [ref=e557]:
          - generic [ref=e558]: ✓ Following
          - article "Profile of Jessica Williams" [ref=e559]:
            - generic [ref=e561]:
              - img "Jessica Williams's avatar" [ref=e563]
              - generic [ref=e564]:
                - heading "Jessica Williams" [level=1] [ref=e565]
                - paragraph [ref=e566]: "@jessicaart"
              - paragraph [ref=e567]: Digital artist & illustrator 🎨 | Commission work available | Bringing imagination to life through art
              - list "Profile statistics" [ref=e568]:
                - listitem [ref=e569]:
                  - generic [ref=e570]: 1.7K
                  - text: Posts
                - listitem [ref=e571]:
                  - generic [ref=e572]: 92.4K
                  - text: Followers
                - listitem [ref=e573]:
                  - generic [ref=e574]: "567"
                  - text: Following
              - generic [ref=e575]:
                - button "Unfollow Jessica Williams" [pressed] [ref=e576]: Following
                - button "Send message to Jessica Williams" [ref=e577]: Message
    - generic [ref=e578]:
      - generic [ref=e579]:
        - generic [ref=e580]: ⭐ FEATURED
        - heading "Task Flow Dashboard" [level=2] [ref=e581]
        - paragraph [ref=e582]: Unified dashboard with Task Management, Support Tickets, and Validation Tests
      - generic [ref=e583]:
        - generic [ref=e584]:
          - generic [ref=e585]:
            - generic [ref=e586]: 📋
            - heading "Task Management" [level=3] [ref=e587]
            - paragraph [ref=e588]: CRUD operations, statistics, status tracking
          - generic [ref=e589]:
            - generic [ref=e590]: 🎫
            - heading "Support Tickets" [level=3] [ref=e591]
            - paragraph [ref=e592]: Full ticket system with SLA tracking
          - generic [ref=e593]:
            - generic [ref=e594]: ✅
            - heading "Validation Tests" [level=3] [ref=e595]
            - paragraph [ref=e596]: Interactive validation testing suite
        - button "Open Task Flow Dashboard →" [ref=e598]
    - generic [ref=e599]:
      - generic [ref=e600]:
        - heading "Team Collaboration Dashboard" [level=2] [ref=e601]
        - paragraph [ref=e602]: Project overview, team members, progress charts, and activity feed
      - generic [ref=e603]:
        - paragraph [ref=e604]: Click the button below to view the team collaboration dashboard
        - button "Open Team Dashboard" [ref=e606]
    - generic [ref=e607]:
      - generic [ref=e608]:
        - heading "Analytics Dashboard" [level=2] [ref=e609]
        - paragraph [ref=e610]: Data analytics with KPIs, charts, tables, and filters
      - generic [ref=e611]:
        - paragraph [ref=e612]: Click the button below to view the analytics dashboard
        - button "Open Analytics" [ref=e614]
    - generic [ref=e615]:
      - generic [ref=e616]:
        - heading "Social Media Feed" [level=2] [ref=e617]
        - paragraph [ref=e618]: Posts, comments, likes, shares, and infinite scroll
      - generic [ref=e619]:
        - paragraph [ref=e620]: Click the button below to view the social feed
        - button "Open Social Feed" [ref=e622]
    - generic [ref=e623]:
      - generic [ref=e624]:
        - heading "About This Demo" [level=2] [ref=e625]
        - paragraph [ref=e626]: A showcase of React components built with TypeScript and Tailwind CSS
      - generic [ref=e628]:
        - paragraph [ref=e629]: "This demo showcases several reusable React components including:"
        - list [ref=e630]:
          - listitem [ref=e631]:
            - strong [ref=e632]: NavBar
            - text: "- Responsive navigation with search, user dropdown, and mobile menu"
          - listitem [ref=e633]:
            - strong [ref=e634]: ProductCard
            - text: "- E-commerce cards with ratings, prices, and animations"
          - listitem [ref=e635]:
            - strong [ref=e636]: UserProfile
            - text: "- Social media profile cards with follow/message actions"
          - listitem [ref=e637]:
            - strong [ref=e638]: Dashboard
            - text: "- Task management with sidebar, statistics, and dark mode"
          - listitem [ref=e639]:
            - strong [ref=e640]: Team Dashboard
            - text: "- Project overview, team avatars, progress charts, activity feed"
          - listitem [ref=e641]:
            - strong [ref=e642]: Analytics
            - text: "- Data dashboard with KPIs, charts, tables, and filters"
          - listitem [ref=e643]:
            - strong [ref=e644]: Social Feed
            - text: "- Posts, comments, likes, shares, and infinite scroll"
        - paragraph [ref=e645]: Built with React, TypeScript, Vite, and Tailwind CSS v4.
```

# Test source

```ts
  1  | import { test, expect } from '../fixtures/auth.fixture';
  2  | 
  3  | test.describe('Task Management', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('/');
> 6  |     await page.getByRole('button', { name: /open dashboard/i }).click();
     |                                                                 ^ Error: locator.click: Test timeout of 30000ms exceeded.
  7  |     await page.waitForTimeout(500);
  8  |   });
  9  | 
  10 |   // Test 1: Display existing tasks
  11 |   test('should display existing tasks', async ({ page }) => {
  12 |     const taskCards = page.locator('article');
  13 |     const count = await taskCards.count();
  14 |     expect(count).toBeGreaterThan(0);
  15 |   });
  16 | 
  17 |   // Test 2: Show task details
  18 |   test('should show task title and details', async ({ page }) => {
  19 |     const firstTask = page.locator('article').first();
  20 |     await expect(firstTask).toBeVisible();
  21 |     const taskText = await firstTask.textContent();
  22 |     expect(taskText).toBeTruthy();
  23 |   });
  24 | 
  25 |   // Test 3: Filter tasks by status
  26 |   test('should filter tasks by status', async ({ page }) => {
  27 |     const allFilter = page.getByRole('button', { name: /^all$/i });
  28 |     if (await allFilter.isVisible()) {
  29 |       await allFilter.click();
  30 |       const tasks = page.locator('article');
  31 |       const count = await tasks.count();
  32 |       expect(count).toBeGreaterThan(0);
  33 |     }
  34 |   });
  35 | 
  36 |   // Test 4: Change task status
  37 |   test('should change task status', async ({ page }) => {
  38 |     const taskCard = page.locator('article').first();
  39 |     const statusButton = taskCard.getByRole('button').first();
  40 |     if (await statusButton.isVisible()) {
  41 |       await statusButton.click();
  42 |     }
  43 |   });
  44 | 
  45 |   // Test 5: Mark task as completed
  46 |   test('should mark task as completed', async ({ page }) => {
  47 |     const completedFilter = page.getByRole('button', { name: /completed/i });
  48 |     if (await completedFilter.isVisible()) {
  49 |       await completedFilter.click();
  50 |       await page.waitForTimeout(300);
  51 |     }
  52 |   });
  53 | 
  54 |   // Test 6: Edit task
  55 |   test('should open edit mode for task', async ({ page }) => {
  56 |     const taskCard = page.locator('article').first();
  57 |     const editButton = taskCard.getByRole('button', { name: /edit/i });
  58 |     if (await editButton.isVisible()) {
  59 |       await editButton.click();
  60 |     }
  61 |   });
  62 | 
  63 |   // Test 7: Delete task
  64 |   test('should show delete confirmation', async ({ page }) => {
  65 |     const taskCard = page.locator('article').first();
  66 |     const deleteButton = taskCard.getByRole('button', { name: /delete|remove/i });
  67 |     if (await deleteButton.isVisible()) {
  68 |       await deleteButton.click();
  69 |     }
  70 |   });
  71 | 
  72 |   // Test 8: Search tasks
  73 |   test('should search tasks', async ({ page }) => {
  74 |     const searchInput = page.getByPlaceholder(/search/i);
  75 |     if (await searchInput.isVisible()) {
  76 |       await searchInput.fill('test');
  77 |       await page.waitForTimeout(300);
  78 |     }
  79 |   });
  80 | });
  81 | 
```