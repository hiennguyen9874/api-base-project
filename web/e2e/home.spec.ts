import { expect, test } from '@playwright/test'

test('shows the application shell', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'CashLens' })).toBeVisible()
})
