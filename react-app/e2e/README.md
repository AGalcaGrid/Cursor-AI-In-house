# E2E Tests for Task Management Application

This directory contains comprehensive end-to-end tests using Playwright.

## Structure

```
e2e/
├── fixtures/
│   └── auth.fixture.ts      # Test fixtures and page objects
├── helpers/
│   └── test-helpers.ts      # Utility functions for tests
├── tests/
│   ├── auth.spec.ts         # Authentication tests (5 tests)
│   ├── tasks.spec.ts        # Task management tests (8 tests)
│   ├── navigation.spec.ts   # Navigation tests (4 tests)
│   ├── accessibility.spec.ts # Accessibility tests (6 tests)
│   ├── responsive.spec.ts   # Responsive design tests (8 tests)
│   └── errors.spec.ts       # Error handling tests (6 tests)
└── README.md
```

## Test Coverage

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| Authentication | 5 | Registration, login, logout, session persistence |
| Task Management | 8 | CRUD operations, filtering, search |
| Navigation | 4 | Page navigation, sidebar, back button |
| Accessibility | 6 | Keyboard nav, ARIA, contrast, focus |
| Responsive | 8 | Mobile, tablet, desktop, orientation |
| Error Handling | 6 | Network errors, validation, XSS |

**Total: 37 tests**

## Running Tests

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install

# Run all tests
npm run test:e2e

# Run tests with UI
npm run test:e2e:ui

# Run tests in headed mode (see browser)
npm run test:e2e:headed

# Run tests in debug mode
npm run test:e2e:debug

# View test report
npm run test:e2e:report
```

## Running Specific Tests

```bash
# Run only auth tests
npx playwright test auth.spec.ts

# Run only responsive tests
npx playwright test responsive.spec.ts

# Run tests matching a pattern
npx playwright test -g "should login"
```

## Test Configuration

Tests are configured in `playwright.config.ts`:

- **Browser**: Chromium (Desktop Chrome)
- **Base URL**: http://localhost:5174
- **Timeout**: 30 seconds per test
- **Retries**: 2 in CI, 0 locally
- **Screenshots**: On failure only
- **Video**: Retained on failure

## Writing New Tests

### Using Fixtures

```typescript
import { test, expect } from '../fixtures/auth.fixture';

test('my test', async ({ page, dashboardPage }) => {
  await dashboardPage.goto();
  // ... test code
});
```

### Using Helpers

```typescript
import { waitForPageLoad, setViewport } from '../helpers/test-helpers';

test('my test', async ({ page }) => {
  await setViewport(page, 'mobile');
  await waitForPageLoad(page);
  // ... test code
});
```

## CI/CD Integration

Tests run automatically in CI with:
- Single worker for stability
- 2 retries on failure
- HTML report generation
- Artifact upload on failure

## Debugging Failed Tests

1. Check the HTML report: `npm run test:e2e:report`
2. View screenshots in `test-results/`
3. Watch video recordings of failures
4. Run in debug mode: `npm run test:e2e:debug`
