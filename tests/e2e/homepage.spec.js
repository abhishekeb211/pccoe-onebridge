const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'https://abhishekeb211.github.io/pccoe-onebridge/';

test('homepage loads and shows main UI', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/OneBridge/i);
  await expect(page.locator('.hero-container')).toBeVisible();
});

test('tab navigation works correctly', async ({ page }) => {
  await page.goto('/');
  
  // Click Learn & Grow
  await page.click('.main-tab[data-tab="learn-grow"]');
  await expect(page.locator('#learn-grow')).toHaveClass(/active/);
  
  // Click Hire Me
  await page.click('.main-tab[data-tab="hire-me"]');
  await expect(page.locator('#hire-me')).toHaveClass(/active/);
  
  // Click Beyond Limits
  await page.click('.main-tab[data-tab="beyond-limits"]');
  await expect(page.locator('#beyond-limits')).toHaveClass(/active/);
});

test('global search filters content', async ({ page }) => {
  await page.goto('/');
  
  const searchInput = page.locator('#global-search');
  await searchInput.fill('UPSC');
  
  // Beyond Limits should show Ravi Raj (who has UPSC in achievement)
  const achieverCards = page.locator('#achiever-grid .achiever-card');
  await expect(achieverCards).toContainText(/UPSC/i);
  
  // Filter for something that doesn't exist
  await searchInput.fill('NonExistentScholarship123');
  await expect(page.locator('#achiever-grid')).toBeEmpty();
});
