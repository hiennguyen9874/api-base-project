import { expect, test } from '@playwright/test'

import { expectDashboard, signIn } from './auth-helpers'

const email = process.env.CASHLENS_E2E_EMAIL
const password = process.env.CASHLENS_E2E_PASSWORD
const apiOrigin = process.env.CASHLENS_E2E_API_ORIGIN ?? 'http://localhost:11112'

if (!email || !password) {
  throw new Error(
    'Set CASHLENS_E2E_EMAIL and CASHLENS_E2E_PASSWORD before running pnpm test:e2e:real.'
  )
}

const credentials = { email, password }

test.describe('CashLens real backend cookie lifecycle', () => {
  test('logs in with credentialed cookies and restores after reload', async ({ page }) => {
    await signIn(page, credentials)
    await expectDashboard(page, email)

    const cookies = await page.context().cookies(apiOrigin)
    expect(cookies.map(cookie => cookie.name)).toEqual(
      expect.arrayContaining(['access_token', 'refresh_token'])
    )
    expect(cookies.every(cookie => cookie.httpOnly)).toBe(true)

    const storage = await page.evaluate(() => ({
      localStorage: window.localStorage.length,
      sessionStorage: window.sessionStorage.length,
    }))
    expect(storage).toEqual({ localStorage: 0, sessionStorage: 0 })
    expect(page.url()).not.toContain('token')

    await page.reload()
    await expectDashboard(page, email)
  })

  test('refreshes after the access cookie is replaced with an invalid value', async ({ page }) => {
    await signIn(page, credentials)
    await expectDashboard(page, email)

    const refreshBefore = (await page.context().cookies(apiOrigin)).find(
      cookie => cookie.name === 'refresh_token'
    )
    expect(refreshBefore).toBeDefined()

    // The backend JWT contains second-resolution expiry only; cross a second
    // boundary so a rotated token has a distinct serialized value.
    await page.waitForTimeout(1100)
    await page.context().clearCookies({ name: 'access_token' })
    await page
      .context()
      .addCookies([{ name: 'access_token', value: 'expired-access-token', url: apiOrigin }])

    await page.goto('/')
    await expectDashboard(page, email)

    const cookies = await page.context().cookies(apiOrigin)
    const accessAfter = cookies.find(cookie => cookie.name === 'access_token')
    const refreshAfter = cookies.find(cookie => cookie.name === 'refresh_token')
    expect(accessAfter?.value).not.toBe('expired-access-token')
    expect(refreshAfter?.value).not.toBe(refreshBefore?.value)
  })

  test('revokes the session on logout and rejects current-user afterward', async ({ page }) => {
    await signIn(page, credentials)
    await expectDashboard(page, email)

    await page.getByRole('button', { name: 'Đăng xuất' }).click()
    await expect(page.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()

    const currentUserStatus = await page.evaluate(async origin => {
      const response = await fetch(`${origin}/api/v0/users/me`, {
        credentials: 'include',
      })
      return response.status
    }, apiOrigin)
    expect(currentUserStatus).toBe(401)

    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()
    await expect(page.getByText(email)).toHaveCount(0)
  })
})
