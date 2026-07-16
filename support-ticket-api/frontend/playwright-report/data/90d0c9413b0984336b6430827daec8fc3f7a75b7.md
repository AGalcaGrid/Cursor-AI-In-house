# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: accessibility.spec.ts >> Accessibility Tests >> should have no WCAG violations on authenticated pages
- Location: e2e/accessibility.spec.ts:25:3

# Error details

```
Error: expect(received).toEqual(expected) // deep equality

- Expected  -   1
+ Received  + 165

- Array []
+ Array [
+   Object {
+     "description": "Ensure buttons have discernible text",
+     "help": "Buttons must have discernible text",
+     "helpUrl": "https://dequeuniversity.com/rules/axe/4.11/button-name?application=playwright",
+     "id": "button-name",
+     "impact": "critical",
+     "nodes": Array [
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": null,
+             "id": "button-has-visible-text",
+             "impact": "critical",
+             "message": "Element does not have inner text that is visible to screen readers",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "aria-label",
+             "impact": "critical",
+             "message": "aria-label attribute does not exist or is empty",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "aria-labelledby",
+             "impact": "critical",
+             "message": "aria-labelledby attribute does not exist, references elements that do not exist or references elements that are empty",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": Object {
+               "messageKey": "noAttr",
+             },
+             "id": "non-empty-title",
+             "impact": "critical",
+             "message": "Element has no title attribute",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "implicit-label",
+             "impact": "critical",
+             "message": "Element does not have an implicit (wrapped) <label>",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "explicit-label",
+             "impact": "critical",
+             "message": "Element does not have an explicit <label>",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "presentational-role",
+             "impact": "critical",
+             "message": "Element's default semantics were not overridden with role=\"none\" or role=\"presentation\"",
+             "relatedNodes": Array [],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element does not have inner text that is visible to screen readers
+   aria-label attribute does not exist or is empty
+   aria-labelledby attribute does not exist, references elements that do not exist or references elements that are empty
+   Element has no title attribute
+   Element does not have an implicit (wrapped) <label>
+   Element does not have an explicit <label>
+   Element's default semantics were not overridden with role=\"none\" or role=\"presentation\"",
+         "html": "<button disabled=\"\" class=\"p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed\">",
+         "impact": "critical",
+         "none": Array [],
+         "target": Array [
+           ".disabled\\:opacity-50.disabled\\:cursor-not-allowed.p-2:nth-child(1)",
+         ],
+       },
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": null,
+             "id": "button-has-visible-text",
+             "impact": "critical",
+             "message": "Element does not have inner text that is visible to screen readers",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "aria-label",
+             "impact": "critical",
+             "message": "aria-label attribute does not exist or is empty",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "aria-labelledby",
+             "impact": "critical",
+             "message": "aria-labelledby attribute does not exist, references elements that do not exist or references elements that are empty",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": Object {
+               "messageKey": "noAttr",
+             },
+             "id": "non-empty-title",
+             "impact": "critical",
+             "message": "Element has no title attribute",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "implicit-label",
+             "impact": "critical",
+             "message": "Element does not have an implicit (wrapped) <label>",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "explicit-label",
+             "impact": "critical",
+             "message": "Element does not have an explicit <label>",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "presentational-role",
+             "impact": "critical",
+             "message": "Element's default semantics were not overridden with role=\"none\" or role=\"presentation\"",
+             "relatedNodes": Array [],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element does not have inner text that is visible to screen readers
+   aria-label attribute does not exist or is empty
+   aria-labelledby attribute does not exist, references elements that do not exist or references elements that are empty
+   Element has no title attribute
+   Element does not have an implicit (wrapped) <label>
+   Element does not have an explicit <label>
+   Element's default semantics were not overridden with role=\"none\" or role=\"presentation\"",
+         "html": "<button disabled=\"\" class=\"p-2 rounded-lg border hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed\">",
+         "impact": "critical",
+         "none": Array [],
+         "target": Array [
+           ".disabled\\:opacity-50.disabled\\:cursor-not-allowed.p-2:nth-child(2)",
+         ],
+       },
+     ],
+     "tags": Array [
+       "cat.name-role-value",
+       "wcag2a",
+       "wcag412",
+       "section508",
+       "section508.22.a",
+       "TTv5",
+       "TT6.a",
+       "EN-301-549",
+       "EN-9.4.1.2",
+       "ACT",
+       "RGAAv4",
+       "RGAA-11.9.1",
+     ],
+   },
+ ]
```

# Page snapshot

```yaml
- generic [ref=e3]:
  - link "Skip to main content" [ref=e4] [cursor=pointer]:
    - /url: "#main-content"
  - navigation "Main navigation" [ref=e5]:
    - link "Support Desk" [ref=e7] [cursor=pointer]:
      - /url: /
    - navigation "Sidebar navigation" [ref=e8]:
      - link "Tickets" [ref=e9] [cursor=pointer]:
        - /url: /tickets
        - img [ref=e10]
        - generic [ref=e12]: Tickets
      - link "New Ticket" [ref=e13] [cursor=pointer]:
        - /url: /tickets/new
        - img [ref=e14]
        - generic [ref=e15]: New Ticket
      - link "Settings" [ref=e16] [cursor=pointer]:
        - /url: /settings
        - img [ref=e17]
        - generic [ref=e20]: Settings
    - button "Switch to dark mode" [ref=e22] [cursor=pointer]:
      - img [ref=e23]
      - generic [ref=e25]: Dark Mode
  - generic [ref=e26]:
    - banner [ref=e27]:
      - heading "Tickets" [level=1] [ref=e29]
      - generic [ref=e30]:
        - button "Notifications, 2 unread" [ref=e32] [cursor=pointer]:
          - img [ref=e33]
          - generic [ref=e36]: "2"
        - button "User menu" [ref=e38] [cursor=pointer]:
          - img [ref=e40]
          - generic [ref=e43]: Test Customer
          - img [ref=e44]
    - main [ref=e46]:
      - generic [ref=e47]:
        - generic [ref=e48]:
          - generic [ref=e49]:
            - heading "Tickets" [level=1] [ref=e50]
            - paragraph [ref=e51]: Your support tickets
          - link "New Ticket" [ref=e52] [cursor=pointer]:
            - /url: /tickets/new
            - img [ref=e53]
            - text: New Ticket
        - generic [ref=e55]:
          - generic [ref=e56]:
            - img [ref=e57]
            - textbox "Search tickets..." [ref=e60]
          - generic [ref=e61]:
            - generic [ref=e62]:
              - img [ref=e63]
              - combobox [ref=e65]:
                - option "All Status" [selected]
                - option "Open"
                - option "Assigned"
                - option "In Progress"
                - option "Waiting"
                - option "Resolved"
                - option "Closed"
            - combobox [ref=e66]:
              - option "All Priority" [selected]
              - option "Low"
              - option "Medium"
              - option "High"
              - option "Urgent"
        - generic [ref=e67]:
          - table [ref=e69]:
            - rowgroup [ref=e70]:
              - row "Ticket Status Priority Category Created SLA" [ref=e71]:
                - columnheader "Ticket" [ref=e72]
                - columnheader "Status" [ref=e73]
                - columnheader "Priority" [ref=e74]
                - columnheader "Category" [ref=e75]
                - columnheader "Created" [ref=e76]
                - columnheader "SLA" [ref=e77]
            - rowgroup [ref=e78]:
              - row "Its a subject test TICK-20260624-0001 open medium general Jun 24, 07:47 AM On Track" [ref=e79] [cursor=pointer]:
                - cell "Its a subject test TICK-20260624-0001" [ref=e80]:
                  - generic [ref=e81]:
                    - paragraph [ref=e82]: Its a subject test
                    - paragraph [ref=e83]: TICK-20260624-0001
                - cell "open" [ref=e84]:
                  - generic [ref=e85]: open
                - cell "medium" [ref=e86]:
                  - generic [ref=e87]:
                    - img [ref=e88]
                    - text: medium
                - cell "general" [ref=e91]
                - cell "Jun 24, 07:47 AM" [ref=e92]
                - cell "On Track" [ref=e93]
          - generic [ref=e94]:
            - paragraph [ref=e95]: Page 1 of 1
            - generic [ref=e96]:
              - button [disabled] [ref=e97]:
                - img [ref=e98]
              - button [disabled] [ref=e100]:
                - img [ref=e101]
```

# Test source

```ts
  1   | import { test, expect, testUsers } from './fixtures/test-fixtures';
  2   | import AxeBuilder from '@axe-core/playwright';
  3   | 
  4   | test.describe('Accessibility Tests', () => {
  5   |   // Combined: WCAG compliance for public pages (2 -> 1)
  6   |   test('should have no critical WCAG violations on public pages', async ({ page }) => {
  7   |     // Login page
  8   |     await page.goto('/login');
  9   |     let results = await new AxeBuilder({ page })
  10  |       .withTags(['wcag2a', 'wcag2aa'])
  11  |       .disableRules(['color-contrast']) // Known issue: demo account text has low contrast
  12  |       .analyze();
  13  |     expect(results.violations).toEqual([]);
  14  | 
  15  |     // Registration page
  16  |     await page.goto('/register');
  17  |     results = await new AxeBuilder({ page })
  18  |       .withTags(['wcag2a', 'wcag2aa'])
  19  |       .disableRules(['color-contrast'])
  20  |       .analyze();
  21  |     expect(results.violations).toEqual([]);
  22  |   });
  23  | 
  24  |   // Combined: WCAG compliance for authenticated pages (3 -> 1)
  25  |   test('should have no WCAG violations on authenticated pages', async ({ page }) => {
  26  |     await page.goto('/login');
  27  |     await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
  28  |     await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
  29  |     await page.getByRole('button', { name: /sign in/i }).click();
  30  |     await expect(page).toHaveURL(/\/(tickets|dashboard)/);
  31  | 
  32  |     // Tickets page
  33  |     await page.goto('/tickets');
  34  |     let results = await new AxeBuilder({ page })
  35  |       .withTags(['wcag2a', 'wcag2aa'])
  36  |       .disableRules(['color-contrast', 'select-name']) // Known UI issues
  37  |       .analyze();
> 38  |     expect(results.violations).toEqual([]);
      |                                ^ Error: expect(received).toEqual(expected) // deep equality
  39  | 
  40  |     // Settings page
  41  |     await page.goto('/settings');
  42  |     results = await new AxeBuilder({ page })
  43  |       .withTags(['wcag2a', 'wcag2aa'])
  44  |       .disableRules(['color-contrast', 'select-name'])
  45  |       .analyze();
  46  |     expect(results.violations).toEqual([]);
  47  |   });
  48  | 
  49  |   // Combined: Keyboard navigation + focus + Enter submit (3 -> 1)
  50  |   test('should support full keyboard navigation', async ({ page }) => {
  51  |     await page.goto('/login');
  52  | 
  53  |     // Tab through form elements - find email input
  54  |     const emailInput = page.getByPlaceholder(/email|you@example/i);
  55  |     await emailInput.focus();
  56  |     
  57  |     // Check focus indicator
  58  |     const focusStyles = await emailInput.evaluate((el) => {
  59  |       const styles = window.getComputedStyle(el);
  60  |       return { outline: styles.outline, boxShadow: styles.boxShadow };
  61  |     });
  62  |     expect(focusStyles.outline !== 'none' || focusStyles.boxShadow !== 'none').toBeTruthy();
  63  | 
  64  |     // Fill and submit with Enter
  65  |     await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
  66  |     await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
  67  |     await page.keyboard.press('Enter');
  68  |     await expect(page).toHaveURL(/\/(tickets|dashboard)/);
  69  |   });
  70  | 
  71  |   // Combined: Screen reader support (4 -> 1)
  72  |   test('should have proper screen reader support', async ({ page }) => {
  73  |     await page.goto('/login');
  74  | 
  75  |     // Check heading hierarchy
  76  |     const h1 = page.locator('h1');
  77  |     await expect(h1).toBeVisible();
  78  | 
  79  |     // Check form has inputs with placeholders (accessible)
  80  |     const emailInput = page.getByPlaceholder(/email|you@example/i);
  81  |     await expect(emailInput).toBeVisible();
  82  | 
  83  |     // Login and check ARIA roles
  84  |     await page.getByPlaceholder(/email|you@example/i).fill(testUsers.customer.email);
  85  |     await page.getByPlaceholder(/password|••••/i).fill(testUsers.customer.password);
  86  |     await page.getByRole('button', { name: /sign in/i }).click();
  87  |     await expect(page).toHaveURL(/\/(tickets|dashboard)/);
  88  | 
  89  |     // Check navigation and main roles
  90  |     const nav = page.locator('nav, [role="navigation"]');
  91  |     await expect(nav.first()).toBeVisible();
  92  |     const main = page.locator('main, [role="main"]');
  93  |     await expect(main.first()).toBeVisible();
  94  |   });
  95  | 
  96  |   // Color contrast - check main interactive elements (excluding demo text)
  97  |   test('should have sufficient color contrast on main elements', async ({ page }) => {
  98  |     await page.goto('/login');
  99  | 
  100 |     const results = await new AxeBuilder({ page })
  101 |       .withTags(['wcag2aa'])
  102 |       .include('button, input, a, h1, h2, label')
  103 |       .analyze();
  104 | 
  105 |     const contrastViolations = results.violations.filter((v) => v.id === 'color-contrast');
  106 |     expect(contrastViolations).toEqual([]);
  107 |   });
  108 | });
  109 | 
```