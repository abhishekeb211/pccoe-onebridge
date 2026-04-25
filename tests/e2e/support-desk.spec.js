const { test, expect } = require('@playwright/test');

test.describe('Support Desk Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should allow student to login and send a message', async ({ page }) => {
    // 1. Open Support Modal
    const supportToggle = page.locator('#support-toggle');
    await supportToggle.click();

    const modal = page.locator('#support-modal');
    await expect(modal).toHaveClass(/active/);

    // 2. Login with PRN
    await page.fill('#chat-student-prn', '103221001');
    await page.click('#chat-start-form button[type="submit"]');

    // 3. Verify Chat View
    const chatView = page.locator('#chat-view');
    await expect(chatView).toBeVisible();

    // 4. Send a message
    const chatInput = page.locator('#chat-input');
    await chatInput.fill('WiFi');
    await page.click('#send-chat-msg');

    // 5. Verify Student Message
    const studentMsg = page.locator('.msg.student-msg').last();
    await expect(studentMsg).toContainText('WiFi');

    // 6. Verify Bot Response (Mock)
    const botMsg = page.locator('.msg.bot-msg').last();
    // Wait for the timeout-based response
    await expect(botMsg).toContainText(/\(Demo\)/i, { timeout: 5000 });
  });

  test('should close modal when clicking X', async ({ page }) => {
    await page.click('#support-toggle');
    await page.click('.close-modal');
    const modal = page.locator('#support-modal');
    await expect(modal).not.toHaveClass(/active/);
  });
});
