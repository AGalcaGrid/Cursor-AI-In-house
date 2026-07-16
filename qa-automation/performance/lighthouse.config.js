/**
 * Lighthouse CI Configuration
 * Performance, accessibility, best practices, and SEO auditing
 */

module.exports = {
  ci: {
    collect: {
      // URLs to audit
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/login',
        'http://localhost:3000/dashboard',
        'http://localhost:3000/tickets'
      ],
      
      // Number of runs per URL for more accurate results
      numberOfRuns: 3,
      
      // Chrome flags for headless testing
      settings: {
        chromeFlags: '--no-sandbox --headless --disable-gpu',
        preset: 'desktop',
        throttling: {
          rttMs: 40,
          throughputKbps: 10240,
          cpuSlowdownMultiplier: 1,
          requestLatencyMs: 0,
          downloadThroughputKbps: 0,
          uploadThroughputKbps: 0
        },
        screenEmulation: {
          mobile: false,
          width: 1920,
          height: 1080,
          deviceScaleFactor: 1,
          disabled: false
        },
        formFactor: 'desktop',
        onlyCategories: [
          'performance',
          'accessibility',
          'best-practices',
          'seo'
        ]
      },
      
      // Start server before running tests
      startServerCommand: 'npm run start',
      startServerReadyPattern: 'Server is running',
      startServerReadyTimeout: 30000
    },
    
    assert: {
      // Assertion configuration
      assertions: {
        // Performance assertions
        'categories:performance': ['error', { minScore: 0.8 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.85 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
        
        // Core Web Vitals
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
        'speed-index': ['warn', { maxNumericValue: 3000 }],
        'interactive': ['error', { maxNumericValue: 3500 }],
        
        // Resource optimization
        'uses-optimized-images': 'warn',
        'uses-webp-images': 'warn',
        'uses-text-compression': 'error',
        'uses-responsive-images': 'warn',
        'efficient-animated-content': 'warn',
        
        // JavaScript optimization
        'unused-javascript': 'warn',
        'unminified-javascript': 'error',
        'unminified-css': 'error',
        'render-blocking-resources': 'warn',
        
        // Security
        'is-on-https': 'off', // Disabled for localhost
        'uses-http2': 'off',
        
        // Accessibility
        'color-contrast': 'error',
        'document-title': 'error',
        'html-has-lang': 'error',
        'meta-viewport': 'error',
        'image-alt': 'error',
        'label': 'error',
        'link-name': 'error',
        'button-name': 'error',
        
        // SEO
        'meta-description': 'warn',
        'crawlable-anchors': 'warn',
        'robots-txt': 'off' // Disabled for localhost
      },
      
      // Preset for specific environments
      preset: 'lighthouse:recommended'
    },
    
    upload: {
      // Upload results to Lighthouse CI server (if configured)
      target: 'temporary-public-storage',
      
      // Or use filesystem for local storage
      // target: 'filesystem',
      // outputDir: './reports/lighthouse'
    },
    
    server: {
      // Lighthouse CI server configuration (optional)
      // baseUrl: 'http://localhost:9001',
      // token: process.env.LHCI_TOKEN
    }
  },
  
  // Custom audits configuration
  extends: 'lighthouse:default',
  
  // Additional settings
  settings: {
    // Skip audits that don't apply
    skipAudits: [
      'uses-http2',
      'is-on-https'
    ],
    
    // Extra headers for authenticated pages
    extraHeaders: {
      'Authorization': 'Bearer ${LIGHTHOUSE_AUTH_TOKEN}'
    }
  }
};
