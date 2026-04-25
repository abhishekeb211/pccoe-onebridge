const { test, expect } = require('@playwright/test');

test.describe('Accessibility Feedback Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should allow user to submit accessibility feedback', async ({ page }) => {
    // 1. Open Feedback Modal
    const feedbackToggle = page.locator('#a11y-feedback-toggle');
    await feedbackToggle.click();

    const modal = page.locator('#a11y-feedback-modal');
    await expect(modal).toHaveClass(/active/);

    // 2. Fill Feedback
    const feedbackText = 'The contrast on the roadmap section is a bit low for me.';
    await page.fill('#a11y-feedback-desc', feedbackText);

    // 3. Submit
    await page.click('#a11y-feedback-form button[type="submit"]');

    // 4. Verify Success State
    const status = page.locator('#a11y-feedback-status');
    await expect(status).toHaveClass(/active/);
    await expect(page.locator('#a11y-feedback-form')).not.toBeVisible();

    // 5. Verify Auto-close (optional, depends on timeout)
    // The timeout is 2 seconds, so we can wait for it to disappear
    await expect(modal).not.toHaveClass(/active/, { timeout: 5000 });
  });

  test('should close modal when clicking X', async ({ page }) => {
    await page.click('#a11y-feedback-toggle');
    await page.click('#close-a11y-feedback');
    const modal = page.locator('#a11y-feedback-modal');
    await expect(modal).not.toHaveClass(/active/);
  });
});
